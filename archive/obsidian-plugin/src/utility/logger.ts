import { App, normalizePath, TFile } from "obsidian";

const defaultLogPath = ".obsidian/plugins/obsidian-sample-plugin/logs/luma-log.json";
const defaultTextLogPath = ".obsidian/plugins/obsidian-sample-plugin/logs/luma-haikus.md";

async function ensureDirectory(app: App, filePath: string): Promise<void> {
  const parts = filePath.split("/");
  parts.pop(); // remove the filename
  let currentPath = "";
  for (const part of parts) {
    currentPath = currentPath ? `${currentPath}/${part}` : part;
    try {
      await app.vault.adapter.stat(currentPath);
    } catch {
      await app.vault.createFolder(currentPath);
    }
  }
}

export async function logToFormattedFile(
  app: App,
  content: string,
  logFilePath = defaultTextLogPath
): Promise<void> {
  const logPath = normalizePath(logFilePath);
  await ensureDirectory(app, logPath);

  const existing = await app.vault.adapter.read(logPath).catch(() => "");
  const updated = `${existing}\n${content.trim()}\n\n`;

  await app.vault.adapter.write(logPath, updated);
}


export async function logToFile(app: App, data: any, logFilePath = defaultLogPath): Promise<void> {
  // Ensure it's normalized but still relative
  const logPath = normalizePath(logFilePath);

  await ensureDirectory(app, logPath);

  const json = JSON.stringify(data, null, 2);
  await app.vault.adapter.write(logPath, json);
}


export async function clearLog(app: App): Promise<void> {
  const paths = [defaultLogPath, defaultTextLogPath];

  for (const path of paths) {
    const logPath = normalizePath(path);
    await ensureDirectory(app, logPath);
    await app.vault.adapter.write(logPath, "");
  }
}
