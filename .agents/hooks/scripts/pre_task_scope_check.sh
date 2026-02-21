#!/usr/bin/env bash
set -euo pipefail

# 초안: 허용 경로 정책을 출력하고, 실제 차단 로직은 추후 확장
echo "[hook:pre-task-scope-check] Allowed paths: .claude/, .agents/"
