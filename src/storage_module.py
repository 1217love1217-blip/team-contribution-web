# src/storage_module.py - 14주차 고도화: 저장, 실시간 수정·삭제 및 멀티 팀 파일 지원
import csv
import os

DEFAULT_FILE = "data/study_log.csv"
FIELDS = ["member", "task", "due_date", "progress", "memo"]


def save_record(record, file_path=DEFAULT_FILE):
    """팀플 태스크 기록 1건을 지정된 CSV 파일 끝에 덧붙인다."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    is_new = not os.path.exists(file_path)
    with open(file_path, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerow(record)
    return True


def overwrite_records(records, file_path=DEFAULT_FILE):
    """수정·삭제된 전체 기록 리스트를 CSV 파일에 다시 저장한다."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)


def update_progress(file_path=DEFAULT_FILE):
    """터미널(CLI)에서 태스크 번호를 선택해 진행률과 메모를 수정한다."""
    if not os.path.exists(file_path):
        print("저장된 데이터가 없습니다.")
        return False

    with open(file_path, "r", encoding="utf-8-sig") as f:
        records = list(csv.DictReader(f))

    print("\n=== 현재 등록된 팀플 태스크 목록 ===")
    for idx, r in enumerate(records, start=1):
        print(f"[{idx}] {r['member']} | {r['task']} | 마감: {r['due_date']} | 진행률: {r['progress']}% ({r['memo']})")

    try:
        choice = int(input("\n수정할 태스크 번호를 입력하세요 (취소=0): "))
        if choice == 0 or not (1 <= choice <= len(records)):
            print("수정을 취소했습니다.")
            return False

        new_prog = int(input("새로운 진행률 (0~100): "))
        if not (0 <= new_prog <= 100):
            print("0~100 사이의 숫자만 입력 가능합니다.")
            return False

        new_memo = input("변경 메모 (엔터 시 기존 메모 유지): ").strip()
        records[choice - 1]["progress"] = str(new_prog)
        if new_memo:
            records[choice - 1]["memo"] = new_memo

        overwrite_records(records, file_path)
        print(f"수정 완료 -> [{records[choice - 1]['member']}] '{records[choice - 1]['task']}' 진행률 {new_prog}%")
        return True
    except ValueError:
        print("숫자만 입력해 주세요.")
        return False
