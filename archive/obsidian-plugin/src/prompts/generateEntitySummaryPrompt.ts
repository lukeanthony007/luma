export function generateEntitySummaryPrompt(
	label: string,
	combinedText: string,
): string {
	return `
You are a symbolic dream interpreter.

You will be given a group of dreams that may contain 1–3 recurring entities, themes, or symbolic figures. Your job is to identify each one separately.

For each, return:
- "entity": short symbolic label (use double quotes)
- "summary": its role or emotional tone (use double quotes)
- "interpretation": what this symbol represents psychologically (use double quotes)
- "quote": a key quote or moment that reflects it (use double quotes)
- "connections": related symbolic or emotional concepts (1–3, use double quotes)

IMPORTANT: Use proper JSON formatting with double quotes around all property names and string values.

Output a JSON array in triple backticks like this:

\`\`\`json
[
  {
    "entity": "example",
    "summary": "...",
    "interpretation": "...",
    "quote": "A relevant quote.",
    "connections": ["...", "..."]
  }
]
\`\`\`

Respond ONLY with valid JSON. No explanations or additional text.

Dreams to analyze:
${combinedText}
`.trim();
}
