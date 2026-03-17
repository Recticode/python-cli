import typer
from rich import print
from functools import wraps
from time import sleep
from git import clone_repo, save_access_token, get_access_token, get_user_data, remove_access_token, get_user_code
import requests

app = typer.Typer()

def require_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        access_token = get_access_token()
        if not access_token:
            print("[red]You must login first[/red]")
            raise typer.Exit()
        return func(*args, **kwargs)
    return wrapper

@app.command()
def login():
    access_token = get_access_token()
    if not access_token:
        headers = {
            "Accept": "application/json"
        }

        device_code, verification_uri, expires_in, user_code, interval = get_user_code()

        print(f"Go to {verification_uri} and enter code [bold]{user_code}[/bold]")

        for i in range(expires_in // interval):
            poll_values = {
                "client_id": "Ov23lizX5wFSpnR89gKJ",
                "device_code": device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
            }
            poll_post = requests.post("https://github.com/login/oauth/access_token", data=poll_values, headers=headers)

            poll_json = poll_post.json()

            if "access_token" in poll_json:
                access_token = poll_json['access_token']

                username, email, name = get_user_data(access_token=access_token)

                save_access_token(access_token=access_token)
                print(f"[green]✓ Logged in as {name}[/green]")
                break

            if "error" in poll_json:
                if poll_json["error"] == "authorization_pending":
                    sleep(interval)
                    continue
                elif poll_json["error"] == "slow_down":
                    interval += 5
                    sleep(interval)
                elif poll_json["error"] == "expired_token":
                    print("[red]Device code expired, try login again[/red]")
                    break
    else:
        username, email, name = get_user_data(access_token=access_token)

        print("You are already logged in")

@app.command()
@require_login
def whoami():
    access_token = get_access_token()
    username, email, name = get_user_data(access_token=access_token)
    print("Hi", name)

@app.command()
def logout():
    access_token = get_access_token()
    if not access_token:
        print("You are not logged in")
    else:
        remove_access_token()

        print("[yellow]✓ Logged out[/yellow]")


@app.command()
@require_login
def start(challenge_name):
    access_token = get_access_token()

    request_url = "https://api.recticode.com/challenge_repo/"

    response = requests.get(request_url + challenge_name + "?token=" + access_token)
    if response.status_code == 200:
        if "error" in response.json():
            print(response.json()['error'])
        else:
            clone_repo(response.json()['repo_name'])
            print(f"[green]Challenge cloned![/green] cd {challenge_name} to start")
    else:
        print("Error occurred")

@app.command()
@require_login
def list_challenges():
    access_token = get_access_token()

    request_url = "https://api.recticode.com/list_challenges?token=" + access_token

    response = requests.get(request_url)
    if response.status_code == 200:
        challenges = response.json()['challenges']

        print("[bold][yellow]All Challenges[/yellow][/bold]")
        for challenge in challenges:
            print(f"[bold]{challenge['name']}[/bold]: {challenge['description']} ({challenge['language']})")
    else:
        print("Error occurred")

if __name__ == "__main__":
    app()
