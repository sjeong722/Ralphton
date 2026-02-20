#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ThinkGym backend engine (mock-first).
- stdout: JSON ONLY (machine-readable)
- stderr: debug logs ONLY
- Modes: debate | structure | report | full
- Deterministic mock via --seed
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from typing import Any, Dict, List, Literal, Optional

Mode = Literal["debate", "structure", "report", "full"]
Role = Literal["pro", "con"]


def eprint(*args: Any) -> None:
    """Debug logs to stderr only."""
    print(*args, file=sys.stderr)


def write_json(payload: Dict[str, Any]) -> None:
    """Print JSON to stdout only."""
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    sys.stdout.flush()


def ok_response(payload: Dict[str, Any]) -> None:
    """Write OK JSON and exit 0."""
    write_json(payload)
    raise SystemExit(0)


def err_response(mode: str, code: str, message: str, http_hint: int = 400, exit_code: int = 1) -> None:
    """Write error JSON and exit with requested exit code."""
    payload = {
        "ok": False,
        "mode": mode,
        "error": {
            "code": code,
            "message": message,
            "http_hint": http_hint,
        },
    }
    write_json(payload)
    raise SystemExit(exit_code)


def safe_json_loads(s: str, field: str) -> Any:
    try:
        return json.loads(s)
    except Exception as ex:  # noqa: BLE001
        raise ValueError(f"{field} must be valid JSON string ({ex})")


def normalize_sentences_3(text: str) -> str:
    """Normalize a text into exactly 3 period-separated sentences."""
    parts = [p.strip() for p in text.replace("\n", " ").split(".") if p.strip()]
    if len(parts) >= 3:
        parts = parts[:3]
    else:
        while len(parts) < 3:
            parts.append("다음 라운드에서 주장과 근거를 더 명확히 보완하십시오")
    return ". ".join(parts) + "."


def validate_structure(structure: Dict[str, Any]) -> None:
    required_keys = ["claim", "reasons", "assumptions", "counterpoints", "missing_info", "next_revision"]
    for key in required_keys:
        if key not in structure:
            raise ValueError(f"structure missing key: {key}")

    for arr_key in ["reasons", "assumptions", "counterpoints", "missing_info"]:
        if not isinstance(structure[arr_key], list):
            raise ValueError(f"structure.{arr_key} must be a list")

    if not isinstance(structure["next_revision"], str):
        raise ValueError("structure.next_revision must be a string")

    if "\n" in structure["next_revision"] or "\r" in structure["next_revision"]:
        structure["next_revision"] = structure["next_revision"].replace("\r", " ").replace("\n", " ").strip()
    structure["next_revision"] = normalize_sentences_3(structure["next_revision"])


def validate_debate(debate: List[Dict[str, Any]]) -> None:
    if not isinstance(debate, list) or len(debate) != 4:
        raise ValueError("debate must be a list of exactly 4 turns")
    for i, turn in enumerate(debate):
        if "role" not in turn or "text" not in turn:
            raise ValueError(f"debate[{i}] must have role and text")
        if turn["role"] not in ("pro", "con"):
            raise ValueError(f"debate[{i}].role must be 'pro' or 'con'")
        if not isinstance(turn["text"], str) or not turn["text"].strip():
            raise ValueError(f"debate[{i}].text must be a non-empty string")


def extract_keywords_koreanish(text: str) -> List[str]:
    tokens: List[str] = []
    cur: List[str] = []
    for ch in text:
        if ch.isalnum() or ("가" <= ch <= "힣"):
            cur.append(ch)
        else:
            if cur:
                tokens.append("".join(cur))
                cur = []
    if cur:
        tokens.append("".join(cur))

    filtered = [t for t in tokens if 2 <= len(t) <= 6]
    seen = set()
    out: List[str] = []
    for t in filtered:
        if t not in seen:
            out.append(t)
            seen.add(t)
    return out[:8]


def infer_stance_korean(note: str) -> str:
    n = note.lower()
    if any(k in n for k in ["찬성", "필요", "도입", "좋", "해야"]):
        return "긍정적인"
    if any(k in n for k in ["반대", "우려", "위험", "문제", "안"]):
        return "신중한"
    return "조건부"


