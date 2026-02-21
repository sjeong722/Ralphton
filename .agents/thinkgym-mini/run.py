#!/usr/bin/env python3
import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


PROMPT_DIR = Path(__file__).parent / "prompts"
SHORT_NOTE_THRESHOLD = 20
STOPWORDS = {
    "저는",
    "나는",
    "제가",
    "우리",
    "그리고",
    "하지만",
    "그러나",
    "다만",
    "이것",
    "그것",
    "주장",
}


@dataclass
class RoundResult:
    round_no: int
    topic: str
    pro_statement: str
    con_statement: str
    user_note: str
    structure_feedback: Dict[str, object]
    summary_report: str
    next_question: str


def load_prompt(name: str) -> str:
    path = PROMPT_DIR / name
    return path.read_text(encoding="utf-8").strip()


def render_template(text: str, variables: Dict[str, str]) -> str:
    rendered = text
    for key, value in variables.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def sentence_count(text: str) -> int:
    return len(split_sentences(text))


def split_sentences(text: str) -> List[str]:
    # Split only on likely sentence boundaries: punctuation + whitespace.
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+(?=[\"'\\(\\[]?[가-힣A-Za-z0-9])", text.strip()) if p.strip()]


def ensure_three_sentences(text: str, agent_name: str) -> None:
    if sentence_count(text) != 3:
        raise ValueError(f"{agent_name} 출력은 정확히 3문장이어야 합니다: {text}")


def extract_keywords(text: str) -> List[str]:
    words = re.findall(r"[가-힣A-Za-z0-9]{2,}", text)
    seen = set()
    keywords = []
    for word in words:
        w = word.lower()
        if w not in seen:
            seen.add(w)
            keywords.append(word)
    return keywords


def extract_salient_keywords(text: str) -> List[str]:
    return [w for w in extract_keywords(text) if w.lower() not in STOPWORDS]


def validate_con_first_sentence(con_text: str, pro_text: str) -> None:
    sentences = split_sentences(con_text)
    if not sentences:
        raise ValueError("Con 출력이 비어 있습니다.")
    first = sentences[0]
    pro_keywords = extract_salient_keywords(pro_text)
    if not pro_keywords:
        return
    if not any(keyword in first for keyword in pro_keywords[:5]):
        raise ValueError("Con 첫 문장이 Pro 발언 키워드를 직접 참조하지 않았습니다.")


def validate_con_topic_relevance(con_text: str, topic: str) -> None:
    topic_keywords = extract_salient_keywords(topic)
    if not topic_keywords:
        return
    if not any(keyword in con_text for keyword in topic_keywords[:5]):
        raise ValueError("Con 출력이 주제 키워드를 충분히 반영하지 않았습니다.")


def validate_structure_json(data: Dict[str, object], user_note: str) -> None:
    expected_keys = [
        "claim",
        "reasons",
        "assumptions",
        "counterpoints",
        "missing_info",
        "next_revision",
    ]
    if list(data.keys()) != expected_keys:
        raise ValueError("Structure JSON 키 순서/구조가 스키마와 다릅니다.")

    for key in expected_keys:
        if key not in data:
            raise ValueError(f"Structure JSON 누락 키: {key}")

    for key in ["reasons", "assumptions", "counterpoints", "missing_info"]:
        if not isinstance(data[key], list):
            raise ValueError(f"{key}는 배열이어야 합니다.")

    if not isinstance(data["claim"], str) or not isinstance(data["next_revision"], str):
        raise ValueError("claim/next_revision은 문자열이어야 합니다.")

    compact = json.dumps(data, ensure_ascii=False)
    if "\n" in compact or "\r" in compact:
        raise ValueError("Structure JSON 값에 줄바꿈이 있으면 안 됩니다.")

    if len(user_note.strip()) < SHORT_NOTE_THRESHOLD:
        if data["claim"] != "입장이 아직 명확히 정리되지 않았습니다.":
            raise ValueError("짧은 user_note 규칙 claim 불일치")
        if data["reasons"] != [] or data["assumptions"] != [] or data["counterpoints"] != []:
            raise ValueError("짧은 user_note 규칙 배열이 비어 있어야 합니다.")
        expected_missing = ["주장을 1문장으로 명확히 작성하세요", "근거를 최소 2개 제시하세요"]
        if data["missing_info"] != expected_missing:
            raise ValueError("짧은 user_note 규칙 missing_info 불일치")
        expected_next = (
            "주장을 1문장으로 정리하십시오. 그 주장을 뒷받침하는 근거 2가지를 추가하십시오. "
            "반대 의견에 대한 대비를 포함하십시오."
        )
        if data["next_revision"] != expected_next:
            raise ValueError("짧은 user_note 규칙 next_revision 불일치")
    else:
        if not 2 <= len(data["reasons"]) <= 3:
            raise ValueError("reasons는 2~3개여야 합니다.")
        if not 1 <= len(data["assumptions"]) <= 2:
            raise ValueError("assumptions는 1~2개여야 합니다.")
        if not 1 <= len(data["counterpoints"]) <= 2:
            raise ValueError("counterpoints는 1~2개여야 합니다.")
        if not 1 <= len(data["missing_info"]) <= 2:
            raise ValueError("missing_info는 1~2개여야 합니다.")
        if sentence_count(data["next_revision"]) != 3:
            raise ValueError("next_revision은 정확히 3문장이어야 합니다.")


