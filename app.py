import importlib.util
import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src-election-system")
os.chdir(SRC_DIR)

sys.path.insert(0, SRC_DIR)
MODULE_PATH = os.path.join(SRC_DIR, "app.py")

spec = importlib.util.spec_from_file_location("assignment_app", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

if hasattr(module, "app"):
    port = int(os.environ.get("PORT", 5000))
    module.app.run(debug=True, host="0.0.0.0", port=port)
else:
    raise RuntimeError("Failed to load Flask app from src-election-system/app.py")
