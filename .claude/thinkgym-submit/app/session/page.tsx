"use client";

import { useMemo, useState } from "react";
import Stepper from "./_components/Stepper";
import { Step1Topic, Step2Debate, Step3Note, Step4Structure, Step5Report } from "./_components/StepViews";

type Step = 1 | 2 | 3 | 4 | 5;

type DebateTurn = { role: "pro" | "con"; text: string };
type Structure = {
  claim: string;
  reasons: string[];
  assumptions: string[];
  counterpoints: string[];
  missing_info: string[];
  next_revision: string;
};
type ApiAction = "debate" | "structure" | "report";

const TOPIC_PRESETS = [
  "AI가 교사를 대체해야 하는가?",
  "대학 입시에서 면접 비중을 늘려야 하는가?",
  "청소년의 스마트폰 사용을 법으로 제한해야 하는가?",
  "원격근무를 기본 근무 형태로 전환해야 하는가?",
  "탄소세를 강하게 도입해야 하는가?",
];

export default function SessionPage() {
  const [round, setRound] = useState<number>(1);
  const [step, setStep] = useState<Step>(1);
  const [seed] = useState<number>(42);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [lastAction, setLastAction] = useState<ApiAction | null>(null);

  const [topic, setTopic] = useState<string>(TOPIC_PRESETS[0]);
  const [customTopic, setCustomTopic] = useState<string>("");
  const [debate, setDebate] = useState<DebateTurn[]>([]);
  const [structure, setStructure] = useState<Structure | null>(null);
  const [report, setReport] = useState<string>("");
  const [userNote, setUserNote] = useState<string>("");

  const sampleDebate: DebateTurn[] = useMemo(
    () => [
      {
        role: "pro",
        text: "저는 'AI가 교사를 대체해야 하는가?'에 대해 찬성합니다. 그 이유는 학습 접근성과 효율을 크게 높일 수 있고 개인별 맞춤 피드백으로 격차를 줄이기 쉽기 때문입니다. 다만 검증 체계가 없다면 품질 편차가 커질 수 있습니다.",
      },
      {
        role: "con",
        text: "효율에 대한 주장은 매력적이지만, 그 자체가 곧 타당성을 보장하진 않습니다. 전제 조건(검증, 책임, 안전장치)이 빠져 있어 실행 시 실패 가능성이 큽니다. 따라서 혼합 모델로 사람의 감독을 의무화하는 조건부 도입이 합리적입니다.",
      },
      {
        role: "pro",
        text: "저는 여전히 찬성합니다. AI는 반복 학습과 즉시 피드백에 강하고, 교사의 시간을 고차원 코칭에 재배치할 수 있습니다. 다만 정서적 상호작용은 사람 중심으로 남겨야 합니다.",
      },
      {
        role: "con",
        text: "감독이라는 말 자체가 핵심 리스크를 인정하는 셈입니다. 사용자가 결과에 의존해 스스로 사고를 덜 하게 될 위험도 충분히 고려해야 합니다. 그래서 고위험 영역을 제외하고 단계적으로 확대하는 게 안전합니다.",
      },
    ],
    [],
  );

  const sampleStructure: Structure = useMemo(
    () => ({
      claim: "저는 'AI가 교사를 대체해야 하는가?'에 대해 조건부로 긍정적인 입장입니다.",
      reasons: ["학습 접근성과 효율이 개선될 수 있습니다", "맞춤형 피드백으로 격차 완화가 가능합니다"],
      assumptions: ["피드백 품질이 일관되게 유지된다는 가정"],
      counterpoints: ["정서적 상호작용·동기부여는 사람의 역할이 중요하다는 점"],
      missing_info: ["피드백 품질을 어떤 지표로 검증하고 책임질지"],
      next_revision:
        "내 주장을 한 문장으로 더 명확히 쓰십시오. 근거는 사례나 기준으로 구체화하십시오. 가장 강한 반론 1개에 대한 답을 포함하십시오.",
    }),
    [],
  );

  const sampleReport = useMemo(
    () => `# 📝 ThinkGym 세션 리포트

## 1. 오늘의 질문
${topic}

## 2. 찬반 핵심 요약
- **찬성:** 접근성과 효율 개선을 강조합니다.
  맞춤형 피드백으로 격차 완화 가능성을 말합니다.
  다만 검증 체계가 필요하다고 전제합니다.
- **반대:** 전제 조건(검증/책임/안전장치)의 부재를 지적합니다.
  의존성·사고력 저하 위험을 강조합니다.
  혼합 모델/단계적 도입을 대안으로 제시합니다.

## 3. 사용자의 입장
조건부로 찬성입니다.
효율과 접근성은 장점입니다.
감독과 검증 장치가 필요합니다.

## 4. 논리 구조 개선 포인트
- 피드백 품질이 일관되게 유지된다는 가정을 점검하세요.
- 정서적 상호작용 영역의 반론에 대한 답을 포함하세요.
- 검증 지표와 책임 주체를 더 명확히 정의하세요.

## 5. 다음 라운드 추천 질문
조건부 도입을 한다면 어떤 범위와 안전장치가 필요한가?
`,
    [topic],
  );

  const loadingLabel = useMemo(() => {
    if (!isLoading) return "";
    if (lastAction === "debate") return "토론 생성 중...";
    if (lastAction === "structure") return "구조 분석 중...";
    if (lastAction === "report") return "리포트 생성 중...";
    return "처리 중...";
  }, [isLoading, lastAction]);

  const primaryLabel = useMemo(() => {
    if (isLoading) return loadingLabel;
    switch (step) {
      case 1:
        return "토론 시작";
      case 2:
        return "내 생각 정리하기";
      case 3:
        return "구조 피드백 받기";
      case 4:
        return "세션 리포트 생성";
      case 5:
        return "다음 라운드 시작";
      default:
        return "다음";
    }
  }, [step, isLoading, loadingLabel]);

  const secondaryLabel = useMemo(() => {
    if (step === 1) return "초기화";
    return "뒤로";
  }, [step]);

  function resetSession() {
    setRound(1);
    setStep(1);
    setTopic(TOPIC_PRESETS[0]);
    setCustomTopic("");
    setDebate([]);
    setStructure(null);
    setReport("");
    setUserNote("");
    setErrorMessage("");
    setLastAction(null);
  }

  async function postJson(path: string, payload: Record<string, unknown>) {
    const response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    let body: any = null;
    try {
      body = await response.json();
    } catch {
      throw new Error("응답 파싱에 실패했습니다.");
    }

    if (!response.ok || !body?.ok) {
      throw new Error(body?.error?.message ?? "요청 처리에 실패했습니다.");
    }
    return body;
  }

  async function runDebate() {
    const finalTopic = (customTopic || topic).trim();
    if (!finalTopic) {
      setErrorMessage("질문을 입력해 주세요.");
      return;
    }

    setIsLoading(true);
    setLastAction("debate");
    setErrorMessage("");
    try {
      const body = await postJson("/api/debate", {
        topic: finalTopic,
        round,
        seed,
        userNote,
      });
      setTopic(finalTopic);
      setDebate(body.debate ?? []);
      setStructure(null);
      setReport("");
      setStep(2);
    } catch (error: any) {
      setErrorMessage(error?.message ?? "토론 생성에 실패했습니다.");
    } finally {
      setIsLoading(false);
    }
  }

  async function runStructure() {
    if (debate.length !== 4) {
      setErrorMessage("토론 데이터가 없어 구조 분석을 진행할 수 없습니다.");
      return;
    }
    setIsLoading(true);
    setLastAction("structure");
    setErrorMessage("");
    try {
      const body = await postJson("/api/structure", {
        topic,
        round,
        seed,
        debate,
        userNote,
      });
      setStructure(body.structure ?? null);
      setStep(4);
    } catch (error: any) {
      setErrorMessage(error?.message ?? "구조 분석에 실패했습니다.");
    } finally {
      setIsLoading(false);
    }
  }

  async function runReport() {
    if (debate.length !== 4) {
      setErrorMessage("토론 데이터가 없어 리포트를 생성할 수 없습니다.");
      return;
    }
    setIsLoading(true);
    setLastAction("report");
    setErrorMessage("");
    try {
      const body = await postJson("/api/report", {
        topic,
        round,
        seed,
        debate,
        userNote,
        structure,
      });
      setReport(body.report ?? "");
      setStep(5);
    } catch (error: any) {
      setErrorMessage(error?.message ?? "리포트 생성에 실패했습니다.");
    } finally {
      setIsLoading(false);
    }
  }

  async function retryLastAction() {
    if (lastAction === "debate") await runDebate();
    if (lastAction === "structure") await runStructure();
    if (lastAction === "report") await runReport();
  }

  async function goNext() {
    if (isLoading) return;

    if (step === 1) {
      await runDebate();
      return;
    }
    if (step === 2) {
      setErrorMessage("");
      setStep(3);
      return;
    }
    if (step === 3) {
      await runStructure();
      return;
    }
    if (step === 4) {
      await runReport();
      return;
    }
    if (step === 5) {
      const nextDraft = structure?.next_revision ?? "";
      setRound((r) => r + 1);
      setStep(1);
      setDebate([]);
      setStructure(null);
      setReport("");
      setCustomTopic("");
      setUserNote(nextDraft);
      setErrorMessage("");
      return;
    }
  }

  function goBackOrReset() {
    if (isLoading) return;
    if (step === 1) {
      resetSession();
      return;
    }
    setErrorMessage("");
    setStep((s) => Math.max(1, (s - 1) as Step) as Step);
  }

  return (
    <div className="min-h-screen bg-neutral-50 text-neutral-900">
      <div className="border-b bg-white">
        <div className="mx-auto flex w-full max-w-[1100px] items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-neutral-900" />
            <div>
              <div className="text-sm font-semibold">ThinkGym</div>
              <div className="text-xs text-neutral-500">Thinking Session</div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="rounded-full border px-3 py-1 text-xs text-neutral-700">Round {round}</div>
            <button
              onClick={() => {
                if (isLoading) return;
                resetSession();
              }}
              className="rounded-xl border px-3 py-2 text-xs font-medium hover:bg-neutral-50 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={isLoading}
            >
              Reset
            </button>
          </div>
        </div>
      </div>

      <div className="mx-auto w-full max-w-[1100px] px-6 pt-6">
        <Stepper step={step} />
      </div>

      <div className="mx-auto w-full max-w-[1100px] px-6 pb-28 pt-6">
        <div className="rounded-2xl border bg-white p-6 shadow-sm">
          {step === 1 && (
            <Step1Topic
              presets={TOPIC_PRESETS}
              topic={topic}
              setTopic={setTopic}
              customTopic={customTopic}
              setCustomTopic={setCustomTopic}
            />
          )}
          {step === 2 && <Step2Debate debate={debate.length ? debate : sampleDebate} />}
          {step === 3 && <Step3Note userNote={userNote} setUserNote={setUserNote} />}
          {step === 4 && <Step4Structure structure={structure ?? sampleStructure} />}
          {step === 5 && <Step5Report report={report || sampleReport} />}
        </div>
      </div>

      <div className="fixed bottom-0 left-0 right-0 border-t bg-white/90 backdrop-blur">
        <div className="mx-auto flex w-full max-w-[1100px] items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <button
              onClick={goBackOrReset}
              className="rounded-xl border px-4 py-2 text-sm font-medium hover:bg-neutral-50 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={isLoading}
            >
              {secondaryLabel}
            </button>
            {errorMessage && (
              <button
                onClick={retryLastAction}
                className="rounded-xl border border-amber-300 bg-amber-50 px-4 py-2 text-sm font-medium text-amber-800 hover:bg-amber-100 disabled:cursor-not-allowed disabled:opacity-60"
                disabled={isLoading || !lastAction}
              >
                재시도
              </button>
            )}
          </div>
          <div className="flex flex-col items-end gap-1">
            {errorMessage && <p className="text-xs text-rose-600">{errorMessage}</p>}
            <button
              onClick={goNext}
              className="rounded-xl bg-neutral-900 px-5 py-2.5 text-sm font-semibold text-white hover:bg-neutral-800 disabled:cursor-not-allowed disabled:bg-neutral-400"
              disabled={isLoading}
            >
              {primaryLabel}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
