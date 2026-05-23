from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
import os
import re
import difflib

app = FastAPI()

# =========================
# MEMORY FILE
# =========================

FACT_MEMORY_FILE = "fact_memory.json"

# =========================
# LOAD MEMORY
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
# UNIVERSAL FACT EXTRACTOR
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
# MEMORY SEARCH
# =========================

def memory_response(prompt):

    global fact_memory

    text = prompt.lower()

    memory_triggers = [

        "what is my",
        "tell me my",
        "who is my",
        "which is my",
        "what's my"
    ]

    is_memory_question = any(
        trigger in text
        for trigger in memory_triggers
    )

    if not is_memory_question:

        return None

    cleaned = (
        text.replace("what is", "")
        .replace("tell me", "")
        .replace("what's", "")
        .replace("which", "")
        .replace("who", "")
        .replace("my", "")
        .replace("the", "")
        .replace("name of", "")
        .replace("?", "")
        .replace("makes", "")
        .replace("brand", "")
        .replace("company", "")
        .replace("called", "")
        .strip()
    )

    cleaned = cleaned.replace(" ", "_")

    best_match = None
    best_score = 0

    for key in fact_memory.keys():

        similarity = difflib.SequenceMatcher(
            None,
            cleaned,
            key
        ).ratio()

        if similarity > best_score:

            best_score = similarity
            best_match = key

    if best_match and best_score > 0.65:

        value = fact_memory[best_match]

        readable_key = best_match.replace("_", " ")

        return f"Your {readable_key} is {value}."

    return None

# =========================
# INTENT DETECTION
# =========================

def detect_intent(prompt):

    text = prompt.lower()

    if (
        "python" in text
        or "javascript" in text
        or "code" in text
        or "api" in text
        or "backend" in text
    ):

        return "coding"

    elif (
        "startup" in text
        or "business" in text
        or "strategy" in text
        or "investor" in text
        or "saas" in text
    ):

        return "startup"

    elif (
        "linkedin" in text
        or "marketing" in text
        or "content" in text
        or "instagram" in text
    ):

        return "marketing"

    return "general"

# =========================
# MODEL ROUTER
# =========================

def select_model(intent):

    if intent == "coding":

        return "deepseek-coder:1.3b"

    elif intent == "marketing":

        return "tinyllama"

    elif intent == "general":

        return "tinyllama"

    return "phi3"

# =========================
# SYSTEM PROMPTS
# =========================

def get_system_prompt(intent):

    base_prompt = """
Respond clearly and practically.

Rules:
- avoid fluff
- avoid philosophy
- avoid fake narratives
- avoid overexplaining
"""

    prompts = {

        "coding": """
Think like a senior software engineer.
Focus on:
- architecture
- clean code
- optimization
""",

        "startup": """
Think like a startup strategist.
Focus on:
- growth
- execution
- scalability
""",

        "marketing": """
Think like a growth marketer.
Focus on:
- hooks
- persuasion
- engagement
"""
    }

    return base_prompt + prompts.get(intent, "")

# =========================
# HOME
# =========================

@app.get("/")
def home():

    return {
        "status": "running",
        "memory_items": len(fact_memory)
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

    # MEMORY EXTRACTION
    extract_memory(prompt)

    # MEMORY SEARCH
    memory_answer = memory_response(prompt)

    if memory_answer:

        return {
            "response": memory_answer,
            "source": "memory"
        }

    # INTENT
    intent = detect_intent(prompt)

    # MODEL ROUTING
    model = select_model(intent)

    # SYSTEM PROMPT
    system_prompt = get_system_prompt(intent)

    # MODEL RESPONSE
    response = requests.post(

        "http://localhost:11434/api/generate",

        json={

            "model": model,

            "prompt": f"""

SYSTEM:
{system_prompt}

USER:
{prompt}

ASSISTANT:
""",

            "stream": False,

            "options": {

                "temperature": 0.2,
                "top_p": 0.8,
                "num_predict": 120,
                "repeat_penalty": 1.05,
                "num_ctx": 256,
                "num_thread": 4
            }
        },

        timeout=120
    )

    result = response.json()["response"].strip()

    return {
        "response": result,
        "intent": intent,
        "model_used": model
    }