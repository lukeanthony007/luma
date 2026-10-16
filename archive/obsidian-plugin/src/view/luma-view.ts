import { ItemView, Notice, type WorkspaceLeaf } from "obsidian";
import { getDB } from "../db";
import { runLuna } from "../luma";
import type { LumaData } from "../types/types";
import { generateNoteClusters } from "../utility/cluster";

export const LUMA_VIEW_TYPE = "luma-sidebar-view";

export class LumaView extends ItemView {
	private isRunning = false;
	private refreshInterval: number | null = null;
	private isRendering = false;
	private clusterThreshold = 0.7; // Default clustering threshold

	constructor(leaf: WorkspaceLeaf) {
		super(leaf);
	}

	getViewType(): string {
		return LUMA_VIEW_TYPE;
	}

	getDisplayText(): string {
		return "Luma Panel";
	}

	async onOpen() {
		const container = this.containerEl.children[1] as HTMLElement;
		container.empty();
		container.addClass("luma-panel");

		await this.renderPanel(container);

		// Auto-refresh every 30 seconds
		this.refreshInterval = window.setInterval(() => {
			this.refreshPanel();
		}, 30000);
	}

	async onClose() {
		if (this.refreshInterval) {
			clearInterval(this.refreshInterval);
			this.refreshInterval = null;
		}
	}

	private async renderPanel(container: HTMLElement) {
		// Prevent multiple simultaneous renders
		if (this.isRendering) return;
		this.isRendering = true;

		try {
			// Clear the container completely to prevent duplicates
			container.empty();

			// Header
			const header = container.createDiv("luma-header");
			header.createEl("h2", { text: "🌙 Luma Panel" });

			// Status indicator
			const statusDiv = header.createDiv("luma-status");
			this.updateStatus(statusDiv);

			// Main content sections
			const content = container.createDiv("luma-content");

			// Triggers section
			await this.renderTriggers(content);

			// Insights section
			await this.renderInsights(content);

			// Recent activity section
			await this.renderRecentActivity(content);
		} finally {
			this.isRendering = false;
		}
	}

	private async renderTriggers(container: HTMLElement) {
		const triggersSection = container.createDiv("luma-section");
		triggersSection.createEl("h3", { text: "🔹 Triggers" });

		const triggerButtons = triggersSection.createDiv("luma-triggers");

		// Cluster size slider
		const sliderDiv = triggerButtons.createDiv("luma-slider-group");
		sliderDiv.createEl("label", {
			text: "Cluster Size:",
			cls: "luma-slider-label",
		});

		const slider = sliderDiv.createEl("input", {
			type: "range",
			min: "0.1",
			max: "0.9",
			step: "0.05",
			value: this.clusterThreshold.toString(),
			cls: "luma-slider",
		}) as HTMLInputElement;

		const sliderValue = sliderDiv.createEl("span", {
			text: this.clusterThreshold.toString(),
			cls: "luma-slider-value",
		});

		slider.oninput = () => {
			const value = parseFloat(slider.value);
			sliderValue.textContent = value.toFixed(2);
			this.clusterThreshold = value;
			console.log(`🔧 Cluster threshold updated to: ${this.clusterThreshold}`);
		};

		// Full analysis button
		const fullAnalysisBtn = triggerButtons.createEl("button", {
			text: "Run Full Analysis",
			cls: "luma-btn luma-btn-primary",
		});
		fullAnalysisBtn.onclick = () => this.runFullAnalysis();

		// Quick sync button
		const quickSyncBtn = triggerButtons.createDiv("luma-btn-group");
		quickSyncBtn.createEl("button", {
			text: "Sync Notes",
			cls: "luma-btn luma-btn-secondary",
		}).onclick = () => this.syncNotes();

		quickSyncBtn.createEl("button", {
			text: "Generate Clusters",
			cls: "luma-btn luma-btn-secondary",
		}).onclick = () => this.generateClusters();

		quickSyncBtn.createEl("button", {
			text: "Generate Entities",
			cls: "luma-btn luma-btn-secondary",
		}).onclick = () => this.generateEntities();
	}

