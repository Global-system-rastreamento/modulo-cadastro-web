import os

def apply_general_settings():
    if not os.path.exists("./data"):
        os.makedirs("./data", exist_ok=True)
    if not os.path.exists("./app/data/uploads"):
        os.makedirs("./app/data/uploads", exist_ok=True)
    if not os.path.exists("./app/data/uploads/spc"):
        os.makedirs("./app/data/uploads/spc", exist_ok=True)
    if not os.path.exists("./app/data/uploads/contract"):
        os.makedirs("./app/data/uploads/contract", exist_ok=True)
    if not os.path.exists("/app/data/uploads/contract/pdf"):
        os.makedirs("./app/data/uploads/contract/pdf", exist_ok=True)
    if not os.path.exists("/app/data/uploads/contract/docx"):
        os.makedirs("./app/data/uploads/contract/docx", exist_ok=True)