def parse_structure_json(text: str, user_note: str) -> Dict[str, object]:
    data = json.loads(text)
    validate_structure_json(data, user_note)
    return data


def extract_section(report: str, section_title: str, next_section_title: str) -> str:
    start = report.find(section_title)
    if start < 0:
        return ""
    if not next_section_title:
        return report[start + len(section_title):].strip()
    end = report.find(next_section_title, start + len(section_title))
    if end < 0:
        return report[start + len(section_title):].strip()
    return report[start + len(section_title):end].strip()


def validate_summary_report(report: str) -> None:
    required_headers = [
        "# 📝 ThinkGym 세션 리포트",
        "## 1. 오늘의 질문",
        "## 2. 찬반 핵심 요약",
        "## 3. 사용자의 입장",
        "## 4. 논리 구조 개선 포인트",
        "## 5. 다음 라운드 추천 질문",
    ]
    for header in required_headers:
        if header not in report:
            raise ValueError(f"Summary 리포트 헤더 누락: {header}")

    user_section = extract_section(report, "## 3. 사용자의 입장", "## 4. 논리 구조 개선 포인트")
    user_lines = [line.strip() for line in user_section.splitlines() if line.strip()]
    if len(user_lines) != 3:
        raise ValueError("사용자의 입장 섹션은 정확히 3줄이어야 합니다.")

    improve_section = extract_section(report, "## 4. 논리 구조 개선 포인트", "## 5. 다음 라운드 추천 질문")
    improve_lines = [line.strip() for line in improve_section.splitlines() if line.strip().startswith("-")]
    if len(improve_lines) != 3:
        raise ValueError("논리 구조 개선 포인트는 정확히 3개여야 합니다.")

    next_q_section = extract_section(report, "## 5. 다음 라운드 추천 질문", "")
    next_lines = [line.strip() for line in next_q_section.splitlines() if line.strip()]
    if len(next_lines) != 1:
        raise ValueError("다음 라운드 추천 질문은 정확히 1줄이어야 합니다.")


def make_debate_transcript(pro_text: str, con_text: str) -> str:
    return f"[찬성] {pro_text}\n[반대] {con_text}"


def mock_pro(topic: str, user_note: str) -> str:
    context = "이전 라운드 사용자 메모가 쟁점을 구체화" if user_note.strip() else "핵심 질문의 방향성"
    return (
        f"저는 '{topic}'에 찬성하며 이 선택이 장기적으로 더 높은 의사결정 품질을 만든다고 봅니다. "
        f"첫째 {context}을 강화하고 둘째 실행 기준을 명확히 해 팀의 혼선을 줄일 수 있습니다. "
        "다만 단기 성과 압박이 큰 환경에서는 초기 비용이 부담이라는 반론이 나올 수 있습니다."
    )


def mock_con(topic: str, pro_statement: str) -> str:
    pro_keywords = extract_salient_keywords(pro_statement)
    keyword = pro_keywords[0] if pro_keywords else "핵심 근거"
    return (
        f"저는 '{topic}'에 반대하며, 찬성 측의 '{keyword}'만으로는 정책 전환의 타당성을 충분히 입증하기 어렵다고 봅니다. "
        "첫째 초기 비용과 운영 복잡도가 커지고 둘째 실행 실패 시 책임과 복구 기준이 불명확해 실제 성과가 악화될 수 있습니다. "
        f"다만 전면 도입 대신 제한된 파일럿과 명확한 중단 기준을 먼저 합의한다면 '{topic}'에 대해 조건부 논의는 가능합니다."
    )


