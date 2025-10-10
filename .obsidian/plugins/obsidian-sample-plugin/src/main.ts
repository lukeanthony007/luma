import { Notice, Plugin } from "obsidian";
import { initDB, persistDB } from "./db";
import { runLuna } from "./luma";
import { DEFAULT_SETTINGS, type LumaSettings, SettingTab } from "./ui/settings";
import { clearLog } from "./utility/logger";
import { LUMA_VIEW_TYPE, LumaView } from "./view/luma-view";

export default class MyPlugin extends Plugin {
	settings: LumaSettings;

	async onload() {
		await this.loadSettings();
		this.addStyles();
		this.registerView(LUMA_VIEW_TYPE, (leaf) => new LumaView(leaf));
		this.addUI();
		this.addSettingTab(new SettingTab(this.app, this));

		await initDB(this.app);
		await clearLog(this.app);
	}

	// Helper method to get API key
	getApiKey(): string {
		return this.settings.googleApiKey || "";
	}

	async onunload() {
		await persistDB(this.app);
		this.app.workspace.detachLeavesOfType(LUMA_VIEW_TYPE);
		new Notice("💾 Luma: Database saved");
	}

	private addUI() {
		this.addRibbonIcon("sparkle", "Luma", async () => {
			const leaf = this.app.workspace.getRightLeaf(false);
			if (leaf) {
				runLuna(this.app, this.settings.googleApiKey);
				await leaf.setViewState({ type: LUMA_VIEW_TYPE, active: true });
				this.app.workspace.revealLeaf(leaf);
			}
		});
	}

	private async loadSettings() {
		this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
	}

	async saveSettings() {
		await this.saveData(this.settings);
	}

