import { ResearcherConfig } from "../config";
import type { SearchResult } from "../searcher";

const GITHUB_API = "https://api.github.com/search/code";

export async function searchGitHub(
  query: string,
  language: string,
  config: ResearcherConfig
): Promise<SearchResult[]> {
  const results: SearchResult[] = [];
  const params = new URLSearchParams({
    q: `${query} language:${language}`,
    per_page: String(Math.min(config.maxResults * 3, 30)),
    sort: "indexed",
  });

  let resp: Response;
  try {
    resp = await fetch(`${GITHUB_API}?${params}`, {
      headers: config.authHeaders,
      signal: AbortSignal.timeout(config.timeoutMs),
    });
  } catch (e) {
    console.log(`  [GitHub] Network error: ${e}`);
    return [];
  }

  if (resp.status === 401 || resp.status === 403) {
    const remaining = resp.headers.get("X-RateLimit-Remaining") ?? "?";
    console.log(`  [GitHub] Auth/rate-limit error (remaining: ${remaining})`);
    if (!config.isPaid) {
      console.log("  [GitHub] Tip: set GITHUB_TOKEN in .env for 5,000 req/h");
    }
    return [];
  }
  if (!resp.ok) {
    console.log(`  [GitHub] HTTP ${resp.status}`);
    return [];
  }

  const data = await resp.json() as { items?: any[] };
  const items = data.items ?? [];

  for (const item of items) {
    if (results.length >= config.maxResults) break;

    const repo: string = item.repository?.full_name ?? "";
    const filePath: string = item.path ?? "";
    const htmlUrl: string = item.html_url ?? "";
    const rawUrl = htmlUrl
      .replace("https://github.com", "https://raw.githubusercontent.com")
      .replace("/blob/", "/");

    const code = await fetchRaw(rawUrl, config);
    if (!code) continue;

    const lines = code.split("\n");
    if (lines.length < 5 || lines.length > 600) continue;

    results.push({
      source: "github",
      repo,
      file: filePath,
      url: htmlUrl,
      code: code.slice(0, config.maxCharsPerFile),
    });

    await sleep(100);
  }

  return results;
}

async function fetchRaw(url: string, config: ResearcherConfig): Promise<string | null> {
  try {
    const resp = await fetch(url, { signal: AbortSignal.timeout(config.timeoutMs) });
    if (resp.ok) return await resp.text();
  } catch (_) {}
  return null;
}

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}
