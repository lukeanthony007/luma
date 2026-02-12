import type { App } from "obsidian";
import type { NoteData } from "src/types/types";
import callOllama from "src/utility/langchain";
import { extractJson } from "src/utility/utility";

export async function generateClusterMetadata(
	app: App,
	cluster: NoteData[],
	apiKey: string,
): Promise<{ title: string; description: string }> {
	const text = cluster
		.map((n) => n.content)
		.join("\n---\n")
		.slice(0, 8000); // Keep token size safe
	const prompt = `
You are a poetic AI librarian. Summarize the theme of the following collection of notes.

Return a JSON object with:
- "title": a short, symbolic name (1–3 words)
- "description": a 1–2 sentence abstract that describes the theme or insight of this cluster.

Respond only in this JSON format:
{
  "title": "...",
  "description": "..."
}

Here are the notes:
\`\`\`
${text}
\`\`\`
`;

	try {
		const response = await callOllama(app, prompt, {
			model: "llama3.2:3b",
			temperature: 0.6,
			systemPrompt: "You are a symbolic clustering summarizer",
			apiKey,
		});

		const json = extractJson(response.toString());
		return JSON.parse(json);
	} catch (error) {
		console.warn(
			"❌ Failed to generate cluster metadata, using fallback:",
			error.message,
		);

		// Fallback: create simple metadata from cluster content
		const firstNote = cluster[0];
		const title =
			firstNote?.content?.split("\n")[0]?.slice(0, 20) || "Untitled Cluster";
		const description = `A collection of ${cluster.length} related notes.`;

		return {
			title: title.replace(/[^a-zA-Z0-9\s]/g, "").trim() || "Untitled Cluster",
			description,
		};
	}
}
