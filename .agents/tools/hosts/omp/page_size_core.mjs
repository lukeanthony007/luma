// Pure decision logic for the OMP page-size guard (no I/O beyond reading the current page).
// A retained Markdown page may not grow past `limit` bytes, and may not gain per-batch, per-session or dated
// headings; shrinking edits (as a split needs) are always allowed. Mirrors luma_knowledge.py's account check.
import fs from "node:fs";
import path from "node:path";

export const EPISODIC = /(?:^|[-_ .])(?:batch|session|sess|run|part|round|day|week|chunk)[-_ ]?\d+|\d{4}-\d{2}-\d{2}/i;
// Overflow pages split by position rather than subject ("-continued", "part-2", item ranges like "31-52"); mirrors luma_knowledge.py.
export const OVERFLOW_NAME = /[-_ .](?:continued|contd|cont|more|overflow|remainder)(?:[-_ .]?\d+)?$|^(?:continued|overflow)\b|(?:^|[-_ .])part[-_ ]?\d+|(?<!\d)\d{2,3}[-_\u2013]\d{2,3}(?!\d)/i;
export const OVERFLOW_HEADING = /\bcontinued\b|\(cont(?:d|\.)?\)|\bpart\s+\d+\b|(?<!\d)\d{2,3}\s*[-\u2013]\s*\d{2,3}(?!\d)/i;
// A line that starts with a batch, session or date label lists findings by arrival, not by subject.
export const BATCH_LINE = /^\s*(?:[-*+]|\d+[.)])?\s*(?:\*\*|__)?(?:batch|session|round|day|week|run)\s*\d+\b|^\s*(?:[-*+]\s*)?\d{4}-\d{2}-\d{2}\b/i;
export const SOFT_TARGET = 12288;
const EXCLUDED_ROOTS = new Set(["inputs", "screenshots", ".agents", ".git"]);

function unfenced(text) {
  const out = [];
  let fence = null;
  for (const line of text.split("\n")) {
    const marker = line.match(/^\s{0,3}(`{3,}|~{3,})/);
    if (fence) {
      if (marker && marker[1][0] === fence[0] && marker[1].length >= fence.length) fence = null;
      continue;
    }
    if (marker) { fence = marker[1]; continue; }
    out.push(line);
  }
  return out;
}

const batchLines = (text) => unfenced(text).filter((line) => BATCH_LINE.test(line)).length;

function headings(text) {
  const out = [];
  let fence = null;
  for (const line of text.split("\n")) {
    const marker = line.match(/^\s{0,3}(`{3,}|~{3,})/);
    if (fence) {
      if (marker && marker[1][0] === fence[0] && marker[1].length >= fence.length) fence = null;
      continue;
    }
    if (marker) { fence = marker[1]; continue; }
    const h = line.match(/^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$/);
    if (h && h[1].length <= 3) out.push(h[2]);
  }
  return out;
}

export function retainedPage(cwd, rawPath) {
  if (typeof rawPath !== "string" || !rawPath.trim()) return null;
  const bare = rawPath.trim().replace(/(:raw)?(:\d+([-+]\d*)?(,\d+)*)?(:raw)?$/, "");
  const absolute = path.resolve(cwd, bare);
  const rel = path.relative(path.resolve(cwd), absolute);
  if (!rel || rel.startsWith("..") || path.isAbsolute(rel)) return null; // the workspace guard owns out-of-workspace paths
  if (!rel.toLowerCase().endsWith(".md") || EXCLUDED_ROOTS.has(rel.split(path.sep)[0])) return null;
  return { absolute, rel: rel.split(path.sep).join("/") };
}

export function proposed(current, toolName, input) {
  if (toolName === "write") return typeof input.content === "string" ? input.content : null;
  if (toolName === "edit") {
    const { old_string: oldText, new_string: newText, replace_all: all } = input;
    if (typeof oldText !== "string" || typeof newText !== "string" || current === null || !current.includes(oldText)) return null; // the edit itself will fail
    return all ? current.split(oldText).join(newText) : current.replace(oldText, () => newText);
  }
  return null;
}

function evaluate(cwd, toolName, input) {
  if (!["write", "edit"].includes(toolName) || !input || typeof input !== "object") return null;
  const page = retainedPage(cwd, input.path);
  if (!page) return null;
  const current = fs.existsSync(page.absolute) ? fs.readFileSync(page.absolute, "utf8") : null;
  const next = proposed(current, toolName, input);
  if (next === null) return null;
  return { page, current, next, before: current === null ? 0 : Buffer.byteLength(current, "utf8"), after: Buffer.byteLength(next, "utf8") };
}

export function decide(cwd, toolName, input, limit = 16384) {
  const state = evaluate(cwd, toolName, input);
  if (!state) return null;
  const { page, current, next, before, after } = state;
  const stem = path.basename(page.rel, ".md");
  const reasons = [];
  if (current === null && EPISODIC.test(stem)) {
    reasons.push(`the new page name "${page.rel}" is per-batch, per-session or dated; name pages for their subject`);
  }
  if (current === null && OVERFLOW_NAME.test(stem)) {
    reasons.push(`the new page name "${page.rel}" marks an overflow or numbered continuation; name the page for the sub-subject it holds`);
  }
  const old = headings(current || "");
  const added = headings(next).filter((h) => EPISODIC.test(" " + h) && !old.includes(h));
  if (added.length) {
    reasons.push(`it adds per-batch, per-session or dated headings (${added.slice(0, 3).map((h) => `"${h}"`).join(", ")}); merge the findings into the subject sections they belong to`);
  }
  const overflow = headings(next).filter((h) => OVERFLOW_HEADING.test(h) && !old.includes(h));
  if (overflow.length) {
    reasons.push(`it adds overflow or numbered-continuation headings (${overflow.slice(0, 3).map((h) => `"${h}"`).join(", ")}); head sections by subject`);
  }
  if (batchLines(next) > batchLines(current || "")) {
    reasons.push("it adds lines listed by batch, session or date; file each finding under the subject it concerns and keep provenance in parentheses");
  }
  const grows = after > limit && after > before;
  if (grows) {
    reasons.push(`it would make ${page.rel} ${(after / 1024).toFixed(1)} KB, over the ${(limit / 1024).toFixed(0)} KB that can be read in one pass`);
  }
  if (!reasons.length) return null;
  return {
    path: page.rel, before, after, limit, reasons,
    message: `Refused: ${reasons.join("; and ")}. ` +
      (grows
        ? `Split ${page.rel} by subject at about ${(SOFT_TARGET / 1024).toFixed(0)} KB before adding to it: move a coherent sub-subject (not the newest items, and not a numbered or "continued" overflow) into its own page named for that sub-subject, replace it here with a one-line summary and a link, link the new page from the index, then retry. Edits that make the page smaller are always allowed.`
        : "Retry with the change organised by subject."),
  };
}

// Non-blocking: an allowed change that grows a page past the soft target gets a reminder to split by subject soon.
export function advise(cwd, toolName, input, soft = SOFT_TARGET, limit = 16384) {
  const state = evaluate(cwd, toolName, input);
  if (!state || decide(cwd, toolName, input, limit)) return null;
  const { page, before, after } = state;
  if (after <= soft || after <= before) return null;
  return `Note: ${page.rel} is now ${(after / 1024).toFixed(1)} KB. Pages work best under about ${(soft / 1024).toFixed(0)} KB, and changes past ${(limit / 1024).toFixed(0)} KB will be refused; before adding much more, split off a coherent sub-subject into its own page named for it (not by batch, and not a "continued" page).`;
}
