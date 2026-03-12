import subprocess
import os
import json
import requests

def get_user_code():
    url = "https://github.com/login/device/code"

    values = {
        "client_id": "Ov23lizX5wFSpnR89gKJ",
        "scope": "read:user repo"
    }

    headers = {
        "Accept": "application/json"
    }

    r = requests.post(url, data=values, headers=headers)

    r_json = r.json()

    device_code = r_json["device_code"]
    verification_uri = r_json['verification_uri']
    expires_in = r_json['expires_in']
    user_code = r_json['user_code']
    interval = r_json['interval']

    return device_code, verification_uri, expires_in, user_code, interval

def get_access_token():
    try:
        config_dir = os.path.expanduser("~/.config/recticode")
        os.makedirs(config_dir, exist_ok=True)

        token_path = os.path.join(config_dir, "token.json")
        with open(token_path) as f:
            token = json.load(f)["access_token"]
        return token
    except:
        return False


def save_access_token(access_token):
    try:
        config_dir = os.path.expanduser("~/.config/recticode")
        os.makedirs(config_dir, exist_ok=True)

        token_path = os.path.join(config_dir, "token.json")

        data = {"access_token": access_token}

        with open(token_path, "w") as f:
            json.dump(data, f)

        return True
    except:
        return False


def clone_repo(url):
    cmd = ["git", "clone", url]
    subprocess.run(cmd, check=True)
    return True

def get_user_data(access_token):
    check_headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json"
    }

    check_post = requests.get("https://api.github.com/user", headers=check_headers)

    user_json = check_post.json()
    username = user_json['login']
    email = user_json['email']
    name = user_json['name']

    return username, email, name

def remove_access_token():
    try:
        config_dir = os.path.expanduser("~/.config/recticode")
        os.makedirs(config_dir, exist_ok=True)

        token_path = os.path.join(config_dir, "token.json")

        os.remove(token_path)

        return True
    except:
        return False
