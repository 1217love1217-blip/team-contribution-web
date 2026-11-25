# src/analysis_module.py - 14주차 고도화: 팀원별 평균 진행률 + 가중치 기반 객관적 기여도 지분 산출
import csv
import os
from collections import defaultdict
from datetime import date

FILE = "data/study_log.csv"


def load_records(file_path=FILE):
    """CSV의 모든 팀플 기록을 읽어 리스트로 돌려준다."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def analyze_by_member(records):
    """팀원별 평균 진행률(%)과 담당 태스크 수를 계산해 진행률이 큰 순서로 반환한다."""
    total_prog = defaultdict(int)
    task_count = defaultdict(int)

    for r in records:
        m = r["member"]
        total_prog[m] += int(r["progress"])
        task_count[m] += 1

    avg_dict = {
        m: round(total_prog[m] / task_count[m], 1) for m in total_prog
    }
    sorted_avg = dict(sorted(avg_dict.items(), key=lambda x: x[1], reverse=True))
    return sorted_avg, dict(task_count)


def calculate_weighted_contribution(records, today=None):
    """마감 준수 가중치(기한 내 완료 1.2배, 지연 미완료 0.8배)를 반영해 팀 내 기여도 지분(%)을 산출한다."""
    base_day = today or date.today()
    scores = defaultdict(float)

    for r in records:
        m = r["member"]
        prog = int(r["progress"])
        due = date.fromisoformat(r["due_date"])

        if prog >= 100 and due >= base_day:
            weight = 1.2  # 기한 내 완수 가산점
        elif prog < 100 and due < base_day:
            weight = 0.8  # 마감 경과 지연 감점
        else:
            weight = 1.0  # 정상 진행

        scores[m] += prog * weight

    total_score = sum(scores.values())
    if total_score == 0:
        return {m: 0.0 for m in scores}

    share_dict = {
        m: round((sc / total_score) * 100, 1) for m, sc in scores.items()
    }
    return dict(sorted(share_dict.items(), key=lambda x: x[1], reverse=True))


def count_by_status(records, today=None):
    """태스크 상태별(완료 / 진행중 / 지연) 건수를 집계한다."""
    base_day = today or date.today()
    status = {"완료(100%)": 0, "진행중": 0, "지연(마감경과)": 0}

    for r in records:
        prog = int(r["progress"])
        due = date.fromisoformat(r["due_date"])
        if prog >= 100:
            status["완료(100%)"] += 1
        elif due < base_day:
            status["지연(마감경과)"] += 1
        else:
            status["진행중"] += 1
    return status


if __name__ == "__main__":
    recs = load_records()
    member_avgs, member_counts = analyze_by_member(recs)
    shares = calculate_weighted_contribution(recs)
    status_counts = count_by_status(recs)
    overall_avg = round(sum(int(r["progress"]) for r in recs) / len(recs), 1)

    print(f"=== 팀플 기여도 & 일정 집계 (총 {len(recs)}건 / 전체 평균 진행률 {overall_avg}%) ===")
    print("\n[팀원별 평균 진행률 및 객관적 기여도 지분]")
    for m, avg in member_avgs.items():
        print(f"- {m}: 평균 진행률 {avg}% | 객관적 기여도 지분 {shares[m]}% (담당 {member_counts[m]}건)")

    print("\n[태스크 진행 상태별 현황]")
    for st, cnt in status_counts.items():
        print(f"- {st}: {cnt}건")