def summarize_role_lines(debate: List[Dict[str, Any]], role: Role, n: int) -> List[str]:
    texts = [t["text"].strip() for t in debate if t["role"] == role and t["text"].strip()]
    lines: List[str] = []
    for text in texts:
        sentences = [p.strip() for p in text.split(".") if p.strip()]
        for sentence in sentences:
            if len(lines) < n:
                lines.append(sentence + ".")
    while len(lines) < n:
        lines.append("핵심 논지를 더 명확히 정리할 여지가 있습니다.")
    return lines[:n]


def summarize_text_lines(text: str, n: int) -> List[str]:
    t = (text or "").strip()
    if not t:
        return ["(사용자 입력이 비어 있습니다.)", "주장을 1문장으로 정리해보세요.", "근거 2개를 추가해보세요."]

    raw = [p.strip() for p in t.replace("\r", "\n").split("\n") if p.strip()]
    if len(raw) < n:
        sentences = [p.strip() for p in t.split(".") if p.strip()]
        raw = raw + [s + "." for s in sentences]

    lines: List[str] = []
    for p in raw:
        if len(lines) >= n:
            break
        lines.append(p)

    while len(lines) < n:
        lines.append("추가 근거 또는 반론 대비를 보완해보세요.")
    return lines[:n]


def mock_pro(topic: str, user_context: Optional[str], rng: random.Random) -> str:
    reasons = [
        "현실적인 효율과 접근성을 크게 높일 수 있습니다",
        "개인의 학습 격차를 맞춤형으로 줄이는 데 유리합니다",
        "빠른 피드백 루프로 반복 학습을 강화합니다",
    ]
    counters = [
        "다만 편향된 정보나 과도한 의존이 생길 수 있다는 점은 대비가 필요합니다",
        "하지만 인간 교사의 역할까지 완전히 대체하기엔 정서적 상호작용이 부족할 수 있습니다",
        "그럼에도 검증 체계가 없다면 품질 편차가 커질 위험이 있습니다",
    ]
    r1, r2 = rng.sample(reasons, 2)
    c = rng.choice(counters)
    claim = f"저는 '{topic}'에 대해 찬성합니다"
    s2 = f"그 이유는 {r1} 그리고 {r2}"
    return f"{claim}. {s2}. {c}."


def mock_con(topic: str, pro_statement: str, rng: random.Random) -> str:
    keywords = extract_keywords_koreanish(pro_statement)
    kw = rng.choice(keywords) if keywords else "효율"
    weaknesses = [
        "핵심 가정이 '모든 사용자에게 동일한 품질의 피드백이 제공된다'는 점인데 현실에서 흔들릴 수 있습니다",
        "근거가 비용 절감에 치우쳐 장기적 부작용(사고력 저하, 의존성)을 충분히 고려하지 않았습니다",
        "전제 조건(검증, 책임, 안전장치)이 빠져 있어 실행 시 실패 가능성이 큽니다",
    ]
    alternatives = [
        "따라서 전면 도입보다 제한된 범위에서 검증하고, 사람의 감독을 의무화하는 조건부 도입이 합리적입니다",
        "대안으로는 AI를 보조 도구로 두고, 최종 판단과 코칭은 사람에게 남기는 혼합 모델이 더 안전합니다",
        "그래서 고위험 영역부터 제외하고, 평가 기준과 책임 주체를 명확히 한 뒤 단계적으로 확대해야 합니다",
    ]
    s1 = f"{kw}에 대한 주장은 매력적이지만, 그 자체가 곧 타당성을 보장하진 않습니다"
    s2 = rng.choice(weaknesses)
    s3 = rng.choice(alternatives)
    return f"{s1}. {s2}. {s3}."


