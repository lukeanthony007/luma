import { type App, Notice } from "obsidian";
import { upsertNote } from "src/db/notes";
import { getObsidianNotes } from "src/utility/obsidian";

export default async function syncNotesToDatabase(
	app: App,
	apiKey: string,
): Promise<void> {
	const notes = await getObsidianNotes(app);
	let synced = 0;

	for (const note of notes) {
		const path = note.file.path;

		// Skip notes that are inside the Luna folder
		if (path.startsWith("Luma/")) {
			continue;
		}

		try {
			await upsertNote(note.file.path, note.content, apiKey);
			synced++;

			// Small delay for stability
			await new Promise((resolve) => setTimeout(resolve, 500));
		} catch (e) {
			console.warn(`❌ Failed to upsert note: ${note.file.path}`, e);
		}
	}

	new Notice(`✅ Synced ${synced} notes to index.`);
}
