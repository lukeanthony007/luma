import { describe, it, expect, } from 'vitest';
import {
  cosineSimilarity,
  averageVectors,
  splitLines,
  parseTopicsFromNote,
  generateTitleAndSummary
} from 'src/daily-note-synth/note-parser'; // adjust path as needed
import { Topic } from 'src/utils/types';
import * as fs from "fs";

describe('Utility Functions', () => {
  it('cosineSimilarity should return 1 for identical vectors', () => {
    const vec = [1, 2, 3];
    expect(cosineSimilarity(vec, vec)).toBeCloseTo(1);
  });

  it('averageVectors should average two vectors correctly', () => {
    const a = [2, 4];
    const b = [4, 6];
    expect(averageVectors(a, b)).toEqual([3, 5]);
  });

  it('splitLines should trim and remove empty lines', () => {
    const text = ` line one \n\n line two \n `;
    expect(splitLines(text)).toEqual(['line one', 'line two']);
  });
});

describe("splitLines", () => {
  it("should split poem note into lines", () => {
    const filePath = "/home/ln64/Documents/ln64-vault/Daily Notes/2025-05-21.md"
    const sampleNote = fs.readFileSync(filePath, "utf-8");

    const result = splitLines(sampleNote);
    expect(result.length).toBeGreaterThan(40);
    expect(result[0]).toMatch(/^So you think I’m the lonely one, eh/);
    expect(result[result.length - 1]).toMatch(/^Find some dignity/);
  });

  it("should split text block sentences into lines", () => {
    const filePath = "/home/ln64/Documents/ln64-vault/Daily Notes/2025-05-19.md"
    const sampleNote = fs.readFileSync(filePath, "utf-8");

    const result = splitLines(sampleNote);
    expect(result.length).toBeGreaterThan(10);
    expect(result[result.length - 4]).toContain("Asperger");
  });
});


describe('LangChain Title/Summary Generation', async () => {
  it('generateTitleAndSummary returns a title and summary', async () => {
    const input = ['This is a test of emotional narrative.'];
    const result = await generateTitleAndSummary(input);
    expect(result).toHaveProperty('title');
    expect(result).toHaveProperty('summary');
    expect(result.title.length).toBeGreaterThan(0);
    expect(result.summary.length).toBeGreaterThan(0);
  }, 20000);
});

describe('Topic Parsing End-to-End', () => {
  it('parses a basic poetic input into topics', async () => {
    const sample = `So you think I’m the lonely one, eh\nMaybe you’re right\nNever accepted\nAnd now I don’t need it`;
    const result = await parseTopicsFromNote(sample, 0.2);
    expect(result.length).toBeGreaterThan(0);
    result.forEach((topic: Topic) => {
      expect(topic).toHaveProperty('title');
      expect(topic).toHaveProperty('summary');
      expect((topic.lines as string[]).length).toBeGreaterThan(0);
    });
  }, 30000);
});




