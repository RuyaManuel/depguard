tools = [
    {
        "type": "function",
        "function": {
            "name": "check_vulnerability",
            "description": "Check multiple Python packages for known vulnerabilities at once",
            "parameters": {
                "type": "object",
                "properties": {
                    "packages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "version": {"type": "string"}
                            },
                            "required": ["name", "version"]
                        }
                    }
                },
                "required": ["packages"]
            }
        }
    }
]