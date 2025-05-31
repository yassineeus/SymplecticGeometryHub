# Enhanced arXiv scraper for symplectic geometry with historical data collection
# Collects articles from 1980-2025 with automatic weekly updates
import arxiv
import pandas as pd
import datetime
import os
import yaml
import time
import re
import schedule
import threading
from tqdm import tqdm
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('symplectic_scraper.log'),
        logging.StreamHandler()
    ]
)

# Keywords for symplectic geometry and related topics
SEARCH_QUERIES = [
    '"symplectic geometry"',
    '"symplectic manifold"',
    '"symplectic structure"',
    '"lagrangian submanifold"',
    '"coisotropic submanifold"',
    '"moment map"',
    '"symplectic reduction"',
    '"hamiltonian action"',
    '"symplectic groupoid"',
    '"Poisson geometry"',
    '"Dirac structure"',
    '"Marsden–Weinstein reduction"',
    '"pre-symplectic geometry"',
    '"shifted symplectic structure"',
    '"derived symplectic geometry"',
    '"symplectic foliation"',
    '"symplectic Lie algebroid"',
    '"Poisson sigma model"',
    '"coisotropic brane"',
]

# Categories to target
CATEGORIES = [
    'math.SG',  # Symplectic Geometry
    'math.DG',  # Differential Geometry
    'math.AG',  # Algebraic Geometry
    'math-ph',  # Mathematical Physics
    'math.QA',  # Quantum Algebra
]

# Files and configuration
RESULTS_FILE = "symplectic_geometry_articles.csv"
HISTORICAL_FILE = "symplectic_historical_articles.csv"
README_FILE = "README.md"
CONFIG_FILE = "config_symplectic.yaml"
LAST_UPDATE_FILE = "last_update.txt"

# Configuration
MAX_RESULTS_PER_QUERY = 2000  # Increased for historical collection
DELAY_BETWEEN_REQUESTS = 3
START_YEAR = 1980
END_YEAR = 2025

def create_config():
    """Create configuration file for tracking updates"""
    config = {
        'last_full_update': None,
        'last_weekly_update': None,
        'start_year': START_YEAR,
        'end_year': END_YEAR,
        'total_articles_collected': 0,
        'weekly_update_enabled': True
    }
    
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    return config

