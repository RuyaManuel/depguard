import json
from dotenv import load_dotenv
import os
from groq import Groq
from tools.functions import check_vulnerability,decide_next_step

load_dotenv()
class Agent:

    def __init__(self,project_path):
        self.groq_key = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.project_path = project_path

    def run_agent(self) -> dict:
        results = check_vulnerability(self.project_path)
        if results:
            decide_next_step(results, self.project_path)