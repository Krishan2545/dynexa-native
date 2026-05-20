from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

# Enable frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request structure
class PromptRequest(BaseModel):
    prompt: str

# Home route
@app.get("/")
def home():
    return {"message": "Dynexa FastAPI Backend Running"}

# AI optimization route
@app.post("/optimize")
def optimize(data: PromptRequest):

    prompt = data.prompt

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi3:latest",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 120
            }
        }
    )

    result = response.json()["response"]

    return {
        "optimized_prompt": result
    }