import { pipeline, Tensor } from '@xenova/transformers';

function splitIntoSegments(text: string): string[] {
  const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
  const segments: string[] = [];
  for (const line of lines) {
    if (line.length > 300 || line.split(/[.!?]/).length > 1) {
      segments.push(...line.split(/(?<=[.!?])\s+/).map(s => s.trim()).filter(Boolean));
    } else {
      segments.push(line);
    }
  }
  return segments;
}

export async function parseNoteEntities(text: string) {
  const segments = splitIntoSegments(text);

  const embedder = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
  const embeddings: number[][] = await Promise.all(
    segments.map(async s => ((await embedder(s)) as Tensor).data as number[])
  );

  const topic: string[] = [];
  let currentEmbedding = embeddings[0];

  for (let i = 0; i < segments.length; i++) {
    topic.push(segments[i]);
    if (i > 0) {
      currentEmbedding = averageVectors(currentEmbedding, embeddings[i]);
    }
  }

  console.log(`\n--- Topic 1 ---`);
  console.log({ topic });

  return [{ topic }];
}

export function cosineSimilarity(a: number[], b: number[]): number {
  const dot = a.reduce((sum, ai, i) => sum + ai * b[i], 0);
  const magA = Math.sqrt(a.reduce((sum, ai) => sum + ai * ai, 0));
  const magB = Math.sqrt(b.reduce((sum, bi) => sum + bi * bi, 0));
  return dot / (magA * magB);
}

function averageVectors(a: number[], b: number[]): number[] {
  return a.map((val, i) => (val + b[i]) / 2);
}
