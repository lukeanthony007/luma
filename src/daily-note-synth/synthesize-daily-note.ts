import { Notice } from "obsidian";
import callOllama from "src/lib/langchain";
import { SYSTEM_PROMPT_ORGANIZER } from "./format-note";

export async function synthesizeDailyNote(content: string): Promise<string> {
  new Notice("Synthesizing daily note...");

  // 1. I need to parse the text inside of the note and derive entities with vector embeddings
  // 2. for example, pulls: "hypercore protocol", "secure scuttlebutt", "discord", "workplace"
  // 3. once I have the entities, I can use them to generate relevant callouts

  const systemPrompt = SYSTEM_PROMPT_ORGANIZER;

  const response = await callOllama(content, {
    prompt: systemPrompt,
  });

  if (!response.text) {
    console.error("Error in synthesis: No text returned");
    new Notice("Synthesis failed!");
    return content; // fallback to raw
  }

  return response.text;
}
