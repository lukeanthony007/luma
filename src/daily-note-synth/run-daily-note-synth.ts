import { TFile, App, Notice, } from 'obsidian';
import { getNotesFromFolder, } from './utils';
import { synthesizeDailyNote } from './synthesize-daily-note';

export default async function runDailyNoteSynthesis(app: App) {
  const dailyNotes = getNotesFromFolder(app, "Daily Notes");
  if (dailyNotes.length === 0) {
    console.log(`No daily notes found in Daily Notes folder.`);
    return;
  }
  
  const today = new Date().toLocaleDateString('sv'); // 'sv' locale gives YYYY-MM-DD
  const pastDailyNotes = dailyNotes.filter((file: TFile) => file.name !== `${today}.md`);
  
  // Ensure the directory exists
  const synthDir = "synthesized-notes";
  if (!app.vault.getAbstractFileByPath(synthDir)) {
    await app.vault.createFolder(synthDir);
  }

  pastDailyNotes.forEach((file: TFile) => {
    app.vault.read(file)
      .then(async (content: string) => {
        const processedContent = await synthesizeDailyNote(content);
        // write to new file in synthesized-notes directory
        const newFileName = `${synthDir}/${file.name.replace('.md', '')}-synthesized.md`;
        const newFile = app.vault.getAbstractFileByPath(newFileName);
        if (newFile) {
          console.log(`File ${newFileName} already exists. Skipping.`);
          return;
        }
        await app.vault.create(newFileName, processedContent);
        new Notice(`Synthesized daily note created: ${newFileName}`);
      });
  });
}