#!/usr/bin/env bash
# Check your manifest before submitting. Runs the same four stages as the grader.
#
#     ./selfcheck.sh                  # checks starter/manifest.yaml
#     ./selfcheck.sh AIE23001.yaml    # checks a specific file
set -uo pipefail
cd "$(dirname "$0")"

SRC="${1:-starter/manifest.yaml}"
[ -f "$SRC" ] || SRC="manifest.yaml"
[ -f "$SRC" ] || { echo "no manifest found"; exit 1; }

rc=0
for stage in parse deployment service production; do
  echo "==> $stage"
  python3 tests/check.py "$SRC" --stage "$stage" || rc=1
  echo
done
exit $rc
