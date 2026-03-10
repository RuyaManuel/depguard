from dotenv import load_dotenv
import os
from google import genai
from tools.functions import check_vulnerability, decide_next_step


load_dotenv()
class Agent:

    def __init__(self, project_path: str):
        self.client = genai.Client()
        self.project_path = project_path

    def run_agent(self) -> list[str]:
        vulnerable, audit_logs = check_vulnerability(self.project_path)

        if not vulnerable:
            return audit_logs

        decision_logs = decide_next_step(vulnerable, self.project_path)

        return audit_logs + decision_logs