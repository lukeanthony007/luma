// OMP host adapter for Luma's page-size rule: refuse (not stop) a write or edit that would grow a retained Markdown page
// past LUMA_PAGE_LIMIT bytes (default 16384), add per-batch, per-session or dated headings or lines, or create an overflow page
// ("-continued", "part-2", "31-52"); past LUMA_PAGE_SOFT bytes (default 12288) an allowed change gets a non-blocking reminder to split
// by subject. Refusals and reminders are appended to $LUMA_PAGE_GUARD_LOG. Load with `omp -e page-size-guard.ts`. Not part of the portable seed payload.
import fs from "node:fs";
import { advise, decide } from "./page_size_core.mjs";

export default function (pi: any) {
  pi.on("tool_call", async (event: any, ctx: any) => {
    const limit = Number(process.env.LUMA_PAGE_LIMIT || 16384);
    const log = process.env.LUMA_PAGE_GUARD_LOG;
    const verdict = decide(ctx.cwd, event.toolName, event.input, limit);
    if (!verdict) {
      const advice = advise(ctx.cwd, event.toolName, event.input, Number(process.env.LUMA_PAGE_SOFT || 12288), limit);
      if (!advice) return;
      if (log) fs.appendFileSync(log, JSON.stringify({ at: new Date().toISOString(), tool: event.toolName, kind: "advice", path: event.input?.path }) + "\n");
      return { additionalContext: advice };
    }
    if (log) fs.appendFileSync(log, JSON.stringify({ at: new Date().toISOString(), tool: event.toolName, kind: "refusal", ...verdict, message: undefined }) + "\n");
    return { block: true, reason: verdict.message };
  });
}
