import { NextResponse } from "next/server";
import { runPython } from "../_utils/runPy";

export const runtime = "nodejs";

export async function POST(req: Request) {
  try {
    const body = await req.json();

    const topic = String(body?.topic ?? "").trim();
    const round = Number(body?.round ?? 1);
    const seed = Number(body?.seed ?? 42);
    const userNote = String(body?.userNote ?? "");
    const debate = body?.debate;

    if (!topic) {
      return NextResponse.json({ ok: false, error: { code: "INVALID_INPUT", message: "topic is required" } }, { status: 400 });
    }
    if (!Array.isArray(debate) || debate.length !== 4) {
      return NextResponse.json({ ok: false, error: { code: "INVALID_INPUT", message: "debate (4 turns) is required" } }, { status: 400 });
    }

    const debateJson = JSON.stringify(debate);

    const args = [
      "backend/run.py",
      "--mode",
      "structure",
      "--topic",
      topic,
      "--round",
      String(round),
      "--seed",
      String(seed),
      "--debate-json",
      debateJson,
      "--mock",
    ];

    args.push("--user-note", userNote);

    const r = await runPython(args, 25_000);
    if (!r.ok) {
      const hint = Number(r.error?.detail?.engine?.error?.http_hint);
      const status = Number.isFinite(hint) && hint >= 400 && hint <= 599 ? hint : 500;
      return NextResponse.json({ ok: false, error: r.error }, { status });
    }

    return NextResponse.json({
      ok: true,
      topic: r.data.topic,
      round: r.data.round,
      structure: r.data.structure,
      meta: r.data.meta,
    });
  } catch (e: any) {
    return NextResponse.json({ ok: false, error: { code: "SERVER_ERROR", message: e?.message ?? "Unknown error" } }, { status: 500 });
  }
}
