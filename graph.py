# graph.py

from dotenv import load_dotenv
import os
load_dotenv()

from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from sqlalchemy import text
from database import engine
from models import AgentState
from prompts import INTENT_PROMPT, SQL_GENERATION_PROMPT


# =============================
# Groq LLM Configuration
# =============================
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)


# =============================
# 1️⃣ Intent Node
# =============================
def intent_node(state: AgentState):

    prompt = INTENT_PROMPT.format(
        input=state["user_input"]
    )

    response = llm.invoke(prompt)

    state["intent"] = response.content.strip().lower()

    return state


# =============================
# 2️⃣ SQL Generator Node
# =============================
def sql_generator_node(state: AgentState):

    prompt = SQL_GENERATION_PROMPT.format(
        input=state["user_input"]
    )

    response = llm.invoke(prompt)

    state["sql_query"] = response.content.strip()

    return state


# =============================
# 3️⃣ SQL Executor Node
# =============================
def execute_sql_node(state: AgentState):

    try:
        with engine.connect() as connection:
            result = connection.execute(text(state["sql_query"]))
            rows = result.fetchall()

            if rows:
                state["result"] = str(rows)
            else:
                state["result"] = "No matching records found."

            state["error"] = None

    except Exception as e:
        state["error"] = str(e)

    return state


# =============================
# 4️⃣ SQL Correction Node
# =============================
def sql_correction_node(state: AgentState):

    correction_prompt = f"""
    The following SQL query caused this error:

    ERROR:
    {state['error']}

    SQL:
    {state['sql_query']}

    Fix the SQL query.
    Return ONLY the corrected SQL.
    """

    response = llm.invoke(correction_prompt)

    state["sql_query"] = response.content.strip()

    return state


# =============================
# 5️⃣ Responder Node
# =============================
def responder_node(state: AgentState):

    # Greeting case
    if state["intent"] == "greeting":
        state["result"] = "Hello 👋 How can I help you with inventory today?"
        return state

    response_prompt = f"""
    You are an enterprise inventory assistant.

    The user asked:
    "{state['user_input']}"

    The SQL result returned:
    {state['result']}

    Instructions:
    - Respond professionally and clearly.
    - If the result is a count, state it naturally.
    - If it is a list, format it clearly using bullet points.
    - Always mention that only Active records are included unless specified.
    - If no records were found, clearly say so.

    Provide a concise but professional response.
    """

    response = llm.invoke(response_prompt)

    state["result"] = response.content.strip()

    return state


# =============================
# Build LangGraph
# =============================
builder = StateGraph(AgentState)

builder.add_node("intent", intent_node)
builder.add_node("generate_sql", sql_generator_node)
builder.add_node("execute_sql", execute_sql_node)
builder.add_node("correct_sql", sql_correction_node)
builder.add_node("respond", responder_node)

builder.set_entry_point("intent")

# Greeting → respond
builder.add_conditional_edges(
    "intent",
    lambda state: "respond" if state["intent"] == "greeting" else "generate_sql"
)

builder.add_edge("generate_sql", "execute_sql")

# If execution fails → correct → retry
builder.add_conditional_edges(
    "execute_sql",
    lambda state: "correct_sql" if state["error"] else "respond"
)

builder.add_edge("correct_sql", "execute_sql")

builder.add_edge("respond", END)

app = builder.compile()