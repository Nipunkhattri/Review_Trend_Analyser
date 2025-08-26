from typing import Dict, List, TypedDict

class ReviewAnalysisState(TypedDict):
    analysis_id: int
    app_url: str
    target_date: str
    
    raw_reviews: Dict[str, List[Dict]]  
    extracted_topics: Dict[str, Dict[str, int]]
    consolidated_topics: Dict[str, int]  
    topic_mapping: Dict[str, str] 
    daily_frequencies: Dict[str, Dict[str, int]] 
    trend_analysis: Dict
    
    processing_status: str
    errors: List[str]
    current_step: str
