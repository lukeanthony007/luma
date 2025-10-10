import { type App, Notice } from "obsidian";
import { generateNoteClusters } from "./utility/cluster";
import {
	generateEntities,
	generateLuna,
	getEntities,
} from "./utility/entities";
import syncNotesToDatabase from "./utility/note";

export async function runLuna(
	app: App,
	apiKey: string,
	clusterThreshold = 0.7,
) {
	new Notice("✨ Luma is analyzing your vault...");

	// 1. Sync Vault → Database
	await syncNotesToDatabase(app, apiKey);

	// 2. Generate Living Notes (symbolic entities)
	console.log(
		`🔍 Starting cluster generation with threshold: ${clusterThreshold}...`,
	);
	const clusters = await generateNoteClusters(app, apiKey, clusterThreshold); // returns Record<string, Cluster[]>
	const clusterLog = clusters.map((cluster) => ({
		title: cluster.title,
		description: cluster.description,
	}));
	console.log(`🔍 Clusters: ${JSON.stringify(clusterLog, null, 2)}`);

	// 3. Generate entities from clusters
	console.log(`🔍 Starting entity generation...`);
	await generateEntities(app, apiKey, clusters);
	console.log(`🔍 Entity generation completed`);

	new Notice("✅ Luma: Vault reflection complete.");
}
