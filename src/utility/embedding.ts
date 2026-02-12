import { OllamaEmbeddings } from "@langchain/ollama";
import { Cluster, NoteData } from "src/types/types";

export async function getEmbedding(
	text: string,
	apiKey: string, // Keep parameter for compatibility but won't be used
	model = "nomic-embed-text",
): Promise<number[]> {
	try {
		// Use Ollama embeddings with the correct model
		const embeddings = new OllamaEmbeddings({
			model: model,
			baseUrl: "http://127.0.0.1:11434",
		});

		const result = await embeddings.embedQuery(text);
		return result;
	} catch (error) {
		console.warn(`❌ Ollama embedding failed, using fallback:`, error.message);
		return generateFallbackEmbedding(text);
	}
}

function generateFallbackEmbedding(text: string): number[] {
	// Simple hash-based embedding fallback
	const hash = simpleHash(text);
	const embedding = new Array(384); // Standard embedding size

	for (let i = 0; i < embedding.length; i++) {
		embedding[i] = Math.sin(hash + i) * 0.1; // Small values around 0
	}

	return embedding;
}

function simpleHash(str: string): number {
	let hash = 0;
	for (let i = 0; i < str.length; i++) {
		const char = str.charCodeAt(i);
		hash = (hash << 5) - hash + char;
		hash = hash & hash; // Convert to 32-bit integer
	}
	return Math.abs(hash);
}
