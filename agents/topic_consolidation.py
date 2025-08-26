from collections import defaultdict
from agents.state_types import ReviewAnalysisState
import json

# LangChain imports
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import azure_config

async def topic_consolidation_node(state: ReviewAnalysisState) -> ReviewAnalysisState:
    """
    AGENT NODE - Complex reasoning needed for topic consolidation
    This is where we need intelligent decision making!
    """
    print(f"Starting topic consolidation for analysis {state['analysis_id']}")

    try:
        all_topics = set()
        topic_frequencies = defaultdict(int)
        
        # aggregate all topics across days
        for date, topics in state['extracted_topics'].items():
            for topic, frequency in topics.items():
                all_topics.add(topic)
                topic_frequencies[topic] += frequency

        print(f"Found {len(topic_frequencies)} significant topics to consolidate")
        print(f"Topic frequencies: {dict(topic_frequencies)}")

        topics_text = ", ".join([f"{topic}: {freq}" for topic, freq in topic_frequencies.items() if freq > 0])

        consolidation_message = ChatPromptTemplate.from_template("""
        TASK: Consolidate similar topics to avoid fragmentation
        
        TOPICS TO CONSOLIDATE:
        {topics_text}
        
        CONSOLIDATION RULES:
        1. Merge topics that refer to the same underlying issue
        2. Examples of topics that should be merged:
           - "delivery_late", "slow_delivery", "delivery_delayed" → "delivery_time_issue"
           - "rude_delivery_partner", "delivery_guy_rude", "impolite_delivery" → "delivery_partner_behavior"
        3. Keep distinct topics separate (don't over-consolidate)
        4. Use clear, descriptive names for consolidated topics
        
        REQUIRED OUTPUT FORMAT:
        {{
            "consolidated_topics": {{
                "final_topic_name": total_frequency
            }},
            "topic_mapping": {{
                "original_topic": "consolidated_topic_name"
            }}
        }}
        """)

        if not azure_config.is_configured():
            raise Exception("Azure OpenAI not configured. Please set AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT_NAME environment variables.")
        
        llm = AzureChatOpenAI(
            azure_deployment=azure_config.deployment_name,
            openai_api_version=azure_config.api_version,
            azure_endpoint=azure_config.endpoint,
            api_key=azure_config.api_key,
            temperature=0.1
        )

        print("Calling Azure OpenAI for topic consolidation...")
        result = await llm.ainvoke(
            consolidation_message.format(
                topics_text=topics_text
            )
        )

        print("Azure OpenAI call completed successfully!")

        print(f"Result of topic consolidation: {result}")
        print(f"Result content: {result.content}")
        print(f"Result type: {type(result)}")
        print(f"Result content type: {type(result.content)}")
        
        try:
            content = result.content.strip()
            if content.startswith('```json'):
                content = content[7:] 
                if content.endswith('```'):
                    content = content[:-3] 
            elif content.startswith('```'):
                content = content[3:] 
                if content.endswith('```'):
                    content = content[:-3] 
            
            consolidation_result = json.loads(content.strip())
            print(f"Parsed consolidation result: {consolidation_result}")
        except Exception as parse_err:
            print(f"JSON parsing error: {parse_err}")
            print(f"Raw content: {content}")
            print(f"Content length: {len(content)}")
            print(f"Content starts with: {content[:100]}")
            print(f"Content ends with: {content[-100:]}")
            print("Continuing with empty consolidation due to parsing error")
            consolidation_result = {
                "consolidated_topics": {},
                "topic_mapping": {}
            }

        consolidated_daily_frequencies = {}
        print(f"Processing daily frequencies for {len(state['extracted_topics'])} dates")
        
        for date, daily_topics in state['extracted_topics'].items():
            consolidated_daily = defaultdict(int)
            print(f"Processing date {date} with topics: {daily_topics}")
            
            for original_topic, frequency in daily_topics.items():
                consolidated_topic = consolidation_result['topic_mapping'].get(
                    original_topic, original_topic
                )
                consolidated_daily[consolidated_topic] += frequency
                print(f"  {original_topic} ({frequency}) -> {consolidated_topic}")
            
            consolidated_daily_frequencies[date] = dict(consolidated_daily)
            print(f"  Consolidated for {date}: {dict(consolidated_daily)}")
        
        print(f"Final consolidated daily frequencies: {consolidated_daily_frequencies}")

        if not consolidation_result['consolidated_topics']:
            print("Consolidation failed, using original topics as fallback")
            fallback_consolidated_topics = {}
            fallback_topic_mapping = {}
            
            for topic, freq in topic_frequencies.items():
                if freq > 0:  
                    fallback_consolidated_topics[topic] = freq
                    fallback_topic_mapping[topic] = topic
            
            consolidation_result['consolidated_topics'] = fallback_consolidated_topics
            consolidation_result['topic_mapping'] = fallback_topic_mapping
            
            consolidated_daily_frequencies = {}
            for date, daily_topics in state['extracted_topics'].items():
                consolidated_daily = defaultdict(int)
                for original_topic, frequency in daily_topics.items():
                    consolidated_topic = fallback_topic_mapping.get(original_topic, original_topic)
                    consolidated_daily[consolidated_topic] += frequency
                consolidated_daily_frequencies[date] = dict(consolidated_daily)
            
            print(f"Fallback consolidated topics: {fallback_consolidated_topics}")
            print(f"Fallback daily frequencies: {consolidated_daily_frequencies}")

        return {
            **state,
            "consolidated_topics": consolidation_result['consolidated_topics'],
            "topic_mapping": consolidation_result['topic_mapping'],
            "daily_frequencies": consolidated_daily_frequencies,
            "current_step": "topic_consolidation_completed",
            "processing_status": "consolidation_complete"
        }

    except Exception as e:
        print(f"Topic consolidation failed with error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return {
            **state,
            "errors": state.get("errors", []) + [f"Consolidation error: {str(e)}"],
            "processing_status": "consolidation_failed"
        }
