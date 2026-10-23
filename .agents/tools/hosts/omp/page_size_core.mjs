// Pure decision logic for the OMP page-size guard (no I/O beyond reading the current page).
// A retained Markdown page may not grow past `limit` bytes, and may not gain per-batch, per-session or dated
// headings; shrinking edits (as a split needs) are always allowed. Mirrors luma_knowledge.py's account check.
import fs from "node:fs";
import path from "node:path";

export const EPISODIC = /(?:^|[-_ .])(?:batch|session|sess|run|part|round|day|week|chunk)[-_ ]?\d+|\d{4}-\d{2}-\d{2}/i;
const EXCLUDED_ROOTS = new Set(["inputs", "screenshots", ".agents", ".git"]);

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

export function decide(cwd, toolName, input, limit = 16384) {
  if (!["write", "edit"].includes(toolName) || !input || typeof input !== "object") return null;
  const page = retainedPage(cwd, input.path);
  if (!page) return null;
  const current = fs.existsSync(page.absolute) ? fs.readFileSync(page.absolute, "utf8") : null;
  const next = proposed(current, toolName, input);
  if (next === null) return null;
  const before = current === null ? 0 : Buffer.byteLength(current, "utf8");
  const after = Buffer.byteLength(next, "utf8");
  const reasons = [];
  if (current === null && EPISODIC.test(path.basename(page.rel, ".md"))) {
    reasons.push(`the new page name "${page.rel}" is per-batch, per-session or dated; name pages for their subject`);
  }
  const added = headings(next).filter((h) => EPISODIC.test(" " + h) && !headings(current || "").includes(h));
  if (added.length) {
    reasons.push(`it adds per-batch, per-session or dated headings (${added.slice(0, 3).map((h) => `"${h}"`).join(", ")}); merge the findings into the subject sections they belong to`);
  }
  if (after > limit && after > before) {
    reasons.push(`it would make ${page.rel} ${(after / 1024).toFixed(1)} KB, over the ${(limit / 1024).toFixed(0)} KB that can be read in one pass`);
  }
  if (!reasons.length) return null;
  return {
    path: page.rel, before, after, limit, reasons,
    message: `Refused: ${reasons.join("; and ")}. ` +
      (after > limit && after > before
        ? `Split ${page.rel} before adding to it: move a sub-subject into its own page named for that sub-subject, replace it here with a one-line summary and a link, link the new page from the index, then retry. Edits that make the page smaller are always allowed.`
        : "Retry with the change organised by subject."),
  };
}
