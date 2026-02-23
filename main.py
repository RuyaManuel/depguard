import sys
from agents.agent import Agent

if __name__ == "__main__":
    agent = Agent()
    project_path = sys.argv[1] if len(sys.argv) > 1 else "."  # current directory, can be changed to any path containing a requirements.txt
    packages = agent.get_installed_packages(project_path)  

    user_message = f"""
        You are a preventive maintenance agent. Analyze the installed packages 
        and identify any known vulnerabilities. Check every single package.

        Here are the installed packages:
        {packages}
    """

    result = agent.run_agent(user_message)

    print(f"\nScan complete. {result['total_checked']} packages checked.")

    if result["critical"]:
        print(f"Vulnerable packages found:")
        for v in result["vulnerable"]:
            print(f"  - {v}")
        sys.exit(1)  # tells GitHub Actions the scan failed
    else:
        print("All packages clean. No vulnerabilities found.")
        sys.exit(0)  # tells GitHub Actions the scan passed