import { expect, test } from "bun:test";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import guard from "./page-size-guard.ts";

test("the extension blocks an oversized append through the tool_call hook and logs it", async () => {
  const ws = fs.mkdtempSync(path.join(os.tmpdir(), "page-guard-ext-"));
  fs.mkdirSync(path.join(ws, "wiki"));
  fs.writeFileSync(path.join(ws, "wiki/env.md"), "# Env\n" + "a".repeat(16000) + "\nEND\n");
  const log = path.join(ws, "guard.jsonl");
  process.env.LUMA_PAGE_GUARD_LOG = log;
  let handler: any;
  guard({ on: (name: string, fn: any) => { if (name === "tool_call") handler = fn; } });
  const blocked = await handler({ toolName: "edit", input: { path: "wiki/env.md", old_string: "END", new_string: "END\n" + "b".repeat(1000) } }, { cwd: ws });
  expect(blocked.block).toBe(true);
  expect(blocked.reason).toContain("Split wiki/env.md");
  expect(await handler({ toolName: "edit", input: { path: "wiki/env.md", old_string: "END", new_string: "E" } }, { cwd: ws })).toBeUndefined();
  expect(fs.readFileSync(log, "utf8").trim().split("\n").length).toBe(1);
});
