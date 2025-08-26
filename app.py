import streamlit as st
import asyncio
from datetime import datetime
from workflow import create_review_analysis_workflow
from agents.state_types import ReviewAnalysisState
from config import azure_config
import os

workflow = create_review_analysis_workflow()

st.set_page_config(page_title="Review Analysis Agent", layout="wide")

st.title("📊 Review Analysis Agent")
st.write("Test your end-to-end workflow for app review analysis.")

st.sidebar.header("🔧 Azure OpenAI Configuration")

api_key = st.sidebar.text_input(
    "Azure OpenAI API Key", 
    value=os.getenv("AZURE_OPENAI_API_KEY", ""),
    type="password",
    help="Your Azure OpenAI API key"
)

endpoint = st.sidebar.text_input(
    "Azure OpenAI Endpoint", 
    value=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
    help="Your Azure OpenAI endpoint URL (e.g., https://your-resource.openai.azure.com/)"
)

deployment_name = st.sidebar.text_input(
    "Deployment Name", 
    value=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
    help="Your Azure OpenAI deployment name"
)

api_version = st.sidebar.text_input(
    "API Version", 
    value=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
    help="Azure OpenAI API version"
)

if api_key:
    os.environ["AZURE_OPENAI_API_KEY"] = api_key
if endpoint:
    os.environ["AZURE_OPENAI_ENDPOINT"] = endpoint
if deployment_name:
    os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = deployment_name
if api_version:
    os.environ["AZURE_OPENAI_API_VERSION"] = api_version

azure_config.api_key = api_key
azure_config.endpoint = endpoint
azure_config.deployment_name = deployment_name
azure_config.api_version = api_version

if azure_config.is_configured():
    st.sidebar.success("✅ Azure OpenAI configured")
else:
    st.sidebar.error("❌ Azure OpenAI not configured")
    st.sidebar.info("Please configure Azure OpenAI settings in the sidebar")

with st.form("review_form"):
    analysis_id = st.number_input("Analysis ID", min_value=1, value=1)
    app_url = st.text_input("App URL or Package Name", value="com.whatsapp")
    target_date = st.date_input("Target Date", value=datetime.today())
    submitted = st.form_submit_button("Run Analysis 🚀")

if submitted:
    if not azure_config.is_configured():
        st.error("❌ Azure OpenAI is not configured. Please set up your Azure OpenAI credentials in the sidebar.")
    else:
        state: ReviewAnalysisState = {
            "analysis_id": analysis_id,
            "app_url": app_url,
            "target_date": target_date.strftime("%Y-%m-%d"),
            "raw_reviews": {},
            "extracted_topics": {},
            "consolidated_topics": {},
            "topic_mapping": {},
            "daily_frequencies": {},
            "trend_analysis": {},
            "processing_status": "started",
            "errors": [],
            "current_step": "init"
        }

        with st.spinner("Running workflow..."):
            result = asyncio.run(workflow.ainvoke(state))

        st.success("✅ Workflow completed!")
        
        st.subheader("Processing Status")
        st.json(result.get("processing_status", ""))

        if result.get("errors"):
            st.error(result["errors"])

        st.subheader("Trend Analysis")
        st.json(result.get("trend_analysis", {}))