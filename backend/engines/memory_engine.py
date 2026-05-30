import json
import os
import re
from datetime import datetime

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

    for key, value in fact_memory.items():

        readable_key = key.replace("_", " ")

        if readable_key in text:

            return f"Your {readable_key} is {value}."

    return None