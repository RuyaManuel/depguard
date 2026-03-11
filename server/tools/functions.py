import subprocess
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import json
import requests
from tools.descriptions import tools

load_dotenv()


def check_vulnerability(project_path: str) -> tuple[list, list[str]]:
    logs = []
    logs.append("Starting security audit...")

    process = subprocess.run(
        ["python", "-m", "pip_audit", "--requirement", os.path.join(project_path, "requirements.txt"), "--format", "json"],
        capture_output=True,
        text=True,
        cwd=project_path,
        timeout=90.0
    )

    data = json.loads(process.stdout)
    dependencies = data.get("dependencies", [])

    vulnerable = [d for d in dependencies if d.get("vulns")]
    clean = [d for d in dependencies if not d.get("vulns") and "skip_reason" not in d]
    skipped = [d for d in dependencies if "skip_reason" in d]


    logs.append(f"Clean: {len(clean)}")
    logs.append(f"Skipped: {len(skipped)}")
    logs.append(f"Vulnerable: {len(vulnerable)}")


    for dep in vulnerable:
        logs.append(f"--compromised packages:")
        logs.append(f"{dep['name']} {dep['version']}")
        for vuln in dep['vulns']:
            logs.append(f"   - {vuln['id']}: fix in {vuln['fix_versions']}")

    return vulnerable, logs


def update_requirements(vulnerable: list, project_path: str) -> list[str]:
    logs = []
    req_path = os.path.join(project_path, "requirements.txt")

    with open(req_path, "r") as f:
        lines = f.readlines()

    for dep in vulnerable:
        fix_version = dep['vulns'][0]['fix_versions'][-1]
        lines = [
            f"{dep['name']}=={fix_version}\n" if line.lower().startswith(dep['name'].lower())
            else line
            for line in lines
        ]

    with open(req_path, "w") as f:
        f.writelines(lines)

    logs.append("requirements.txt updated!")
    return logs


def generate_report(vulnerable: list, project_path: str) -> list[str]:
    logs = []
    report = {"vulnerabilities": vulnerable}
    report_path = os.path.join(project_path, "audit_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    logs.append("📄 Report saved to audit_report.json")
    return logs


# def decide_next_step(vulnerable: list, project_path: str) -> list[str]:
#     logs = []

#     if not vulnerable:
#         logs.append("No vulnerabilities found. project safe!")
#         return logs

#     client = genai.Client()

#     vuln_summary = []
#     for dep in vulnerable:
#         vuln_summary.append({
#             "package": dep["name"],
#             "version": dep["version"],
#             "vulnerabilities": [
#                 {"id": v["id"], "fix_versions": v["fix_versions"]}
#                 for v in dep["vulns"]
#             ],
#         })

#     system_instructions = """
#         You are an automated security remediation agent.
#         You have just completed a pip-audit scan and found vulnerable dependencies.
#         Your job is to decide the best sequence of actions to remediate the issues.
#         Use the available tools to: update requirements.txt, generate a report,
#         and re-run the audit to confirm fixes. Call tools one at a time.
#         When everything is resolved, call the 'exit' tool.
#     """

#     messages = [
#         {"role": "system", "content": system_instructions},
#         {
#             "role": "user",
#             "content": (
#                 f"The audit found {len(vulnerable)} vulnerable package(s):\n"
#                 f"{json.dumps(vuln_summary, indent=2)}\n\n"
#                 "Please decide and execute the appropriate remediation steps."
#             ),
#         },
#     ]

#     logs.append("depguard is reasoning...")

#     while True:
#         response = client.models.generate_content(
#             model="gen-lang-client-0157849620",
#             messages=messages,
#             tools=tools,
#             tool_choice="auto",
#         )

#         message = response.choices[0].message

#         if message.content:
#             logs.append(message.content)

#         if not message.tool_calls:
#             logs.append("✅ LLM finished done reasoning.")
#             break

#         messages.append(message)

#         for tool_call in message.tool_calls:
#             tool_name = tool_call.function.name
#             logs.append(f"▶ AI chose action: {tool_name}")

#             if tool_name == "update_requirements":
#                 logs.extend(update_requirements(vulnerable, project_path))
#                 result = "requirements.txt updated successfully."
#             elif tool_name == "generate_report":
#                 logs.extend(generate_report(vulnerable, project_path))
#                 result = "audit_report.json generated successfully."
#             elif tool_name == "re_run_audit":
#                 vulnerable, audit_logs = check_vulnerability(project_path)
#                 logs.extend(audit_logs)
#                 result = f"Re-audit complete. {len(vulnerable)} vulnerable package(s) remaining."
#             elif tool_name == "exit":
#                 logs.append("LLM decided no further action is needed. Done!")
#                 return logs
#             elif tool_name == "open_pull_request":
#                 logs.extend(open_pull_request(vulnerable, project_path))
#                 result = "Pull request opened and merged on GitHub."
#             else:
#                 result = f"Unknown tool: {tool_name}"

#             logs.append(f"↩ Result: {result}")
#             messages.append({
#                 "role": "tool",
#                 "tool_call_id": tool_call.id,
#                 "content": result,
#             })

#     return logs
def decide_next_step(vulnerable: list, project_path: str) -> list[str]:
    logs = []

    if not vulnerable:
        logs.append("No vulnerabilities found. project safe!")
        return logs

    client = genai.Client()

    vuln_summary = []
    for dep in vulnerable:
        vuln_summary.append({
            "package": dep["name"],
            "version": dep["version"],
            "vulnerabilities": [
                {"id": v["id"], "fix_versions": v["fix_versions"]}
                for v in dep["vulns"]
            ],
        })

    system_instruction = """
        You are an automated security remediation agent.
        You have just completed a pip-audit scan and found vulnerable dependencies.
        Your job is to decide the best sequence of actions to remediate the issues.
        Use the available tools to: update requirements.txt, generate a report,
        and re-run the audit to confirm fixes. Call tools one at a time.
        When everything is resolved, call the 'exit' tool.
    """

    # google-genai uses `contents` (list of Content objects), not `messages`
    # system_instruction is passed via GenerateContentConfig, not as a message role
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part(text=(
                    f"The audit found {len(vulnerable)} vulnerable package(s):\n"
                    f"{json.dumps(vuln_summary, indent=2)}\n\n"
                    "Please decide and execute the appropriate remediation steps."
                ))
            ],
        )
    ]

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        tools=[types.Tool(function_declarations=tools)],  # tools must be wrapped in Tool()
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    logs.append("depguard is reasoning...")

    while True:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",   # replace with your actual model
            contents=contents,
            config=config,
        )

        # response.text is the text output (None if the turn is a function call)
        candidate = response.candidates[0]
        
        # Collect any text parts from this turn
        text_parts = [
            part.text
            for part in candidate.content.parts
            if part.text is not None
        ]
        if text_parts:
            logs.append(" ".join(text_parts))

        # Check for function calls — response.function_calls is a convenience list
        function_calls = response.function_calls  # List[types.FunctionCall] | None
        
        if not function_calls:
            logs.append("✅ LLM finished reasoning.")
            break

        # Append the model's turn to contents before adding tool results
        contents.append(candidate.content)

        # Collect all tool results for this turn into one Content block
        function_response_parts = []

        for fn_call in function_calls:
            tool_name = fn_call.name
            logs.append(f"▶ AI chose action: {tool_name}")

            if tool_name == "update_requirements":
                logs.extend(update_requirements(vulnerable, project_path))
                result = "requirements.txt updated successfully."
            elif tool_name == "generate_report":
                logs.extend(generate_report(vulnerable, project_path))
                result = "audit_report.json generated successfully."
            elif tool_name == "re_run_audit":
                vulnerable, audit_logs = check_vulnerability(project_path)
                logs.extend(audit_logs)
                result = f"Re-audit complete. {len(vulnerable)} vulnerable package(s) remaining."
            elif tool_name == "exit":
                logs.append("LLM decided no further action is needed. Done!")
                return logs
            elif tool_name == "open_pull_request":
                logs.extend(open_pull_request(vulnerable, project_path))
                result = "Pull request opened and merged on GitHub."
            else:
                result = f"Unknown tool: {tool_name}"

            logs.append(f"↩ Result: {result}")

            # Build a FunctionResponse Part for each call
            function_response_parts.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        name=tool_name,
                        response={"result": result},  # must be a dict
                    )
                )
            )

        # All function responses go into a single "tool" Content turn
        contents.append(
            types.Content(role="tool", parts=function_response_parts)
        )

    return logs


