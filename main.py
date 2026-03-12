import typer
from rich import print
import requests
from time import sleep
from git import clone_repo, save_access_token, get_access_token, get_user_data, remove_access_token

app = typer.Typer()

challenges = {"python": {"example-python": "https://github.com/Recticode/example-python"}}
challenge_names = {"example-python": challenges['python']['example-python']}

@app.command()
def login():
    access_token = get_access_token()
    if not access_token:
        url = "https://github.com/login/device/code"

        values = {
            "client_id": "Ov23lizX5wFSpnR89gKJ",
            "scope": "read:user repo"
        }

        headers = {
            "Accept": "application/json"
        }

        r = requests.post(url, data=values, headers=headers)

        json = r.json()

        device_code = json["device_code"]
        verification_uri = json['verification_uri']
        expires_in = json['expires_in']
        user_code = json['user_code']
        interval = json['interval']

        print(f"Go to {verification_uri} and enter code [bold]{user_code}[/bold]")

        for i in range(int(expires_in / interval)):
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
                print(f"Hi {name}. You are logged in")
                break

            sleep(interval)
    else:
        username, email, name = get_user_data(access_token=access_token)

        print("You are already logged in")

@app.command()
def whoami():
    access_token = get_access_token()
    if not access_token:
        print("You are not logged in")
    else:
        username, email, name = get_user_data(access_token=access_token)

        print("Hi", name)

@app.command()
def logout():
    access_token = get_access_token()
    if not access_token:
        print("You are not logged in")
    else:
        remove_access_token()

        print("Logged out")


@app.command()
def start(challenge_name):
    if challenge_name in challenge_names:
        clone_repo(challenge_names[challenge_name])
        print("Cloned repo")
    else:
        print("Not a challenge name")

@app.command()
def list_challenges():
    print("[bold][yellow]All Challenges[/yellow][/bold]")
    for language in challenges:
        print(f"[bold][green]{language.title()}[/bold][/green]")
        for challenge in challenges[language]:
            print(challenge)

if __name__ == "__main__":
    app()
