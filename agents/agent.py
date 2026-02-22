import requests
from snapshot import SnapShot 
import importlib.metadata as meta
import httpx
import asyncio
import json
from dotenv import load_dotenv
import os
from typing import Dict, Any
from groq import Groq


load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class Agent:
    def __init__(self):
        self.snapshot = SnapShot()

    def threat_query(self, package_name: str) -> str:
        url = f"https://pypi.org/pypi/{package_name}/json"
        try:
            r = requests.get(url)
            data = r.json()
            return data['info']['version']
        except requests.RequestException as e:
            print(f"Error fetching version for {package_name}: {e}")
            return "Unknown"
    
    def ai_strategy(self, snapshot_data: str) -> str:
        prompt = f"""
        You are a software agent architect.

        Here is a raw package data obtained from the snapshot of a codebases installed packages.

        {json.dumps(snapshot_data, indent=2)}
        

        Your task:
        1. Suggest the next step or tool to build that would allow me to leverage this data to identify potential security vulnerabilities in the codebase.
        2. Suggest strategies for analyzing the package health, maintenance and compatibility with the codebase.
        3. Provide a rationale for your suggestions, explaining how they would help in identifying vulnerabilities and assessing package health.

        Return your response in a structure JSON format:
        {{
            "next_step": "Description of the next step or tool to build",
            "strategies": [
                "Strategy 1: Description of strategy 1",
                "Strategy 2: Description of strategy 2",
                ...
            ],
            "rationale": "Explanation of how these suggestions would help in identifying vulnerabilities and assessing package health."
        }}
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  
            messages=[  
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )

        llm_output = response.choices[0].message.content
        print("LLM Output:", llm_output)
        return llm_output

    def get_installed_packages(self):
        package_list: list[dict] = []
        data = self.snapshot.map_versions(self.snapshot.collect_imports('../codebase'))
        for file, imports in data.items():
            if imports:
                for name, version in imports.items():
                    package_list.append({
                        "name": name,
                        "version": version
                    })

        return package_list

    @staticmethod
    async def get_pypi_metadata(package_name: str) -> Dict[str, Any]:
        url = f"https://pypi.org/pypi/{package_name}/json"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=10)
        if r.status_code != 200:
            return {"error": f"Package {package_name} not found on PyPI."}
        data = r.json()
        return {
            "name": data['info']['name'],
            "latest_version": data['info']['version'],
            "dependencies": list(data.get("info", {}).get("requires_dist", []) or []),
            "home_page": data['info']['home_page'],
            "author": data['info']['author'],
            "license": data['info']['license']
        }


if __name__ == "__main__":
    agent = Agent()
    result = agent.get_installed_packages()
    agent.ai_strategy(result)