def load_config():
    """Load configuration from file"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f)
    else:
        return create_config()

def save_config(config):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

def build_query(term, categories, start_date=None, end_date=None):
    """Build query with optional date range"""
    cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
    base_query = f"({term}) AND ({cat_query})"
    
    if start_date and end_date:
        # arXiv date format: YYYYMMDD
        date_query = f" AND submittedDate:[{start_date} TO {end_date}]"
        base_query += date_query
    
    return base_query

def get_date_ranges(start_year, end_year):
    """Generate year-by-year date ranges for comprehensive collection"""
    ranges = []
    for year in range(start_year, end_year + 1):
        start_date = f"{year}0101"
        end_date = f"{year}1231"
        ranges.append((start_date, end_date, year))
    return ranges

def fetch_articles_by_year(year, start_date, end_date):
    """Fetch articles for a specific year"""
    all_results = []
    client = arxiv.Client(page_size=100, delay_seconds=DELAY_BETWEEN_REQUESTS, num_retries=5)
    
    logging.info(f"Fetching articles for year {year}")
    
    for query_term in tqdm(SEARCH_QUERIES, desc=f"Fetching {year}", leave=False):
        query = build_query(query_term, CATEGORIES, start_date, end_date)
        search = arxiv.Search(
            query=query,
            max_results=MAX_RESULTS_PER_QUERY,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        try:
            results = list(client.results(search))
            all_results.extend(results)
            time.sleep(DELAY_BETWEEN_REQUESTS)
        except Exception as e:
            logging.error(f"Error fetching for term {query_term} in {year}: {e}")
            time.sleep(10)  # Wait longer on error
    
    # Remove duplicates within the year
    unique = {r.get_short_id(): r for r in all_results}
    logging.info(f"Found {len(unique)} unique articles for {year}")
    return list(unique.values())

def fetch_recent_articles(days_back=7):
    """Fetch articles from the last N days for weekly updates"""
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days_back)
    
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")
    
    logging.info(f"Fetching recent articles from {start_str} to {end_str}")
    
    all_results = []
    client = arxiv.Client(page_size=100, delay_seconds=DELAY_BETWEEN_REQUESTS, num_retries=5)
    
    for query_term in tqdm(SEARCH_QUERIES, desc="Fetching recent articles"):
        query = build_query(query_term, CATEGORIES, start_str, end_str)
        search = arxiv.Search(
            query=query,
            max_results=500,  # Smaller limit for recent articles
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        try:
            results = list(client.results(search))
            all_results.extend(results)
            time.sleep(DELAY_BETWEEN_REQUESTS)
        except Exception as e:
            logging.error(f"Error fetching recent articles for term {query_term}: {e}")
    
    unique = {r.get_short_id(): r for r in all_results}
    return list(unique.values())

def extract_info(result):
    """Extract article information"""
    return {
        "id": result.get_short_id(),
        "title": result.title,
        "authors": ", ".join(a.name for a in result.authors),
        "published": result.published.strftime("%Y-%m-%d"),
        "updated": result.updated.strftime("%Y-%m-%d") if hasattr(result, 'updated') else '',
        "summary": result.summary,
        "categories": ", ".join(result.categories),
        "url": result.entry_id,
        "pdf": result.pdf_url,
        "year": result.published.year
    }

def load_existing_articles():
    """Load existing articles to avoid duplicates"""
    existing_ids = set()
    
    # Load from main file
    if os.path.exists(RESULTS_FILE):
        df = pd.read_csv(RESULTS_FILE)
        existing_ids.update(df['id'].tolist())
    
    # Load from historical file
    if os.path.exists(HISTORICAL_FILE):
        df = pd.read_csv(HISTORICAL_FILE)
        existing_ids.update(df['id'].tolist())
    
    return existing_ids

def save_articles(results, filename, append=False):
    """Save articles to CSV file"""
    if not results:
        return None
    
    articles = [extract_info(r) for r in results]
    new_df = pd.DataFrame(articles)
    
    if append and os.path.exists(filename):
        existing_df = pd.read_csv(filename)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        # Remove duplicates based on ID
        combined_df = combined_df.drop_duplicates(subset=['id'], keep='first')
        df = combined_df.sort_values(by="published", ascending=False)
    else:
        df = new_df.sort_values(by="published", ascending=False)
    
    df.to_csv(filename, index=False)
    logging.info(f"Saved {len(df)} articles to {filename}")
    return df

def full_historical_collection():
    """Collect all articles from 1980 to 2025"""
    logging.info("Starting full historical collection...")
    
    existing_ids = load_existing_articles()
    date_ranges = get_date_ranges(START_YEAR, END_YEAR)
    all_new_results = []
    
    for start_date, end_date, year in tqdm(date_ranges, desc="Processing years"):
        year_results = fetch_articles_by_year(year, start_date, end_date)
        
        # Filter out existing articles
        new_results = [r for r in year_results if r.get_short_id() not in existing_ids]
        all_new_results.extend(new_results)
        
        # Update existing IDs to avoid duplicates in subsequent years
        existing_ids.update([r.get_short_id() for r in new_results])
        
        # Save progress periodically (every 5 years)
        if year % 5 == 0 and all_new_results:
            save_articles(all_new_results, HISTORICAL_FILE, append=True)
            all_new_results = []  # Reset to save memory
    
    # Save any remaining results
    if all_new_results:
        save_articles(all_new_results, HISTORICAL_FILE, append=True)

def weekly_update():
    """Perform weekly update of recent articles"""
    logging.info("Starting weekly update...")
    
    try:
        # Fetch recent articles (last 10 days to ensure we don't miss anything)
        recent_results = fetch_recent_articles(days_back=10)
        
        if recent_results:
            existing_ids = load_existing_articles()
            new_results = [r for r in recent_results if r.get_short_id() not in existing_ids]
            
            if new_results:
                save_articles(new_results, RESULTS_FILE, append=True)
                logging.info(f"Weekly update: Added {len(new_results)} new articles")
            else:
                logging.info("Weekly update: No new articles found")
        
        # Update configuration
        config = load_config()
        config['last_weekly_update'] = datetime.datetime.now().isoformat()
        save_config(config)
        
        # Generate updated README
        generate_readme()
        
    except Exception as e:
        logging.error(f"Error during weekly update: {e}")

def merge_all_data():
    """Merge historical and current data into one comprehensive file"""
    all_dfs = []
    
    if os.path.exists(HISTORICAL_FILE):
        df_hist = pd.read_csv(HISTORICAL_FILE)
        all_dfs.append(df_hist)
    
    if os.path.exists(RESULTS_FILE):
        df_current = pd.read_csv(RESULTS_FILE)
        all_dfs.append(df_current)
    
    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=['id'], keep='first')
        combined_df = combined_df.sort_values(by="published", ascending=False)
        
        # Save complete dataset
        combined_df.to_csv("symplectic_complete_dataset.csv", index=False)
        return combined_df
    
    return None

def generate_readme():
    """Generate comprehensive README with statistics"""
    df = merge_all_data()
    
    if df is None:
        return
    
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(f"# Symplectic Geometry Article Tracker (1980-2025)\n\n")
        f.write(f"Last updated: **{now}**\n\n")
        f.write(f"Total articles collected: **{len(df)}**\n\n")
        
        # Statistics by year
        year_stats = df['year'].value_counts().sort_index()
        f.write("## Articles by Year\n\n")
        f.write("| Year | Count |\n")
        f.write("|------|-------|\n")
        for year in range(START_YEAR, END_YEAR + 1):
            count = year_stats.get(year, 0)
            f.write(f"| {year} | {count} |\n")
        
        # Recent articles
        f.write("\n## Latest Articles (Last 30 days)\n\n")
        recent_cutoff = datetime.datetime.now() - datetime.timedelta(days=30)
        recent_articles = df[pd.to_datetime(df['published']) >= recent_cutoff]
        
        if len(recent_articles) > 0:
            f.write("| Date | Title | Authors | PDF |\n")
            f.write("|------|-------|---------|-----|\n")
            for _, row in recent_articles.head(20).iterrows():
                title = row['title'].replace('|', ' ').replace('\n', ' ')[:100]
                authors = row['authors'][:50] + "..." if len(row['authors']) > 50 else row['authors']
                f.write(f"| {row['published']} | {title} | {authors} | [PDF]({row['pdf']}) |\n")
        else:
            f.write("No articles found in the last 30 days.\n")
        
        # Search queries used
        f.write("\n## Search Queries Used\n\n")
        for i, query in enumerate(SEARCH_QUERIES, 1):
            f.write(f"{i}. {query}\n")
        
        f.write(f"\n## Categories Monitored\n\n")
        for cat in CATEGORIES:
            f.write(f"- {cat}\n")

def setup_scheduler():
    """Setup automatic weekly updates"""
    # Schedule weekly updates every Sunday at 2 AM
    schedule.every().sunday.at("02:00").do(weekly_update)
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour
    
    # Run scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logging.info("Weekly update scheduler started (runs every Sunday at 2 AM)")

def main():
    """Main execution function"""
    print("Starting Enhanced Symplectic Geometry Article Collection...")
    logging.info("Starting Enhanced Symplectic Geometry Article Collection...")
    
    config = load_config()
    
    # Check if full historical collection has been done
    if config.get('last_full_update') is None:
        print("Performing full historical collection (1980-2025)...")
        print("This may take several hours due to API rate limits...")
        full_historical_collection()
        
        config['last_full_update'] = datetime.datetime.now().isoformat()
        save_config(config)
    else:
        print("Full historical collection already completed.")
        print("Performing weekly update...")
        weekly_update()
    
    # Merge all data and generate README
    df = merge_all_data()
    generate_readme()
    
    if df is not None:
        print(f"Total articles in database: {len(df)}")
        print(f"Date range: {df['published'].min()} to {df['published'].max()}")
    
    # Setup automatic weekly updates
    if config.get('weekly_update_enabled', True):
        setup_scheduler()
        print("Automatic weekly updates enabled.")
        print("The script will continue running and update every Sunday at 2 AM.")
        print("Press Ctrl+C to stop.")
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("\nStopping automatic updates...")
            logging.info("Stopping automatic updates...")
    
    print("Done!")

if __name__ == "__main__":
    main()
