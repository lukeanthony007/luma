import { TFile, App, } from 'obsidian';

export function getTemplate(app: App, templateName: string): TFile | null {
  const vault = app.vault;
  const files = vault.getMarkdownFiles()
    .filter((file: TFile) => file.path.startsWith('Resources/Templates/') && file.name === templateName);
  if (files.length === 0) {
    console.log(`Template ${templateName} not found in Ressources/Templates.`);
    return null;
  }
  return files[0];
}

export function getNotesFromFolder(app: App, folderPath: string): TFile[] {
  const vault = app.vault;
  const allFiles = vault.getMarkdownFiles();

  const files = allFiles.filter((file: TFile) => {
    const matches = file.path.startsWith(folderPath + '/');
    return matches;
  });

  if (files.length === 0) {
    console.log(`No notes found in ${folderPath}`);
  }
  return files;
}

export function formattedNote(app: App, content: string,): boolean {
  return true;
}