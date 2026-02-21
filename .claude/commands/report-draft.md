---
description: 보고서 초안 생성 및 품질 점검
argument-hint: "<주제> | <대상 독자> | <핵심 근거>"
allowed-tools: Read,Write,Edit,MultiEdit,Grep,Glob,Bash
---

다음 순서로 보고서 초안을 작성합니다.

1. `/Users/t2024-m0246/Documents/GitHub/Ralphton/.agents/skills/보고서-작성/SKILL.md`를 기준 규약으로 읽습니다.
2. 입력 인자 `$ARGUMENTS`를 `주제 | 대상 독자 | 핵심 근거`로 파싱합니다.
3. SKILL의 출력 형식(제목, 요약 3줄, 본문, 다음 액션)으로 초안을 작성합니다.
4. 숫자/근거 누락, 과장 표현, 분량(3분 내 읽기)을 자체 점검합니다.
5. 결과는 `변경 요약 / 변경 파일 목록 / 검증 결과 / 주의사항` 형식으로 보고합니다.
