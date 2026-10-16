import { type Adapter, Low } from "lowdb";
import { type App, normalizePath, TFile } from "obsidian";
import type { LumaData } from "src/types/types";

class ObsidianAdapter<T> implements Adapter<T> {
	private app: App;
	private filePath: string;

	constructor(app: App, filePath: string) {
		this.app = app;
		this.filePath = normalizePath(filePath);
	}

	async read(): Promise<T | null> {
		const file = this.app.vault.getAbstractFileByPath(this.filePath);
		if (file && file instanceof TFile) {
			const content = await this.app.vault.read(file);
			try {
				return JSON.parse(content) as T;
			} catch (err) {
				console.warn(`⚠️ Failed to parse JSON from ${this.filePath}:`, err);
				return null;
			}
		}
		return null;
	}

	async write(data: T): Promise<void> {
		const content = JSON.stringify(data, null, 2);

		try {
			// Check if file exists
			const file = this.app.vault.getAbstractFileByPath(this.filePath);

			if (file && file instanceof TFile) {
				// File exists, modify it
				await this.app.vault.modify(file, content);
				console.log(`✏️ Updated existing DB file: ${this.filePath}`);
			} else {
				// File doesn't exist, create it
				// First ensure the directory exists
				const dirPath = this.filePath.split("/").slice(0, -1).join("/");
				if (dirPath) {
					try {
						const existingDir = this.app.vault.getAbstractFileByPath(dirPath);
						if (!existingDir) {
							await this.app.vault.createFolder(dirPath);
						}
					} catch (dirError) {
						// Directory might already exist, continue with file creation
						console.log(`📁 Directory check: ${dirError.message}`);
					}
				}

				await this.app.vault.create(this.filePath, content);
				console.log(`📄 Created new DB file: ${this.filePath}`);
			}
		} catch (error) {
			// If create fails because file exists, try to modify instead
			if (error.message && error.message.includes("File already exists")) {
				try {
					const file = this.app.vault.getAbstractFileByPath(this.filePath);
					if (file && file instanceof TFile) {
						await this.app.vault.modify(file, content);
						console.log(`✏️ Updated existing DB file (retry): ${this.filePath}`);
					}
				} catch (retryError) {
					console.error(
						`❌ Failed to write DB file after retry: ${this.filePath}`,
						retryError,
					);
				}
			} else {
				console.error(`❌ Failed to write DB file: ${this.filePath}`, error);
			}
		}
	}
}

let db: Low<LumaData>;

export async function initDB(app: App): Promise<void> {
	const adapter = new ObsidianAdapter<LumaData>(app, "Luma/luma_index.json");
	db = new Low(adapter, { notes: [], entities: [] });

	try {
		await db.read();
		db.data ||= { notes: [], entities: [] };
		await db.write();
		console.log("✅ Luma DB initialized.");
	} catch (err) {
		console.error("❌ Failed to initialize Luma DB:", err);
	}
}

export async function persistDB(app: App): Promise<void> {
	if (!db || !db.data) return;

	const filePath = normalizePath("Luma/luma_index.json");
	const data = JSON.stringify(db.data, null, 2);

	try {
		const file = app.vault.getAbstractFileByPath(filePath);

		if (file && file instanceof TFile) {
			await app.vault.modify(file, data);
			console.log("💾 DB persisted to:", filePath);
		} else {
			// Ensure directory exists before creating file
			const dirPath = filePath.split("/").slice(0, -1).join("/");
			if (dirPath) {
				try {
					const existingDir = app.vault.getAbstractFileByPath(dirPath);
					if (!existingDir) {
						await app.vault.createFolder(dirPath);
					}
				} catch (dirError) {
					// Directory might already exist, continue with file creation
					console.log(`📁 Directory check: ${dirError.message}`);
				}
			}

			await app.vault.create(filePath, data);
			console.log("💾 DB created and persisted to:", filePath);
		}
	} catch (error) {
		// If create fails because file exists, try to modify instead
		if (error.message && error.message.includes("File already exists")) {
			try {
				const file = app.vault.getAbstractFileByPath(filePath);
				if (file && file instanceof TFile) {
					await app.vault.modify(file, data);
					console.log("💾 DB persisted to (retry):", filePath);
				}
			} catch (retryError) {
				console.error("❌ Error persisting DB after retry:", retryError);
			}
		} else {
			console.error("❌ Error persisting DB:", error);
		}
	}
}

export function getDB(): Low<LumaData> {
	if (!db) throw new Error("Database not initialized. Call initDB first.");
	return db;
}
