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

    def __init__(self):
        self.snapshot = SnapShot()

    def get_installed_packages(self,project_path) -> list[dict]:
        return self.snapshot.read_requirements(project_path)

    def run_agent(self, user_message) -> dict:
        messages = [
            {"role": "system", "content": "You are a vulnerability checker. Use the check_vulnerability tool to check every package provided to you."},
            {"role": "user", "content": user_message}
        ]

        all_results = []

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
                print("Final response:", choice.message.content)
                break

            if finish_reason == "tool_calls" and choice.message.tool_calls:
                messages.append(choice.message)

                for tool_call in choice.message.tool_calls:
                    function_args = json.loads(tool_call.function.arguments)

                    if tool_call.function.name == "check_vulnerability":
                        result = check_vulnerability(**function_args)

                        if isinstance(result, list):
                            all_results.extend(result)
                        else:
                            all_results.append(result)

                    messages.append({           # ← now inside the for loop
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })

        # determine if any vulnerabilities were found
        vulnerable = [r for r in all_results if "no known" not in r.lower()]
       
        return {
            "total_checked": len(all_results),
            "vulnerable": vulnerable,
            "critical": len(vulnerable) > 0
        }