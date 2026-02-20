import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-neutral-100 p-8">
      <div className="w-full max-w-xl rounded-2xl border bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-semibold">ThinkGym Demo</h1>
        <p className="mt-2 text-sm text-neutral-600">세션 데모 페이지로 이동해 5단계 플로우를 확인하세요.</p>
        <Link
          href="/session"
          className="mt-6 inline-flex rounded-xl bg-neutral-900 px-4 py-2 text-sm font-semibold text-white hover:bg-neutral-800"
        >
          /session 열기
        </Link>
      </div>
    </main>
  );
}
