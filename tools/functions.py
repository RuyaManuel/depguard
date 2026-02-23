import requests

def check_vulnerability(package,version):
    response = requests.post('https://api.osv.dev/v1/query', json = {
        "version" : version,
        "package" : {"name" : package, "ecosystem" : "PYPI"}
    })

    data = response.json()
    if data.get("vulns"):
        return f"{package} version {version} has {len(data['vulns'])} known vulnerabilities"


