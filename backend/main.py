from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.controllers.execution_controller import execute_prompt

# =========================
# FASTAPI
# =========================

app = FastAPI()

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
# HOME
# =========================

@app.get("/")
def home():

    return {
        "status": "Dynexa Running"
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

    return execute_prompt(prompt)