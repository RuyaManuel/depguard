import subprocess
import json

def check_vulnerability(project_path) -> list:
    print("\n🔍 Starting security audit...\n")

    process = subprocess.run(
        ["py", "-m", "pip_audit", "--format", "json"],
        capture_output=True,
        text=True,
        cwd=project_path    
    )

    data = json.loads(process.stdout)
    dependencies = data.get("dependencies", [])
    
    vulnerable = [d for d in dependencies if d.get("vulns")]
    clean = [d for d in dependencies if not d.get("vulns") and "skip_reason" not in d]
    skipped = [d for d in dependencies if "skip_reason" in d]

    print(f"✅ Clean: {len(clean)}")
    print(f"⚠️  Skipped: {len(skipped)}")
    print(f"🚨 Vulnerable: {len(vulnerable)}")

    for dep in vulnerable:
        print(f"\n❌ {dep['name']} {dep['version']}")
        for vuln in dep['vulns']:
            print(f"   - {vuln['id']}: fix in {vuln['fix_versions']}")

    return dependencies