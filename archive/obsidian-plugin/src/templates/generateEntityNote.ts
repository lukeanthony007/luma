import type { NoteData } from "src/types/types";

export function renderEntityNote(params: {
	label: string;
	summary: string;
	interpretation: string;
	connections: string[];
	notes: NoteData[];
	entity?: string;
}) {
	const { summary, notes } = params;

	const sourceLinks = notes.map((n) => `- [[${n.file.path}]]`).join("\n");

	return `# ${params.label}

**Linked Notes:**  
${sourceLinks}

## Summary

${summary || "_No summary provided._"}
`.trim();
}
