# LangGraph Chatbot

A simple chat application built with **LangGraph**, **LangChain (Groq)**, and **Streamlit**, with persistent conversation history stored in SQLite and live web search via DuckDuckGo.

## Features

- Streaming chat responses powered by Groq's `qwen/qwen3-32b` model
- Tool calling: web search (DuckDuckGo) and URL content fetching
- Conversation persistence across sessions using SQLite checkpoints
- Multiple chat threads with the ability to switch between past conversations
- Clean, dark-themed custom UI

## Project Structure

```
.
├── app.py              # Streamlit frontend
├── workflow.py         # LangGraph backend (graph, model, tools, checkpointer)
├── requirements.txt
├── .env                # Environment variables (not committed)
└── chatbot.db          # SQLite database (auto-created on first run)
```

## Setup

### 1. Clone the repository and create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

- `GROQ_API_KEY` is required to use the Groq-hosted `qwen/qwen3-32b` model (free tier available at console.groq.com).
- The `search` tool uses **DuckDuckGo Search** (via `langchain_community.tools.DuckDuckGoSearchRun`), which is free and requires no API key.

### 4. Run the app

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`.

## Usage

- Type a message in the input box at the bottom and press Enter to chat.
- Click **＋ New** to start a fresh conversation thread.
- Open **Conversation history** to view and switch between previous threads — your messages are persisted in `chatbot.db` and reloaded automatically.
- Ask about current events, recent news, or specific URLs to trigger the `search` and `fetch_url_content` tools.

## Notes

- The first run will create a `chatbot.db` SQLite file in the project root, used by `SqliteSaver` to checkpoint conversation state per thread.
- The model is configured with a system prompt that instructs it to use the `search` tool for time-sensitive questions (current events, scores, news, prices, etc.) rather than relying on its training data, and `fetch_url_content` to read specific pages.
- `fetch_url_content` truncates page text to the first 1000 characters to keep responses manageable — increase this in `workflow.py` if you need more content from a page.
- DuckDuckGo's search is an unofficial scraping-based API and may occasionally rate-limit under heavy use.
- If you see `groq.APIError: Failed to call a function`, it usually means the model attempted a malformed tool call. Try rephrasing the prompt, or switch the model in `workflow.py` (e.g., `openai/gpt-oss-120b`) if it persists.
