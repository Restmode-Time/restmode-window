import requests

API_BASE = "https://your-backend.com/api"  # Change to your real API base URL

def register_user(email, password, name, location):
    resp = requests.post(f"{API_BASE}/register", json={
        "email": email,
        "password": password,
        "name": name,
        "location": location
    })
    resp.raise_for_status()
    return resp.json()

def login_user(email, password):
    resp = requests.post(f"{API_BASE}/login", json={
        "email": email,
        "password": password
    })
    resp.raise_for_status()
    return resp.json()

def get_user_info(user_id, token):
    resp = requests.get(
        f"{API_BASE}/user/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    resp.raise_for_status()
    return resp.json() 