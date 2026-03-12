/**
 * Core CodeResearcher class (TypeScript).
 */

import { ResearcherConfig, ResearcherConfigOptions } from "./config";
import { searchGitHub } from "./sources/github";
import { searchGrepApp } from "./sources/grepApp";

export interface SearchResult {
  source: string;   // "github" | "grep.app" | "stackoverflow"
  repo: string;
  file: string;
  url: string;
  code: string;
}

export interface ResearchResult {
  task: string;
  results: SearchResult[];
  contextBlock: string;
  found: number;
  mode: string;
}

export class CodeResearcher {
  private config: ResearcherConfig;

  /**
   * Create a CodeResearcher instance.
   *
   * @example Free mode (no token):
   *   const r = new CodeResearcher();
   *
   * @example Paid mode (GitHub token):
   *   const r = new CodeResearcher({ githubToken: "ghp_..." });
   *
   * @example From .env:
   *   // Set GITHUB_TOKEN=ghp_... in .env
   *   const r = new CodeResearcher();  // auto-detects
   */
  constructor(opts: ResearcherConfigOptions = {}) {
    this.config = new ResearcherConfig(opts);
  }

  /**
   * Search for code examples relevant to the task.
   *
   * @param task     - Description of the programming task (English works best)
   * @param language - Target language: "python", "typescript", "javascript", "rust", ...
   */
  async search(task: string, language = "javascript"): Promise<ResearchResult> {
    const allResults: SearchResult[] = [];
    const modeLabel = this.config.isPaid ? "paid" : "free";
    const queryPreview = task.length > 60 ? task.slice(0, 60) + "..." : task;

    console.log(`  [Researcher] Mode: ${modeLabel} | Query: '${queryPreview}'`);

    // Source 1: GitHub
    if (this.config.useGithub) {
      const authLabel = this.config.isPaid
        ? "authenticated"
        : "unauthenticated, 60 req/h limit";
      console.log(`  [Researcher] Searching GitHub (${authLabel})...`);
      const raw = await searchGitHub(task, language, this.config);
      allResults.push(...raw);
      console.log(`    → ${raw.length} files found`);
    }

    // Source 2: grep.app (always free)
    if (this.config.useGrepApp && allResults.length < this.config.maxResults) {
      console.log("  [Researcher] Searching grep.app (no token needed)...");
      const raw = await searchGrepApp(task, language, this.config);
      allResults.push(...raw);
      console.log(`    → ${raw.length} files found`);
    }

    // Deduplicate by URL
    const seenUrls = new Set<string>();
    const unique = allResults.filter((r) => {
      if (seenUrls.has(r.url)) return false;
      seenUrls.add(r.url);
      return true;
    });

    const final = unique.slice(0, this.config.maxResults);
    console.log(`  [Researcher] Total: ${final.length} unique results`);

    const contextBlock = this.buildContextBlock(final);
    return { task, results: final, contextBlock, found: final.length, mode: modeLabel };
  }

  private buildContextBlock(results: SearchResult[]): string {
    if (!results.length) return "";

    const lines = [
      "## Code Examples from GitHub (use as reference, adapt don't copy blindly)\n",
    ];

    results.forEach((r, i) => {
      lines.push(`### [${i + 1}] [${r.source.toUpperCase()}] ${r.repo}`);
      if (r.file) lines.push(`File: \`${r.file}\``);
      lines.push(`URL: ${r.url}`);
      lines.push("```");
      lines.push(r.code.trimEnd());
      lines.push("```\n");
    });

    return lines.join("\n");
  }
}
