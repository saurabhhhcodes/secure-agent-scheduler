import streamlit as st
import requests

# Configuration
FASTAPI_BASE_URL = "http://localhost:8000"
SCHEDULE_ENDPOINT = f"{FASTAPI_BASE_URL}/api/schedule"

st.set_page_config(page_title="Secure Agent Scheduler", layout="centered")

st.title("Secure Agent Scheduler")
st.markdown("### Schedule tasks and get notifications securely.")

st.write("--- ")

# Input fields
user_request = st.text_area("Your Request:", "Schedule a team meeting for tomorrow at 10am to review the Q3 report.", height=100)
user_id = st.text_input("Your User ID:", "user-123")

if st.button("Schedule Task"):
    if user_request and user_id:
        payload = {
            "user_request": user_request,
            "user_id": user_id
        }
        
        st.info("Sending request to Planner Agent...")
        
        try:
            response = requests.post(SCHEDULE_ENDPOINT, json=payload)
            
            if response.status_code == 200:
                st.success("Task Scheduled Successfully!")
                st.json(response.json())
            else:
                st.error(f"Error scheduling task: {response.status_code}")
                st.json(response.json())
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the FastAPI backend. Please ensure your FastAPI server is running at http://localhost:8000.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
    else:
        st.warning("Please provide both a request and a user ID.")

st.write("--- ")
st.markdown("**Note:** Ensure your FastAPI backend is running (`uvicorn src.main:app --reload`) before using this application.")
