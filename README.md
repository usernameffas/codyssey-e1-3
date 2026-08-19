# E1-3 AI가 계산하는 방식을 흉내 내는 작은 계산기 만들기

이 저장소는 **원본 미션의 필수 요구사항만** 구현합니다. Bonus(보너스)는 포함하지 않습니다.

> 현재 필요한 파일: 미션 페이지에 별도 첨부된 **공식 `data.json`** 1개. 이 파일은 프로젝트 루트에 그대로 넣으면 됩니다.

## 1. 프로젝트 개요

이 프로그램은 Mini NPU Simulator(미니 NPU 시뮬레이터)입니다.

- NPU = Neural Processing Unit, AI 계산에 특화된 처리 장치
- MAC = Multiply-Accumulate, 곱하고 누적해서 더하는 연산
- Filter(필터) = 어떤 모양인지 판단하기 위한 기준 숫자 배열
- Pattern(패턴) = 실제로 판정할 입력 숫자 배열

예를 들어 Cross(십자가) 모양과 X 모양을 숫자 배열로 만든 뒤, 같은 위치의 값을 곱해서 모두 더합니다.

```text
Pattern      Filter
0 1 0        0 1 0
1 1 1   ×    1 1 1
0 1 0        0 1 0

MAC Score = 5
```

점수가 더 높은 Filter를 입력 Pattern과 더 비슷한 것으로 판단합니다.

## 2. 실행 환경

- macOS
- Python 3.8 이상
- 외부 Library(라이브러리) 사용 금지
- Python Standard Library(표준 라이브러리)만 사용
  - `json`: JSON 파일 읽기
  - `re`: pattern key에서 크기 N 추출
  - `time`: MAC 연산 시간 측정
  - `pathlib`: 파일 경로 처리

## 3. 가장 빠른 실행 순서

```bash
git clone https://github.com/usernameffas/codyssey-e1-3.git
cd codyssey-e1-3
chmod +x scripts/*.sh
./scripts/setup_mac.sh
./scripts/verify.sh
python3 main.py
```

공식 `data.json`은 아래 위치여야 합니다.

```text
codyssey-e1-3/
├── main.py
├── data.json   <-- 미션 페이지에서 받은 공식 파일
└── README.md
```

## 4. 메뉴

```text
=== Mini NPU Simulator ===
1. 사용자 입력 (3x3)
2. data.json 분석
0. 종료
```

## 5. 모드 1: 사용자 입력 3×3

필터 A 3줄, 필터 B 3줄, 패턴 3줄을 입력합니다.

예:

```text
0 1 0
1 1 1
0 1 0
```

각 줄은 숫자 3개가 정확히 있어야 합니다.

오류 예:

```text
0 1
```

이 경우 프로그램은 종료되지 않고 다시 입력하라고 안내합니다.

출력:

- A MAC 점수
- B MAC 점수
- 판정 A/B/판정 불가
- 평균 MAC 연산 시간(ms)
- 연산 횟수 N²

## 6. 모드 2: data.json 분석

공식 `data.json`에서 아래 구조를 사용합니다.

```text
filters
├── size_5
├── size_13
└── size_25

patterns
├── size_5_1
├── size_5_2
├── size_13_1
└── ...
```

각 pattern의 key에서 N을 추출합니다.

예:

```text
size_13_2
   ↓
N = 13
   ↓
filters["size_13"] 사용
```

## 7. Label Normalization(라벨 정규화)

외부 파일의 라벨은 표현 방식이 다를 수 있습니다.

프로그램 내부에서는 두 표준 라벨만 사용합니다.

```text
Cross
X
```

변환 규칙:

| 외부 값 | 내부 표준 |
|---|---|
| `+` | `Cross` |
| `cross` | `Cross` |
| `Cross` | `Cross` |
| `x` | `X` |
| `X` | `X` |

이렇게 같은 뜻을 하나의 이름으로 맞추는 작업을 Normalization(정규화)이라고 합니다.

## 8. MAC 연산

MAC = Multiply-Accumulate

1. 같은 위치 값을 Multiply(곱하기)
2. 결과를 Accumulate(누적해서 더하기)

코드 핵심:

```python
score = 0.0
for row in range(size):
    for col in range(size):
        score += pattern[row][col] * filter_data[row][col]
```

NumPy 같은 외부 계산 라이브러리를 사용하지 않습니다.

## 9. epsilon과 부동소수점

컴퓨터의 실수(float) 계산은 아주 작은 오차가 생길 수 있습니다.

