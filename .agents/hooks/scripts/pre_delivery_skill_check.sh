#!/usr/bin/env bash
set -euo pipefail

required_sections=(
  "## 목적"
  "## 입력"
  "## 워크플로"
  "## 품질 기준"
  "## 실패 처리 규칙"
)

while IFS= read -r file; do
  if ! grep -qE "^## (출력 형식|출력 계약)" "${file}"; then
    echo "[hook:pre-delivery-skill-check][warn] missing output section in ${file}" >&2
  fi

  for section in "${required_sections[@]}"; do
    if ! grep -qF "${section}" "${file}"; then
      echo "[hook:pre-delivery-skill-check][warn] missing '${section}' in ${file}" >&2
    fi
  done
done < <(find .agents/skills -mindepth 2 -maxdepth 2 -name SKILL.md -type f ! -path "*/_template/*" | sort)

exit 0
