# DepGuard 🛡️
An AI-powered dependency vulnerability scanner that autonomously inspects your Python codebase, identifies installed packages, checks them against known vulnerability databases, and suggests fixes — all driven by an LLM agent.

## What it does
DepGuard scans your Python project, extracts every imported package, maps each one to its installed version, and uses an AI agent to call the OSV vulnerability database to check for known security issues. It then suggests upgrade paths for any vulnerable packages it finds.


## How it works
Your codebase
      ↓
Collect all imports (AST parsing)
      ↓
Map imports → installed versions (importlib.metadata)
      ↓
LLM Agent decides which tools to call
      ↓
check_vulnerability() hits the OSV API for each package
      ↓
Agent summarizes findings + suggests fixes

# Project Structure
depguard/
├── agents/
│   ├── agent.py          # Core LLM agent logic and tool call loop
│   └── snapshot.py       # AST import collector and version mapper
├── tools/
│   ├── functions.py      # check_vulnerability() implementation
│   └── descriptions.py   # Tool schema definitions for the LLM
├── codebase/             # Drop the project you want to scan here
├── main.py               # Entry point
├── .env                  # API keys (not committed)
└── requirements.txt

## Getting Started
### Prerequisites

 Python 3.11+
A Groq API key

## Installation
git clone https://github.com/yourusername/depguard.git
cd depguard
pip install -r requirements.txt

## Configuration
Create a .env file in your root directory 

GROQ_API_KEY=your_api_key_here

Usage
Drop the codebase you want to scan into the codebase/ directory, then run:
bashpython main.py

Example Output
Checked: groq 0.4.1 → groq version 0.4.1 has no known vulnerabilities
Checked: requests 2.28.0 → requests version 2.28.0 has 1 known vulnerability

Final Report:
- requests 2.28.0 is vulnerable. Upgrade to 2.32.5
  Run: pip install requests==2.32.5

Tech Stack

Groq — LLM inference
OSV API — Open source vulnerability database
importlib.metadata — Package version resolution
Python AST — Static import analysis


Roadmap

 AST-based import collection
 Version mapping via importlib.metadata
 Batch vulnerability checking via OSV API
 Auto-fix version suggestions
 Structured vulnerability report (PDF/Markdown)
 Scheduled monitoring
 CI/CD integration (GitHub Actions)
 Support for npm and other ecosystems


Contributing
This project is in early development. Feel free to open issues or submit pull requests.

License
MIT