def mock_structure(topic: str, transcript: str, user_note: str) -> str:
    if len(user_note.strip()) < SHORT_NOTE_THRESHOLD:
        data = {
            "claim": "입장이 아직 명확히 정리되지 않았습니다.",
            "reasons": [],
            "assumptions": [],
            "counterpoints": [],
            "missing_info": ["주장을 1문장으로 명확히 작성하세요", "근거를 최소 2개 제시하세요"],
            "next_revision": "주장을 1문장으로 정리하십시오. 그 주장을 뒷받침하는 근거 2가지를 추가하십시오. 반대 의견에 대한 대비를 포함하십시오.",
        }
    else:
        data = {
            "claim": f"사용자는 '{topic}'에 대해 실행 가능성을 중심으로 조건부 찬성 입장을 보입니다.",
            "reasons": [
                "의사결정 기준을 명확히 해야 팀의 혼선이 줄어든다고 보았습니다.",
                "단계적 검증을 통해 실패 비용을 통제할 수 있다고 판단했습니다.",
            ],
            "assumptions": ["팀이 공통 지표를 합의하면 실행 마찰이 줄어든다는 가정이 있습니다."],
            "counterpoints": ["초기 리소스 부족 상황에서는 점진적 실험도 부담이 될 수 있습니다."],
            "missing_info": ["실행 우선순위를 정하는 정량 기준이 아직 제시되지 않았습니다."],
            "next_revision": "핵심 주장을 한 문장으로 더 선명하게 고정하세요. 실행 기준을 수치로 제시해 설득력을 높이세요. 반대 상황에서의 대응 계획을 한 문장으로 덧붙이세요.",
        }
    return json.dumps(data, ensure_ascii=False)


def mock_summary(topic: str, pro_text: str, con_text: str, user_note: str, structure: Dict[str, object]) -> str:
    assumptions = structure.get("assumptions", [])
    counterpoints = structure.get("counterpoints", [])
    missing_info = structure.get("missing_info", [])

    assumption_point = assumptions[0] if assumptions else "입장 가정이 아직 충분히 명시되지 않았습니다."
    counter_point = counterpoints[0] if counterpoints else "반대 논점을 먼저 정의하면 논의 균형이 좋아집니다."
    missing_point = missing_info[0] if missing_info else "핵심 근거를 더 구체적으로 보완하세요."

    user_line1 = "사용자는 핵심 입장을 정교화하려는 의지가 분명합니다."
    user_line2 = "의견은 실행 가능성과 리스크 통제를 함께 고려합니다."
    user_line3 = "다음 라운드에서는 근거의 정량화가 필요합니다."
    if user_note.strip():
        user_line1 = f"사용자는 '{user_note[:35]}'를 중심으로 입장을 정리했습니다."

    next_question = "현재 입장을 유지하면서도 실패 비용을 최소화하기 위한 첫 번째 검증 지표는 무엇인가요?"

    return "\n".join(
        [
            "# 📝 ThinkGym 세션 리포트",
            "",
            "## 1. 오늘의 질문",
            topic,
            "",
            "## 2. 찬반 핵심 요약",
            "- **찬성:**",
            f"  1) {split_sentences(pro_text)[0]}",
            f"  2) {split_sentences(pro_text)[1]}",
            f"  3) {split_sentences(pro_text)[2]}",
            "- **반대:**",
            f"  1) {split_sentences(con_text)[0]}",
            f"  2) {split_sentences(con_text)[1]}",
            f"  3) {split_sentences(con_text)[2]}",
            "",
            "## 3. 사용자의 입장",
            user_line1,
            user_line2,
            user_line3,
            "",
            "## 4. 논리 구조 개선 포인트",
            f"- {assumption_point}",
            f"- {counter_point}",
            f"- {missing_point}",
            "",
            "## 5. 다음 라운드 추천 질문",
            next_question,
        ]
    )


def build_full_prompt(system_text: str, user_text: str, variables: Dict[str, str]) -> str:
    return (
        "[SYSTEM]\n"
        + render_template(system_text, variables)
        + "\n\n[USER]\n"
        + render_template(user_text, variables)
    )


def run_agent(kind: str, variables: Dict[str, str], mock_mode: bool) -> str:
    if mock_mode:
        if kind == "pro":
            return mock_pro(variables["topic"], variables.get("user_note", ""))
        if kind == "con":
            return mock_con(variables["topic"], variables["pro_statement"])
        if kind == "structure":
            return mock_structure(variables["topic"], variables["debate_transcript"], variables["user_note"])
        if kind == "summary":
            structure = json.loads(variables["structure_feedback"])
            return mock_summary(
                variables["topic"],
                variables["pro_statement"],
                variables["con_statement"],
                variables["user_note"],
                structure,
            )
        raise ValueError(f"알 수 없는 kind: {kind}")

    raise RuntimeError("MVP는 현재 --mock 모드만 지원합니다. 실제 모델 연동은 후속 단계에서 연결하세요.")