# Open pull request tool (function) not properly tested and vetted.
def open_pull_request(vulnerable: list, project_path: str) -> list[str]:
    logs = []
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPO")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    base_url = f"https://api.github.com/repos/{repo}"

    # get default branch SHA
    ref_res = requests.get(f"{base_url}/git/ref/heads/main", headers=headers)
    sha = ref_res.json()["object"]["sha"]

    # create new branch
    branch = "depguard/fix-vulnerabilities"
    requests.post(f"{base_url}/git/refs", headers=headers, json={
        "ref": f"refs/heads/{branch}",
        "sha": sha
    })

    # read updated requirements.txt and push it
    req_path = os.path.join(project_path, "requirements.txt")
    with open(req_path, "r") as f:
        content = f.read()

    import base64
    # get current file SHA (needed to update)
    file_res = requests.get(f"{base_url}/contents/requirements.txt", headers=headers)
    file_sha = file_res.json()["sha"]

    requests.put(
        f"{base_url}/contents/requirements.txt",
        headers=headers,
        json={
            "message": "fix: upgrade vulnerable dependencies (depguard)",
            "content": base64.b64encode(content.encode()).decode(),
            "sha": file_sha,
            "branch": branch
        }
    )

    # build PR description
    summary_lines = []
    for dep in vulnerable:
        for vuln in dep["vulns"]:
            fix = vuln["fix_versions"][-1] if vuln["fix_versions"] else "unknown"
            summary_lines.append(f"- **{dep['name']}** {dep['version']} → {fix} ({vuln['id']})")
    summary = "\n".join(summary_lines)

    pr_body = f"## DepGuard Security Fix 🛡️\n\nThe following vulnerabilities were detected and fixed:\n\n{summary}\n\n> Auto-generated by DepGuard"

    # open the PR
    pr_res = requests.post(f"{base_url}/pulls", headers=headers, json={
        "title": "fix: patch vulnerable dependencies (depguard)",
        "body": pr_body,
        "head": branch,
        "base": "main"
    })

    pr_data = pr_res.json()

    # auto-merge
    pr_number = pr_data.get("number")
    if pr_number:
        requests.put(
            f"{base_url}/pulls/{pr_number}/merge",
            headers=headers,
            json={"merge_method": "squash"}
        )
        logs.append(f"✅ PR #{pr_number} opened and merged: {pr_data.get('html_url')}")
    else:
        logs.append(f"⚠️ PR may already exist or failed: {pr_data.get('message')}")

    return logs