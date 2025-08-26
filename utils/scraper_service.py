# scraper_service.py
from google_play_scraper import reviews, Sort
from datetime import datetime, timedelta

class ScraperService:
    async def scrape_reviews_for_date(self, app_url: str, date: datetime):
        """
        Scrape reviews for a given date from Google Play Store.
        app_url: e.g. "com.whatsapp"
        date: datetime object (we'll filter manually)
        """
        package_name = app_url.split("id=")[-1] if "id=" in app_url else app_url

        result, _ = reviews(
            package_name,
            lang="en",
            country="in",
            sort=Sort.NEWEST,
            count=200,
        )

        date_str = date.strftime("%Y-%m-%d")
        daily_reviews = [
            {
                "user": r["userName"],
                "rating": r["score"],
                "content": r["content"],
                "at": r["at"].strftime("%Y-%m-%d"),
                "reply": r.get("replyContent"),
            }
            for r in result
            if r["at"].strftime("%Y-%m-%d") == date_str
        ]

        return daily_reviews
