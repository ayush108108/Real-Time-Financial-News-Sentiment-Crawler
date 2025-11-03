# Real-Time Financial News Sentiment Crawler

A lightweight, asynchronous Python pipeline that ingests financial headlines from major outlets (Reuters, CNBC), enriches them with transformer-based sentiment scores, persists results in SQLite, and exports a ready-to-consume JSON feed—ideal for quant research ingestion stacks or downstream alerting flows.

## Key Features
- **Async RSS ingestion** via `aiohttp` with graceful fallbacks and logging for partial failures.
- **Robust parsing** that tolerates XML/HTML inconsistencies across feeds.
- **Transformer sentiment** using Hugging Face pipelines with lazy loading for minimal startup cost.
- **Data persistence** through SQLAlchemy ORM targeting SQLite (extensible to PostgreSQL).
- **JSON feed export** for integration with dashboards, n8n workflows, or trading bots.
- **Configurable settings** powered by Pydantic, honoring environment overrides.
- **Test coverage** with `pytest` + `pytest-asyncio` to ensure crawler resilience.

## Project Layout
```
news_crawler/
├── __main__.py         # CLI entry point
├── settings.py         # Pydantic settings & env handling
├── fetcher.py          # Async RSS fetch + parsing helpers
├── sentiment.py        # Hugging Face pipeline wrapper
├── database.py         # SQLAlchemy models & persistence helpers
├── exporter.py         # JSON serialization utilities
├── pipeline.py         # Orchestration of end-to-end flow
└── schemas.py          # Pydantic data contracts

tests/
├── test_fetcher.py     # RSS parsing & fetch handling tests
└── test_pipeline.py    # Pipeline orchestration tests
```

## Quickstart
1. **Create virtual environment & install deps**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. **Run the crawler**
   ```powershell
   python -m news_crawler
   ```
   Output JSON defaults to `output/latest.json` and an SQLite DB at `data/news.db`.

3. **Run the test suite**
   ```powershell
   python -m pytest
   ```

## Configuration
All runtime settings can be tweaked via environment variables (prefixed with `CRAWLER_`) or a `.env` file:

| Setting | Description | Default |
|---------|-------------|---------|
| `CRAWLER_REUTERS_FEED_URL` | Reuters RSS endpoint | `https://feeds.reuters.com/reuters/businessNews` |
| `CRAWLER_CNBC_FEED_URL` | CNBC RSS endpoint | `https://www.cnbc.com/id/10001169/device/rss/rss.html` |
| `CRAWLER_HTTP_TIMEOUT_SECONDS` | Request timeout window | `15` |
| `CRAWLER_USER_AGENT` | Custom HTTP user agent | `RealTimeFinancialNewsCrawler/0.1` |
| `CRAWLER_SENTIMENT_MODEL_NAME` | Hugging Face sentiment model | `distilbert-base-uncased-finetuned-sst-2-english` |
| `CRAWLER_SENTIMENT_DEVICE` | Pipeline device (`cpu`, `cuda`, or GPU index) | `None` |
| `CRAWLER_DATABASE_URL` | SQLAlchemy DB URL | `sqlite:///data/news.db` |
| `CRAWLER_OUTPUT_PATH` | JSON export path | `output/latest.json` |

## Data Flow
1. **Fetch feeds** concurrently from configured sources with retry-safe error handling.
2. **Parse and deduplicate** feed entries into normalized `RawArticle` objects.
3. **Annotate sentiment** (batch call to transformer pipeline for efficiency).
4. **Persist** unseen articles using SQLAlchemy UPSERT logic.
5. **Export** aggregated results into JSON for down-stream consumption.

## Extending
- **Additional feeds**: add to the tuple in `fetcher.fetch_feeds` or expose via config.
- **Alternate persistence**: swap `database_url` to a Postgres DSN; models already compatible.
- **Alerting/N8N**: point the generated JSON to a webhook or use `write_json` output as trigger.
- **Model upgrades**: adjust `sentiment_model_name` to any text-classification pipeline-compatible model.

## Troubleshooting
- Ensure an XML parser is available; the crawler falls back to `html.parser`/`ElementTree` when necessary.
- Transformer weights download on first run; pre-fetch models if deploying in restricted environments.
- For GPU acceleration, install CUDA-compatible PyTorch and set `CRAWLER_SENTIMENT_DEVICE=cuda`.

## Roadmap Ideas
- Add rate-limiting/backoff stategy for aggressive polling.
- Include additional publishers (Bloomberg, WSJ) or SEC filings.
- Surface metadata for trend analytics (entity tagging, topic clustering).

## License
MIT (pending). Update with your org’s licensing requirements.
