import re

# =========================
# CLEAN RESPONSE
# =========================

def clean_response(text):

    if not text:
        return "No response generated."

    # Remove model identity leakage
    blocked_phrases = [

        "I am an AI model",
        "trained by",
        "developed by",
        "as an AI",
        "language model",
        "DeepSeek",
        "Phi3",
        "TinyLlama"
    ]

    cleaned = text

    for phrase in blocked_phrases:

        cleaned = re.sub(
            phrase,
            "",
            cleaned,
            flags=re.IGNORECASE
        )

    # Remove excessive newlines
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    # Remove weird spacing
    cleaned = cleaned.strip()

    # Fallback
    if len(cleaned) < 2:

        return "Unable to generate proper response."

    return cleaned

# =========================
# SYNTHESIZE RESPONSE
# =========================

def synthesize_response(
    raw_response,
    source
):

    cleaned = clean_response(raw_response)

    final_response = {

        "response": cleaned,
        "source": source
    }

    return final_response