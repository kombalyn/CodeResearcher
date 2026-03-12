use crate::config::ResearcherConfig;
use crate::searcher::SearchResult;
use regex::Regex;

pub async fn search_grep_app(
    client: &reqwest::Client,
    query: &str,
    language: &str,
    config: &ResearcherConfig,
) -> Vec<SearchResult> {
    let mut results = Vec::new();
    let lang_map = [
        ("python", "Python"), ("javascript", "JavaScript"),
        ("typescript", "TypeScript"), ("rust", "Rust"),
        ("go", "Go"), ("java", "Java"),
    ];
    let lang_param = lang_map
        .iter()
        .find(|(k, _)| k.eq_ignore_ascii_case(language))
        .map(|(_, v)| *v)
        .unwrap_or(language);

    let url = format!(
        "https://grep.app/search?q={}&filter[lang][0]={}",
        urlencoding::encode(query),
        urlencoding::encode(lang_param),
    );

    let html = match client
        .get(&url)
        .header("User-Agent", "code-researcher/1.0")
        .send()
        .await
        .and_then(|r| {
            if r.status().is_success() { Ok(r) } else { Err(reqwest::Error::from(std::io::Error::new(std::io::ErrorKind::Other, "HTTP error"))) }
        }) {
        Ok(r) => match r.text().await {
            Ok(t) => t,
            Err(_) => return results,
        },
        Err(e) => {
            println!("  [grep.app] Error: {}", e);
            return results;
        }
    };

    let re = Regex::new(r#"href="(https://github\.com/[^"]+/blob/[^"]+\.[a-zA-Z]+)""#).unwrap();
    let mut seen = std::collections::HashSet::new();
    let urls: Vec<String> = re
        .captures_iter(&html)
        .filter_map(|c| c.get(1).map(|m| m.as_str().to_string()))
        .filter(|u| seen.insert(u.clone()))
        .collect();

    for html_url in urls.iter().take(config.max_results * 2) {
        if results.len() >= config.max_results {
            break;
        }

        let raw_url = html_url
            .replace("https://github.com", "https://raw.githubusercontent.com")
            .replace("/blob/", "/");

        let parts: Vec<&str> = html_url
            .trim_start_matches("https://github.com/")
            .split('/')
            .collect();
        let repo = parts.get(..2).map(|p| p.join("/")).unwrap_or_default();
        let file_path = parts.get(4..).map(|p| p.join("/")).unwrap_or_default();

        if let Some(code) = fetch_raw(client, &raw_url).await {
            let line_count = code.lines().count();
            if line_count >= 5 && line_count <= 600 {
                results.push(SearchResult {
                    source: "grep.app".to_string(),
                    repo,
                    file: file_path,
                    url: html_url.clone(),
                    code: code.chars().take(config.max_chars_per_file).collect(),
                });
                tokio::time::sleep(std::time::Duration::from_millis(150)).await;
            }
        }
    }

    results
}

async fn fetch_raw(client: &reqwest::Client, url: &str) -> Option<String> {
    client.get(url).send().await.ok()?.text().await.ok()
}
