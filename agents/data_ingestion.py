from datetime import datetime, timedelta
import asyncio
from agents.state_types import ReviewAnalysisState
from utils.scraper_service import ScraperService

async def data_ingestion_node(state: ReviewAnalysisState) -> ReviewAnalysisState:
    """
    Data Scraping Node to get data from the review platform
    """
    print(f"Starting data ingestion for analysis {state['analysis_id']}")
    
    try:
        scraper = ScraperService()
        
        target_date = datetime.strptime(state['target_date'], '%Y-%m-%d')
        start_date = target_date - timedelta(days=30)
        
        raw_reviews = {}
        current_date = start_date
        
        while current_date <= target_date:
            date_str = current_date.strftime('%Y-%m-%d')
            print(f"Scraping reviews for {date_str}")
            
            daily_reviews = await scraper.scrape_reviews_for_date(
                app_url=state['app_url'],
                date=current_date
            )

            raw_reviews[date_str] = daily_reviews
            current_date += timedelta(days=1)
            
            await asyncio.sleep(0.5)
            
        return {
            **state,
            "raw_reviews": raw_reviews,
            "current_step": "data_ingestion_completed",
            "processing_status": "ingestion_complete"
        }
        
    except Exception as e:
        return {
            **state,
            "errors": state.get("errors", []) + [f"Ingestion error: {str(e)}"],
            "processing_status": "ingestion_failed"
        }