import { App, TFile } from "obsidian";

export async function getObsidianNotes(app: App): Promise<{ file: TFile; content: string }[]> {
  const files = app.vault.getMarkdownFiles();
  const result = [];

  for (const file of files) {
    const content = await app.vault.read(file);
    result.push({ file, content });
  }

  return result;
}
