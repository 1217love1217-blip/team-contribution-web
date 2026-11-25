# app.py - 14주차 최종 결과물: <팀플 기여도 & 일정 관리 상용 웹 서비스>
import os
import sys
import csv
import io
from datetime import date
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from analysis_module import (
    load_records,
    analyze_by_member,
    calculate_weighted_contribution,
    count_by_status,
)
from storage_module import FIELDS, DEFAULT_FILE, save_record, overwrite_records
from report_module import make_feedback, draw_bar

st.set_page_config(
    page_title="팀플 기여도 & 일정 관리 플랫폼",
    page_icon="📊",
    layout="wide",
)

# --- 사이드바: 멀티 팀 워크스페이스 및 CSV 입출력 ---
st.sidebar.title("🏢 팀 워크스페이스")
os.makedirs("data/teams", exist_ok=True)

team_files = {"기본 프로젝트 (13주차 대표 팀)": DEFAULT_FILE}
for fname in sorted(os.listdir("data/teams")):
    if fname.endswith(".csv"):
        team_name = fname[:-4]
        team_files[f"팀: {team_name}"] = os.path.join("data/teams", fname)

selected_label = st.sidebar.selectbox("현재 관리 중인 팀 선택", list(team_files.keys()))
active_file = team_files[selected_label]

# 새 팀 만들기 (다른 사람들도 자기 팀을 바로 생성해 사용 가능)
with st.sidebar.expander("➕ 새 조별과제 팀 만들기"):
    new_team_name = st.text_input("새 팀 이름", placeholder="예: 경영학 조별과제 3조")
    if st.button("팀 워크스페이스 생성"):
        clean_name = new_team_name.strip().replace("/", "_")
        if clean_name:
            new_path = os.path.join("data/teams", f"{clean_name}.csv")
            if not os.path.exists(new_path):
                overwrite_records([], new_path)
            st.success(f"'{clean_name}' 팀이 생성되었습니다!")
            st.rerun()

st.sidebar.markdown("---")
target_progress = st.sidebar.slider("팀 목표 평균 진행률 (%)", 50, 100, 80, 5)

# 외부 CSV 업로드 & 현재 데이터 다운로드
uploaded_file = st.sidebar.file_uploader("📂 기존 팀 CSV 불러오기", type=["csv"])
if uploaded_file is not None:
    content = uploaded_file.getvalue().decode("utf-8-sig")
    reader = list(csv.DictReader(io.StringIO(content)))
    if reader and set(FIELDS).issubset(set(reader[0].keys())):
        overwrite_records(reader, active_file)
        st.sidebar.success(f"총 {len(reader)}건 적용 완료!")
    else:
        st.sidebar.error("열 이름(member, task, due_date, progress, memo)을 확인해 주세요.")

if os.path.exists(active_file):
    with open(active_file, "rb") as f:
        st.sidebar.download_button(
            label="📥 현재 팀 데이터(CSV) 다운로드",
            data=f,
            file_name=os.path.basename(active_file),
            mime="text/csv",
        )

# --- 메인 대시보드 헤더 ---
st.title("📊 팀플 기여도 & 일정 관리 웹 플랫폼")
st.caption(f"현재 접속 워크스페이스: **{selected_label}** | 마감 준수 가중치 기반 객관적 기여도 산출 시스템")

records = load_records(active_file)

# --- 기능별 4개 탭 ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 기여도 & 리스크 대시보드",
    "➕ 새 태스크 등록",
    "✏️ 진행률 실시간 수정 · 삭제",
    "🤖 AI 주간 회의 안건 생성 (AX)",
])

with tab1:
    if not records:
        st.info("아직 등록된 태스크가 없습니다. [➕ 새 태스크 등록] 탭에서 첫 업무를 추가해 주세요!")
    else:
        member_avgs, member_counts = analyze_by_member(records)
        shares = calculate_weighted_contribution(records)
        status_counts = count_by_status(records)
        overall_avg = round(sum(int(r["progress"]) for r in records) / len(records), 1)

        # KPI 4개 카드
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("전체 등록 태스크", f"{len(records)}건")
        c2.metric("팀 전체 평균 진행률", f"{overall_avg}%", delta=f"{round(overall_avg - target_progress, 1)}%p (목표 대비)")
        c3.metric("완료된 태스크", f"{status_counts['완료(100%)']}건")
        c4.metric("지연(마감 경과) 태스크", f"{status_counts['지연(마감경과)']}건", delta_color="inverse")

        st.markdown("---")
        st.subheader("🚨 실시간 일정 및 기여도 리스크 자동 진단")
        feedbacks = make_feedback(records, member_avgs, target_progress=target_progress)
        if not feedbacks:
            st.success("🎉 모든 팀원이 목표 진행률을 달성했으며 지연된 업무가 없습니다!")
        else:
            for msg in feedbacks:
                if "[지연 경고]" in msg or "[기여도 경고]" in msg:
                    st.error(f"🔴 {msg}")
                else:
                    st.warning(f"🟡 {msg}")

        st.markdown("---")
        left_col, right_col = st.columns([1.2, 1])
        with left_col:
            st.markdown("#### 팀원별 평균 진행률 (%)")
            st.bar_chart(member_avgs, height=320)

        with right_col:
            st.markdown("#### 객관적 기여도 지분(%) 및 종합 평가표")
            st.caption("※ 기한 내 완수(1.2x), 정상 진행(1.0x), 마감 지연(0.8x) 가중치 반영")
            summary_rows = [
                {
                    "팀원": m,
                    "평균 진행률": f"{avg}%",
                    "기여도 지분(%)": f"{shares[m]}%",
                    "담당 업무": f"{member_counts[m]}건",
                    "진단": "우수" if avg >= target_progress else ("주의 필요" if avg < overall_avg / 2 else "양호"),
                }
                for m, avg in member_avgs.items()
            ]
            st.dataframe(summary_rows, use_container_width=True, hide_index=True)

            if st.button("🖼️ 보고서용 그래프 이미지(PNG) 저장"):
                draw_bar(member_avgs)
                st.success("data/weekly_report.png 파일이 최신 상태로 갱신되었습니다!")

        st.markdown("#### 전체 태스크 상세 내역")
        st.dataframe(records, use_container_width=True, hide_index=True)

