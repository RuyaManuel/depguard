import typer
import httpx
import os
import json

app = typer.Typer()

API_URL = "https://depguard.onrender.com/scan"


@app.command()
def scan():
    """Scan your project's requirements.txt for known vulnerabilities."""

    req_path = os.path.join(os.getcwd(), "requirements.txt")

    if not os.path.exists(req_path):
        typer.echo("❌ No requirements.txt found in the current directory.")
        raise typer.Exit()

    typer.echo("📦 Found requirements.txt — sending to DepGuard...\n")

    with open(req_path, "rb") as f:
        response = httpx.post(
            API_URL,
            files={"requirements": ("requirements.txt", f, "text/plain")},
            timeout=120.0
        )

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

    # Write audit_report.json to the developer's project
    if data.get("audit_report"):
        report_path = os.path.join(os.getcwd(), "audit_report.json")
        with open(report_path, "w") as f:
            json.dump(data["audit_report"], f, indent=2)
        typer.echo("✅ audit_report.json saved in your project.")


def main():
    app()