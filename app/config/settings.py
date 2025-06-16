import os

def apply_general_settings():
    if not os.path.exists("./data"):
        os.makedirs("./data", exist_ok=True)
    if not os.path.exists("./data/uploads"):
        os.makedirs("./data/uploads", exist_ok=True)
    if not os.path.exists("./data/uploads/spc"):
        os.makedirs("./data/uploads/spc", exist_ok=True)
    if not os.path.exists("./data/uploads/contract"):
        os.makedirs("./data/uploads/contract", exist_ok=True)
    if not os.path.exists("/data/uploads/contract/pdf"):
        os.makedirs("./data/uploads/contract/pdf", exist_ok=True)
    if not os.path.exists("/data/uploads/contract/docx"):
        os.makedirs("./data/uploads/contract/docx", exist_ok=True)