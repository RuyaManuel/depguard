from pathlib import Path
import importlib.metadata as meta
import ast


class SnapShot:                              
    def __init__(self, agent):               # ← __init__ was missing entirely
        self.agent = agent
        self.snapshots = []

    def collect_imports(self, codebase_dir):  
        file_imports = {}                     

        for py_file in Path(codebase_dir).rglob('*.py'): 
            source = py_file.read_text(encoding='utf-8')

            tree = ast.parse(source)

            imports = set()                  

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:          
                        imports.add(node.module.split('.')[0])

            if imports:           
                print("found the imports:",imports)            
                file_imports[str(py_file)] = imports

        return file_imports                   


    def map_versions(self, file_imports):    # ← renamed param to file_imports, was shadowing the outer variable
        mapped = {}                          # ← changed [] to {}, you're building a dict not a list

        for file, imports in file_imports.items():
            packages = {}

            for import_name in imports:      # ← fixed indentation, was misaligned
                try:
                    version = meta.version(import_name)
                    packages[import_name] = version
                except meta.PackageNotFoundError:
                    pass

            if imports:                      # ← fixed indentation, belongs inside the for loop
                mapped[file] = packages

        return mapped                        # ← fixed indentation, belongs inside the method


if __name__ == "__main__":
    agent = SnapShot(agent=None)
    file_imports = agent.collect_imports("../codebase")
    mapped = agent.map_versions(file_imports)   # ← fixed method name, was map_to_packages
    for file, packages in mapped.items():
        print(file, "→", packages)