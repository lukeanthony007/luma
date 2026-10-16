import { TFile } from "obsidian";

interface LumaSettings {
  mySetting: string;
}

export type NoteData = {
  file: TFile;
  content: string;
  vector: number[];
};



export type Cluster = {
  title: string;
  description: string;
  threshold: number;
  size: number;
  notes: NoteData[];
};


export interface NoteEntry {
  id: string;
  path: string;
  content: string;
  embedding: number[];
  updated_at: number;
}

export interface EntityEntry {
  id: string;
  label: string;
  summary: string;
  connections: string[];
}

export interface LumaData {
  notes: NoteEntry[];
  entities: EntityEntry[];
}
