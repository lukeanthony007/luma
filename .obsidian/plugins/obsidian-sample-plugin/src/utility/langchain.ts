// src/ai/callOllama.ts
import { HumanMessage, SystemMessage } from "@langchain/core/messages";
import { ChatOllama } from "@langchain/ollama";
import type { App } from "obsidian";
import { logToFile } from "./logger";

interface CallOllamaOptions {
	systemPrompt?: string;
	model?: string;
	temperature?: number;
	maxRetries?: number;
	log?: boolean;
	apiKey?: string; // Keep for compatibility but won't be used
}

/**
 * General-purpose call to Ollama chat model with role-based messages.
 */
export default async function callOllama(
	app: App,
	inputText: string,
	options: CallOllamaOptions = {},
) {
	const {
		systemPrompt = "You are a helpful assistant.",
		model = "llama3.2:3b",
		temperature = 0.7,
		maxRetries = 2,
		log = true,
	} = options;

	const chat = new ChatOllama({
		model,
		temperature,
		maxRetries,
		baseUrl: "http://127.0.0.1:11434",
	});

	const messages = [
		new SystemMessage(systemPrompt),
		new HumanMessage(inputText),
	];

	try {
		console.log(`🔍 Calling Ollama with model: ${model}`);

		// Add timeout wrapper
		const timeoutPromise = new Promise((_, reject) => {
			setTimeout(
				() => reject(new Error("Ollama call timed out after 30 seconds")),
				30000,
			);
		});

		const chatPromise = chat.invoke(messages);
		const response = await Promise.race([chatPromise, timeoutPromise]);

		console.log(`✅ Ollama response received for model: ${model}`);

		if (log) {
			await logToFile(app, {
				systemPrompt,
				input: inputText,
				output: response.content,
				model,
				timestamp: new Date().toISOString(),
			});
		}

		return response.content;
	} catch (error) {
		console.error(`❌ Ollama call failed:`, error.message);

		// Handle timeout errors
		if (error.message.includes("timed out")) {
			console.warn(
				"⏳ Ollama call timed out, this might indicate the model is overloaded",
			);
			throw new Error(
				`Ollama model ${model} timed out. Try again later or use a different model.`,
			);
		}

		// Handle Ollama connection errors
		if (
			error.message.includes("ECONNREFUSED") ||
			error.message.includes("fetch")
		) {
			console.warn("⏳ Ollama service unavailable, waiting before retry...");
			await new Promise((resolve) => setTimeout(resolve, 2000)); // Wait 2 seconds

			// Single retry
			try {
				console.log(`🔍 Retrying Ollama call with model: ${model}`);
				const response = await chat.invoke(messages);
				console.log(`✅ Ollama retry successful for model: ${model}`);
				return response.content;
			} catch (retryError) {
				console.error("❌ Ollama retry failed:", retryError.message);
				throw retryError;
			}
		}
		throw error;
	}
}
