# Preventive Maintenance Agent (minimal)

This is a tiny example project to get you chatting with an LLM quickly using Groq.

Setup

1. Install dependencies:

```powershell
py -m pip install -r requirements.txt
```

2. Add your Groq API key. Copy `.env.example` to `.env` and set `GROQ_API_KEY`.

3. Run the chat:

```powershell
py agent_one.py
```

Usage

- Type a message and press Enter to send it to the model.
- Type `exit` or `quit` or press Ctrl+C to stop.

Notes

- This example uses the `groq` Python client. If you prefer to call the HTTP API directly, swap `query_model()` implementation.
- If you still want to run local models with Ollama later, keep Ollama installed — this example uses Groq to avoid download issues.
