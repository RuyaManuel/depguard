from agents.agent import Agent
import asyncio

if __name__ == "__main__":
    agent = Agent()
    #get installed packages and versions and run agent
    result = agent.get_installed_packages()
    print(result)
    user_message = f"""
            You are a preventive maintenance agent. Your goal is to analyze the installed packages in a codebase and identify any known vulnerabilities.

            Reason step by step and decide which tools to call and in what order.


            Here are the installed packages:
            {agent.get_installed_packages()}
            
    """
    agent.run_agent(user_message)

 