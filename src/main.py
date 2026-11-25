# src/main.py - 14주차: 전체 모듈을 하나로 통합하는 메인 컨트롤 타워
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from input_module import get_record
from storage_module import save_record, update_progress
from analysis_module import (
    load_records,
    analyze_by_member,
    calculate_weighted_contribution,
    count_by_status,
)
from report_module import draw_bar, make_feedback


def generate_ai_prompt(records, member_avgs, shares, feedbacks):
    """13주차 교안 AX 2단계 적용: 집계 결과를 AI 회의록 생성용 프롬프트로 변환한다."""
    overall_avg = round(sum(int(r["progress"]) for r in records) / len(records), 1)
    print("\n" + "=" * 55)
    print("[AX 2단계: ChatGPT / Gemini 붙여넣기용 주간 회의 프롬프트]")
    print("=" * 55)
    print("당신은 대학생 조별과제 프로젝트 매니저(PM)입니다.")
    print(f"현재 팀 전체 평균 진행률은 {overall_avg}%이며, 팀원별 평균 진행률은 {member_avgs}, 객관적 기여도 지분(%)은 {shares}입니다.")
    print("시스템이 탐지한 주요 위험 경고는 다음과 같습니다:")
    for fb in feedbacks:
        print(f"- {fb}")
    print("\n위 데이터를 바탕으로 (1) 이번 주 주간 회의 핵심 안건 3가지와 (2) 지연 업무 해결을 위한 업무 재분배 방안을 제안해 주세요.")
    print("=" * 55 + "\n")


def main():
    while True:
        print("\n==============================================")
        print("   <팀플 기여도 & 일정 관리 시스템 v2.0>   ")
        print("==============================================")
        print(" 1. 팀플 현황 조회 및 객관적 기여도 지분 집계")
        print(" 2. 새 팀플 태스크 등록 및 저장")
        print(" 3. 기존 태스크 진행률 실시간 수정")
        print(" 4. 주간 리포트(그래프 이미지 + 경고 피드백) 생성")
        print(" 5. AI 주간 회의 안건 프롬프트 추출 (AX 확장)")
        print(" 0. 프로그램 종료")
        print("----------------------------------------------")

        menu = input("원하는 메뉴 번호를 선택하세요: ").strip()

        if menu == "1":
            recs = load_records()
            avgs, counts = analyze_by_member(recs)
            shares = calculate_weighted_contribution(recs)
            status = count_by_status(recs)
            overall = round(sum(int(r["progress"]) for r in recs) / len(recs), 1)
            print(f"\n[전체 요약] 총 {len(recs)}건 | 팀 평균 진행률 {overall}%")
            for m, avg in avgs.items():
                print(f" - {m}: 평균 {avg}% | 기여도 지분 {shares[m]}% (담당 {counts[m]}건)")
            print("[상태 현황]", status)

        elif menu == "2":
            rec = get_record()
            if rec:
                save_record(rec)
                print("새 태스크가 성공적으로 저장되었습니다.")

        elif menu == "3":
            update_progress()

        elif menu == "4":
            recs = load_records()
            avgs, _ = analyze_by_member(recs)
            draw_bar(avgs)
            print("\n[규칙 기반 자동 피드백 결과]")
            for msg in make_feedback(recs, avgs, target_progress=80):
                print("▶", msg)

        elif menu == "5":
            recs = load_records()
            avgs, _ = analyze_by_member(recs)
            shares = calculate_weighted_contribution(recs)
            fbs = make_feedback(recs, avgs, target_progress=80)
            generate_ai_prompt(recs, avgs, shares, fbs)

        elif menu == "0":
            print("팀플 기여도 & 일정 관리 시스템을 종료합니다.")
            break
        else:
            print("0~5 사이의 올바른 번호를 입력해 주세요.")


if __name__ == "__main__":
    main()