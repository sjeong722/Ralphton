import { spawn } from "child_process";

type RunResult =
  | { ok: true; data: any; exitCode: number }
  | { ok: false; error: { code: string; message: string; detail?: any }; exitCode: number };

export async function runPython(args: string[], timeoutMs = 30_000): Promise<RunResult> {
  return new Promise((resolve) => {
    const child = spawn("python3", args, {
      cwd: process.cwd(),
      env: process.env,
    });

    let stdout = "";
    let stderr = "";

    const killTimer = setTimeout(() => {
      try {
        child.kill("SIGKILL");
      } catch {}
    }, timeoutMs);

    child.stdout.on("data", (d) => (stdout += d.toString("utf-8")));
    child.stderr.on("data", (d) => (stderr += d.toString("utf-8")));

    child.on("close", (code) => {
      clearTimeout(killTimer);
      const exitCode = code ?? -1;

      let parsed: any = null;
      try {
        parsed = JSON.parse(stdout);
      } catch (e) {
        resolve({
          ok: false,
          exitCode,
          error: {
            code: "BAD_JSON_FROM_ENGINE",
            message: "Backend engine did not return valid JSON.",
            detail: { stdout: stdout.slice(0, 2000), stderr: stderr.slice(0, 2000), exitCode },
          },
        });
        return;
      }

      if (!parsed?.ok) {
        resolve({
          ok: false,
          exitCode,
          error: {
            code: parsed?.error?.code ?? "ENGINE_ERROR",
            message: parsed?.error?.message ?? "Engine returned ok:false",
            detail: { engine: parsed, stderr: stderr.slice(0, 2000), exitCode },
          },
        });
        return;
      }

      resolve({ ok: true, data: { ...parsed, _stderr: stderr }, exitCode });
    });
  });
}
