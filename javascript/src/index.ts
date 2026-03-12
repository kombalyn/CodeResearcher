/**
 * code-researcher – TypeScript/JavaScript
 *
 * Search GitHub for real code examples and inject them into LLM prompts.
 *
 * Free mode:  No token needed. GitHub: 60 req/hour, grep.app: unlimited.
 * Paid mode:  Set GITHUB_TOKEN in .env for 5,000 GitHub req/hour.
 */

export { CodeResearcher } from "./searcher";
export { ResearcherConfig, Mode } from "./config";
export type { SearchResult, ResearchResult } from "./searcher";
