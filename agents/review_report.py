from agents.state_types import ReviewAnalysisState
import pandas as pd
import os
from datetime import datetime

async def review_report_node(state: ReviewAnalysisState) -> ReviewAnalysisState:
    """
    Generate review report and save to database
    """
    print(f"Starting review report generation for analysis {state['analysis_id']}")
    
    try:
        print(f"Consolidated topics: {state.get('consolidated_topics', {})}")
        print(f"Daily frequencies: {state.get('daily_frequencies', {})}")
        
        trend_data = {}
        
        for topic in state['consolidated_topics'].keys():
            topic_trend = []
            dates = sorted(state['daily_frequencies'].keys())
            
            for date in dates:
                frequency = state['daily_frequencies'][date].get(topic, 0)
                topic_trend.append({
                    'date': date,
                    'frequency': frequency
                })
            
            trend_data[topic] = {
                'daily_data': topic_trend
            }

        print(f"Trend data: {trend_data}")

        csv_filename = save_trend_data_to_csv(state['analysis_id'], trend_data)
        print(f"Trend data saved to: {csv_filename}")

        return {
            **state,
            "trend_analysis": trend_data,
            "current_step": "trend_analysis_completed",
            "processing_status": "completed"
        }
        
    except Exception as e:
        return {
            **state,
            "errors": state.get("errors", []) + [f"Analysis error: {str(e)}"],
            "processing_status": "analysis_failed"
        }


def save_trend_data_to_csv(analysis_id: str, trend_data: dict) -> str:
    """
    Save trend data to CSV file with topics as columns and dates as rows
    """
    try:
        data_dir = "output"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        csv_data = {}
        all_dates = set()
        
        for topic, topic_info in trend_data.items():
            for daily_data in topic_info['daily_data']:
                all_dates.add(daily_data['date'])
        
        sorted_dates = sorted(all_dates)
        
        csv_data['date'] = sorted_dates
        
        for topic, topic_info in trend_data.items():
            topic_frequencies = []
            for date in sorted_dates:
                frequency = 0
                for daily_data in topic_info['daily_data']:
                    if daily_data['date'] == date:
                        frequency = daily_data['frequency']
                        break
                topic_frequencies.append(frequency)
            
            csv_data[topic] = topic_frequencies
        
        df = pd.DataFrame(csv_data)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output/trend_analysis_{analysis_id}_{timestamp}.csv"
        
        df.to_csv(filename, index=False)
        
        print(f"CSV file created successfully: {filename}")
        print(f"Data shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        return filename
        
    except Exception as e:
        print(f"Error saving CSV file: {str(e)}")
        return None