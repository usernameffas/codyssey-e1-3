"""Codyssey E1-3 필수 과제: Mini NPU Simulator.

- 외부 라이브러리 없이 Python 표준 라이브러리만 사용합니다.
- MAC(Multiply-Accumulate) 연산은 반복문으로 직접 구현합니다.
- Bonus(보너스) 기능은 포함하지 않습니다.
"""

import json
import re
import time
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data.json"
EPSILON = 1e-9
REPEAT_COUNT = 10


def normalize_label(label):
    """외부 라벨을 프로그램 내부 표준 라벨 Cross/X로 바꿉니다."""
    text = str(label).strip()
    label_map = {
        "+": "Cross",
        "cross": "Cross",
        "Cross": "Cross",
        "x": "X",
        "X": "X",
    }
    if text not in label_map:
        raise ValueError(f"지원하지 않는 라벨: {text}")
    return label_map[text]


def validate_matrix(matrix, expected_size=None):
    """matrix가 숫자로 된 N×N 2차원 배열인지 검사합니다."""
    if not isinstance(matrix, list) or not matrix:
        return False, "2차원 배열이 아닙니다."

    size = len(matrix)
    if expected_size is not None and size != expected_size:
        return False, f"행 개수 {size}가 기대 크기 {expected_size}와 다릅니다."

    for row_number, row in enumerate(matrix, start=1):
        if not isinstance(row, list) or len(row) != size:
            return False, f"{row_number}번째 행의 열 개수가 {size}가 아닙니다."
        for value in row:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                return False, f"{row_number}번째 행에 숫자가 아닌 값이 있습니다."

    return True, "OK"


def calculate_mac(pattern, filter_data):
    """같은 위치의 값을 곱하고 모두 더해 MAC 점수를 계산합니다."""
    valid_pattern, reason = validate_matrix(pattern)
    if not valid_pattern:
        raise ValueError(f"패턴 오류: {reason}")

    size = len(pattern)
    valid_filter, reason = validate_matrix(filter_data, size)
    if not valid_filter:
        raise ValueError(f"필터 오류: {reason}")

    score = 0.0
    # 외부 수치 연산 라이브러리를 사용하지 않고 이중 반복문으로 직접 계산합니다.
    for row in range(size):
        for col in range(size):
            score += pattern[row][col] * filter_data[row][col]
    return score


def decide_pattern(score_cross, score_x):
    """epsilon 이내의 차이는 부동소수점 오차를 고려해 동점으로 처리합니다."""
    if abs(score_cross - score_x) < EPSILON:
        return "UNDECIDED"
    if score_cross > score_x:
        return "Cross"
    return "X"


def measure_mac(pattern, filter_data, repeat=REPEAT_COUNT):
    """파일 읽기/출력을 제외하고 MAC 함수 호출 시간만 반복 측정합니다."""
    total_seconds = 0.0
    for _ in range(repeat):
        start = time.perf_counter()
        calculate_mac(pattern, filter_data)
        end = time.perf_counter()
        total_seconds += end - start
    return (total_seconds / repeat) * 1000.0


def input_matrix(name, size=3):
    """사용자에게 N줄을 입력받아 N×N 숫자 배열을 만듭니다."""
    print(f"\n{name} ({size}줄 입력, 공백 구분)")
    matrix = []

    while len(matrix) < size:
        row_number = len(matrix) + 1
        raw = input(f"{row_number}행: ").strip()
        parts = raw.split()

        if len(parts) != size:
            print(f"입력 형식 오류: 각 줄에 {size}개의 숫자를 공백으로 구분해 입력하세요.")
            continue

        try:
            row = [float(value) for value in parts]
        except ValueError:
            print("입력 형식 오류: 숫자만 입력하세요.")
            continue

        matrix.append(row)

    return matrix


def extract_pattern_size(pattern_key):
    """size_13_2 같은 key에서 N=13을 꺼냅니다."""
    match = re.fullmatch(r"size_(\d+)_\d+", pattern_key)
    if not match:
        raise ValueError("패턴 key가 size_{N}_{idx} 형식이 아닙니다.")
    return int(match.group(1))


def normalize_filter_set(raw_filters):
    """filter key의 cross/x를 Cross/X로 바꾸고 필요한 두 필터가 있는지 확인합니다."""
    normalized = {}
    for key, matrix in raw_filters.items():
        normalized[normalize_label(key)] = matrix

    if "Cross" not in normalized or "X" not in normalized:
        raise ValueError("Cross와 X 필터가 모두 필요합니다.")
    return normalized


def load_data():
    """프로젝트 루트의 공식 data.json을 읽습니다."""
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            "data.json이 없습니다. 미션 페이지에서 제공된 공식 data.json을 프로젝트 루트에 넣어 주세요."
        )

    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("data.json 최상위 데이터가 object가 아닙니다.")
    if "filters" not in data or "patterns" not in data:
        raise ValueError("data.json에 filters와 patterns가 모두 필요합니다.")
    if not isinstance(data["filters"], dict) or not isinstance(data["patterns"], dict):
        raise ValueError("filters와 patterns는 object 형식이어야 합니다.")
    return data


def print_performance_table(rows):
    print("\n[성능 분석: 평균/10회]")
    print("크기       평균 시간(ms)       연산 횟수(N²)")
    print("-" * 48)
    for size, average_ms in rows:
        print(f"{size}x{size:<5} {average_ms:>14.6f} {size * size:>15}")


