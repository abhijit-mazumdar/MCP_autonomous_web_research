# MCP Autonomous Web Research Agent Server

## Project Overview

The MCP Autonomous Web Research Agent Server is an intelligent, autonomous platform designed to perform advanced web scraping, research, and content analysis. It leverages adaptive scraping techniques, local LLM integration, and robust validation mechanisms to deliver reliable, real-time research results with full citation management and monitoring.

---

## Core Functionality
- **Intelligent web scraping** with anti-detection and adaptive strategies
- **Autonomous research planning and execution** using local LLMs
- **Content validation and fact-checking** for accuracy and reliability
- **Citation management and source verification**
- **Real-time monitoring and alerts** for research progress and site changes

---

## Key Features
- Adaptive web scraping with anti-detection (headless browsers, proxy rotation)
- Content validation and fact-checking using LLMs
- LLM-driven research planning and task decomposition
- Citation management with source reliability scoring
- Real-time monitoring and alerting system

---

## Tech Stack
- **Python 3.10+**
- **Web Scraping:** selenium, playwright, scrapy, beautifulsoup4, newspaper3k, requests-html, aiohttp
- **API Server:** FastAPI
- **Database:** SQLite (dev), Postgres (prod)
- **LLM Integration:** Ollama (local server) with Code Llama (scraping logic) and Llama 3.2 (content analysis)
- **Task Queue:** Celery or asyncio
- **Notifications:** Email, Websockets, or Slack API

---

## System Architecture

```
graph TD
    Client[User/Client] -->|API/Web UI| MCPServer
    MCPServer -->|Task Queue| ScraperEngine
    MCPServer -->|LLM API| OllamaLLM
    ScraperEngine -->|Scraping| TargetWebsites
    ScraperEngine -->|Content| ContentValidator
    ContentValidator -->|Fact-Check| OllamaLLM
    MCPServer -->|DB| CitationManager
    MCPServer -->|Alerts| NotificationSystem
```

---

## Development Phases
1. **Project Setup:** Scaffold FastAPI server and endpoints
2. **Scraper Engine:** Adaptive, modular scraping with anti-detection
3. **Research & Planning:** LLM-driven research task planning
4. **Content Validation:** Fact-checking and cross-referencing
5. **Citation Management:** Database and citation formatting
6. **Monitoring & Alerts:** Real-time job and site monitoring
7. **Testing & Hardening:** Anti-detection, security, and testing

---

## Directory Structure (Suggested)

```
MCPAgent/
│
├── app/
│   ├── main.py            # FastAPI entrypoint
│   ├── scraper/
│   │   ├── engine.py
│   │   ├── adapters/
│   │   └── utils.py
│   ├── llm/
│   │   └── ollama_client.py
│   ├── research/
│   │   ├── planner.py
│   │   └── validator.py
│   ├── citations/
│   │   └── manager.py
│   ├── notifications/
│   │   └── alerts.py
│   └── db/
│       └── models.py
│
├── tests/
├── requirements.txt
└── README.md
```

---

## Streamlit Frontend

A modern Streamlit-based frontend is included for easy interaction with the MCPAgent server.

### Features
- Create a research task (submit a query)
- View all research tasks in a table and detailed expandable sections
- Update the status and result of any research task
- Analyze any content using Llama 3.2
- Health check sidebar for backend status

### How to Run
1. Make sure the FastAPI backend is running (`uvicorn app.main:app --reload`)
2. In a new terminal, activate your venv and run:
   ```sh
   streamlit run streamlit_app.py
   ```
3. Open [http://localhost:8501](http://localhost:8501) in your browser

---

## Model Context Protocol (MCP) Integration

The MCPAgent project now includes full Model Context Protocol (MCP) server functionality, allowing AI assistants to discover and use research tools programmatically.

### MCP Server Features

The MCP server exposes the following tools to AI assistants:

- **`create_research_task`** - Create a new research task with a query
- **`list_research_tasks`** - List all existing research tasks
- **`update_research_task`** - Update the status or result of a research task
- **`analyze_content`** - Analyze content using Llama 3.2

### How to Use with AI Assistants

1. **Configure MCP Client**: Add the `mcp_config.json` to your AI assistant's MCP configuration
2. **Connect to Server**: The AI assistant will automatically discover and connect to the MCP server
3. **Use Research Tools**: AI assistants can now create research tasks, list results, and analyze content

### Running the MCP Server

```sh
python app/mcp_server.py
```

The MCP server runs independently of the FastAPI backend and Streamlit frontend, providing a standardized interface for AI assistants to interact with your research capabilities.

---

## Example Usage

- Submit a research query and see the LLM-generated scraping strategy
- View and update research task results in a user-friendly UI
- Analyze any text content for accuracy and key points using Llama 3.2

---
