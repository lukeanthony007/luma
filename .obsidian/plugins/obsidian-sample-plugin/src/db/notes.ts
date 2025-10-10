import { getEmbedding } from "src/utility/embedding";
import { getDB } from "./index";

export async function upsertNote(
	id: string,
	content: string,
	apiKey: string,
): Promise<void> {
	const vector = await getEmbedding(content, apiKey);
	const db = getDB();
	const now = Date.now();

	const existing = db.data!.notes.find((n) => n.id === id);
	if (existing) {
		Object.assign(existing, {
			content,
			embedding: vector,
			updated_at: now,
		});
	} else {
		db.data!.notes.push({
			id,
			path: id,
			content,
			embedding: vector,
			updated_at: now,
		});
	}

	await db.write();
}
