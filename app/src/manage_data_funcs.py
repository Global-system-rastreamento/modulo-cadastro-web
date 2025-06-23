import json

def load_cloud():
    try:
        with open("./data/event_register_data.json", "r") as f:
            return json.load(f)
    except:
        return {}

def load_data():
    try:
        cloud_data = load_cloud()
        return cloud_data
    except:
        return {}
    
def save_data(data):
    try:
        return send_cloud_data(data)
    except:
        return False

def send_cloud_data(data):
    try:
        with open("./data/event_register_data.json", "w") as f:
            json.dump(data, f)
        return True
    except:
        return False