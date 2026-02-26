import os
from agents.agent import Agent

def main():
    project_path = os.getcwd()
    
    agent = Agent(project_path=project_path)
    result = agent.run_agent()

    if result:
        print(result)

if __name__ == "__main__":
    main()