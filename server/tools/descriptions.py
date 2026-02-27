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
    },
    {
        "type": "function",
        "function": {
            "name": "auto_fix",
            "description": "Automatically upgrades all vulnerable packages to their fixed versions using pip.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_requirements",
            "description": "Updates requirements.txt to pin vulnerable packages to their fixed versions.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_report",
            "description": "Saves a JSON audit report of all vulnerabilities to audit_report.json.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "re_run_audit",
            "description": "Re-runs the vulnerability audit to verify fixes or check for new issues.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "exit",
            "description": "No further action is needed. Call this when vulnerabilities are resolved or no action is warranted.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]