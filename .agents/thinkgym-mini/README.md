# ThinkGym Mini Flow MVP

ThinkGym Mini Flow 5단계를 라운드 기반으로 실행하는 최소 구현입니다.

## 구성
- `run.py`: 라운드 오케스트레이터 (Pro/Con/Structure/Summary 호출 + 검증)
- `prompts/*.txt`: 사용자 제공 최종 프롬프트 템플릿

## 흐름 (1 라운드)
1. 질문(안건) 제시
2. 찬성(Pro) / 반대(Con) 의견 교환
3. 사용자 생각 입력
4. Structure Agent JSON 피드백 생성
5. Summary Agent 세션 리포트 생성

리포트의 `다음 라운드 추천 질문`이 다음 라운드의 질문으로 자동 연결됩니다.

## 실행
```bash
python3 .agents/thinkgym-mini/run.py \
  --topic "원격근무를 기본 근무제로 전환해야 하는가?" \
  --rounds 2 \
  --user-note "생산성은 오르지만 협업 리듬이 깨질 수 있어요" \
  --user-note "협업 기준을 수치로 합의하면 가능할 것 같습니다" \
  --mock \
  --non-interactive
```

## 현재 범위
- MVP는 `--mock` 모드만 지원합니다.
- 출력 안정화를 위해 다음 검증이 포함됩니다.
  - Pro/Con: 정확히 3문장
  - Con: 첫 문장이 Pro 키워드 참조
  - Structure: JSON 스키마 및 길이 규칙
  - Summary: 필수 섹션/줄 수 규칙
