import { ResearcherConfig } from "../config";
import type { SearchResult } from "../searcher";

export async function searchGrepApp(
  query: string,
  language: string,
  config: ResearcherConfig
): Promise<SearchResult[]> {
  const results: SearchResult[] = [];
  const langMap: Record<string, string> = {
    python: "Python",
    javascript: "JavaScript",
    typescript: "TypeScript",
    rust: "Rust",
    go: "Go",
    java: "Java",
  };
  const langParam = langMap[language.toLowerCase()] ?? language;

  const searchUrl =
    `https://grep.app/search?q=${encodeURIComponent(query)}` +
    `&filter[lang][0]=${encodeURIComponent(langParam)}`;

  let html: string;
  try {
    const resp = await fetch(searchUrl, {
      headers: { "User-Agent": "code-researcher/1.0" },
      signal: AbortSignal.timeout(config.timeoutMs),
    });
    if (!resp.ok) {
      console.log(`  [grep.app] HTTP ${resp.status}`);
      return [];
    }
    html = await resp.text();
  } catch (e) {
    console.log(`  [grep.app] Network error: ${e}`);
    return [];
  }

  // Extract GitHub blob URLs from HTML
  const blobRegex = /href="(https:\/\/github\.com\/[^"]+\/blob\/[^"]+\.[a-zA-Z]+)"/g;
  const seen = new Set<string>();
  const urls: string[] = [];
  let m: RegExpExecArray | null;
  while ((m = blobRegex.exec(html)) !== null) {
    if (!seen.has(m[1])) {
      seen.add(m[1]);
      urls.push(m[1]);
    }
  }

  for (const htmlUrl of urls.slice(0, config.maxResults * 2)) {
    if (results.length >= config.maxResults) break;

    const rawUrl = htmlUrl
      .replace("https://github.com", "https://raw.githubusercontent.com")
      .replace("/blob/", "/");

    const parts = htmlUrl.replace("https://github.com/", "").split("/");
    const repo = parts.slice(0, 2).join("/");
    const filePath = parts.slice(4).join("/");

    const code = await fetchRaw(rawUrl, config);
    if (!code) continue;

    const lines = code.split("\n");
    if (lines.length < 5 || lines.length > 600) continue;

    results.push({
      source: "grep.app",
      repo,
      file: filePath,
      url: htmlUrl,
      code: code.slice(0, config.maxCharsPerFile),
    });

    await sleep(150);
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
