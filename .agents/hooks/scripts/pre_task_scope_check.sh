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

if [[ "${cmd}" =~ (^|[[:space:]])rm[[:space:]]+-rf[[:space:]]+/ ]]; then
  echo "[hook:pre-task-scope-check][warn] destructive pattern detected: ${cmd}" >&2
fi

if [[ "${cmd}" =~ git[[:space:]]+reset[[:space:]]+--hard ]]; then
  echo "[hook:pre-task-scope-check][warn] hard reset command detected: ${cmd}" >&2
fi

if [[ "${cmd}" =~ (^[[:space:]]|[[:space:]])sudo([[:space:]]|$) ]]; then
  echo "[hook:pre-task-scope-check][warn] elevated command detected: ${cmd}" >&2
fi

if [[ "${cmd}" =~ \.\./ ]]; then
  echo "[hook:pre-task-scope-check][warn] parent path traversal detected: ${cmd}" >&2
fi

exit 0
