export function extractJson(raw: string): string {
	// Try multiple patterns to extract JSON
	const patterns = [
		/```json\s*([\s\S]+?)```/,
		/```\s*([\s\S]+?)```/,
		/\{[\s\S]*\}/,
		/\[[\s\S]*\]/,
	];

	for (const pattern of patterns) {
		const match = raw.match(pattern);
		if (match) {
			const jsonStr = match[1] || match[0];
			// Clean up the JSON string
			const cleaned = jsonStr
				.replace(/^\s*```json\s*/, "")
				.replace(/\s*```\s*$/, "")
				.trim();

			// Try to parse it to validate
			try {
				JSON.parse(cleaned);
				return cleaned;
			} catch (e) {
				console.warn("Invalid JSON found, trying next pattern:", e.message);
			}
		}
	}

	throw new Error("No valid JSON found in response.");
}
