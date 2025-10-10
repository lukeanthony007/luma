import { type App, Notice, type TFile } from "obsidian";
import { getDB } from "src/db";
import { generateClusterMetadata } from "src/templates/generateClusterMetadata";
import type { Cluster, NoteData } from "src/types/types";

// Global lock to prevent multiple simultaneous cluster generations
let isGeneratingClusters = false;

export async function generateNoteClusters(
	app: App,
	apiKey: string,
	threshold = 0.25,
): Promise<Cluster[]> {
	// Prevent multiple simultaneous cluster generations
	if (isGeneratingClusters) {
		console.log("🔒 Cluster generation already in progress, skipping...");
		return [];
	}

	isGeneratingClusters = true;

	try {
		console.log("🔍 Starting cluster generation...");
		new Notice("🔍 Clustering notes from Luma database...");

		const db = getDB();
		const rawNotes = db.data?.notes || [];
		console.log(`🔍 Found ${rawNotes.length} notes in database`);

		const notes: NoteData[] = rawNotes.map((row) => ({
			file: { path: row.path } as TFile,
			content: row.content,
			vector: row.embedding,
		}));

		console.log(`🔍 Processing ${notes.length} notes for clustering`);
		const clusters: Cluster[] = [];

		for (const note of notes) {
			let matched = false;
			for (const cluster of clusters) {
				const sims = cluster.notes.map((n) => cosineSim(n.vector, note.vector));
				const avgSim = sims.reduce((a, b) => a + b, 0) / sims.length;
				if (avgSim >= threshold) {
					cluster.notes.push(note);
					cluster.size = cluster.notes.length;
					matched = true;
					break;
				}
			}

			if (!matched) {
				clusters.push({
					title: "Untitled",
					description: "Pending metadata generation...",
					notes: [note],
					threshold,
					size: 1,
				});
			}
		}

		// Add titles + descriptions to each cluster
		console.log(
			`🔍 Generated ${clusters.length} clusters, now adding metadata...`,
		);
		for (let i = 0; i < clusters.length; i++) {
			const cluster = clusters[i];
			console.log(
				`🔍 Generating metadata for cluster ${i + 1}/${clusters.length} with ${cluster.notes.length} notes`,
			);
			try {
				const meta = await generateClusterMetadata(app, cluster.notes, apiKey);
				cluster.title = meta.title;
				cluster.description = meta.description;
				console.log(`✅ Generated metadata for cluster: "${meta.title}"`);
			} catch (error) {
				console.error(
					`❌ Failed to generate metadata for cluster ${i + 1}:`,
					error,
				);
				// Use fallback metadata
				cluster.title = `Cluster ${i + 1}`;
				cluster.description = `A cluster of ${cluster.notes.length} related notes.`;
			}
		}

		new Notice(
			`✅ Clustered ${notes.length} notes into ${clusters.length} clusters.`,
		);
		return clusters;
	} finally {
		isGeneratingClusters = false;
	}
}

function cosineSim(vecA: number[], vecB: number[]): number {
	const dot = vecA.reduce((acc, v, i) => acc + v * vecB[i], 0);
	const normA = Math.sqrt(vecA.reduce((acc, v) => acc + v * v, 0));
	const normB = Math.sqrt(vecB.reduce((acc, v) => acc + v * v, 0));
	return dot / (normA * normB);
}
