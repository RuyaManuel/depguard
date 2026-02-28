# import subprocess
# from groq import Groq
# import os
# from dotenv import load_dotenv
# import json
# from tools.descriptions import tools

# load_dotenv()


# def check_vulnerability(project_path: str) -> tuple[list, list[str]]:
#     logs = []
#     logs.append("🔍 Starting security audit...")

#     process = subprocess.run(
#     ["python", "-m", "pip_audit", "--requirement", os.path.join(project_path, "requirements.txt"), "--format", "json"],
#     capture_output=True,
#     text=True,
#     cwd=project_path,
#     timeout=90.0
#     )

#     data = json.loads(process.stdout)
#     dependencies = data.get("dependencies", [])

#     vulnerable = [d for d in dependencies if d.get("vulns")]
#     clean = [d for d in dependencies if not d.get("vulns") and "skip_reason" not in d]
#     skipped = [d for d in dependencies if "skip_reason" in d]

#     logs.append(f"Clean: {len(clean)}")
#     logs.append(f"Skipped: {len(skipped)}")
#     logs.append(f"Vulnerable: {len(vulnerable)}")

#     for dep in vulnerable:
#         logs.append(f"compromised package:")
#         logs.append(f"{dep['name']} {dep['version']}")
#         for vuln in dep['vulns']:
#             logs.append(f"   - {vuln['id']}: fix in {vuln['fix_versions']}")

#     return vulnerable, logs


# def auto_fix(vulnerable: list) -> list[str]:
#     logs = []
#     for dep in vulnerable:
#         fix_version = dep['vulns'][0]['fix_versions'][-1]
#         logs.append(f"🔧 Upgrading {dep['name']} to {fix_version}...")
#         subprocess.run(["python", "-m", "pip", "install", f"{dep['name']}=={fix_version}"])
#     logs.append("✅ All fixes applied!")
#     return logs


# def update_requirements(vulnerable: list, project_path: str) -> list[str]:
#     logs = []
#     req_path = os.path.join(project_path, "requirements.txt")

#     with open(req_path, "r") as f:
#         lines = f.readlines()

#     for dep in vulnerable:
#         fix_version = dep['vulns'][0]['fix_versions'][-1]
#         lines = [
#             f"{dep['name']}=={fix_version}\n" if line.lower().startswith(dep['name'].lower())
#             else line
#             for line in lines
#         ]

#     with open(req_path, "w") as f:
#         f.writelines(lines)

#     logs.append("📝 requirements.txt updated!")
#     return logs


# def generate_report(vulnerable: list, project_path: str) -> list[str]:
#     logs = []
#     report = {"vulnerabilities": vulnerable}
#     report_path = os.path.join(project_path, "audit_report.json")
#     with open(report_path, "w") as f:
#         json.dump(report, f, indent=2)
#     logs.append("📄 Report saved to audit_report.json")
#     return logs


# def decide_next_step(vulnerable: list, project_path: str) -> list[str]:
#     logs = []

#     if not vulnerable:
#         logs.append("🎉 No vulnerabilities found. Nothing to do!")
#         return logs

#     client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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
#         Use the available tools to: fix packages, update requirements.txt, generate a report,
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

#     logs.append("AI reasoning...")

#     while True:
#         response = client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=messages,
#             tools=tools,
#             tool_choice="auto",
#         )

#         message = response.choices[0].message

#         if message.content:
#             logs.append(message.content)

#         if not message.tool_calls:
#             logs.append("✅ LLM finished without further tool calls.")
#             break

#         messages.append(message)

#         for tool_call in message.tool_calls:
#             tool_name = tool_call.function.name
#             logs.append(f"▶ AI chose action: {tool_name}")

#             if tool_name == "auto_fix":
#                 logs.extend(auto_fix(vulnerable))
#                 result = "auto_fix completed successfully."
#             elif tool_name == "update_requirements":
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
#                 logs.append("👋 LLM decided no further action is needed. Done!")
#                 return logs
#             else:
#                 result = f"Unknown tool: {tool_name}"

#             logs.append(f"↩ Result: {result}")
#             messages.append({
#                 "role": "tool",
#                 "tool_call_id": tool_call.id,
#                 "content": result,
#             })

#     return logs


import subprocess
from groq import Groq
import os
from dotenv import load_dotenv
import json
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


def decide_next_step(vulnerable: list, project_path: str) -> list[str]:
    logs = []

    if not vulnerable:
        logs.append("No vulnerabilities found. project safe!")
        return logs

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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

    system_instructions = """
        You are an automated security remediation agent.
        You have just completed a pip-audit scan and found vulnerable dependencies.
        Your job is to decide the best sequence of actions to remediate the issues.
        Use the available tools to: update requirements.txt, generate a report,
        and re-run the audit to confirm fixes. Call tools one at a time.
        When everything is resolved, call the 'exit' tool.
    """

    messages = [
        {"role": "system", "content": system_instructions},
        {
            "role": "user",
            "content": (
                f"The audit found {len(vulnerable)} vulnerable package(s):\n"
                f"{json.dumps(vuln_summary, indent=2)}\n\n"
                "Please decide and execute the appropriate remediation steps."
            ),
        },
    ]

    logs.append("AI reasoning...")

    while True:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        message = response.choices[0].message

        if message.content:
            logs.append(message.content)

        if not message.tool_calls:
            logs.append("✅ LLM finished done reasoning.")
            break

        messages.append(message)

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
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
            else:
                result = f"Unknown tool: {tool_name}"

            logs.append(f"↩ Result: {result}")
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

    return logs