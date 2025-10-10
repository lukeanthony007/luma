import { Plugin, } from 'obsidian';
import runDailyNoteSynthesis from './daily-note-synth/run-daily-note-synth';

// Remember to rename these classes and interfaces!

interface MyPluginSettings {
	mySetting: string;
}

const DEFAULT_SETTINGS: MyPluginSettings = {
	mySetting: 'default'
}

export default class MyPlugin extends Plugin {
	settings: MyPluginSettings;

	async onload() {
		await this.loadSettings();
		this.app.workspace.onLayoutReady(() => {
			// runDailyNoteSynthesis(this.app);
		});

		// This adds a simple command that can be triggered anywhere
		this.addCommand({
			id: 'run-daily-note-synthesis',
			name: 'Run Daily Note Synthesis',
			callback: () => {
				runDailyNoteSynthesis(this.app);
			}
		});

	}

	onunload() {
	}

	async loadSettings() {
		this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
	}

	async saveSettings() {
		await this.saveData(this.settings);
	}
}
