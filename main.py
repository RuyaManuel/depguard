from agents.agent import Agent
import asyncio

if __name__ == "__main__":
    agent = Agent()
    #get installed packages and versions
    result = agent.get_installed_packages()
    print(result)