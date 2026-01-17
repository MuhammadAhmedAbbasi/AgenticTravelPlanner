# ✈️ Agentic Trip Planner

**Agentic Trip Planner** is an intelligent, AI-powered travel assistant designed to take the stress out of trip planning. Unlike standard chatbots, this system uses a **multi-agent architecture** to actively research, reason, and build comprehensive travel itineraries based on your specific needs.

The system operates in two distinct phases:
1.  **Information Gathering:** An intelligent agent converses with you to understand your travel preferences—budget, destination, dates, and interests—asking clarifying questions until it has a complete picture.
2.  **Autonomous Planning:** Once all details are collected, the system switches to a planning agent that orchestrates various tools (flight search, distance calculation, web search) to build your final itinerary, providing real-time updates on its progress.

---

## 🛠️ Tech Stack

This project leverages modern AI engineering practices and robust Python frameworks:

* **Core Logic:** Python 3.10+
* **LLM Orchestration:** [LangChain](https://www.langchain.com/) & [LangGraph](https://langchain-ai.github.io/langgraph/) for stateful agent workflows.
* **AI Models:** Google Gemini (Flash & Pro models) for reasoning and generation.
* **API Interface:** WebSockets (via `websockets` library) for bi-directional, real-time communication.
* **Frontend:** [Streamlit](https://streamlit.io/) for an interactive, chat-based user interface.
* **Configuration:** Pydantic Settings and DotEnv for secure environment management.
* **Logging:** Custom `RotatingFileHandler` implementation for robust error tracking and debugging.

---

## 📂 Project Structure

```text
AgenticTravelPlanner/
├── main.py                     # Entry point for the WebSocket Backend Server
├── .env                        # Environment variables (API Keys & Secrets)
├── src/
│   ├── agents/                 # LangGraph Agent logic & definitions
│   │   ├── info_gather_agent.py        # Agent responsible for collecting user details
│   │   └── final_trip_planner_agent.py # Agent responsible for generating the itinerary
│   ├── api_manager/            # WebSocket connection handlers
│   ├── config/                 # Pydantic settings & configuration management
│   ├── database/               # Local storage/memory for conversation persistence
│   ├── frontend/               # Streamlit application (UI)
│   ├── logging/                # Custom logging configuration
│   ├── prompts/                # System prompts defining Agent behaviors
│   ├── tools/                  # Custom tools (Flight Search, Distance, Web Search)
│   └── utils/                  # Helper classes, validators, and data models

Prerequisites
Before you begin, ensure you have the following installed:

Python 3.10 or higher.

pip (Python Package Installer).

Required API Keys
To unlock the full capabilities of the agents, you will need the following API keys:

    1. Google Gemini API Key: For the core LLM logic (Get it from Google AI Studio).

    2. Tavily API Key: For optimized AI web search.

    3. Google Places API Key: For location data and attraction details.

    4. SerpAPI Key: (Optional) For additional search capabilities.

Installation & Setup
Follow these steps to set up the project locally.

1. Clone the Repository
git clone [https://github.com/your-username/AgenticTravelPlanner.git](https://github.com/your-username/AgenticTravelPlanner.git)
cd AgenticTravelPlanner

Create a Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

Install Dependencies
    pip install -r requirements.txt


Configure Environment Variables
Create a file named .env in the root directory of the project. You can use the provided .env Template as a reference. Add your API keys and configuration settings:

            # .env file

            # API Keys
            GOOGLE_API_KEY=your_gemini_api_key_here
            TAVILY_API_KEY=your_tavily_api_key_here
            GOOGLE_PLACES_KEY=your_google_places_key_here
            SERPAPI_KEY=your_serpapi_key_here

            # Model Configuration
            FLASH_MODEL=gemini-2.5-flash
            PRO_MODEL=gemini-3-pro-preview

            # Application Settings
            LOG_LEVEL=INFO
            ENVIRONMENT=development


The system requires two separate processes running simultaneously: the Backend Server (which handles the AI logic) and the Frontend Interface (which you interact with).

Step 1: Start the Backend Server
Open your terminal (with the virtual environment activated) and run the main entry point. This starts the WebSocket server.
    python main.py

Step 2: Launch the Frontend
Open a new terminal window (activate the virtual environment here as well) and launch the Streamlit app.
    streamlit run src/frontend/app.py