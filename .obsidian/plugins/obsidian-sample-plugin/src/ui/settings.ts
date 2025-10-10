// settings.ts
import { type App, PluginSettingTab, Setting } from "obsidian";
import type MyPlugin from "src/main";

export interface LumaSettings {
	googleApiKey: string;
}

export const DEFAULT_SETTINGS: LumaSettings = {
	googleApiKey: "",
};

export class SettingTab extends PluginSettingTab {
	plugin: MyPlugin;
	constructor(app: App, plugin: MyPlugin) {
		super(app, plugin);
		this.plugin = plugin;
	}
	display(): void {
		const { containerEl } = this;
		containerEl.empty();

		containerEl.createEl("h2", { text: "Luma Settings" });

		new Setting(containerEl)
			.setName("Google API Key")
			.setDesc(
				"Your Google AI API key for Gemini embeddings. Get one at https://makersuite.google.com/app/apikey",
			)
			.addText((text) =>
				text
					.setPlaceholder("Enter your Google API key")
					.setValue(this.plugin.settings.googleApiKey)
					.onChange(async (value) => {
						this.plugin.settings.googleApiKey = value;
						await this.plugin.saveSettings();
					}),
			);
	}
}