def mock_structure(topic: str, debate: List[Dict[str, Any]], user_note: str, rng: random.Random) -> Dict[str, Any]:
    note = (user_note or "").strip()
    if len(note) < 20:
        structure = {
            "claim": "입장이 아직 명확히 정리되지 않았습니다.",
            "reasons": [],
            "assumptions": [],
            "counterpoints": [],
            "missing_info": ["주장을 1문장으로 명확히 작성하세요", "근거를 최소 2개 제시하세요"],
            "next_revision": "주장을 1문장으로 정리하십시오. 그 주장을 뒷받침하는 근거 2가지를 추가하십시오. 반대 의견에 대한 대비를 포함하십시오.",
        }
        validate_structure(structure)
        return structure

    claim_starters = ["제 입장은", "저는", "결론적으로"]
    claim = f"{rng.choice(claim_starters)} '{topic}'에 대해 {infer_stance_korean(note)} 입장입니다"

    reasons_pool = [
        "현실적인 비용과 시간 측면에서 효과가 큽니다",
        "학습자의 동기와 지속성을 높일 수 있습니다",
        "검증 가능한 기준과 피드백 루프를 만들 수 있습니다",
        "부작용을 줄이기 위한 안전장치를 설계할 수 있습니다",
    ]
    assumptions_pool = [
        "사용자가 충분한 시간을 들여 자신의 논리를 작성한다는 가정",
        "피드백이 편향 없이 일관되게 제공된다는 가정",
    ]
    counter_pool = [
        "AI의 피드백 품질이 상황에 따라 흔들릴 수 있다는 점",
        "사용자가 결과에 의존해 스스로 사고를 덜 하게 될 위험",
    ]
    missing_pool = [
        "사용자군(학생/직장인)에 따라 어떤 효과 지표를 쓸지",
        "피드백 신뢰도를 어떻게 검증하고 책임질지",
    ]

    reasons = rng.sample(reasons_pool, 2 if rng.random() < 0.7 else 3)
    assumptions = rng.sample(assumptions_pool, 1 if rng.random() < 0.7 else 2)
    counterpoints = rng.sample(counter_pool, 1 if rng.random() < 0.6 else 2)
    missing_info = rng.sample(missing_pool, 1 if rng.random() < 0.6 else 2)

    next_revision = normalize_sentences_3(
        "내 주장을 한 문장으로 더 명확히 쓰십시오. 근거는 사례나 기준으로 구체화하십시오. 가장 강한 반론 1개에 대한 답을 포함하십시오"
    )

    structure = {
        "claim": claim,
        "reasons": reasons,
        "assumptions": assumptions,
        "counterpoints": counterpoints,
        "missing_info": missing_info,
        "next_revision": next_revision,
    }
    validate_structure(structure)
    return structure


def mock_report(topic: str, debate: List[Dict[str, Any]], user_note: str, structure: Dict[str, Any], rng: random.Random) -> str:
    pro_lines = summarize_role_lines(debate, "pro", 3)
    con_lines = summarize_role_lines(debate, "con", 3)
    user_lines = summarize_text_lines(user_note, 3)

    a = (structure.get("assumptions") or ["가정이 명확하지 않습니다"])[0]
    c = (structure.get("counterpoints") or ["반론 고려가 부족합니다"])[0]
    m = (structure.get("missing_info") or ["추가 정보가 필요합니다"])[0]

    next_q_candidates = [
        "이 주장을 검증할 수 있는 지표(성과/부작용)는 무엇인가?",
        "가장 강한 반대 논리는 무엇이며, 그에 대한 반박은 무엇인가?",
        "조건부 도입을 한다면 어떤 범위와 안전장치가 필요한가?",
    ]
    next_q = rng.choice(next_q_candidates)

    return (
        "# 📝 ThinkGym 세션 리포트\n\n"
        "## 1. 오늘의 질문\n"
        f"{topic}\n\n"
        "## 2. 찬반 핵심 요약\n"
        f"- **찬성:** {pro_lines[0]}\n"
        f"  {pro_lines[1]}\n"
        f"  {pro_lines[2]}\n"
        f"- **반대:** {con_lines[0]}\n"
        f"  {con_lines[1]}\n"
        f"  {con_lines[2]}\n\n"
        "## 3. 사용자의 입장\n"
        f"{user_lines[0]}\n"
        f"{user_lines[1]}\n"
        f"{user_lines[2]}\n\n"
        "## 4. 논리 구조 개선 포인트\n"
        f"- {a}\n"
        f"- {c}\n"
        f"- {m}\n\n"
        "## 5. 다음 라운드 추천 질문\n"
        f"{next_q}\n"
    )


