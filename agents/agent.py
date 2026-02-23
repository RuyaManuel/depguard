import requests
from agents.snapshot import SnapShot 
import httpx
import asyncio
import json
from dotenv import load_dotenv
import os
from typing import Dict, Any
from groq import Groq
from tools.descriptions import tools
from tools.functions import check_vulnerability


load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class Agent:

    def __init__(self):
        self.snapshot = SnapShot()


    def get_installed_packages(self) -> list[dict]:
        package_list: list[dict] = []
        data = self.snapshot.map_versions(self.snapshot.collect_imports('./codebase'))
        for file, imports in data.items():
            if imports:
                for name, version in imports.items():
                    package_list.append({
                        "name": name,
                        "version": version
                    })

        return package_list

    # def run_agent(self,user_message):
    #     messages = [{"role": "user", "content": user_message}]

    #     response = client.chat.completions.create(
    #         model="openai/gpt-oss-120b",
    #         messages=messages,
    #         tools=tools,
    #         tool_choice="auto"
    #     )

    #     choice = response.choices[0]
    #     # print("Model response:", choice.message)
    #     # # now we check if model has decided to call a tool and if so we execute the tool and send the result back to the model
    #     # # if choice.message.tool_calls:
    #     if choice.message.tool_calls:
    #         for tool_call in choice.message.tool_calls:
    #             function_name = tool_call.function.name
    #             function_args = json.loads(tool_call.function.arguments)

    #             if function_name == "check_vulnerability":
    #                 result = check_vulnerability(**function_args)
    #                 print("Tool result:", result)
    def run_agent(self, user_message):

        messages = [
        {"role": "system", "content": "You are a vulnerability checker. Use the check_vulnerability tool to check every every package using functions available to you."},
        {"role": "user", "content": f"{user_message}"}
        ]

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
                    print("function arguments:",function_args)

                    if tool_call.function.name == "check_vulnerability":
                        result = check_vulnerability(**function_args)
                        print(f"Checked: {function_args} -> {result}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })