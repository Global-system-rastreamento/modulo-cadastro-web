import os

def apply_general_settings():
    if not os.path.exists("./data"):
        os.makedirs("./data", exist_ok=True)