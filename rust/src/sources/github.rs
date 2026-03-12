use crate::config::ResearcherConfig;
use crate::searcher::SearchResult;
use serde::Deserialize;

#[derive(Deserialize)]
struct GitHubSearchResponse {
    items: Option<Vec<GitHubItem>>,
}

#[derive(Deserialize)]
struct GitHubItem {
    path: Option<String>,
    html_url: Option<String>,
    repository: Option<GitHubRepo>,
}

#[derive(Deserialize)]
struct GitHubRepo {
    full_name: Option<String>,
}

pub async fn search_github(
    client: &reqwest::Client,
    query: &str,
    language: &str,
    config: &ResearcherConfig,
) -> Vec<SearchResult> {
    let mut results = Vec::new();
    let q = format!("{} language:{}", query, language);
    let per_page = (config.max_results * 3).min(30);

    let mut req = client
        .get("https://api.github.com/search/code")
        .query(&[("q", q.as_str()), ("sort", "indexed")])
        .query(&[("per_page", per_page.to_string().as_str())]);

    for (k, v) in config.auth_headers() {
        req = req.header(k, v);
    }

    let resp = match req.send().await {
        Ok(r) => r,
        Err(e) => {
            println!("  [GitHub] Network error: {}", e);
            return results;
        }
    };

    match resp.status().as_u16() {
        401 | 403 => {
            println!("  [GitHub] Auth/rate-limit error");
            if !config.is_paid() {
                println!("  [GitHub] Tip: set GITHUB_TOKEN in .env for 5,000 req/h");
            }
            return results;
        }
        200 => {}
        code => {
            println!("  [GitHub] HTTP {}", code);
            return results;
        }
    }

    let data: GitHubSearchResponse = match resp.json().await {
        Ok(d) => d,
        Err(e) => {
            println!("  [GitHub] JSON parse error: {}", e);
            return results;
        }
    };

    for item in data.items.unwrap_or_default() {
        if results.len() >= config.max_results {
            break;
        }

        let html_url = item.html_url.unwrap_or_default();
        let raw_url = html_url
            .replace("https://github.com", "https://raw.githubusercontent.com")
            .replace("/blob/", "/");
        let repo = item.repository.and_then(|r| r.full_name).unwrap_or_default();
        let file_path = item.path.unwrap_or_default();

        if let Some(code) = fetch_raw(client, &raw_url).await {
            let line_count = code.lines().count();
            if line_count >= 5 && line_count <= 600 {
                results.push(SearchResult {
                    source: "github".to_string(),
                    repo,
                    file: file_path,
                    url: html_url,
                    code: code.chars().take(config.max_chars_per_file).collect(),
                });
                tokio::time::sleep(std::time::Duration::from_millis(100)).await;
            }
        }
    }

    results
}

async fn fetch_raw(client: &reqwest::Client, url: &str) -> Option<String> {
    client.get(url).send().await.ok()?.text().await.ok()
}
