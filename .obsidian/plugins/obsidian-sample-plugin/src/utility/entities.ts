import { type App, Notice, normalizePath, TFile, TFolder } from "obsidian";
import { generateEntitySummaryPrompt } from "../prompts/generateEntitySummaryPrompt";
import { renderEntityNote } from "../templates/generateEntityNote";
import type { Cluster } from "../types/types";
import callOllama from "../utility/langchain";
import { generateNoteClusters } from "./cluster";

export async function generateEntityNotes(
	app: App,
	label: string,
	clusters: Cluster[],
	apiKey: string,
) {
	console.log(`🔍 Generating entity notes for label group: ${label}`);

	const allNotes = clusters.flatMap((c) => c.notes);
	const allText = allNotes.map((n) => n.content).join("\n---\n");

	const summaryPrompt = generateEntitySummaryPrompt(label, allText);
	const response = await callOllama(app, summaryPrompt, {
		model: "llama3.2:3b",
		temperature: 0.7,
		systemPrompt: "You are a symbolic dream summarizer.",
		apiKey,
	});

	console.log("🔍 Raw AI response:", response.toString());

	let parsed;
	try {
		const json = extractJson(response.toString());
		console.log("🔍 Extracted JSON:", json);
		parsed = JSON.parse(json);
	} catch (error) {
		console.error("❌ JSON parsing failed:", error);
		console.error("❌ Raw response:", response.toString());

		// Fallback: create a simple entity from the cluster title
		parsed = [
			{
				entity: label,
				summary: `A symbolic entity representing themes found in ${label.toLowerCase()}.`,
				interpretation:
					"This entity emerged from the clustering of related dream content.",
				quote: "Generated from cluster analysis",
				connections: [],
			},
		];
	}

	if (!Array.isArray(parsed)) {
		throw new Error("Expected JSON array of symbolic entities.");
	}

	const results = [];

	for (const entity of parsed) {
		const finalLabel = entity.entity || "Unlabeled";
		const content = renderEntityNote({
			label: finalLabel,
			summary: entity.summary,
			interpretation: entity.interpretation,
			connections: entity.connections,
			notes: allNotes,
		});

		const safeLabel = finalLabel
			.toLowerCase()
			.replace(/[^a-z0-9_-]/gi, "_")
			.replace(/_+/g, "_")
			.replace(/^_+|_+$/g, "");

		results.push({
			label: finalLabel,
			fileName: `${safeLabel}.md`,
			content,
		});
	}

	return results;
}

export async function writeEntityToVault(
	app: App,
	label: string,
	fileName: string,
	content: string,
) {
	const folder = normalizePath("Luma/Entities");
	await app.vault.createFolder(folder).catch(() => {});

	const filePath = normalizePath(`${folder}/${fileName}`);
	const existing = app.vault.getAbstractFileByPath(filePath);

	if (existing instanceof TFile) {
		await app.vault.modify(existing, content);
		console.log(`✅ Modified: ${filePath}`);
	} else {
		await app.vault.create(filePath, content);
		console.log(`✅ Created: ${filePath}`);
	}

	new Notice(`Luma: Updated entity → ${label}`);
}

function extractJson(raw: string): string {
	// Try multiple patterns to extract JSON
	const patterns = [
		/```json\s*([\s\S]+?)```/,
		/```\s*([\s\S]+?)```/,
		/\[[\s\S]*\]/,
		/\{[\s\S]*\}/,
	];

	for (const pattern of patterns) {
		const match = raw.match(pattern);
		if (match) {
			let jsonStr = match[1] || match[0];
			// Clean up the JSON string
			jsonStr = jsonStr
				.replace(/^\s*```json\s*/, "")
				.replace(/\s*```\s*$/, "")
				.trim();

			// Fix common JSON issues: remove extra quotes around values
			jsonStr = jsonStr
				.replace(/"([^"]+)":\s*"([^"]+)"/g, '"$1": "$2"') // Fix property names
				.replace(/"([^"]+)":\s*"([^"]+)"/g, '"$1": "$2"') // Fix string values
				.replace(
					/\[\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\]/g,
					'["$1", "$2", "$3"]',
				); // Fix arrays

			// Try to parse it to validate
			try {
				JSON.parse(jsonStr);
				return jsonStr;
			} catch (e) {
				console.warn("Invalid JSON found, trying next pattern:", e.message);
			}
		}
	}

	throw new Error("No valid JSON found in response.");
}

