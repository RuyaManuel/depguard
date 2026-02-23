import requests
from agents.snapshot import SnapShot 
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


    def get_installed_packages(self) -> list[dict]:
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
