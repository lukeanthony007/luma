// OMP host adapter for Luma's page-size rule: refuse (not stop) a write or edit that would grow a retained Markdown page
// past LUMA_PAGE_LIMIT bytes (default 16384) or add per-batch, per-session or dated headings, and append each refusal to
// $LUMA_PAGE_GUARD_LOG. Load with `omp -e page-size-guard.ts`. Not part of the portable seed payload.
import fs from "node:fs";
import { decide } from "./page_size_core.mjs";

export default function (pi: any) {
  pi.on("tool_call", async (event: any, ctx: any) => {
    const limit = Number(process.env.LUMA_PAGE_LIMIT || 16384);
    const verdict = decide(ctx.cwd, event.toolName, event.input, limit);
    if (!verdict) return;
    const log = process.env.LUMA_PAGE_GUARD_LOG;
    if (log) fs.appendFileSync(log, JSON.stringify({ at: new Date().toISOString(), tool: event.toolName, ...verdict, message: undefined }) + "\n");
    return { block: true, reason: verdict.message };
  });
}