	private async renderInsights(container: HTMLElement) {
		const insightsSection = container.createDiv("luma-section");
		insightsSection.createEl("h3", { text: "🔸 Insights" });

		try {
			const db = getDB();
			const data = db.data as LumaData;

			// Vault statistics
			const statsDiv = insightsSection.createDiv("luma-stats");
			statsDiv.createEl("div", {
				text: `📚 Notes: ${data.notes.length}`,
				cls: "luma-stat",
			});
			statsDiv.createEl("div", {
				text: `🎭 Entities: ${data.entities.length}`,
				cls: "luma-stat",
			});

			// Recent clusters
			if (data.notes.length > 0) {
				const clustersDiv = insightsSection.createDiv("luma-clusters");
				clustersDiv.createEl("h4", { text: "Recent Clusters" });

				try {
					// Get API key from plugin settings
					const plugin = (this.app as any).plugins.plugins["sample-plugin"];
					const apiKey = plugin?.settings?.googleApiKey || "";

					const clusters = await generateNoteClusters(
						this.app,
						apiKey,
						this.clusterThreshold,
					);
					if (clusters.length > 0) {
						clusters.slice(0, 3).forEach((cluster) => {
							const clusterItem = clustersDiv.createDiv("luma-cluster-item");
							clusterItem.createEl("div", {
								text: cluster.title,
								cls: "luma-cluster-title",
							});
							clusterItem.createEl("div", {
								text: `${cluster.size} notes`,
								cls: "luma-cluster-size",
							});
						});
					} else {
						clustersDiv.createEl("p", {
							text: "No clusters found. Run analysis to generate insights.",
							cls: "luma-empty",
						});
					}
				} catch {
					clustersDiv.createEl("p", {
						text: "Unable to load clusters",
						cls: "luma-error",
					});
				}
			}

			// Recent entities
			if (data.entities.length > 0) {
				const entitiesDiv = insightsSection.createDiv("luma-entities");
				entitiesDiv.createEl("h4", { text: "Recent Entities" });

				data.entities.slice(0, 3).forEach((entity) => {
					const entityItem = entitiesDiv.createDiv("luma-entity-item");
					entityItem.createEl("div", {
						text: entity.label,
						cls: "luma-entity-label",
					});
					entityItem.createEl("div", {
						text: entity.summary.substring(0, 100) + "...",
						cls: "luma-entity-summary",
					});
				});
			}
		} catch {
			insightsSection.createEl("p", {
				text: "Unable to load insights. Run analysis first.",
				cls: "luma-error",
			});
		}
	}

	private async renderRecentActivity(container: HTMLElement) {
		const activitySection = container.createDiv("luma-section");
		activitySection.createEl("h3", { text: "📊 Recent Activity" });

		try {
			const db = getDB();
			const data = db.data as LumaData;

			if (data.notes.length > 0) {
				const recentNotes = data.notes
					.sort((a, b) => b.updated_at - a.updated_at)
					.slice(0, 5);

				const activityList = activitySection.createDiv("luma-activity-list");
				recentNotes.forEach((note) => {
					const activityItem = activityList.createDiv("luma-activity-item");
					activityItem.createEl("div", {
						text: note.path,
						cls: "luma-activity-path",
					});
					activityItem.createEl("div", {
						text: new Date(note.updated_at).toLocaleDateString(),
						cls: "luma-activity-date",
					});
				});
			} else {
				activitySection.createEl("p", {
					text: "No recent activity. Run analysis to populate data.",
					cls: "luma-empty",
				});
			}
		} catch {
			activitySection.createEl("p", {
				text: "Unable to load recent activity",
				cls: "luma-error",
			});
		}
	}

