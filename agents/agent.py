import json
from dotenv import load_dotenv
import os
from groq import Groq
from utils.snapshot import SnapShot
from tools.descriptions import tools
from tools.functions import check_vulnerability

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class Agent:

    def __init__(self,project_path):
        self.snapshot = SnapShot()
        self.project_path = project_path

    def run_agent(self) -> dict:

        installed_packages = self.snapshot.read_requirements(self.project_path)
    
        if not installed_packages:
            return {"error": "No packages found in path. update project path or ensure requirements.txt is present."}

        package_list_str = "\n".join(
        [f"- {p['name']}=={p['version']}" for p in installed_packages]
        )

        # Phase 2: LLM Analysis of installed packages
        llm_analysis = self._investigate(package_list_str)

       
        #Phase 3: Generate report
        report = self._synthesize(llm_analysis)
        parsed_report = json.loads(report)

        return {
            "total_checked": len(installed_packages),
            "total_vulnerable":parsed_report["total_vulnerable"],
            "critical" : parsed_report["critical"],
            "report": parsed_report["report"]
        }

    
    def _investigate(self, installed_packages):

        packages = self.snapshot.read_requirements(self.project_path)

        system_instruction =  """

        You are a security analyst agent scanning a Python project for vulnerabilities.
        Your job in this phase is to:
        1. Call check_vulnerability for EVERY package in the list — do not skip any
        2. Check packages one by one until the entire list is exhausted
        3. Do not stop early — if you have not checked every package, keep going
        4. Do not summarize or explain yet — your only job here is to check

        Be thorough. Missing a package is a security risk.
        """

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": installed_packages}
        ]

        llm_results = []
        print(f"\n🔍 Investigating {len(packages)} packages...\n")

        while True:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            choice = response.choices[0]
            finish_reason = choice.finish_reason

            if finish_reason == "stop":
                print(f"\n✅ Investigation complete. {len(llm_results)} packages checked.")
                llm_results.append(choice.message.content)
                break
            
            if finish_reason == "tool_calls" and choice.message.tool_calls:
                messages.append(choice.message)

                for tool_call in choice.message.tool_calls:
                    function_args = json.loads(tool_call.function.arguments)

                    if tool_call.function.name == "check_vulnerability":
                        result = check_vulnerability(**function_args)

                        if isinstance(result, list):
                            llm_results.extend(result)
                        else:
                            llm_results.append(result)

                        messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                        })

    
        return llm_results

    def _synthesize(self, llm_analysis: list) -> str:

        system_instruction = """
        You are a senior application security analyst.
        You will be given raw vulnerability scan results for a Python project.
        Your job is to reason over the findings and produce a clear, actionable report.
        Be precise, prioritize by severity, and give developers exactly what they need to fix the issues.
        """

        synthesis_prompt = f"""
        Here are the raw vulnerability scan results:

        {json.dumps(llm_analysis, indent=2)}

        Now do the following:
        1. Identify which packages are truly vulnerable — ignore anything with no known vulnerabilities
        2. Rank them by severity: Critical → High → Medium → Low
        3. Spot patterns — e.g. one outdated package causing multiple CVEs
        4. For each vulnerable package suggest the exact safe version to upgrade to
        5. Write a plain-English summary a developer can act on immediately

        Format your response as:

        ## Vulnerability Report

        ### Critical / High
        - <package>==<version>: <what the vulnerability is, CVE if known>
        Fix: pip install <package>==<safe_version>

        ### Medium / Low
        - ...

        ### Root Cause Patterns
        ...

        ### Summary
        ...

        synthesis_prompt = f
        
        Return your response as JSON with this structure:
        {{
        "total_vulnerable": <number>,
        "vulnerable_packages": ["package==version", ...],
        "critical": true/false,
        "report": "... the full markdown report ..."
        }}
        """

        response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": synthesis_prompt}
        ]
        )

        return response.choices[0].message.content
        
