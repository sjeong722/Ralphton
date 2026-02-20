"use client";

import { useMemo, useState, type ReactNode } from "react";

type DebateTurn = { role: "pro" | "con"; text: string };
type Structure = {
  claim: string;
  reasons: string[];
  assumptions: string[];
  counterpoints: string[];
  missing_info: string[];
  next_revision: string;
};

export function Step1Topic(props: {
  presets: string[];
  topic: string;
  setTopic: (v: string) => void;
  customTopic: string;
  setCustomTopic: (v: string) => void;
}) {
  const { presets, topic, setTopic, customTopic, setCustomTopic } = props;

  return (
    <div className="space-y-5">
      <div>
        <div className="text-lg font-semibold">오늘의 질문</div>
        <div className="mt-1 text-sm text-neutral-500">데모에서는 프리셋을 추천합니다. 필요하면 직접 입력으로 바꿀 수 있어요.</div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border p-4">
          <div className="text-sm font-semibold">프리셋 선택</div>
          <select value={topic} onChange={(e) => setTopic(e.target.value)} className="mt-3 w-full rounded-xl border px-3 py-2 text-sm">
            {presets.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
          <div className="mt-2 text-xs text-neutral-500">프리셋을 선택하면 데모 안정성이 좋아집니다.</div>
        </div>

        <div className="rounded-2xl border p-4">
          <div className="text-sm font-semibold">직접 입력 (옵션)</div>
          <input
            value={customTopic}
            onChange={(e) => setCustomTopic(e.target.value)}
            placeholder="예: 원격근무를 기본 근무 형태로 전환해야 하는가?"
            className="mt-3 w-full rounded-xl border px-3 py-2 text-sm"
          />
          <div className="mt-2 text-xs text-neutral-500">직접 입력이 비어있으면 프리셋이 사용됩니다.</div>
        </div>
      </div>

      <div className="rounded-2xl bg-neutral-50 p-4 text-sm text-neutral-700">
        <div className="font-semibold">진행 방식</div>
        <div className="mt-1">1) 질문 → 2) 찬반 토론 → 3) 내 생각 정리 → 4) 구조 피드백 → 5) 리포트</div>
      </div>
    </div>
  );
}

