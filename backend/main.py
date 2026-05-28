from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
import os
import re
from dotenv import load_dotenv
from datetime import datetime

# =========================
# LOAD ENV
# =========================

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# =========================
# FASTAPI
# =========================

app = FastAPI()

# =========================
# MEMORY FILES
# =========================

FACT_MEMORY_FILE = "fact_memory.json"
CONTEXT_MEMORY_FILE = "context_memory.json"

# =========================
# LOAD FACT MEMORY
# =========================

if os.path.exists(FACT_MEMORY_FILE):

    with open(FACT_MEMORY_FILE, "r", encoding="utf-8") as f:

        try:
            fact_memory = json.load(f)
        except:
            fact_memory = {}

else:
    fact_memory = {}

# =========================
# LOAD CONTEXT MEMORY
# =========================

if os.path.exists(CONTEXT_MEMORY_FILE):

    with open(CONTEXT_MEMORY_FILE, "r", encoding="utf-8") as f:

        try:
            context_memory = json.load(f)
        except:
            context_memory = []

else:
    context_memory = []

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# REQUEST MODEL
# =========================

class PromptRequest(BaseModel):
    prompt: str

# =========================
# SAVE CONTEXT
# =========================

def save_context(user_prompt, assistant_response):

    global context_memory

    item = {
        "timestamp": str(datetime.now()),
        "user": user_prompt,
        "assistant": assistant_response
    }

    context_memory.append(item)

    context_memory = context_memory[-5:]

    with open(CONTEXT_MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(context_memory, f, indent=2)

# =========================
# GET CONTEXT
# =========================

def get_recent_context():

    if not context_memory:
        return ""

    recent_items = context_memory[-2:]

    text = ""

    for item in recent_items:

        text += f"""

User:
{item['user']}

Assistant:
{item['assistant']}
"""

    return text

# =========================
# MEMORY EXTRACTION
# =========================

def extract_memory(prompt):

    global fact_memory

    text = prompt.lower().strip()

    patterns = [
        r"my (.+?) is (.+)",
        r"my (.+?) brand is (.+)"
    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:

            key = match.group(1).strip().replace(" ", "_")
            value = match.group(2).strip().title()

            fact_memory[key] = value

    with open(FACT_MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(fact_memory, f, indent=2)

# =========================
# MEMORY RESPONSE
# =========================

def memory_response(prompt):

    text = prompt.lower()

    if "car" in text and "brand" in text:
        if "car_brand" in fact_memory:
            return f"Your car brand is {fact_memory['car_brand']}."

    if "fan" in text and "brand" in text:
        if "fan_brand" in fact_memory:
            return f"Your fan brand is {fact_memory['fan_brand']}."

    if "startup" in text:
        if "startup" in fact_memory:
            return f"Your startup is {fact_memory['startup']}."

    return None

# =========================
# DUCK SEARCH
# =========================

def duck_search(query):

    try:

        url = "https://api.duckduckgo.com/"

        params = {
            "q": query,
            "format": "json",
            "no_html": 1
        }

        response = requests.get(
            url,
            params=params,
            timeout=8
        )

        data = response.json()

        abstract = data.get("AbstractText")

        if abstract:
            return abstract[:200]

        return "No results found."

    except Exception as e:

        return f"Duck Error: {str(e)}"

# =========================
# SERPER SEARCH
# =========================

def serper_search(query):

    try:

        url = "https://google.serper.dev/search"

        payload = json.dumps({
            "q": query
        })

        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }

        response = requests.post(
            url,
            headers=headers,
            data=payload,
            timeout=10
        )

        if response.status_code != 200:
            return f"Serper API Error: {response.status_code}"

        data = response.json()

        organic = data.get("organic", [])

        if not organic:
            return "No live results found."

        top = organic[0]

        title = top.get("title", "No title")
        snippet = top.get("snippet", "No summary")

        snippet = snippet[:120]

        return f"{title}\n\n{snippet}"

    except requests.exceptions.Timeout:

        return "Live search timed out."

    except Exception as e:

        return f"Search system error: {str(e)}"

# =========================
# PLANNER
# =========================

def planner_engine(prompt):

    planner_prompt = f"""

Classify request briefly.

USER:
{prompt}
"""

    try:

        response = requests.post(

            "http://localhost:11434/api/generate",

            json={
                "model": "tinyllama",
                "prompt": planner_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 15
                }
            },

            timeout=15
        )

        return response.json()["response"].strip()

    except:
        return "planner_failed"

# =========================
# MODEL ROUTER
# =========================

def route_model(prompt):

    text = prompt.lower()

    coding_keywords = [
        "code",
        "python",
        "fastapi",
        "javascript",
        "react",
        "api",
        "backend"
    ]

    if any(word in text for word in coding_keywords):
        return "deepseek-coder:1.3b"

    return "phi3"

# =========================
# RETRIEVAL DETECTOR
# =========================

def needs_retrieval(prompt):

    text = prompt.lower()

    retrieval_keywords = [
        "latest",
        "today",
        "news",
        "price",
        "stock",
        "share",
        "recent"
    ]

    return any(word in text for word in retrieval_keywords)

# =========================
# HOME
# =========================

@app.get("/")
def home():

    return {
        "status": "running",
        "memory_items": len(fact_memory),
        "context_items": len(context_memory)
    }

# =========================
# MAIN ROUTE
# =========================

@app.post("/optimize")
def optimize(data: PromptRequest):

    prompt = data.prompt.strip()

    if not prompt:
        return {
            "response": "Please enter a prompt."
        }

    # =========================
    # PLANNER
    # =========================

    planner_engine(prompt)

    # =========================
    # MEMORY
    # =========================

    extract_memory(prompt)

    memory_answer = memory_response(prompt)

    if memory_answer:

        save_context(prompt, memory_answer)

        return {
            "response": memory_answer,
            "source": "memory"
        }

    # =========================
    # LIVE RETRIEVAL
    # =========================

    if needs_retrieval(prompt):

        live_result = serper_search(prompt)

        save_context(prompt, live_result)

        return {
            "response": live_result,
            "source": "live_retrieval",
            "model_used": "serper"
        }

    # =========================
    # CONTEXT
    # =========================

    recent_context = get_recent_context()

    short_context = recent_context[:300]

    # =========================
    # MODEL ROUTING
    # =========================

    selected_model = route_model(prompt)

    # =========================
    # FINAL PROMPT
    # =========================

    final_prompt = f"""

You are Dynexa AI.

You are practical, concise and helpful.

Never say:
- you are DeepSeek
- you are Phi3
- you are TinyLlama
- you are trained only for coding

RECENT CONTEXT:
{short_context}

USER:
{prompt}

ASSISTANT:
"""

    response = requests.post(

        "http://localhost:11434/api/generate",

        json={
            "model": selected_model,
            "prompt": final_prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 40
            }
        },

        timeout=60
    )

    result = response.json()["response"].strip()

    save_context(prompt, result)

    return {
        "response": result,
        "model_used": selected_model
    }