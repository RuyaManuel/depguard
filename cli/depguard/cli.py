import typer
import httpx
import os
import json
import subprocess

app = typer.Typer()

API_URL = "https://depguard.onrender.com/scan"
HEALTH_URL = "https://depguard.onrender.com/health"


def wake_server():
    """Ping the server to wake it up if it's sleeping."""
    try:
        typer.echo("⏳ Connecting to DepGuard server...")
        httpx.get(HEALTH_URL, timeout=60.0)
        typer.echo("✅ Server is awake!\n")
    except httpx.TimeoutException:
        typer.echo("⚠️  Server is slow to wake — retrying scan anyway...\n")
    except Exception:
        pass  # Best effort


def auto_fix(req_path: str):
    """Install fixed packages into the user's own environment."""
    typer.echo("\n🔧 Installing fixed packages into your environment...")
    result = subprocess.run(
        ["pip", "install", "-r", req_path],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        typer.echo("✅ Fixed packages installed successfully!")
    else:
        typer.echo(f"⚠️  Some packages failed to install:\n{result.stderr}")


@app.command()
def scan():
    """Scan your project's requirements.txt for known vulnerabilities."""

    req_path = os.path.join(os.getcwd(), "requirements.txt")

    if not os.path.exists(req_path):
        typer.echo("❌ No requirements.txt found in the current directory.")
        raise typer.Exit()

    wake_server()

    typer.echo("📦 requirements.txt Found — Processing for vulnerabilities...\n")

    try:
        with open(req_path, "rb") as f:
            content = f.read()
            response = httpx.post(
                API_URL,
                files={"requirements": ("requirements.txt", content, "text/plain")},
                timeout=180.0
            )
    except httpx.TimeoutException:
        typer.echo("❌ Request timed out. The server may be overloaded — please try again.")
        raise typer.Exit()

    if response.status_code != 200:
        typer.echo(f"❌ Server error: {response.status_code} — {response.text}")
        raise typer.Exit()

    data = response.json()

    # Print the full agent log
    for log in data.get("logs", []):
        typer.echo(log)

    # Write updated requirements.txt back to the developer's project
    if data.get("updated_requirements"):
        with open(req_path, "w") as f:
            f.write(data["updated_requirements"])
        typer.echo("\n✅ requirements.txt updated in your project.")
        auto_fix(req_path)  # 👈 install fixes locally

    # Write audit_report.json to the developer's project
    if data.get("audit_report"):
        report_path = os.path.join(os.getcwd(), "audit_report.json")
        with open(report_path, "w") as f:
            json.dump(data["audit_report"], f, indent=2)
        typer.echo("✅ audit_report.json saved in your project.")


def main():
    app()