# src/report_module.py - 13주차: 팀원별 진행률을 그래프로 그리고, 규칙으로 피드백한다
import matplotlib
matplotlib.use("Agg")  # 창을 띄우지 않고 이미지 파일로 바로 저장
import matplotlib.pyplot as plt
from datetime import date

# 윈도우 한글 글꼴 지정 (맥OS 사용 시 "AppleGothic"으로 변경)
matplotlib.rc("font", family="Malgun Gothic")
matplotlib.rcParams["axes.unicode_minus"] = False  # 마이너스 기호 깨짐 방지


def draw_bar(member_avgs, out="data/weekly_report.png"):
    """팀원별 평균 진행률(%)을 막대그래프로 저장한다."""
    members = list(member_avgs.keys())
    avgs = list(member_avgs.values())

    plt.figure(figsize=(8, 4.5))
    plt.bar(members, avgs)
    plt.ylim(0, 110)  # 100% 막대 위쪽에 여백 확보
    plt.title("팀원별 평균 진행률 (%)")
    plt.xlabel("팀원")
    plt.ylabel("평균 진행률 (%)")
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    print("저장 완료:", out)


def make_feedback(records, member_avgs, target_progress=80, today=None):
    """집계 결과를 바탕으로 팀플 일정·기여도 피드백 메시지를 만든다 (규칙 4개)."""
    messages = []
    base_day = today or date.today()
    overall_avg = round(sum(int(r["progress"]) for r in records) / len(records), 1)

    # 규칙 1: 팀 전체 목표 진행률 달성 여부 확인
    if overall_avg < target_progress:
        gap = round(target_progress - overall_avg, 1)
        messages.append(
            f"[목표 진행률] 목표 {target_progress}% 중 현재 {overall_avg}% 달성 — {gap}%p 추가 진행이 필요합니다."
        )

    # 규칙 2: 기여도(진행률) 저조 팀원 경고 (전체 평균의 절반 미만)
    weakest = min(member_avgs, key=member_avgs.get)
    if member_avgs[weakest] < overall_avg / 2:
        messages.append(
            f"[기여도 경고] '{weakest}' 팀원의 평균 진행률({member_avgs[weakest]}%)이 팀 평균({overall_avg}%)의 절반 미만입니다."
        )

    # 규칙 3: 마감일 경과(지연) 태스크 경고
    for r in records:
        prog = int(r["progress"])
        due = date.fromisoformat(r["due_date"])
        if prog < 100 and due < base_day:
            overdue_days = (base_day - due).days
            messages.append(
                f"[지연 경고] {r['member']} - '{r['task']}' 마감일이 {overdue_days}일 지났습니다 (현재 {prog}%)."
            )

    # 규칙 4: 마감 임박(D-3 이내) 태스크 알림
    for r in records:
        prog = int(r["progress"])
        due = date.fromisoformat(r["due_date"])
        days_left = (due - base_day).days
        if prog < 100 and 0 <= days_left <= 3:
            messages.append(
                f"[마감 임박] {r['member']} - '{r['task']}' 마감 D-{days_left}입니다 (현재 {prog}%)."
            )

    return messages


if __name__ == "__main__":
    from analysis_module import load_records, analyze_by_member

    recs = load_records()
    member_avgs, _ = analyze_by_member(recs)

    draw_bar(member_avgs)
    for msg in make_feedback(recs, member_avgs, target_progress=80):
        print("▶", msg)