export async function generateEntities(
	app: App,
	apiKey: string,
	clusters: Cluster[],
): Promise<void> {
	console.log(`🔍 Starting entity generation for ${clusters.length} clusters`);

	const clusterLog = clusters.map((cluster) => ({
		title: cluster.title,
		description: cluster.description,
	}));

	console.log(
		`🔍 Clusters for entity generation: ${JSON.stringify(clusterLog, null, 2)}`,
	);

	// Generate entities for each cluster
	for (let i = 0; i < clusters.length; i++) {
		const cluster = clusters[i];
		console.log(
			`🔍 Processing cluster ${i + 1}/${clusters.length}: ${cluster.title}`,
		);

		try {
			const result = await generateEntityNotes(
				app,
				cluster.title,
				[cluster],
				apiKey,
			);
			for (const entity of result) {
				await writeEntityToVault(
					app,
					entity.label,
					entity.fileName,
					entity.content,
				);
			}
			console.log(
				`💾 Written entity notes to vault for cluster: ${cluster.title}`,
			);

			// Small delay between clusters for stability
			if (i < clusters.length - 1) {
				await new Promise((resolve) => setTimeout(resolve, 1000));
			}
		} catch (error) {
			console.error(
				`❌ Failed to generate entities for cluster ${cluster.title}:`,
				error,
			);
			// Fallback to simple entity generation
			await generateFallbackEntity(app, cluster);
		}
	}

	console.log(`✅ Entity generation completed`);
}

export async function getEntities(
	app: App,
): Promise<{ label: string; content: string }[]> {
	const folderPath = "Luma/Entities";
	const folder = app.vault.getAbstractFileByPath(folderPath);

	if (!folder || !(folder instanceof TFolder)) {
		throw new Error(`Folder not found or is not a valid folder: ${folderPath}`);
	}

	const result: { label: string; content: string }[] = [];

	for (const file of folder.children) {
		if (file instanceof TFile && file.extension === "md") {
			const content = await app.vault.read(file);
			result.push({ label: file.basename, content });
		}
	}

	return result;
}

export async function generateFallbackEntity(
	app: App,
	cluster: Cluster,
): Promise<void> {
	console.log(`🔧 Generating fallback entity for: ${cluster.title}`);

	// Create a simple entity based on cluster analysis
	const entityName = cluster.title;
	const notes = cluster.notes;
	const sourceLinks = notes.map((n) => `- [[${n.file.path}]]`).join("\n");

	// Generate a meaningful summary based on cluster description and notes
	const summary =
		cluster.description ||
		`A symbolic entity representing themes found in ${entityName.toLowerCase()}.`;

	const content = `# ${entityName}

**Linked Notes:**  
${sourceLinks}

## Summary

${summary}
`;

	const safeLabel = entityName
		.toLowerCase()
		.replace(/[^a-z0-9_-]/gi, "_")
		.replace(/_+/g, "_")
		.replace(/^_+|_+$/g, "");

	await writeEntityToVault(app, entityName, `${safeLabel}.md`, content);
	console.log(`✅ Generated fallback entity: ${entityName}`);
}

export async function generateLuna(app: App): Promise<void> {
	const entities = await getEntities(app);
	const summary = entities
		.map((e) => `- **${e.label}**\n${e.content.slice(0, 200)}...`)
		.join("\n\n");

	const finalNote = `# Luma Reflection\n\n${summary}`;
	const filePath = "Luma/Luma Reflection.md";
	const existing = app.vault.getAbstractFileByPath(filePath);

	if (existing instanceof TFile) {
		await app.vault.modify(existing, finalNote);
	} else {
		await app.vault.create(filePath, finalNote);
	}
}
