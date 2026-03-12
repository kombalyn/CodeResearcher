#!/usr/bin/env node
/**
 * code-researcher CLI (TypeScript/Node.js)
 *
 * Usage:
 *   npx ts-node cli.ts "fetch JSON API typescript"
 *   npx ts-node cli.ts "async http reqwest" --language rust
 *   npx ts-node cli.ts "google search scraping" --language python --paid
 */

import { CodeResearcher } from "./src/index";
import { Mode } from "./src/config";

async function main() {
  const args = process.argv.slice(2);
  if (!args.length || args[0] === "--help") {
    console.log(`
code-researcher – search GitHub for real code examples

Usage:
  npx ts-node cli.ts <query> [options]

Options:
  --language <lang>   python | javascript | typescript | rust | go  [default: typescript]
  --paid              Force paid mode (requires GITHUB_TOKEN in .env)
  --free              Force free mode
  --max <n>           Max results
  --no-grep-app       Skip grep.app
  --stackoverflow     Include StackOverflow results

Examples:
  npx ts-node cli.ts "fetch JSON api typescript"
  npx ts-node cli.ts "websocket server nodejs"
  npx ts-node cli.ts "async http reqwest" --language rust
  npx ts-node cli.ts "google search scraping" --language python --paid
    `);
    process.exit(0);
  }

  const query = args[0];
  let language = "typescript";
  let mode: Mode | undefined;
  let maxResults: number | undefined;
  let useGrepApp = true;
  let useStackOverflow = false;

  for (let i = 1; i < args.length; i++) {
    if (args[i] === "--language" && args[i + 1]) language = args[++i];
    else if (args[i] === "--paid") mode = Mode.PAID;
    else if (args[i] === "--free") mode = Mode.FREE;
    else if (args[i] === "--max" && args[i + 1]) maxResults = parseInt(args[++i], 10);
    else if (args[i] === "--no-grep-app") useGrepApp = false;
    else if (args[i] === "--stackoverflow") useStackOverflow = true;
  }

  const researcher = new CodeResearcher({
    mode,
    maxResults,
    useGrepApp,
    useStackOverflow,
  });

  const result = await researcher.search(query, language);

  console.log();
  console.log("=".repeat(65));
  console.log(`Results: ${result.found} | Mode: ${result.mode} | Language: ${language}`);
  console.log("=".repeat(65));

  if (!result.found) {
    console.log("\nNo results found. Try:");
    console.log("  - English search queries");
    console.log("  - Shorter, more specific terms");
    console.log("  - Set GITHUB_TOKEN in .env for better results");
    return;
  }

  console.log();
  console.log(result.contextBlock);
}

main().catch(console.error);
