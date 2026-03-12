/**
 * Configuration for code-researcher (TypeScript).
 *
 * Environment variables (.env):
 *   GITHUB_TOKEN            GitHub PAT – enables paid mode (5,000 req/h)
 *   RESEARCHER_MODE         "free" | "paid" (auto-detected if not set)
 *   RESEARCHER_MAX_RESULTS  Max files per search (default: 3 free / 10 paid)
 *   RESEARCHER_MAX_CHARS    Max chars per snippet (default: 1500)
 *   RESEARCHER_TIMEOUT_MS   Request timeout in ms (default: 10000)
 *   RESEARCHER_USE_GITHUB   "true"/"false" (default: true)
 *   RESEARCHER_USE_GREP_APP "true"/"false" (default: true)
 *   RESEARCHER_USE_SO       "true"/"false" (default: false)
 */

import * as dotenv from "dotenv";
dotenv.config();

export enum Mode {
  FREE = "free",
  PAID = "paid",
}

export interface ResearcherConfigOptions {
  githubToken?: string;
  mode?: Mode;
  maxResults?: number;
  maxCharsPerFile?: number;
  timeoutMs?: number;
  useGithub?: boolean;
  useGrepApp?: boolean;
  useStackOverflow?: boolean;
}

export class ResearcherConfig {
  githubToken: string;
  mode: Mode;
  maxResults: number;
  maxCharsPerFile: number;
  timeoutMs: number;
  useGithub: boolean;
  useGrepApp: boolean;
  useStackOverflow: boolean;

  constructor(opts: ResearcherConfigOptions = {}) {
    this.githubToken = opts.githubToken ?? process.env.GITHUB_TOKEN ?? "";

    // Auto-detect mode
    const envMode = process.env.RESEARCHER_MODE?.toLowerCase();
    if (opts.mode) {
      this.mode = opts.mode;
    } else if (envMode === "paid") {
      this.mode = Mode.PAID;
    } else if (envMode === "free") {
      this.mode = Mode.FREE;
    } else {
      this.mode = this.githubToken ? Mode.PAID : Mode.FREE;
    }

    const envMax = parseInt(process.env.RESEARCHER_MAX_RESULTS ?? "", 10);
    this.maxResults =
      opts.maxResults ??
      (isNaN(envMax) ? (this.isPaid ? 10 : 3) : envMax);

    this.maxCharsPerFile =
      opts.maxCharsPerFile ??
      parseInt(process.env.RESEARCHER_MAX_CHARS ?? "1500", 10);

    this.timeoutMs =
      opts.timeoutMs ??
      parseInt(process.env.RESEARCHER_TIMEOUT_MS ?? "10000", 10);

    this.useGithub =
      opts.useGithub ?? process.env.RESEARCHER_USE_GITHUB !== "false";
    this.useGrepApp =
      opts.useGrepApp ?? process.env.RESEARCHER_USE_GREP_APP !== "false";
    this.useStackOverflow =
      opts.useStackOverflow ?? process.env.RESEARCHER_USE_SO === "true";
  }

  get isPaid(): boolean {
    return this.mode === Mode.PAID && !!this.githubToken;
  }

  get authHeaders(): Record<string, string> {
    const h: Record<string, string> = {
      Accept: "application/vnd.github+json",
    };
    if (this.isPaid && this.githubToken) {
      h["Authorization"] = `Bearer ${this.githubToken}`;
    }
    return h;
  }
}