def run_engine(
    mode: Mode,
    topic: str,
    round_idx: int,
    user_note: Optional[str],
    debate_json: Optional[str],
    structure_json: Optional[str],
    mock: bool,
    seed: int,
) -> Dict[str, Any]:
    rng = random.Random(seed + round_idx * 1000)

    if mode == "debate":
        user_ctx = (user_note or "").strip() or None
        pro1 = mock_pro(topic, user_ctx, rng)
        con1 = mock_con(topic, pro1, rng)
        pro2 = mock_pro(topic, user_ctx, rng)
        con2 = mock_con(topic, pro2, rng)
        debate = [
            {"role": "pro", "text": pro1},
            {"role": "con", "text": con1},
            {"role": "pro", "text": pro2},
            {"role": "con", "text": con2},
        ]
        validate_debate(debate)
        return {
            "ok": True,
            "mode": "debate",
            "topic": topic,
            "round": round_idx,
            "debate": debate,
            "meta": {"mock": mock, "seed": seed},
        }

    if mode in ("structure", "report"):
        if debate_json is None or not str(debate_json).strip():
            raise ValueError("debate_json is required for structure/report mode")
        debate = safe_json_loads(debate_json, "debate_json")
        validate_debate(debate)

    if mode == "structure":
        note = (user_note or "").strip()
        structure = mock_structure(topic, debate, note, rng)
        validate_structure(structure)
        return {
            "ok": True,
            "mode": "structure",
            "topic": topic,
            "round": round_idx,
            "structure": structure,
            "meta": {"mock": mock, "seed": seed},
        }

    if mode == "report":
        note = (user_note or "").strip()
        if structure_json is not None and str(structure_json).strip():
            structure = safe_json_loads(structure_json, "structure_json")
            if not isinstance(structure, dict):
                raise ValueError("structure_json must decode to an object")
            validate_structure(structure)
            structure_source = "input"
        else:
            structure = mock_structure(topic, debate, note, rng)
            validate_structure(structure)
            structure_source = "generated"

        report = mock_report(topic, debate, note, structure, rng)
        return {
            "ok": True,
            "mode": "report",
            "topic": topic,
            "round": round_idx,
            "report": report,
            "meta": {"mock": mock, "seed": seed, "structure_source": structure_source},
        }

    if mode == "full":
        user_ctx = (user_note or "").strip() or None
        pro1 = mock_pro(topic, user_ctx, rng)
        con1 = mock_con(topic, pro1, rng)
        pro2 = mock_pro(topic, user_ctx, rng)
        con2 = mock_con(topic, pro2, rng)
        debate = [
            {"role": "pro", "text": pro1},
            {"role": "con", "text": con1},
            {"role": "pro", "text": pro2},
            {"role": "con", "text": con2},
        ]
        validate_debate(debate)

        note = (user_note or "").strip()
        structure = mock_structure(topic, debate, note, rng)
        validate_structure(structure)
        report = mock_report(topic, debate, note, structure, rng)

        return {
            "ok": True,
            "mode": "full",
            "topic": topic,
            "round": round_idx,
            "debate": debate,
            "structure": structure,
            "report": report,
            "meta": {"mock": mock, "seed": seed},
        }

    raise ValueError(f"Unknown mode: {mode}")


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ThinkGym run.py (mock-first engine)")
    parser.add_argument("--mode", required=True, choices=["debate", "structure", "report", "full"])
    parser.add_argument("--topic", required=True, help="Debate topic")
    parser.add_argument("--round", type=int, default=1, help="Round index (1-based)")
    parser.add_argument("--user-note", default=None, help="User note text (optional for structure/report/full)")
    parser.add_argument("--debate-json", default=None, help="Debate turns JSON string (required for structure/report)")
    parser.add_argument("--structure-json", default=None, help="Structure JSON string (optional for report; preferred if Step4 result exists)")
    parser.add_argument("--mock", action="store_true", help="Use mock generation (no LLM)")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic seed for mock")
    return parser.parse_args(argv)


def main(argv: List[str]) -> None:
    args = parse_args(argv)
    mode: Mode = args.mode
    topic = (args.topic or "").strip()

    if not topic:
        err_response(mode, "INVALID_INPUT", "topic is required", 400, exit_code=1)

    if args.round < 1:
        err_response(mode, "INVALID_INPUT", "round must be >= 1", 400, exit_code=1)

    if not args.mock:
        err_response(mode, "NOT_IMPLEMENTED", "Non-mock (LLM) mode is not implemented yet. Use --mock.", 501, exit_code=1)

    try:
        payload = run_engine(
            mode=mode,
            topic=topic,
            round_idx=args.round,
            user_note=args.user_note,
            debate_json=args.debate_json,
            structure_json=args.structure_json,
            mock=True,
            seed=args.seed,
        )
        ok_response(payload)
    except ValueError as ve:
        err_response(mode, "INVALID_INPUT", str(ve), 400, exit_code=1)
    except SystemExit:
        raise
    except Exception as ex:  # noqa: BLE001
        eprint("Unexpected error:", repr(ex))
        err_response(mode, "INTERNAL_ERROR", "Unexpected server error", 500, exit_code=2)


if __name__ == "__main__":
    main(sys.argv[1:])
