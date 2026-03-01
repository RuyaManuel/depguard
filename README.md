# DepGuard 🛡️
An AI-powered dependency vulnerability scanner that autonomously inspects your Python project's dependencies, checks them against known vulnerability databases, and suggests fixes — all driven by an LLM agent.

## What it does
DepGuard scans your Python project's `requirements.txt`, maps each package to its installed version, and uses an AI agent to call the OSV vulnerability database to check for known security issues. It then suggests upgrade paths for any vulnerable packages it finds.


## How it works
```
requirements.txt
      ↓
agent activates
      ↓
check for vulnerabilities 
      ↓
LLM Agent decides which tools to call
      ↓
Agent summarizes findings + suggests fixes
```

## Project Structure
```
depguard/
├── agents/
│   ├── agent.py          # Core LLM agent logic and tool call loop
│   └── snapshot.py       # Package collector and version mapper
├── tools/
│   ├── functions.py      # check_vulnerability() implementation
│   └── descriptions.py   # Tool schema definitions for the LLM
├── main.py               # Entry point
├── .env                  # API keys (not committed)
└── requirements.txt
```

## Getting Started
### Prerequisites

Python 3.11+

## Installation
```bash
git clone https://github.com/yourusername/depguard.git
cd depguard
pip install depguard
```

## Usage
Run DepGuard from the root directory where your `requirements.txt` is located:

```bash
python main.py
```

## Example Output
```
Checked: groq 0.4.1 → groq version 0.4.1 has no known vulnerabilities
Checked: requests 2.28.0 → requests version 2.28.0 has 1 known vulnerability

Final Report:
- requests 2.28.0 is vulnerable. Upgrade to 2.32.5
  Run: pip install requests==2.32.5
```

## Tech Stack

- **Groq** — LLM inference
- **OSV API** — Open source vulnerability database
- **py_audit** — Package dependency analysis


## Roadmap

- [x] Package-based dependency collection via py_audit
- [x] Batch vulnerability checking via OSV API
- [x] Auto-fix version suggestions
- [ ] Structured vulnerability report (PDF/Markdown)
- [ ] Scheduled monitoring
- [ ] CI/CD integration (GitHub Actions)
- [ ] Support for npm and other ecosystems


## Contributing
This project is in early development. Feel free to open issues or submit pull requests.

## License
MIT