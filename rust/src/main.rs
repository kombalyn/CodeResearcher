use clap::Parser;
use code_researcher::{CodeResearcher, ResearcherConfig};

#[derive(Parser, Debug)]
#[command(
    name = "code-researcher",
    about = "Search GitHub for real code examples and inject them into LLM prompts",
    long_about = None
)]
struct Args {
    /// Search query (English works best)
    query: String,

    /// Programming language: rust, python, typescript, javascript, go, ...
    #[arg(short, long, default_value = "rust")]
    language: String,

    /// Force paid mode (requires GITHUB_TOKEN in .env)
    #[arg(long)]
    paid: bool,

    /// Force free mode (ignores GITHUB_TOKEN)
    #[arg(long)]
    free: bool,

    /// Max number of results
    #[arg(long)]
    max: Option<usize>,

    /// Skip grep.app source
    #[arg(long)]
    no_grep_app: bool,
}

#[tokio::main]
async fn main() {
    let args = Args::parse();

    let mut config = ResearcherConfig::from_env();

    if args.paid {
        config.mode = code_researcher::Mode::Paid;
    } else if args.free {
        config.mode = code_researcher::Mode::Free;
        config.github_token = String::new();
    }
    if let Some(max) = args.max {
        config.max_results = max;
    }
    if args.no_grep_app {
        config.use_grep_app = false;
    }

    let researcher = CodeResearcher::new(config);
    let result = researcher.search(&args.query, &args.language).await;

    println!();
    println!("{}", "=".repeat(65));
    println!(
        "Results: {} | Mode: {} | Language: {}",
        result.found, result.mode, args.language
    );
    println!("{}", "=".repeat(65));

    if result.is_empty() {
        println!("\nNo results found. Try:");
        println!("  - English search queries");
        println!("  - Shorter, more specific terms");
        println!("  - Set GITHUB_TOKEN in .env for better results");
        return;
    }

    println!();
    println!("{}", result.context_block);
}
