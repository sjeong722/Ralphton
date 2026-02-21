#!/usr/bin/env bash
set -euo pipefail

input="$(cat || true)"

if [[ -z "${input}" ]]; then
  exit 0
fi

cmd="$(printf '%s' "${input}" | python3 -c 'import sys, json; data=json.load(sys.stdin); print(data.get("tool_input", {}).get("command", ""))' 2>/dev/null || true)"

if [[ -z "${cmd}" ]]; then
  exit 0
fi

blocked=0

if [[ "${cmd}" =~ (^|[[:space:]])rm[[:space:]]+-rf[[:space:]]+/ ]]; then
  echo "[hook:pre-task-scope-check][block] destructive pattern detected: ${cmd}" >&2
  blocked=1
fi

if [[ "${cmd}" =~ git[[:space:]]+reset[[:space:]]+--hard ]]; then
  echo "[hook:pre-task-scope-check][block] hard reset command detected: ${cmd}" >&2
  blocked=1
fi

if [[ "${cmd}" =~ (^[[:space:]]|[[:space:]])sudo([[:space:]]|$) ]]; then
  echo "[hook:pre-task-scope-check][block] elevated command detected: ${cmd}" >&2
  blocked=1
fi

if [[ "${cmd}" =~ \.\./ ]]; then
  echo "[hook:pre-task-scope-check][block] parent path traversal detected: ${cmd}" >&2
  blocked=1
fi

if [[ "${blocked}" -eq 1 ]]; then
  echo "[hook:pre-task-scope-check] command blocked for safety." >&2
  exit 2
fi

exit 0
