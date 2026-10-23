import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { decide } from "./page_size_core.mjs";

function workspace(files = {}) {
  const ws = fs.mkdtempSync(path.join(os.tmpdir(), "page-guard-"));
  for (const [name, text] of Object.entries(files)) {
    fs.mkdirSync(path.dirname(path.join(ws, name)), { recursive: true });
    fs.writeFileSync(path.join(ws, name), text);
  }
  return ws;
}

test("growth past the limit is refused with split instructions; growth below it passes", () => {
  const ws = workspace({ "wiki/env.md": "# Env\n\n" + "a".repeat(15000) + "\nEND\n" });
  const small = decide(ws, "edit", { path: "wiki/env.md", old_string: "END", new_string: "END\nmore" });
  assert.equal(small, null);
  const big = decide(ws, "edit", { path: "wiki/env.md", old_string: "END", new_string: "END\n" + "b".repeat(2000) });
  assert.match(big.message, /Split wiki\/env\.md before adding/);
  assert.ok(big.after > 16384 && big.before < 16384);
});

test("shrinking an oversized page is always allowed, so a split can proceed", () => {
  const ws = workspace({ "wiki/env.md": "# Env\n\n## Sites\n" + "s".repeat(20000) + "\n## Forms\nFORMS\n" });
  assert.equal(decide(ws, "edit", { path: "wiki/env.md", old_string: "s".repeat(20000), new_string: "See [sites](env/sites.md)." }), null);
  assert.ok(decide(ws, "edit", { path: "wiki/env.md", old_string: "FORMS", new_string: "FORMS more" }));
});

test("per-batch headings and page names are refused even when small", () => {
  const ws = workspace({ "wiki/env.md": "# Env\n\n## Sites\nx\n" });
  const heading = decide(ws, "edit", { path: "wiki/env.md", old_string: "x\n", new_string: "x\n\n## Batch 07 task records\ny\n" });
  assert.match(heading.reasons[0], /Batch 07 task records/);
  assert.ok(decide(ws, "write", { path: "wiki/batch-07-review.md", content: "# Review\n" }));
  assert.equal(decide(ws, "write", { path: "wiki/checkout-forms.md", content: "# Checkout forms\n" }), null);
});

test("existing episodic headings do not block unrelated edits; sources, seed and other tools are out of scope", () => {
  const ws = workspace({ "wiki/env.md": "# Env\n\n## Batch 01 task records\nx\n", "inputs/t.md": "z" });
  assert.equal(decide(ws, "edit", { path: "wiki/env.md", old_string: "x", new_string: "x2" }), null);
  assert.equal(decide(ws, "write", { path: "inputs/big.md", content: "c".repeat(40000) }), null);
  assert.equal(decide(ws, "write", { path: ".agents/notes.md", content: "c".repeat(40000) }), null);
  assert.equal(decide(ws, "read", { path: "wiki/env.md" }), null);
  assert.equal(decide(ws, "write", { path: "wiki/data.json", content: "c".repeat(40000) }), null);
});

test("replace_all and failing edits are sized correctly", () => {
  const ws = workspace({ "wiki/env.md": "k ".repeat(3000) });
  assert.ok(decide(ws, "edit", { path: "wiki/env.md", old_string: "k", new_string: "kkkkkkk", replace_all: true }));
  assert.equal(decide(ws, "edit", { path: "wiki/env.md", old_string: "absent", new_string: "x".repeat(40000) }), null);
});
