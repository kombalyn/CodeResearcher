//! code-researcher – Rust library
//!
//! Search GitHub (and grep.app) for real code examples
//! and format them as context blocks for LLM prompts.
//!
//! # Free vs Paid Mode
//! - **Free**: No token needed. GitHub: 60 req/hour. grep.app: unlimited.
//! - **Paid**: Set `GITHUB_TOKEN` in `.env`. GitHub: 5,000 req/hour.
//!
//! # Example
//! ```no_run
//! use code_researcher::{CodeResearcher, ResearcherConfig};
//!
//! #[tokio::main]
//! async fn main() {
//!     let config = ResearcherConfig::from_env();
//!     let researcher = CodeResearcher::new(config);
//!     let result = researcher.search("google search earnings date rust reqwest", "rust").await;
//!     println!("{}", result.context_block);
//! }
//! ```

pub mod config;
pub mod searcher;
pub mod sources;

pub use config::{Mode, ResearcherConfig};
pub use searcher::{CodeResearcher, ResearchResult, SearchResult};
