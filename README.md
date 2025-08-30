# Secure Agent Scheduler

A secure multi-agent system for scheduling and notifications, built for the Descope Global MCP Hackathon. It uses a Planner Agent to create calendar events from natural language and a Notifier Agent to send reminders, with all agent-to-agent communication secured by Descope.

## Team
- **Team Name:** [YOUR TEAM NAME]
- **Team Members:** [LIST OF TEAM MEMBERS]

## Hackathon Submission
- **Theme:** Theme 3: Secure Agent-to-Agent Communication
- **Challenge:** Scheduling and Notification Flow

## Demo
**Demo Video Link:** [Link to your 5-minute demo video]

## What We Built
Our project is a multi-agent system that securely handles scheduling tasks based on natural language input.

- **Planner Agent**: Parses user requests (e.g., "schedule a meeting with John tomorrow at 2pm") to extract intent and entities, then creates a structured calendar event.
- **Notifier Agent**: Listens for newly created events and sends a notification to the relevant user, confirming the action.
- **Secure API**: A FastAPI backend exposes a `/api/schedule` endpoint to receive user requests.
- **Agent-to-Agent Security**: Communication between the Planner and Notifier agents is secured using JWTs issued by **Descope**. Each agent is configured with specific OAuth scopes (`calendar.write`, `messaging.send`) to enforce the principle of least privilege.
- **Audit Trail**: All significant agent actions and decisions are logged for full traceability via the `/api/audit` endpoint.

## Tech Stack
- **Backend**: Python, FastAPI
- **Agent Framework**: LangChain, LangGraph
- **Authentication & Authorization**: Descope (for OAuth 2.0 token generation and validation)
- **Core Libraries**: Pydantic, Uvicorn, python-dotenv, python-jose

## How to Run It

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd secure-agent-scheduler
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the root directory and add your Descope credentials. You can find these in your Descope project settings.
    ```env
    DESCOPE_PROJECT_ID="your_descope_project_id"
    DESCOPE_MANAGEMENT_KEY="your_descope_management_key"
    ```

4.  **Run the application:**
    ```bash
    uvicorn src.main:app --reload
    ```
    The API will be available at `http://localhost:8000`.

5.  **Use the API:**
    Send a POST request to `http://localhost:8000/api/schedule` with a JSON body like this:
    ```json
    {
      "user_request": "Schedule a team meeting for tomorrow at 10am to review the Q3 report.",
      "user_id": "user-123"
    }
    ```
    You can view the interactive API documentation at `http://localhost:8000/api/docs`.

## What We'd Do With More Time
- **Expand Notification Channels**: Integrate with services like Slack, Twilio (for SMS), or email to provide more notification options.
- **Stateful Conversations**: Implement a conversational agent that can ask clarifying questions (e.g., "For how long should the meeting be?").
- **Frontend UI**: Build a simple web interface for users to interact with the scheduler directly in a browser.
- **Advanced Scheduling Logic**: Add support for recurring events, time zone handling, and checking calendar availability before booking.
- **User Consent Flow**: Implement a Descope Flow to get explicit, granular user consent before the Notifier agent sends messages on their behalf.