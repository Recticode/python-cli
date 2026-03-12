import subprocess
import os
import json
import requests

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
