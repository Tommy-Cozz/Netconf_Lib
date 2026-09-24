import os
import glob
import importlib

# Automatically find and import all .py files in this folder
modules = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
module_names = [os.path.basename(f)[:-3] for f in modules if not f.endswith('__init__.py')]

for name in module_names:
    globals()[name] = importlib.import_module(f".{name}", package=__package__)