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

    context_entry = {

        "timestamp": str(datetime.now()),

        "user": user_prompt,

        "assistant": assistant_response
    }

    context_memory.append(context_entry)

    # KEEP LAST 20 CONVERSATIONS

    context_memory = context_memory[-20:]

    with open(CONTEXT_MEMORY_FILE, "w", encoding="utf-8") as f:

        json.dump(context_memory, f, indent=2)

# =========================
# GET RECENT CONTEXT
# =========================

def get_recent_context():

    if not context_memory:

        return ""

    recent_items = context_memory[-5:]

    context_text = ""

    for item in recent_items:

        context_text += f"""

User:
{item['user']}

Assistant:
{item['assistant']}

"""

    return context_text

# =========================
# CALCULATOR TOOL
# =========================

def calculator_tool(prompt):

    try:

        expression = re.findall(
            r'[\d\.\+\-\*\/\(\) ]+',
            prompt
        )[0]

        result = eval(expression)

        return f"Calculation result: {result}"

    except:

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
            "no_redirect": 1,
            "no_html": 1
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        data = response.json()

        abstract = data.get("AbstractText")

        if abstract:

            return abstract

        related = data.get("RelatedTopics")

        if related:

            for item in related:

                if isinstance(item, dict):

                    text = item.get("Text")

                    if text:

                        return text

        return "No results found."

    except Exception as e:

        return f"Search failed: {str(e)}"

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
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }

        response = requests.post(
            url,
            headers=headers,
            data=payload,
            timeout=20
        )

        data = response.json()

        organic = data.get("organic", [])

        if organic:

            results = []

            for item in organic[:5]:

                title = item.get("title", "")
                snippet = item.get("snippet", "")

                results.append(
                    f"{title}\n{snippet}"
                )

            return "\n\n".join(results)

        return "No internet results found."

    except Exception as e:

        return f"Serper search failed: {str(e)}"

# =========================
# RETRIEVAL ROUTER
# =========================

def retrieval_router(prompt):

    text = prompt.lower()

    live_keywords = [

        "latest",
        "today",
        "news",
        "price",
        "stock",
        "recent",
        "current",
        "update"
    ]

    if any(keyword in text for keyword in live_keywords):

        return "serper"

    return "duck"

# =========================
# SYNTHESIS ENGINE
# =========================

def synthesize_response(user_prompt, retrieved_context):

    recent_context = get_recent_context()

    synthesis_prompt = f"""

You are Dynexa.

Your job:
- answer directly
- use recent conversation context if relevant
- avoid clutter
- summarize clearly
- be concise

RECENT CONTEXT:
{recent_context}

USER QUESTION:
{user_prompt}

RETRIEVED CONTEXT:
{retrieved_context}

FINAL ANSWER:
"""

    response = requests.post(

        "http://localhost:11434/api/generate",

        json={

            "model": "phi3",

            "prompt": synthesis_prompt,

            "stream": False,

            "options": {

                "temperature": 0.2,

                "num_predict": 150,

                "top_p": 0.8
            }
        },

        timeout=120
    )

    return response.json()["response"].strip()

# =========================
# TOOL ROUTER
# =========================

def tool_router(prompt):

    text = prompt.lower()

    math_symbols = [
        "+",
        "-",
        "*",
        "/"
    ]

    if any(symbol in text for symbol in math_symbols):

        return "calculator"

    if "calculate" in text:

        return "calculator"

    retrieval_keywords = [

        "latest",
        "today",
        "news",
        "price",
        "stock",
        "current",
        "recent",
        "update",
        "search"
    ]

    if any(keyword in text for keyword in retrieval_keywords):

        return "retrieval"

    return None

# =========================
# MEMORY EXTRACTION
# =========================

def extract_memory(prompt):

    global fact_memory

    text = prompt.lower().strip()

    patterns = [

        r"my (.+?) is (.+)",
        r"the (.+?) of my (.+?) is (.+)"
    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:

            try:

                if len(match.groups()) == 2:

                    key = match.group(1).strip()
                    value = match.group(2).strip()

                    key = key.replace(" ", "_")

                    fact_memory[key] = value.title()

                elif len(match.groups()) == 3:

                    attribute = match.group(1).strip()
                    subject = match.group(2).strip()
                    value = match.group(3).strip()

                    key = f"{subject}_{attribute}"

                    key = key.replace(" ", "_")

                    fact_memory[key] = value.title()

            except:
                pass

    with open(FACT_MEMORY_FILE, "w", encoding="utf-8") as f:

        json.dump(fact_memory, f, indent=2)

# =========================
# MEMORY RESPONSE
# =========================

def memory_response(prompt):

    text = prompt.lower()

    if "startup" in text:

        if "startup" in fact_memory:

            return f"Your startup is {fact_memory['startup']}."

    if "car" in text:

        if "car_brand" in fact_memory:

            return f"Your car brand is {fact_memory['car_brand']}."

    return None

# =========================
# HOME
# =========================

@app.get("/")
def home():

    return {

        "status": "running",

        "fact_memory_items": len(fact_memory),

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
    # TOOL ROUTING
    # =========================

    tool = tool_router(prompt)

    # CALCULATOR

    if tool == "calculator":

        result = calculator_tool(prompt)

        save_context(prompt, result)

        return {
            "response": result,
            "tool_used": "calculator"
        }

    # RETRIEVAL

    if tool == "retrieval":

        retrieval_source = retrieval_router(prompt)

        if retrieval_source == "serper":

            retrieved_context = serper_search(prompt)

        else:

            retrieved_context = duck_search(prompt)

        final_answer = synthesize_response(
            prompt,
            retrieved_context
        )

        save_context(prompt, final_answer)

        return {

            "response": final_answer,

            "retrieval_source": retrieval_source
        }

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
    # CONTEXT-AWARE RESPONSE
    # =========================

    recent_context = get_recent_context()

    final_prompt = f"""

You are Dynexa.

Use recent conversation context if relevant.

RECENT CONTEXT:
{recent_context}

USER:
{prompt}

ASSISTANT:
"""

    response = requests.post(

        "http://localhost:11434/api/generate",

        json={

            "model": "phi3",

            "prompt": final_prompt,

            "stream": False,

            "options": {

                "temperature": 0.2,

                "num_predict": 150
            }
        },

        timeout=120
    )

    result = response.json()["response"].strip()

    save_context(prompt, result)

    return {

        "response": result
    }