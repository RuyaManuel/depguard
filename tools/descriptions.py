tools = [
    {
        "type": "function",
        "function": {
            "name": "check_vulnerability",
            "description": "Scan the project requirements.txt for known vulnerabilities. Returns CVE IDs, descriptions, and fix versions for all vulnerable packages. Call this once to get a full audit.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]