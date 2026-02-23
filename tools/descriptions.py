tools = [
    "type" : "functions",
    "function" : {
        "name": "check_vulnerability",
        "description" : "Check if a python package has a known vulnerability"
        "parameters" : {
            "type" : "object",
            "properties" : {
                "package" : {"type" : "string"},
                "version" : {"type" : "string"}
            },
            "required" : ["package","version"]
        }
    }
]