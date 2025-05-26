import { parseNoteEntities } from "./note-parser";

async function run() {
  console.log("Running daily note synthesis...");

  const notePath = '/home/ln64/Documents/ln64-vault/Daily Notes/2025-05-19.md'; // Path to the note you want to parse
  const file = Bun.file(notePath); // Content of the note you want to parse

  const content = await file.text(); // Read the content of the note

  parseNoteEntities(content);
}

run();