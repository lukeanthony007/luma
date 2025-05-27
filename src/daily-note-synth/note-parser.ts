import { pipeline, Tensor } from '@xenova/transformers';
import { Ollama } from '@langchain/ollama';
import { PromptTemplate } from '@langchain/core/prompts';
import { performance } from 'node:perf_hooks';

export function cosineSimilarity(a: number[], b: number[]): number {
  const dot = a.reduce((sum, ai, i) => sum + ai * b[i], 0);
  const magA = Math.sqrt(a.reduce((sum, ai) => sum + ai * ai, 0));
  const magB = Math.sqrt(b.reduce((sum, bi) => sum + bi * bi, 0));
  return dot / (magA * magB);
}

export function averageVectors(a: number[], b: number[]): number[] {
  return a.map((val, i) => (val + b[i]) / 2);
}

export function splitLines(text: string): string[] {
  const lines = text.split(/\n+/)
    .map(line => line.trim())
    .filter(Boolean)
    .flatMap(line =>
      line.match(/[^.!?]+[.!?]+["']?|[^.!?]+$/g)?.map(s => s.trim()) || []
    );

  // console.log(JSON.stringify(lines, null, 2))
  return lines.filter(Boolean);
}


const llm = new Ollama({
  model: 'gemma3',
  temperature: 0,
  maxRetries: 2,
});

const titlePrompt = PromptTemplate.fromTemplate(
  "Give a single, short, poetic title (max 5 words) for the text below. No explanation, just the title.\n\n{lines}"
);

const summaryPrompt = PromptTemplate.fromTemplate(
  "Summarize the emotional theme in 1-2 sentences. Don't include bullet points or lists. No quotes.\n\n{lines}"
);

const titleChain = titlePrompt.pipe(llm);
const summaryChain = summaryPrompt.pipe(llm);

export async function generateTitle(lines: string[]): Promise<{ title: string, duration: number }> {
  const inputText = lines.join('\n');
  const start = performance.now();
  const title = await titleChain.invoke({ lines: inputText });
  const duration = performance.now() - start;
  console.log(`📝 Title done in ${duration.toFixed(2)}ms — Result: "${title.trim()}"`);
  return { title: title.trim(), duration };
}

export async function generateSummary(lines: string[]): Promise<{ summary: string, duration: number }> {
  const inputText = lines.join('\n');
  const start = performance.now();
  const summary = await summaryChain.invoke({ lines: inputText });
  const duration = performance.now() - start;
  console.log(`📘 Summary done in ${duration.toFixed(2)}ms — Snippet: "${summary.trim().slice(0, 60)}..."`);
  return { summary: summary.trim(), duration };
}

export async function generateTitleAndSummary(lines: string[]) {
  console.log(`✍️ Generating title+summary for ${lines.length} lines, ${lines.join('\n').length} chars`);
  const { title, duration: titleTime } = await generateTitle(lines);
  const { summary, duration: summaryTime } = await generateSummary(lines);
  return { title, summary, timings: { title: titleTime, summary: summaryTime } };
}

export async function embedLines(lines: string[]): Promise<number[][]> {
  console.time('🧠 split + embed');
  const embedder = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
  const embeddings = await Promise.all(
    lines.map(async line => ((await embedder(line)) as Tensor).data as number[])
  );
  console.timeEnd('🧠 split + embed');
  return embeddings;
}

export function clusterLines(lines: string[], embeddings: number[][], threshold: number) {
  console.time('🧮 Clustering');
  const topics: { lines: string[]; embedding: number[] }[] = [];
  let currentLines: string[] = [lines[0]];
  let currentEmbedding = embeddings[0];

  for (let i = 1; i < lines.length; i++) {
    const similarity = cosineSimilarity(currentEmbedding, embeddings[i]);
    if (similarity >= threshold) {
      currentLines.push(lines[i]);
      currentEmbedding = averageVectors(currentEmbedding, embeddings[i]);
    } else {
      topics.push({ lines: currentLines, embedding: currentEmbedding });
      currentLines = [lines[i]];
      currentEmbedding = embeddings[i];
    }
  }
  topics.push({ lines: currentLines, embedding: currentEmbedding });
  console.timeEnd('🧮 Clustering');
  return topics;
}

export async function parseTopicsFromNote(text: string, similarityThreshold = 0.3) {
  const lines = splitLines(text);
  const embeddings = await embedLines(lines);
  const topics = clusterLines(lines, embeddings, similarityThreshold);

  console.time('✍️ Title + Summary');
  const detailedTopics = await Promise.all(
    topics.map(async (topic, index) => {
      console.log(`\n📚 Topic ${index + 1} raw lines:\n${topic.lines.join('\n')}\n`);
      const { title, summary } = await generateTitleAndSummary(topic.lines);
      return { title, summary, lines: topic.lines };
    })
  );
  console.timeEnd('✍️ Title + Summary');

  return detailedTopics;
}
