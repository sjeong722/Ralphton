---
description: 리팩토링 범위 점검 및 실행 체크리스트
argument-hint: "<대상 파일/범위> | <현재 문제점> | <허용 변경 범위>"
allowed-tools: Read,Write,Edit,MultiEdit,Grep,Glob,Bash
---

다음 순서로 리팩토링 작업을 진행합니다.

1. `/Users/t2024-m0246/Documents/GitHub/Ralphton/.agents/skills/코드-리팩토링/SKILL.md`를 기준 규약으로 읽습니다.
2. 입력 인자 `$ARGUMENTS`를 `대상 파일/범위 | 현재 문제점 | 허용 변경 범위`로 파싱합니다.
3. 허용 범위를 먼저 고정하고, 동작 동일성 유지 기준으로 최소 변경만 적용합니다.
4. 회귀 위험, 미검증 항목, 수동 확인 포인트를 분리해 작성합니다.
5. 결과는 `변경 요약 / 변경 파일 목록 / 위험 요소 및 확인 포인트 / 검증 결과`로 보고합니다.
