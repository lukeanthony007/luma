import { HumanMessage, SystemMessage } from "@langchain/core/messages";
import { ChatOllama } from "@langchain/ollama";

const SYSTEM_PROMPT_TEMPLATE =
  "You are a call-and-response assistant. Keep replies clear, concise. Your response must be within {{TOKEN_LIMIT}} tokens.";

const DEFAULT_MODEL = "gemma3";
const DEFAULT_TEMPERATURE = 0.7;
const DEFAULT_MAX_RETRIES = 5;

interface CallOllamaOptions {
  prompt?: string;
  model?: string;
  temperature?: number;
  maxRetries?: number;
}


export default async function callOllama(
  inputText: string,
  options: CallOllamaOptions = {}
) {
  const {
    prompt,
    model = DEFAULT_MODEL,
    temperature = DEFAULT_TEMPERATURE,
    maxRetries = DEFAULT_MAX_RETRIES,
  } = options;

  // Smart token estimate if user didn't pass numPredict
  const tokenEstimate = estimateSmartTokenLimit(inputText);

  const chat = new ChatOllama({
    model,
    temperature,
    maxRetries,
    numPredict: tokenEstimate,
  });

  const systemPrompt = SYSTEM_PROMPT_TEMPLATE.replace(
    "{{TOKEN_LIMIT}}",
    tokenEstimate.toString()
  );

  const fullSystemPrompt = [systemPrompt, prompt].filter(Boolean).join('\n\n');

  const messages = [
    new SystemMessage(fullSystemPrompt),
    new HumanMessage(inputText),
  ];

  return chat.invoke(messages);
}

export function estimateSmartTokenLimit(inputText: string): number {
  const wordCount = inputText.trim().split(/\s+/).length;

  let estimatedTokens = 0;

  if (wordCount < 100) {
    estimatedTokens = 128; // Tiny note, set min tokens
  } else if (wordCount < 500) {
    estimatedTokens = Math.ceil(wordCount * 1.5) + 200;
  } else if (wordCount < 1500) {
    estimatedTokens = Math.ceil(wordCount * 1.3) + 300;
  } else {
    estimatedTokens = 2048; // Cap at max
  }

  // Safety net min/max
  const MIN_TOKENS = 128;
  const MAX_TOKENS = 2048;

  return Math.min(Math.max(estimatedTokens, MIN_TOKENS), MAX_TOKENS);
}