	private updateStatus(statusDiv: HTMLElement) {
		statusDiv.empty();
		if (this.isRunning) {
			statusDiv.createEl("div", {
				text: "🔄 Running...",
				cls: "luma-status-running",
			});
		} else {
			statusDiv.createEl("div", {
				text: "✅ Ready",
				cls: "luma-status-ready",
			});
		}

		// Add embedding service status
		const plugin = (this.app as any).plugins.plugins["sample-plugin"];
		const apiKey =
			plugin?.getApiKey?.() || plugin?.settings?.googleApiKey || "";

		statusDiv.createEl("div", {
			text: "🔹 Using local Ollama embeddings",
			cls: "luma-status-ready",
		});
	}

	private updateStatusOnly() {
		const container = this.containerEl.children[1] as HTMLElement;
		const statusDiv = container.querySelector(".luma-status") as HTMLElement;
		if (statusDiv) {
			this.updateStatus(statusDiv);
		}
	}

	private async runFullAnalysis() {
		if (this.isRunning) {
			new Notice("⚠️ Analysis already running...");
			return;
		}

		this.isRunning = true;
		this.updateStatusOnly();

		try {
			// Get API key from plugin settings
			const plugin = (this.app as any).plugins.plugins["sample-plugin"];
			const apiKey =
				plugin?.getApiKey?.() || plugin?.settings?.googleApiKey || "";

			console.log(
				`🔍 Starting full analysis with cluster threshold: ${this.clusterThreshold}`,
			);
			await runLuna(this.app, apiKey, this.clusterThreshold);
			new Notice("✅ Luma: Full analysis complete!");
		} catch (error) {
			new Notice("❌ Luma: Analysis failed");
			console.error("Luma analysis error:", error);
		} finally {
			this.isRunning = false;
			this.refreshPanel();
		}
	}

	private async syncNotes() {
		if (this.isRunning) return;

		this.isRunning = true;
		this.updateStatusOnly();

		try {
			// Get API key from plugin settings
			const plugin = (this.app as any).plugins.plugins["sample-plugin"];
			const apiKey =
				plugin?.getApiKey?.() || plugin?.settings?.googleApiKey || "";

			const syncNotesToDatabase = (await import("../utility/note")).default;
			await syncNotesToDatabase(this.app, apiKey);
			new Notice("✅ Notes synced!");
		} catch (error) {
			new Notice("❌ Note sync failed");
			console.error("Note sync error:", error);
		} finally {
			this.isRunning = false;
			this.refreshPanel();
		}
	}

	private async generateClusters() {
		if (this.isRunning) return;

		this.isRunning = true;
		this.updateStatusOnly();

		try {
			// Get API key from plugin settings
			const plugin = (this.app as any).plugins.plugins["sample-plugin"];
			const apiKey =
				plugin?.getApiKey?.() || plugin?.settings?.googleApiKey || "";

			await generateNoteClusters(this.app, apiKey, this.clusterThreshold);
			new Notice("✅ Clusters generated!");
		} catch (error) {
			new Notice("❌ Cluster generation failed");
			console.error("Cluster generation error:", error);
		} finally {
			this.isRunning = false;
			this.refreshPanel();
		}
	}

	private async generateEntities() {
		if (this.isRunning) return;

		this.isRunning = true;
		this.updateStatusOnly();

		try {
			// Get API key from plugin settings
			const plugin = (this.app as any).plugins.plugins["sample-plugin"];
			const apiKey =
				plugin?.getApiKey?.() || plugin?.settings?.googleApiKey || "";

			const { generateEntities } = await import("../utility/entities");
			await generateEntities(this.app, apiKey);
			new Notice("✅ Entities generated!");
		} catch (error) {
			new Notice("❌ Entity generation failed");
			console.error("Entity generation error:", error);
		} finally {
			this.isRunning = false;
			this.refreshPanel();
		}
	}

	private async refreshPanel() {
		const container = this.containerEl.children[1] as HTMLElement;
		if (container) {
			await this.renderPanel(container);
		}
	}
}
