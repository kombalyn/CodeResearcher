//! Core CodeResearcher struct.

use crate::config::ResearcherConfig;
use crate::sources::{search_github, search_grep_app};

#[derive(Debug, Clone)]
pub struct SearchResult {
    pub source: String,
    pub repo: String,
    pub file: String,
    pub url: String,
    pub code: String,
}

#[derive(Debug)]
pub struct ResearchResult {
    pub task: String,
    pub results: Vec<SearchResult>,
    pub context_block: String,
    pub found: usize,
    pub mode: String,
}

impl ResearchResult {
    pub fn is_empty(&self) -> bool {
        self.found == 0
    }
}

pub struct CodeResearcher {
    config: ResearcherConfig,
}

impl CodeResearcher {
    pub fn new(config: ResearcherConfig) -> Self {
        CodeResearcher { config }
    }

    /// Search for code examples relevant to the task.
    ///
    /// # Arguments
    /// * `task`     - Description of the programming task (English works best)
    /// * `language` - Target language: "rust", "python", "typescript", etc.
    pub async fn search(&self, task: &str, language: &str) -> ResearchResult {
        let mut all_results: Vec<SearchResult> = Vec::new();
        let mode_label = if self.config.is_paid() { "paid" } else { "free" };
        let preview = if task.len() > 60 { &task[..60] } else { task };

        println!("  [Researcher] Mode: {} | Query: '{}'...", mode_label, preview);

        let client = reqwest::Client::builder()
            .timeout(std::time::Duration::from_secs(self.config.timeout_secs))
            .user_agent("code-researcher/1.0")
            .build()
            .unwrap_or_default();

        // Source 1: GitHub
        if self.config.use_github {
            let auth_label = if self.config.is_paid() {
                "authenticated"
            } else {
                "unauthenticated, 60 req/h limit"
            };
            println!("  [Researcher] Searching GitHub ({})...", auth_label);
            let results = search_github(&client, task, language, &self.config).await;
            println!("    → {} files found", results.len());
            all_results.extend(results);
        }

        // Source 2: grep.app (always free)
        if self.config.use_grep_app && all_results.len() < self.config.max_results {
            println!("  [Researcher] Searching grep.app (no token needed)...");
            let results = search_grep_app(&client, task, language, &self.config).await;
            println!("    → {} files found", results.len());
            all_results.extend(results);
        }

        // Deduplicate by URL
        let mut seen_urls = std::collections::HashSet::new();
        let unique: Vec<SearchResult> = all_results
            .into_iter()
            .filter(|r| seen_urls.insert(r.url.clone()))
            .collect();

        let final_results: Vec<SearchResult> = unique
            .into_iter()
            .take(self.config.max_results)
            .collect();

        println!("  [Researcher] Total: {} unique results", final_results.len());

        let context_block = self.build_context_block(&final_results);
        let found = final_results.len();

        ResearchResult {
            task: task.to_string(),
            results: final_results,
            context_block,
            found,
            mode: mode_label.to_string(),
        }
    }

    fn build_context_block(&self, results: &[SearchResult]) -> String {
        if results.is_empty() {
            return String::new();
        }

        let mut lines = vec![
            "## Code Examples from GitHub (use as reference, adapt don't copy blindly)\n".to_string(),
        ];

        for (i, r) in results.iter().enumerate() {
            lines.push(format!("### [{}] [{}] {}", i + 1, r.source.to_uppercase(), r.repo));
            if !r.file.is_empty() {
                lines.push(format!("File: `{}`", r.file));
            }
            lines.push(format!("URL: {}", r.url));
            lines.push("```".to_string());
            lines.push(r.code.trim_end().to_string());
            lines.push("```\n".to_string());
        }

        lines.join("\n")
    }
}
