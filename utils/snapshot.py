from pathlib import Path
import re


class SnapShot:

    def read_requirements(self, project_path: str) -> list[dict]:
        req_file = Path(project_path) / "requirements.txt"

        if not req_file.exists():
            raise FileNotFoundError(f"No requirements.txt found in {project_path}")

        packages = []

        for line in req_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if "==" in line:
                name, version = line.split("==", 1)
                packages.append({"name": name.strip(), "version": version.strip()})

            elif re.match(r'^[a-zA-Z0-9_\-]+$', line):
                packages.append({"name": line.strip(), "version": "unknown"})

        return packages