# Streamlit Cloud Entry Point
# Directs to app_v2/app.py
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_V2_DIR = os.path.join(BASE_DIR, "app_v2")

if APP_V2_DIR not in sys.path:
    sys.path.insert(0, APP_V2_DIR)

# Change working directory so relative dataset paths resolve cleanly
os.chdir(APP_V2_DIR)

# Run app_v2/app.py logic
with open(os.path.join(APP_V2_DIR, "app.py"), "r", encoding="utf-8") as f:
    code = f.read()

exec(code, globals())