export function Step2Debate({ debate }: { debate: DebateTurn[] }) {
  return (
    <div className="space-y-5">
      <div>
        <div className="text-lg font-semibold">찬반 토론</div>
        <div className="mt-1 text-sm text-neutral-500">먼저 양쪽 관점을 빠르게 확인합니다.</div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {debate.map((t, i) => (
          <div key={i} className="rounded-2xl border p-4">
            <div className="flex items-center justify-between">
              <span className={["rounded-full px-2 py-1 text-xs font-semibold", t.role === "pro" ? "bg-blue-50 text-blue-700" : "bg-red-50 text-red-700"].join(" ")}>
                {t.role === "pro" ? "찬성" : "반대"}
              </span>
              <span className="text-xs text-neutral-400">Turn {i + 1}</span>
            </div>
            <div className="mt-3 whitespace-pre-wrap text-sm leading-6 text-neutral-800">{t.text}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function Step3Note({ userNote, setUserNote }: { userNote: string; setUserNote: (v: string) => void }) {
  const [seconds, setSeconds] = useState<number>(120);

  const mmss = useMemo(() => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${String(s).padStart(2, "0")}`;
  }, [seconds]);

  return (
    <div className="space-y-5">
      <div>
        <div className="text-lg font-semibold">내 생각 정리</div>
        <div className="mt-1 text-sm text-neutral-500">정답이 아니라 내 논리의 형태를 정리해보세요.</div>
      </div>

      <div className="flex flex-col items-start justify-between gap-3 rounded-2xl border bg-neutral-50 p-4 md:flex-row md:items-center">
        <div>
          <div className="text-sm font-semibold">생각 시간</div>
          <div className="text-xs text-neutral-500">타이머는 데모용(정적)입니다. API 연결 시 실제로 돌려도 좋아요.</div>
        </div>
        <div className="flex items-center gap-3">
          <div className="rounded-xl border bg-white px-3 py-2 text-sm font-semibold">{mmss}</div>
          <button onClick={() => setSeconds((v) => v + 30)} className="rounded-xl border px-3 py-2 text-sm font-medium hover:bg-white">
            +30초
          </button>
          <button onClick={() => setSeconds(120)} className="rounded-xl border px-3 py-2 text-sm font-medium hover:bg-white">
            리셋
          </button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="md:col-span-2">
          <textarea
            value={userNote}
            onChange={(e) => setUserNote(e.target.value)}
            className="h-56 w-full resize-none rounded-2xl border p-4 text-sm leading-6"
            placeholder={[
              "가이드:",
              "- 내 결론(주장)은?",
              "- 근거 2개는?",
              "- 가장 강한 반론 1개에 대한 답은?",
              "",
              "※ 비워도 다음으로 진행 가능합니다(구조 에이전트 fallback).",
            ].join("\n")}
          />
        </div>
        <div className="rounded-2xl border bg-neutral-50 p-4 text-sm text-neutral-700">
          <div className="font-semibold">작성 팁</div>
          <ul className="mt-2 list-disc space-y-2 pl-5 text-sm">
            <li>주장은 한 문장으로.</li>
            <li>근거는 2개만.</li>
            <li>반론을 먼저 적고 답해도 좋습니다.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export function Step4Structure({ structure }: { structure: Structure }) {
  const [copied, setCopied] = useState(false);

  async function copy(text: string) {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 900);
    } catch {}
  }

  return (
    <div className="space-y-5">
      <div>
        <div className="text-lg font-semibold">논리 구조 피드백</div>
        <div className="mt-1 text-sm text-neutral-500">점수가 아니라 구조를 봅니다.</div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card title="핵심 주장">{structure.claim}</Card>

        <Card title="근거">
          <ul className="list-disc space-y-2 pl-5 text-sm">
            {structure.reasons.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </Card>

        <Card title="숨은 가정">
          <ul className="list-disc space-y-2 pl-5 text-sm">
            {structure.assumptions.map((a, i) => (
              <li key={i}>{a}</li>
            ))}
          </ul>
        </Card>

        <Card title="고려할 반론">
          <ul className="list-disc space-y-2 pl-5 text-sm">
            {structure.counterpoints.map((c, i) => (
              <li key={i}>{c}</li>
            ))}
          </ul>
        </Card>

        <Card title="추가로 필요한 정보">
          <ul className="list-disc space-y-2 pl-5 text-sm">
            {structure.missing_info.map((m, i) => (
              <li key={i}>{m}</li>
            ))}
          </ul>
        </Card>

        <div className="rounded-2xl border p-4">
          <div className="flex items-center justify-between">
            <div className="text-sm font-semibold">다음 라운드 개선 문장</div>
            <button onClick={() => copy(structure.next_revision)} className="rounded-xl border px-3 py-1.5 text-xs font-medium hover:bg-neutral-50">
              {copied ? "복사됨" : "복사"}
            </button>
          </div>
          <div className="mt-3 text-sm leading-6 text-neutral-800">{structure.next_revision}</div>
        </div>
      </div>
    </div>
  );
}

export function Step5Report({ report }: { report: string }) {
  const [copied, setCopied] = useState(false);

  async function copy(text: string) {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 900);
    } catch {}
  }

  return (
    <div className="space-y-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-lg font-semibold">ThinkGym 세션 리포트</div>
          <div className="mt-1 text-sm text-neutral-500">한 장으로 읽히는 결과물입니다.</div>
        </div>
        <button onClick={() => copy(report)} className="rounded-xl border px-3 py-2 text-sm font-medium hover:bg-neutral-50">
          {copied ? "복사됨" : "리포트 복사"}
        </button>
      </div>

      <div className="rounded-2xl border bg-neutral-50 p-6">
        <pre className="whitespace-pre-wrap text-sm leading-6 text-neutral-800">{report}</pre>
      </div>
    </div>
  );
}

function Card({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="rounded-2xl border p-4">
      <div className="text-sm font-semibold">{title}</div>
      <div className="mt-3 text-sm leading-6 text-neutral-800">{children}</div>
    </div>
  );
}
