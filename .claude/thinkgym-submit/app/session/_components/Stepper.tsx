export default function Stepper({ step }: { step: 1 | 2 | 3 | 4 | 5 }) {
  const items = [
    { n: 1, label: "질문" },
    { n: 2, label: "찬반토론" },
    { n: 3, label: "생각정리" },
    { n: 4, label: "구조피드백" },
    { n: 5, label: "리포트" },
  ] as const;

  return (
    <div className="flex flex-wrap items-center gap-3">
      {items.map((it, idx) => {
        const active = it.n === step;
        const done = it.n < step;

        return (
          <div key={it.n} className="flex items-center gap-3">
            <div
              className={[
                "flex items-center gap-2 rounded-full border px-3 py-1.5 text-sm",
                active ? "border-neutral-900 bg-neutral-900 text-white" : "",
                done && !active ? "border-neutral-300 bg-neutral-100 text-neutral-700" : "",
                !done && !active ? "border-neutral-200 bg-white text-neutral-500" : "",
              ].join(" ")}
            >
              <span className="text-xs font-semibold">{it.n}</span>
              <span className="text-xs font-medium">{it.label}</span>
            </div>

            {idx !== items.length - 1 && <div className="hidden h-px w-10 bg-neutral-200 sm:block" />}
          </div>
        );
      })}
    </div>
  );
}
