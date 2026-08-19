#!/usr/bin/env bash
# E1-3 제출 전 자동 검사
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m py_compile main.py
python3 - <<'PY'
from main import calculate_mac, decide_pattern, normalize_label

cross = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
x_filter = [[1, 0, 1], [0, 1, 0], [1, 0, 1]]
assert calculate_mac(cross, cross) == 5.0
assert calculate_mac(cross, x_filter) == 1.0
assert decide_pattern(5.0, 1.0) == "Cross"
assert decide_pattern(1.0, 5.0) == "X"
assert decide_pattern(0.9, 0.8999999999999999) == "UNDECIDED"
assert normalize_label("+") == "Cross"
assert normalize_label("cross") == "Cross"
assert normalize_label("x") == "X"
print("[OK] Python 문법")
print("[OK] 3x3 MAC 점수 5.0 / 1.0")
print("[OK] Cross/X/UNDECIDED 판정")
print("[OK] 라벨 정규화")
PY

if [[ -f data.json ]]; then
  python3 - <<'PY'
import json
from pathlib import Path

data = json.loads(Path("data.json").read_text(encoding="utf-8"))
assert "filters" in data and "patterns" in data
for key in ("size_5", "size_13", "size_25"):
    assert key in data["filters"], f"filters에 {key}가 없습니다."
print("[OK] 공식 data.json 기본 스키마")
PY
else
  echo "[WAIT] 공식 data.json이 아직 없습니다. 미션 페이지 첨부 파일을 프로젝트 루트에 넣어 주세요."
fi
