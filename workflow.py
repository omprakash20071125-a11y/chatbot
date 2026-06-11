from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from typing import TypedDict, Annotated
from tavily import TavilyClient
import requests
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langgraph.prebuilt import ToolNode, tools_condition
from bs4 import BeautifulSoup
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
import sqlite3
from datetime import date
from dotenv import load_dotenv

load_dotenv()

conn = sqlite3.connect("chatbot.db", check_same_thread=False)
checkpoint = SqliteSaver(conn=conn)


# ── Tools ─────────────────────────────────────────────────────────────────
@tool
def search(query: str) -> str:
    """Tool used to search the web and find relevant information."""
    wrapper = DuckDuckGoSearchRun()
    response = wrapper.run(query)
    return response


@tool
def fetch_url_content(url: str) -> str:
    """Fetch the text content of a web page given its URL."""
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text(separator="\n")[:1000]


tools = [search, fetch_url_content]

model = ChatGroq(model="qwen/qwen3-32b")
model_with_tools = model.bind_tools(tools)


# ── State ─────────────────────────────────────────────────────────────────
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# ── Graph nodes ──────────────────────────────────────────────────────────
SYSTEM_PROMPT = SystemMessage(content=(
    f"You are a helpful assistant. Today's date is {date.today().isoformat()}. "
    "Your training data has a knowledge cutoff and may be outdated. "
    "For ANY question about current events, recent news, sports results, scores, "
    "prices, or anything that may have changed or occurred after your training "
    "cutoff, you MUST use the `search` tool to find up-to-date information before "
    "answering. Do not say you don't have information or rely on your training "
    "knowledge for time-sensitive questions — always search first. Use "
    "`fetch_url_content` if you need to read the full content of a specific page."
))


def chat_node(state: State) -> State:
    messages = [SYSTEM_PROMPT] + state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}


tool_node = ToolNode(tools)

# ── Build graph ──────────────────────────────────────────────────────────
graph = StateGraph(State)

graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

workflow = graph.compile(checkpointer=checkpoint)


# ── Helpers ──────────────────────────────────────────────────────────────
def retrive_all_thread(checkpoint):
    """Return a list of all distinct thread IDs that have checkpoints saved."""
    thread_id_set = set()
    for chp in checkpoint.list(None):
        thread_id_set.add(chp.config["configurable"]["thread_id"])
    return list(thread_id_set)