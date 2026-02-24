
import requests

def check_vulnerability(packages):
    # packages should be a list of dicts: [{"name": "groq", "version": "0.4.1"}, ...]
    
    queries = [
        {
            "version": pkg["version"],
            "package": {"name": pkg["name"], "ecosystem": "PyPI"}
        }
        for pkg in packages
    ]

    response = requests.post("https://api.osv.dev/v1/querybatch", json={"queries": queries})
    data = response.json()

    results = []
    for pkg, result in zip(packages, data.get("results", [])):
        vuln_count = len(result.get("vulns", []))
        if vuln_count > 0:
            results.append(f"{pkg['name']} version {pkg['version']} has {vuln_count} known vulnerabilities")
        else:
            results.append(f"{pkg['name']} version {pkg['version']} has no known vulnerabilities")

    return results


# def get_secure_version(vuln_packages):

    
