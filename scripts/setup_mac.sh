#!/usr/bin/env bash
# E1-3 실행에 필요한 최소 Python 환경을 준비합니다.
set -Eeuo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "[ERROR] 이 스크립트는 macOS용입니다."
  exit 1
fi

if ! command -v brew >/dev/null 2>&1; then
  NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  if [[ -x /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [[ -x /usr/local/bin/brew ]]; then
    eval "$(/usr/local/bin/brew shellenv)"
  fi
fi

if ! command -v python3 >/dev/null 2>&1; then
  brew install python
fi

python3 - <<'PY'
import sys
if sys.version_info < (3, 8):
    raise SystemExit("[ERROR] Python 3.8 이상이 필요합니다.")
print("[OK] Python", sys.version.split()[0])
PY
