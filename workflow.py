from langgraph.graph import StateGraph, END
from datetime import datetime
from agents.data_ingestion import data_ingestion_node
from agents.topic_extraction import topic_extraction_node
from agents.topic_consolidation import topic_consolidation_node
from agents.review_report import review_report_node
from agents.state_types import ReviewAnalysisState

def create_review_analysis_workflow():
    """
    SEQUENTIAL WORKFLOW (Not Supervisor Pattern)
    Each step feeds into the next step linearly
    """
    workflow = StateGraph(ReviewAnalysisState)
    
    workflow.add_node("ingest_data", data_ingestion_node)           
    workflow.add_node("extract_topics", topic_extraction_node)    
    workflow.add_node("consolidate_topics", topic_consolidation_node)  
    workflow.add_node("generate_report", review_report_node)

    workflow.set_entry_point("ingest_data")
    workflow.add_edge("ingest_data", "extract_topics")
    workflow.add_edge("extract_topics", "consolidate_topics")
    workflow.add_edge("consolidate_topics", "generate_report")
    workflow.add_edge("generate_report", END)

    return workflow.compile()