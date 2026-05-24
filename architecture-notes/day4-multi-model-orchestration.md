# Day 4 — Multi-Model Orchestration

## Systems Built

- Installed TinyLlama
- Installed DeepSeek Coder
- Added multi-model routing
- Built model selection engine
- Added task-based inference routing
- Optimized low-RAM local inference

## Architecture

Prompt
↓
Intent Detection
↓
Model Router
↓
Selected Model
↓
Response

## Models Used

- TinyLlama
- Phi3
- DeepSeek Coder

## Key Learning

Different models perform better for different task categories.