with tab2:
    st.markdown("#### 새로운 팀플 업무 등록")
    with st.form("add_task_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        new_member = col_a.text_input("담당 팀원 이름", placeholder="예: 이다현")
        new_due = col_b.date_input("마감일", value=date.today())
        new_task = st.text_input("담당 태스크(업무명)", placeholder="예: 최종 발표 시연 점검")
        new_prog = st.slider("현재 진행률 (%)", 0, 100, 0, step=10)
        new_memo = st.text_input("진행 메모", placeholder="예: 초안 작성 완료")

        if st.form_submit_button("✅ 태스크 저장하기"):
            if not new_member.strip() or not new_task.strip():
                st.error("팀원 이름과 담당 태스크를 모두 입력해 주세요.")
            else:
                save_record(
                    {
                        "member": new_member.strip(),
                        "task": new_task.strip(),
                        "due_date": str(new_due),
                        "progress": str(new_prog),
                        "memo": new_memo.strip() or "-",
                    },
                    active_file,
                )
                st.success(f"[{new_member}] '{new_task}' 등록 완료!")
                st.rerun()

with tab3:
    if not records:
        st.info("수정할 태스크가 없습니다.")
    else:
        st.markdown("#### 기존 태스크 진행률 업데이트")
        labels = [
            f"[{i+1}] {r['member']} - {r['task']} (현재 {r['progress']}% / 마감 {r['due_date']})"
            for i, r in enumerate(records)
        ]
        idx = st.selectbox("수정할 태스크 선택", range(len(records)), format_func=lambda x: labels[x])
        target = records[idx]

        u1, u2 = st.columns([2, 1])
        new_p = u1.slider("변경할 진행률 (%)", 0, 100, int(target["progress"]), step=5)
        new_m = u2.text_input("변경 메모", value=target["memo"])

        b1, b2 = st.columns([1, 4])
        if b1.button("💾 진행률 반영"):
            records[idx]["progress"] = str(new_p)
            records[idx]["memo"] = new_m.strip() or "-"
            overwrite_records(records, active_file)
            st.success("반영 완료! 대시보드와 경고 배너가 즉시 업데이트됩니다.")
            st.rerun()

        if b2.button("🗑️ 태스크 삭제"):
            records.pop(idx)
            overwrite_records(records, active_file)
            st.warning("태스크가 삭제되었습니다.")
            st.rerun()

with tab4:
    if not records:
        st.info("데이터를 먼저 등록해 주세요.")
    else:
        st.markdown("#### 🤖 AI 주간 회의록 및 업무 재분배 프롬프트 자동 생성")
        member_avgs, _ = analyze_by_member(records)
        shares = calculate_weighted_contribution(records)
        overall_avg = round(sum(int(r["progress"]) for r in records) / len(records), 1)
        fbs = make_feedback(records, member_avgs, target_progress=target_progress)
        fb_text = "\n".join([f"- {m}" for m in fbs]) if fbs else "- 특이 경고 없음"

        prompt_text = f"""당신은 대학생 조별과제 프로젝트 매니저(PM)입니다.
현재 '{selected_label}'의 진행 데이터는 다음과 같습니다.

1. 전체 태스크 수: {len(records)}건 (팀 평균 진행률 {overall_avg}%, 목표 {target_progress}%)
2. 팀원별 평균 진행률: {member_avgs}
3. 마감 준수 가중치 반영 객관적 기여도 지분(%): {shares}
4. 시스템 자동 탐지 위험 경고:
{fb_text}

위 객관적 수치를 바탕으로 (1) 이번 주 회의에서 반드시 다룰 핵심 안건 3가지와 (2) 지연 업무 해소를 위한 팀원 간 업무 재분배안을 제안해 주세요."""
        st.code(prompt_text, language="text")