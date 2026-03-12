//! Configuration for code-researcher.
//!
//! Environment variables (set in .env):
//!   GITHUB_TOKEN            GitHub PAT – enables paid mode
//!   RESEARCHER_MODE         "free" | "paid"
//!   RESEARCHER_MAX_RESULTS  Max files per search
//!   RESEARCHER_MAX_CHARS    Max chars per snippet (default: 1500)
//!   RESEARCHER_USE_GITHUB   "true"/"false"
//!   RESEARCHER_USE_GREP_APP "true"/"false"

use std::env;

#[derive(Debug, Clone, PartialEq)]
pub enum Mode {
    Free,
    Paid,
}

#[derive(Debug, Clone)]
pub struct ResearcherConfig {
    pub github_token: String,
    pub mode: Mode,
    pub max_results: usize,
    pub max_chars_per_file: usize,
    pub timeout_secs: u64,
    pub use_github: bool,
    pub use_grep_app: bool,
}

impl ResearcherConfig {
    /// Load configuration from environment variables and .env file.
    pub fn from_env() -> Self {
        // Load .env if present
        let _ = dotenvy::dotenv();

        let github_token = env::var("GITHUB_TOKEN").unwrap_or_default();

        let mode = match env::var("RESEARCHER_MODE").as_deref() {
            Ok("paid") => Mode::Paid,
            Ok("free") => Mode::Free,
            _ => {
                if github_token.is_empty() {
                    Mode::Free
                } else {
                    Mode::Paid
                }
            }
        };

        let default_max = if mode == Mode::Paid { 10 } else { 3 };
        let max_results = env::var("RESEARCHER_MAX_RESULTS")
            .ok()
            .and_then(|v| v.parse().ok())
            .unwrap_or(default_max);

        let max_chars_per_file = env::var("RESEARCHER_MAX_CHARS")
            .ok()
            .and_then(|v| v.parse().ok())
            .unwrap_or(1500);

        let use_github = env::var("RESEARCHER_USE_GITHUB")
            .map(|v| v != "false")
            .unwrap_or(true);

        let use_grep_app = env::var("RESEARCHER_USE_GREP_APP")
            .map(|v| v != "false")
            .unwrap_or(true);

        ResearcherConfig {
            github_token,
            mode,
            max_results,
            max_chars_per_file,
            timeout_secs: 10,
            use_github,
            use_grep_app,
        }
    }

    pub fn is_paid(&self) -> bool {
        self.mode == Mode::Paid && !self.github_token.is_empty()
    }

    pub fn auth_headers(&self) -> Vec<(String, String)> {
        let mut headers = vec![
            ("Accept".to_string(), "application/vnd.github+json".to_string()),
        ];
        if self.is_paid() {
            headers.push(("Authorization".to_string(), format!("Bearer {}", self.github_token)));
        }
        headers
    }
}
