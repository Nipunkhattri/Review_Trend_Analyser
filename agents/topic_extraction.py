from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json
from agents.state_types import ReviewAnalysisState
from config import azure_config

async def topic_extraction_node(state: ReviewAnalysisState) -> ReviewAnalysisState:
    """
    Structured topic extraction from the extracted review data
    """
    print(f"Starting topic extraction for analysis {state['analysis_id']}")
    
    try:
        if not azure_config.is_configured():
            raise Exception("Azure OpenAI not configured. Please set AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT_NAME environment variables.")
        
        llm = AzureChatOpenAI(
            azure_deployment=azure_config.deployment_name,
            openai_api_version=azure_config.api_version,
            azure_endpoint=azure_config.endpoint,
            api_key=azure_config.api_key,
            temperature=0.1
        )
        
        seed_topics = [
            "delivery_issue", "food_quality", "delivery_partner_behavior", 
            "app_functionality", "payment_issue", "customer_service",
            "restaurant_availability", "order_accuracy", "packaging_quality",
            "delivery_time", "app_performance", "pricing_concern"
        ]
        
        extraction_prompt = ChatPromptTemplate.from_template("""
        You are an expert at extracting topics from food delivery app reviews.
        
        SEED TOPICS: {seed_topics}
        
        Extract topics from these reviews. Each topic should represent a specific user concern, request, or feedback.
        
        RULES:
        1. Use seed topics when applicable, but identify new topics as needed
        2. Be specific but not overly granular (e.g., "delivery_late" not "delivery_5_minutes_late")
        3. Use snake_case format for topic names
        4. Count frequency of each topic
        
        REVIEWS: {reviews}
        
        Return JSON format:
        {{
            "topic_name": {{
                "frequency": int,
                "keywords": ["keyword1", "keyword2"],
                "sample_reviews": ["review1", "review2"]
            }}
        }}
        """)
        
        extracted_topics = {}
        
        for date, reviews in state['raw_reviews'].items():
            if not reviews:
                extracted_topics[date] = {}
                continue
                
            reviews_text = []
            for review in reviews:
                reviews_text.append(f"Rating: {review.get('rating', 'N/A')} - {review.get('content', '')}")
            
            
            response = await llm.ainvoke(
                extraction_prompt.format(
                    seed_topics=", ".join(seed_topics),
                    reviews="\n".join(reviews_text)
                )
            )

            print(f"Response for {date}: {response}")
            
            try:
                print(f"Response content for {date}: {response.content}")
                
                content = response.content.strip()
                if content.startswith('```json'):
                    content = content[7:]  
                    if content.endswith('```'):
                        content = content[:-3] 
                elif content.startswith('```'):
                    content = content[3:]  
                    if content.endswith('```'):
                        content = content[:-3]
                
                topics_data = json.loads(content.strip())

                print(f"Topics data for {date}: {topics_data}")
                
                daily_topics = {}
                for topic_name, topic_data in topics_data.items():
                    daily_topics[topic_name] = topic_data.get('frequency', 0)
                
                extracted_topics[date] = daily_topics
                print(f"Extracted topics for {date}: {daily_topics}")
                
            except json.JSONDecodeError:
                print(f"Failed to parse LLM response for {date}")
                extracted_topics[date] = {}
        
        print(f"Final extracted topics: {extracted_topics}")
        
        return {
            **state,
            "extracted_topics": extracted_topics,
            "current_step": "topic_extraction_completed",
            "processing_status": "extraction_complete"
        }
        
    except Exception as e:
        return {
            **state,
            "errors": state.get("errors", []) + [f"Extraction error: {str(e)}"],
            "processing_status": "extraction_failed"
        }