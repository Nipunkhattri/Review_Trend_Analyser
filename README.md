# Review Trend Analyzer

## Overview
Review Trend Analyzer is an AI-powered feedback detection and trend analysis tool for app reviews, designed to extract, consolidate, and report on user feedback from platforms like the Google Play Store. The system uses Azure OpenAI for topic extraction and consolidation, providing actionable insights into user sentiment and concerns over time.

## Features
- **Automated Data Ingestion:** Scrapes reviews for a given app and date range using Google Play Scraper.
- **Topic Extraction:** Uses Azure OpenAI to identify and categorize topics from review data.
- **Topic Consolidation:** Merges similar topics to avoid fragmentation and improve clarity.
- **Trend Analysis:** Tracks topic frequencies over time and generates CSV reports for further analysis.
- **Modular Workflow:** Each step (ingestion, extraction, consolidation, reporting) is implemented as an async node for easy extension and orchestration.

## Project Structure
```
app.py                  # Main application entry point
config.py               # Azure OpenAI and other configuration
requirements.txt        # Python dependencies
workflow.py             # Orchestrates the analysis workflow
agents/
    data_ingestion.py   # Scrapes review data
    topic_extraction.py # Extracts topics from reviews
    topic_consolidation.py # Consolidates similar topics
    review_report.py    # Generates trend analysis report
    state_types.py      # State management types
utils/
    scraper_service.py  # Google Play review scraping logic
```

## How It Works
1. **Data Ingestion:** Scrapes reviews for the past 30 days for a specified app.
2. **Topic Extraction:** Extracts structured topics from reviews using Azure OpenAI.
3. **Topic Consolidation:** Merges similar topics for clarity and actionable insights.
4. **Trend Analysis:** Generates a CSV report showing topic trends over time.

## Setup & Installation
1. Clone the repository.
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Configure Azure OpenAI credentials in `config.py` or via environment variables.
4. Run the workflow:
   ```powershell
   python app.py
   ```

## Requirements
- Python 3.8+
- Azure OpenAI credentials
- Internet access for scraping reviews

## Extending the Project
Here are some ideas for future enhancements:
- **Sentiment Analysis:** Add sentiment scoring for each review/topic.
- **Dashboard UI:** Build a web dashboard for interactive trend visualization.
- **Multi-platform Support:** Extend scraping to iOS App Store, Amazon, etc.
- **Automated Alerts:** Notify stakeholders when certain topics spike.
- **Custom Topic Seeds:** Allow users to define their own seed topics.
- **Historical Data Storage:** Store and query historical trends in a database.
- **Advanced Filtering:** Filter reviews by rating, region, or keywords.
- **Model Fine-tuning:** Fine-tune LLMs for more accurate topic extraction.
- **Batch Processing:** Support for analyzing multiple apps in parallel.
- **API Integration:** Expose analysis results via REST API.
