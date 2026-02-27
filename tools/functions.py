import subprocess
from groq import Groq
import os
from dotenv import load_dotenv
import json
from tools.descriptions import tools

load_dotenv()

def check_vulnerability(project_path) -> list:
    print("\n🔍 Starting security audit...\n")

    process = subprocess.run(
        ["py", "-m", "pip_audit", "--format", "json"],
        capture_output=True,
        text=True,
        cwd=project_path
    )

    data = json.loads(process.stdout)
    dependencies = data.get("dependencies", [])

    vulnerable = [d for d in dependencies if d.get("vulns")]
    clean = [d for d in dependencies if not d.get("vulns") and "skip_reason" not in d]
    skipped = [d for d in dependencies if "skip_reason" in d]

    print(f"✅ Clean: {len(clean)}")
    print(f"⚠️  Skipped: {len(skipped)}")
    print(f"🚨 Vulnerable: {len(vulnerable)}")

    for dep in vulnerable:
        print(f"\n❌ {dep['name']} {dep['version']}")
        for vuln in dep['vulns']:
            print(f"   - {vuln['id']}: fix in {vuln['fix_versions']}")

    return vulnerable

def decide_next_step(vulnerable: list, project_path: str):
    if not vulnerable:
        print("\n🎉 No vulnerabilities found. Nothing to do!")
        return
    
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

    # LLM integration
    system_instructions = f""" 
        You are an automated security remediation agent. "
                "You have just completed a pip-audit scan and found vulnerable dependencies. "
                "Your job is to decide the best sequence of actions to remediate the issues. "
                "Use the available tools to: fix packages, update requirements.txt, generate a report, "
                "and re-run the audit to confirm fixes. Call tools one at a time. "
                "When everything is resolved, call the 'exit' tool."
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

    print("\n AI reasoning..... ")

    while True:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        message = response.choices[0].message
        if message.content:
            print(f"{message.content}")

        if not message.tool_calls:
            print("\n✅ LLM finished without further tool calls.")
            break

        messages.append(message)

        # Execute each tool and feed results back
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            print(f"\n▶ LLM chose action: {tool_name}")

            if tool_name == "auto_fix":
                auto_fix(vulnerable)
                result = "auto_fix completed successfully."
            elif tool_name == "update_requirements":
                update_requirements(vulnerable)
                result = "requirements.txt updated successfully."
            elif tool_name == "generate_report":
                generate_report(vulnerable)
                result = "audit_report.json generated successfully."
            elif tool_name == "re_run_audit":
                vulnerable = check_vulnerability(project_path)
                result = f"Re-audit complete. {len(vulnerable)} vulnerable package(s) remaining."
            elif tool_name == "exit":
                print("\n👋 LLM decided no further action is needed. Done!")
                return
            else:
                result = f"Unknown tool: {tool_name}"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })


def auto_fix(vulnerable: list):
    for dep in vulnerable:
        fix_version = dep['vulns'][0]['fix_versions'][-1]
        print(f"\n🔧 Upgrading {dep['name']} to {fix_version}...")
        subprocess.run(["py", "-m", "pip", "install", f"{dep['name']}=={fix_version}"])
    print("\n✅ All fixes applied!")


def update_requirements(vulnerable: list, req_path="requirements.txt"):
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
    print(f"\n📝 requirements.txt updated!")


def generate_report(vulnerable: list):
    report = {"vulnerabilities": vulnerable}
    with open("audit_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n📄 Report saved to audit_report.json")


def prompt_next_step(vulnerable: list, project_path: str):
    if not vulnerable:
        print("\n🎉 No vulnerabilities found. Nothing to do!")
        return

    actions = {
        "1": ("Auto-fix vulnerable packages", auto_fix),
        "2": ("Update requirements.txt", update_requirements),
        "3": ("Generate JSON report", generate_report),
        "4": ("Re-run audit", lambda _: check_vulnerability(project_path)),
        "5": ("Exit", None),
    }

    while True:
        print("\n🤖 What would you like to do next?\n")
        for key, (label, _) in actions.items():
            print(f"  [{key}] {label}")

        choice = input("\nEnter choice: ").strip()

        if choice == "5":
            print("\n👋 Exiting. Goodbye!")
            break
        elif choice in actions:
            label, fn = actions[choice]
            print(f"\n▶ Running: {label}")
            fn(vulnerable)
        else:
            print("❌ Invalid choice, try again.")
