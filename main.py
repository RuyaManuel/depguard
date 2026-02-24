import os
from agents.agent import Agent

def main():
    project_path = os.getcwd()
    
    print(f"🔍 Scanning project at: {project_path}\n")
    
    agent = Agent(project_path=os.getcwd())
    result = agent.run_agent()

    if "error" in result:
        print(f"❌ {result['error']}")
        return

    print(f"📦 Packages checked: {result['total_checked']}")
    print(f"⚠️  Vulnerable: {result['total_vulnerable']}")
    print(f"\n{'─'*50}\n")
    print(result["report"])

if __name__ == "__main__":
    main()