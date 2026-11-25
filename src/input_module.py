# src/input_module.py - 팀플 태스크 기록 1건을 입력받는 모듈 (12주차)
from datetime import datetime  # 마감일(YYYY-MM-DD) 형식을 검증하기 위한 표준 라이브러리


def ask_text(question, min_len, max_len):
    """min_len ~ max_len 글자 수 사이의 문자열이 들어올 때까지 다시 묻는다."""
    while True:  # 조건에 맞는 글자 수가 입력될 때까지 반복
        text = input(question).strip()  # 앞뒤 공백을 제거하고 입력받기
        if min_len <= len(text) <= max_len:  # 글자 수 조건을 만족하면
            return text  # 입력받은 문자열 반환
        print(f"{min_len}~{max_len}자 이내로 입력해 주세요.")  # 범위 안내 문구 출력


def ask_date(question):
    """YYYY-MM-DD 형식의 올바른 날짜가 들어올 때까지 다시 묻는다."""
    while True:  # 올바른 날짜 형식이 입력될 때까지 반복
        d = input(question).strip()  # 날짜 문자열 입력받기
        try:
            datetime.strptime(d, "%Y-%m-%d")  # YYYY-MM-DD 형식인지 검증
            return d  # 형식이 맞으면 날짜 문자열 반환
        except ValueError:  # 형식이 틀리거나 존재하지 않는 날짜일 때
            print("YYYY-MM-DD 형식(예: 2026-11-25)으로 입력해 주세요.")


def ask_number(question, low, high):
    """low ~ high 사이의 정수가 들어올 때까지 다시 묻는다."""
    while True:  # 올바른 정수가 입력될 때까지 반복
        try:
            n = int(input(question))  # 입력받은 글자를 정수로 변환
            if low <= n <= high:  # 지정된 숫자 범위 안이면
                return n  # 정수 반환
            print(f"{low}~{high} 사이의 정수로 입력해 주세요.")  # 범위 초과 안내
        except ValueError:  # 숫자가 아닌 글자를 입력했을 때
            print("숫자만 입력해 주세요.")


def get_record():
    """팀플 태스크 기록 1건을 입력받아 키 5개 딕셔너리로 돌려준다."""
    member = ask_text("팀원명 (2~10자): ", 2, 10)  # 필수 팀원명 입력
    task = ask_text("담당 태스크명 (1~50자): ", 1, 50)  # 필수 태스크명 입력
    due_date = ask_date("마감일 (YYYY-MM-DD): ")  # 필수 마감일 입력
    progress = ask_number("진행률 (0~100): ", 0, 100)  # 필수 진행률(%) 입력
    memo = input("메모 (선택, 엔터=생략): ").strip()  # 선택 메모 입력

    # 키 5개를 가진 딕셔너리 1개로 반환
    return {
        "member": member,
        "task": task,
        "due_date": due_date,
        "progress": progress,
        "memo": memo,
    }


if __name__ == "__main__":  # 이 파일만 단독 실행했을 때 동작 확인
    print(get_record())  # 입력받은 딕셔너리 1건 출력