def generate_with_retry(kind: str, variables: Dict[str, str], mock_mode: bool, max_retries: int = 2):
    errors = []
    for _ in range(max_retries + 1):
        text = run_agent(kind, variables, mock_mode)
        try:
            if kind == "pro":
                ensure_three_sentences(text, "Pro")
                return text
            if kind == "con":
                ensure_three_sentences(text, "Con")
                validate_con_first_sentence(text, variables["pro_statement"])
                validate_con_topic_relevance(text, variables["topic"])
                return text
            if kind == "structure":
                parsed = parse_structure_json(text, variables["user_note"])
                return parsed
            if kind == "summary":
                validate_summary_report(text)
                return text
            raise ValueError(f"지원하지 않는 kind: {kind}")
        except Exception as exc:  # pylint: disable=broad-except
            errors.append(str(exc))

    raise RuntimeError(f"{kind} 생성 실패: {' | '.join(errors)}")


def pick_user_note(round_no: int, notes: List[str], interactive: bool) -> str:
    if round_no - 1 < len(notes):
        return notes[round_no - 1]
    if interactive:
        return input(f"\n[Round {round_no}] 사용자 생각 입력: ").strip()
    return ""


def extract_next_question(summary_report: str, fallback_topic: str) -> str:
    section = extract_section(summary_report, "## 5. 다음 라운드 추천 질문", "")
    lines = [line.strip() for line in section.splitlines() if line.strip()]
    if not lines:
        return fallback_topic
    return lines[0]


def run_session(topic: str, rounds: int, notes: List[str], mock_mode: bool, interactive: bool) -> List[RoundResult]:
    results: List[RoundResult] = []
    current_topic = topic
    previous_note = ""

    for round_no in range(1, rounds + 1):
        pro_statement = generate_with_retry(
            "pro",
            {"topic": current_topic, "user_note": previous_note},
            mock_mode,
        )

        con_statement = generate_with_retry(
            "con",
            {"topic": current_topic, "pro_statement": pro_statement},
            mock_mode,
        )

        debate_transcript = make_debate_transcript(pro_statement, con_statement)
        user_note = pick_user_note(round_no, notes, interactive)

        structure_feedback = generate_with_retry(
            "structure",
            {
                "topic": current_topic,
                "debate_transcript": debate_transcript,
                "user_note": user_note,
            },
            mock_mode,
        )

        summary_report = generate_with_retry(
            "summary",
            {
                "topic": current_topic,
                "debate_transcript": debate_transcript,
                "user_note": user_note,
                "structure_feedback": json.dumps(structure_feedback, ensure_ascii=False),
                "pro_statement": pro_statement,
                "con_statement": con_statement,
            },
            mock_mode,
        )

        next_question = extract_next_question(summary_report, current_topic)

        results.append(
            RoundResult(
                round_no=round_no,
                topic=current_topic,
                pro_statement=pro_statement,
                con_statement=con_statement,
                user_note=user_note,
                structure_feedback=structure_feedback,
                summary_report=summary_report,
                next_question=next_question,
            )
        )

        current_topic = next_question
        previous_note = user_note

    return results


def print_round_output(result: RoundResult) -> None:
    print(f"\n===== Round {result.round_no} =====")
    print(f"질문: {result.topic}")
    print(f"\n[찬성]\n{result.pro_statement}")
    print(f"\n[반대]\n{result.con_statement}")
    print(f"\n[사용자 생각]\n{result.user_note if result.user_note else '(미입력)'}")
    print("\n[구조 피드백 JSON]")
    print(json.dumps(result.structure_feedback, ensure_ascii=False, indent=2))
    print("\n[세션 리포트]")
    print(result.summary_report)
    print(f"\n[다음 라운드 질문]\n{result.next_question}")


def verify_prompt_files() -> None:
    required = [
        "pro_agent_system.txt",
        "pro_agent_user.txt",
        "con_agent_system.txt",
        "con_agent_user.txt",
        "structure_agent_system.txt",
        "structure_agent_user.txt",
        "summary_agent_system.txt",
        "summary_agent_user.txt",
    ]
    for filename in required:
        _ = load_prompt(filename)


def main() -> None:
    parser = argparse.ArgumentParser(description="ThinkGym Mini Flow MVP Runner")
    parser.add_argument("--topic", required=True, help="첫 라운드 질문")
    parser.add_argument("--rounds", type=int, default=2, help="라운드 수 (기본 2)")
    parser.add_argument("--user-note", action="append", default=[], help="라운드별 사용자 생각 (순서대로 반복 입력)")
    parser.add_argument("--mock", action="store_true", help="모의 응답 모드")
    parser.add_argument("--non-interactive", action="store_true", help="입력 프롬프트 없이 실행")
    args = parser.parse_args()

    if args.rounds < 1:
        raise ValueError("--rounds는 1 이상이어야 합니다.")

    verify_prompt_files()
    results = run_session(
        topic=args.topic,
        rounds=args.rounds,
        notes=args.user_note,
        mock_mode=args.mock,
        interactive=not args.non_interactive,
    )

    for result in results:
        print_round_output(result)


if __name__ == "__main__":
    main()