예:

```text
0.9000000000000000
0.8999999999999999
```

사실상 같은 값인데 문자 그대로 비교하면 다르다고 판단할 수 있습니다.

그래서 이 프로젝트는 다음 정책을 사용합니다.

```python
abs(score_cross - score_x) < 1e-9
```

차이가 `1e-9`보다 작으면 `UNDECIDED`(판정 불가)로 처리합니다.

- epsilon(엡실론) = 매우 작은 허용 오차
- `UNDECIDED` = 두 점수가 사실상 같아서 결정할 수 없음

## 10. PASS / FAIL 규칙

각 case마다 출력합니다.

```text
Cross 점수: ...
X 점수: ...
판정: Cross/X/UNDECIDED
expected: Cross/X
PASS 또는 FAIL
```

판정이 expected와 같으면 PASS, 다르면 FAIL입니다.

스키마나 크기가 잘못된 case가 있어도 프로그램 전체를 종료하지 않고 그 case만 FAIL 처리합니다.

## 11. 성능 분석

각 크기별 MAC 함수 호출 시간을 최소 10회 반복해 평균을 구합니다.

출력 표:

```text
크기       평균 시간(ms)       연산 횟수(N²)
3x3        ...                 9
5x5        ...                 25
13x13      ...                 169
25x25      ...                 625
```

I/O(Input/Output, 파일 읽기/화면 출력) 시간은 측정하지 않고 MAC 계산 함수 구간만 측정합니다.

## 12. 시간 복잡도 분석

N×N 배열의 모든 위치를 한 번씩 처리합니다.

```text
N행 × N열 = N²회
```

따라서 Time Complexity(시간 복잡도)는 **O(N²)** 입니다.

예:

- 3×3 → 9번
- 5×5 → 25번
- 13×13 → 169번
- 25×25 → 625번

N이 커질수록 처리해야 할 위치 수가 제곱으로 증가합니다.

## 13. 결과 리포트

프로그램은 data.json 분석이 끝나면 다음을 출력합니다.

```text
총 테스트: N개
통과: N개
실패: N개
```

실패가 있으면 case ID와 이유도 함께 출력합니다.

실패 원인은 크게 세 종류로 구분할 수 있습니다.

1. Data/Schema(데이터/스키마) 문제
   - 필요한 key가 없음
   - 배열 크기가 잘못됨
   - 숫자가 아닌 값이 있음

2. Logic(로직) 문제
   - 잘못된 filter 선택
   - MAC 계산이나 label 변환 오류

3. Numeric Comparison(수치 비교) 문제
   - 부동소수점 오차
   - epsilon 범위 때문에 `UNDECIDED` 처리

현재 프로그램은 key에서 N을 추출하고 같은 `size_N` filter만 선택하므로 다른 크기 filter를 대신 사용하지 않습니다.

## 14. 자동 검사

```bash
./scripts/verify.sh
```

현재 자동으로 확인하는 항목:

- Python 문법
- 3×3 Cross MAC = 5.0
- 3×3 Cross vs X MAC = 1.0
- Cross/X 판정
- epsilon 동점 처리
- 라벨 정규화
- `data.json`이 있으면 기본 스키마 확인

공식 `data.json`이 아직 없으면 `[WAIT]`만 출력하고 프로그램 소스 검사는 정상 완료됩니다.

## 15. 제출 전 캡처

공식 `data.json`을 넣은 뒤 다음을 실행합니다.

```bash
./scripts/verify.sh
python3 main.py
```

캡처할 화면:

1. 사용자 입력 3×3 정상 실행
2. 잘못된 3×3 입력 후 재입력 처리
3. data.json 각 case PASS/FAIL
4. 성능 분석 3×3/5×5/13×13/25×25
5. 총 테스트/통과/실패 요약

## 16. 제출 체크

- [x] 3×3 사용자 입력
- [x] 행/열/숫자 입력 검증
- [x] MAC 직접 반복문 구현
- [x] epsilon 비교
- [x] Cross/X 라벨 정규화
- [x] data.json 스키마/크기 검증
- [x] case 단위 FAIL 처리
- [x] PASS/FAIL 출력
- [x] 평균 10회 성능 측정
- [x] N² 연산 횟수 출력
- [x] 전체 결과 요약
- [x] README 실패 원인/시간 복잡도 설명
- [ ] 공식 `data.json` 추가
- [ ] 실제 실행 결과 캡처
