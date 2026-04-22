import typer
from rich import print
from functools import wraps
from time import sleep
from recticode.git_code import clone_repo, save_access_token, get_access_token, get_user_data, remove_access_token, get_user_code
import requests
import os.path
import subprocess
import sys
import shutil
import json

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
            difficulty = challenge['difficulty']
            difficulty_text = ""
            if difficulty == "easy":
                difficulty_text = f"[green][{difficulty.title()}][/green]"
            elif difficulty == "medium":
                difficulty_text = f"[dark_orange][{difficulty.title()}][/dark_orange]"
            else:
                difficulty_text = f"[red][{difficulty.title()}][/red]"
            print(f"[bold]{challenge['name']}[/bold]: {challenge['description']} {difficulty_text} ({challenge['language']})")
    else:
        print("Error occurred")

# @app.command()
# @require_login
# def check():
#     if os.path.exists("challenge.json"):
#         env = os.environ.copy()
#         env["PYTHONPATH"] = "."
#         subprocess.run(
#             [sys.executable, "-m", "pytest", "tests/"],
#             env=env
#         )
#     else:
#         print("This is not a valid challenge")

@app.command()
@require_login
def passed_challenges():
    access_token = get_access_token()

    request_url = "https://api.recticode.com/passed_challenges?token=" + access_token

    response = requests.get(request_url)
    if response.status_code == 200:
        challenges = response.json()['challenges']

        print("[bold][green]Passed Challenges[/green][/bold]")
        for challenge in challenges:
            print(f"[bold]{challenge['challenge_name']}[/bold]")
    else:
        print("Error occurred")


@app.command()
@require_login
def submit():
    if os.path.exists("challenge.json"):
        access_token = get_access_token()

        # creates a zip file which contains all the files in the src folder
        shutil.make_archive("zip_file", 'zip', "src")

        # gets the challenge name from challenge.json
        with open("challenge.json") as f:
            challenge_name = json.load(f)["name"]

        request_url = f"https://api.recticode.com/submit/{challenge_name}?token=" + access_token

        # sends the request with the zip file
        with open("zip_file.zip", "rb") as f:
            response = requests.post(
                request_url,
                files={'file': ("zip_file.zip", f, "application/zip")}
            )

        # checks response and shows relevant text
        if response.status_code == 200:
            r_json = response.json()
            print(f"[yellow]Tests passed: {r_json['correct']}/{r_json['total']}[/yellow]")
            if r_json['passed']:
                print("[green]You passed all the tests! Challenge complete![/green]")
            else:
                print("[red]You did not pass all the tests[/red]")
        else:
            print(f"[red]request failed ({response.status_code})[/red]")
            try:
                print(response.json()['detail'])
            except Exception:
                print(response.text)

        os.remove("zip_file.zip")
    else:
        print("This is not a valid challenge")

if __name__ == "__main__":
    app()
