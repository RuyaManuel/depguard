from pathlib import Path
import importlib.metadata as meta
import ast


class SnapShot:                              
    def __init__(self):               
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
                file_imports[str(py_file)] = imports
        
        return file_imports                   


    # def map_versions(self, file_imports):    
    #     mapped = {}                 
    #     for file, imports in file_imports.items():
    #         packages = {}
    
    #         for import_name in imports:      
    #             try:
    #                 for dist in meta.distributions():
    #                     packages[import_name] = {
    #                         "meta_data" : dist.metadata["import_name"],
    #                         "requires": dist.requires,
    #                         "version" : dist.version,
    #                         "required-python-version": dist.metadata.get("Requires-Python"),
    #                         "name": import_name,
    #                     }
    #             except meta.PackageNotFoundError:
    #                 pass

    #         if imports:               
    #             mapped[file] = packages

    #     return mapped                       


    def map_versions(self, file_imports):
        mapped = {}
        # Build a mapping of top-level import names -> distribution package names
        import_to_pkg = meta.packages_distributions()

        for file, imports in file_imports.items():
            packages = {}  # key: import_name, value: metadata dict

            for import_name in imports:
                pkg_names = import_to_pkg.get(import_name)
                if not pkg_names:
                    continue
                try:
                    dist = meta.distribution(pkg_names[0])  # use first match
                    packages[import_name] = {
                    "meta_data":    dist.metadata["Name"],
                    "requires":     dist.requires,
                    "version":      dist.version,
                    "required-python-version": dist.metadata.get("Requires-Python"),
                    "name":         import_name,
                }
                except meta.PackageNotFoundError:
                    pass

            if packages:
                mapped[file] = packages

        return mapped