	private addStyles() {
		const styleEl = document.createElement("style");
		styleEl.textContent = `
			/* Luma Panel Styles */
			.luma-panel {
				padding: 12px;
				font-family: var(--font-family);
				color: var(--text-normal);
				min-width: 200px;
			}

			.luma-header {
				margin-bottom: 20px;
				border-bottom: 1px solid var(--background-modifier-border);
				padding-bottom: 12px;
			}

			.luma-header h2 {
				margin: 0 0 8px 0;
				font-size: 1.2em;
				font-weight: 600;
			}

			.luma-status {
				font-size: 0.9em;
				opacity: 0.8;
			}

			.luma-status-running {
				color: var(--text-accent);
			}

			.luma-status-ready {
				color: var(--text-success);
			}

			.luma-status-warning {
				color: var(--text-warning);
				font-size: 0.8em;
				margin-top: 4px;
			}

			.luma-content {
				display: flex;
				flex-direction: column;
				gap: 12px;
			}

			.luma-section {
				background: var(--background-secondary);
				border-radius: 6px;
				padding: 12px;
				border: 1px solid var(--background-modifier-border);
				margin-bottom: 12px;
			}

			.luma-section h3 {
				margin: 0 0 8px 0;
				font-size: 1em;
				font-weight: 500;
				color: var(--text-accent);
			}

			.luma-section h4 {
				margin: 12px 0 8px 0;
				font-size: 1em;
				font-weight: 500;
				color: var(--text-normal);
			}

            /* Slider */
            .luma-slider-group {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 12px;
                padding: 8px;
                background: var(--background-primary);
                border-radius: 6px;
                border: 1px solid var(--background-modifier-border);
            }

            .luma-slider-label {
                font-size: 0.85em;
                color: var(--text-normal);
                white-space: nowrap;
            }

            .luma-slider {
                flex: 1;
                height: 6px;
                background: var(--background-modifier-border);
                border-radius: 3px;
                outline: none;
                cursor: pointer;
            }

            .luma-slider::-webkit-slider-thumb {
                appearance: none;
                width: 16px;
                height: 16px;
                background: var(--interactive-accent);
                border-radius: 50%;
                cursor: pointer;
            }

            .luma-slider::-moz-range-thumb {
                width: 16px;
                height: 16px;
                background: var(--interactive-accent);
                border-radius: 50%;
                cursor: pointer;
                border: none;
            }

            .luma-slider-value {
                font-size: 0.8em;
                color: var(--text-accent);
                font-weight: 500;
                min-width: 30px;
                text-align: center;
            }

			.luma-btn {
				padding: 8px 12px;
				border: none;
				border-radius: 6px;
				font-size: 0.85em;
				font-weight: 500;
				cursor: pointer;
				transition: all 0.2s ease;
				text-align: center;
				white-space: nowrap;
				overflow: hidden;
				text-overflow: ellipsis;
			}

			.luma-btn-primary {
				background: var(--interactive-accent);
				color: var(--text-on-accent);
			}

			.luma-btn-primary:hover {
				background: var(--interactive-accent-hover);
			}

			.luma-btn-secondary {
				background: var(--background-modifier-border);
				color: var(--text-normal);
			}

			.luma-btn-secondary:hover {
				background: var(--background-modifier-border-hover);
			}

			.luma-btn-group {
				display: flex;
				flex-direction: column;
				gap: 6px;
			}

			.luma-btn-group .luma-btn {
				width: 100%;
				min-width: 0;
				font-size: 0.85em;
				padding: 6px 12px;
			}

			/* Stats */
			.luma-stats {
				display: flex;
				flex-direction: column;
				gap: 8px;
				margin-bottom: 16px;
			}

			.luma-stat {
				font-size: 0.85em;
				color: var(--text-muted);
				white-space: nowrap;
				overflow: hidden;
				text-overflow: ellipsis;
			}

			/* Clusters */
			.luma-clusters {
				margin-top: 12px;
			}

			.luma-cluster-item {
				background: var(--background-primary);
				border-radius: 6px;
				padding: 12px;
				margin-bottom: 8px;
				border: 1px solid var(--background-modifier-border);
			}

			.luma-cluster-title {
				font-weight: 500;
				margin-bottom: 4px;
				color: var(--text-normal);
			}

			.luma-cluster-size {
				font-size: 0.8em;
				color: var(--text-muted);
			}

			/* Entities */
			.luma-entities {
				margin-top: 12px;
			}

			.luma-entity-item {
				background: var(--background-primary);
				border-radius: 6px;
				padding: 12px;
				margin-bottom: 8px;
				border: 1px solid var(--background-modifier-border);
			}

			.luma-entity-label {
				font-weight: 500;
				margin-bottom: 4px;
				color: var(--text-accent);
			}

			.luma-entity-summary {
				font-size: 0.85em;
				color: var(--text-muted);
				line-height: 1.4;
			}

			/* Activity */
			.luma-activity-list {
				margin-top: 12px;
			}

			.luma-activity-item {
				display: flex;
				justify-content: space-between;
				align-items: center;
				padding: 8px 0;
				border-bottom: 1px solid var(--background-modifier-border);
			}

			.luma-activity-item:last-child {
				border-bottom: none;
			}

			.luma-activity-path {
				font-size: 0.9em;
				color: var(--text-normal);
				flex: 1;
				margin-right: 8px;
				overflow: hidden;
				text-overflow: ellipsis;
				white-space: nowrap;
			}

			.luma-activity-date {
				font-size: 0.8em;
				color: var(--text-muted);
				white-space: nowrap;
			}

			/* States */
			.luma-empty {
				color: var(--text-muted);
				font-style: italic;
				text-align: center;
				padding: 20px;
			}

			.luma-error {
				color: var(--text-error);
				font-size: 0.9em;
				text-align: center;
				padding: 20px;
			}

			/* Responsive adjustments for very narrow panels */
			@media (max-width: 250px) {
				.luma-panel {
					padding: 8px;
				}
				
				.luma-section {
					padding: 8px;
				}
				
				.luma-btn {
					font-size: 0.8em;
					padding: 6px 8px;
				}
			}
		`;
		document.head.appendChild(styleEl);
	}
}