def run_user_mode():
    """모드 1: 3×3 필터 A/B와 패턴을 직접 입력받습니다."""
    print("\n[1] 필터 입력")
    filter_a = input_matrix("필터 A", 3)
    filter_b = input_matrix("필터 B", 3)
    print("필터 A/B 저장 완료")

    print("\n[2] 패턴 입력")
    pattern = input_matrix("패턴", 3)

    print("\n[3] MAC 결과")
    score_a = calculate_mac(pattern, filter_a)
    score_b = calculate_mac(pattern, filter_b)

    if abs(score_a - score_b) < EPSILON:
        decision = "판정 불가"
    elif score_a > score_b:
        decision = "A"
    else:
        decision = "B"

    time_a = measure_mac(pattern, filter_a)
    time_b = measure_mac(pattern, filter_b)
    average_ms = (time_a + time_b) / 2

    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"판정: {decision}")
    print(f"연산 시간(두 필터 평균/각 {REPEAT_COUNT}회): {average_ms:.6f} ms")
    print_performance_table([(3, average_ms)])


def run_json_mode():
    """모드 2: 공식 data.json의 모든 패턴을 검증하고 판정합니다."""
    try:
        data = load_data()
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"[ERROR] data.json을 사용할 수 없습니다: {error}")
        return

    filters_data = data["filters"]
    patterns_data = data["patterns"]

    print("\n[1] 필터 로드")
    normalized_by_size = {}
    for size_key in ("size_5", "size_13", "size_25"):
        try:
            if size_key not in filters_data:
                raise KeyError(f"{size_key} 필터가 없습니다.")
            normalized_by_size[size_key] = normalize_filter_set(filters_data[size_key])
            print(f"OK: {size_key} 필터 로드 완료 (Cross, X)")
        except (KeyError, TypeError, ValueError) as error:
            print(f"WARN: {size_key}: {error}")

    total = 0
    passed = 0
    failures = []
    representative_patterns = {}

    print("\n[2] 패턴 분석")
    for pattern_key, case in patterns_data.items():
        total += 1
        try:
            size = extract_pattern_size(pattern_key)
            size_key = f"size_{size}"

            if size_key not in normalized_by_size:
                raise ValueError(f"{size_key} 필터를 사용할 수 없습니다.")
            if not isinstance(case, dict) or "input" not in case or "expected" not in case:
                raise ValueError("input 또는 expected가 없습니다.")

            pattern = case["input"]
            valid, reason = validate_matrix(pattern, size)
            if not valid:
                raise ValueError(f"패턴 크기/형식 오류: {reason}")

            filters = normalized_by_size[size_key]
            for label in ("Cross", "X"):
                valid, reason = validate_matrix(filters[label], size)
                if not valid:
                    raise ValueError(f"{label} 필터 크기/형식 오류: {reason}")

            expected = normalize_label(case["expected"])
            score_cross = calculate_mac(pattern, filters["Cross"])
            score_x = calculate_mac(pattern, filters["X"])
            decision = decide_pattern(score_cross, score_x)
            is_pass = decision == expected

            print(f"\n--- {pattern_key} ---")
            print(f"Cross 점수: {score_cross}")
            print(f"X 점수: {score_x}")
            print(f"판정: {decision} | expected: {expected} | {'PASS' if is_pass else 'FAIL'}")

            if is_pass:
                passed += 1
            else:
                reason_text = "epsilon 동점 규칙" if decision == "UNDECIDED" else "판정과 expected 불일치"
                failures.append((pattern_key, reason_text))

            representative_patterns.setdefault(size, pattern)
        except (KeyError, TypeError, ValueError) as error:
            print(f"\n--- {pattern_key} ---")
            print(f"FAIL: {error}")
            failures.append((pattern_key, str(error)))

    # 3×3은 미션 설명의 기본 Cross 배열로 연산 시간을 측정합니다.
    cross3 = [[0.0, 1.0, 0.0], [1.0, 1.0, 1.0], [0.0, 1.0, 0.0]]
    performance = [(3, measure_mac(cross3, cross3))]

    for size in (5, 13, 25):
        pattern = representative_patterns.get(size)
        filters = normalized_by_size.get(f"size_{size}")
        if pattern is not None and filters is not None:
            performance.append((size, measure_mac(pattern, filters["Cross"])))

    print_performance_table(performance)

    print("\n[4] 결과 요약")
    print(f"총 테스트: {total}개")
    print(f"통과: {passed}개")
    print(f"실패: {len(failures)}개")
    if failures:
        print("실패 케이스:")
        for case_id, reason in failures:
            print(f"- {case_id}: {reason}")


def read_menu():
    while True:
        raw = input("선택: ").strip()
        if raw in {"1", "2", "0"}:
            return raw
        print("0, 1, 2 중 하나를 입력하세요.")


def main():
    print("=== Mini NPU Simulator ===")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    print("0. 종료")

    try:
        choice = read_menu()
        if choice == "1":
            run_user_mode()
        elif choice == "2":
            run_json_mode()
        else:
            print("종료합니다.")
    except (KeyboardInterrupt, EOFError):
        print("\n입력이 중단되어 안전하게 종료합니다.")


if __name__ == "__main__":
    main()
