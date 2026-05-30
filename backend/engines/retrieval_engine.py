import requests
import json
import os

from dotenv import load_dotenv
from duckduckgo_search import DDGS

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

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
        "recent",
        "current",
        "update"
    ]

    return any(word in text for word in retrieval_keywords)

# =========================
# DUCK SEARCH
# =========================

def duckduckgo_search(query):

    try:

        with DDGS() as ddgs:

            results = list(

                ddgs.text(
                    query,
                    max_results=3
                )
            )

        if not results:

            return None

        top = results[0]

        title = top.get("title", "")
        body = top.get("body", "")

        return f"{title}\n\n{body}"

    except Exception as e:

        return f"DuckDuckGo Error: {str(e)}"

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

            return None

        data = response.json()

        organic = data.get("organic", [])

        if not organic:

            return None

        top = organic[0]

        title = top.get("title", "")
        snippet = top.get("snippet", "")

        return f"{title}\n\n{snippet}"

    except:
        return None

# =========================
# HYBRID RETRIEVAL
# =========================

def hybrid_search(query):

    # =========================
    # LIVE / FINANCIAL / NEWS
    # =========================

    live_keywords = [

        "latest",
        "today",
        "news",
        "stock",
        "share",
        "price",
        "current"
    ]

    text = query.lower()

    # =========================
    # USE SERPER FOR LIVE DATA
    # =========================

    if any(word in text for word in live_keywords):

        serper_result = serper_search(query)

        if serper_result:

            return {

                "response": serper_result,
                "source": "serper"
            }

    # =========================
    # USE DUCK FOR GENERAL SEARCH
    # =========================

    duck_result = duckduckgo_search(query)

    if duck_result:

        return {

            "response": duck_result,
            "source": "duckduckgo"
        }

    # =========================
    # FAILURE
    # =========================

    return {

        "response": "Unable to retrieve information currently.",
        "source": "retrieval_failure"
    }