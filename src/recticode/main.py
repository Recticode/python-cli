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
    existing_token = get_access_token()
    if existing_token:
        try:
            username, email, name = get_user_data(access_token=existing_token)
            if username:
                print(f"[green]You are already logged in as {name}[/green]")
                return
            else:
                print("[yellow]Stored token invalid. Re-authenticating...[/yellow]")
                remove_access_token()
        except Exception:
            print("[yellow]Stored token invalid. Re-authenticating...[/yellow]")
            remove_access_token()

    headers = {"Accept": "application/json"}

    try:
        device_code, verification_uri, expires_in, user_code, interval = get_user_code()
    except Exception as e:
        print(f"[red]Failed to start login process: {e}[/red]")
        raise typer.Exit()

    print(f"\nGo to [bold]{verification_uri}[/bold]")
    print(f"And enter code: [bold]{user_code}[/bold]\n")

    elapsed = 0

    while elapsed < expires_in:
        sleep(interval)
        elapsed += interval

        poll_values = {
            "client_id": "Ov23lizX5wFSpnR89gKJ",
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
        }

        try:
            poll_post = requests.post(
                "https://github.com/login/oauth/access_token",
                data=poll_values,
                headers=headers,
                timeout=10
            )
        except requests.RequestException:
            print("[red]Network error while polling GitHub[/red]")
            raise typer.Exit()

        if poll_post.status_code != 200:
            print(f"[red]GitHub returned status {poll_post.status_code}[/red]")
            raise typer.Exit()

        poll_json = poll_post.json()

        # success case
        if "access_token" in poll_json:
            access_token = poll_json["access_token"]

            try:
                username, email, name = get_user_data(access_token=access_token)
            except Exception:
                print("[red]Failed to fetch user data from GitHub[/red]")
                raise typer.Exit()

            if not username:
                print("[red]Login failed: could not retrieve user info[/red]")
                raise typer.Exit()

            save_access_token(access_token)

            try:
                requests.get(
                    "https://api.recticode.com/login",
                    params={"token": access_token},
                    timeout=10
                )
            except requests.RequestException:
                print("[yellow]Warning: could not notify recticode backend[/yellow]")

            print(f"[green]✓ Logged in as {name}[/green]")
            return

        # error cases
        if "error" in poll_json:
            error = poll_json["error"]

            if error == "authorization_pending":
                continue

            elif error == "slow_down":
                interval += 5
                continue

            elif error == "expired_token":
                print("[red]Device code expired. Please run login again.[/red]")
                raise typer.Exit()

            else:
                print(f"[red]Login failed: {error}[/red]")
                raise typer.Exit()

    print("[red]Login timed out. Please try again.[/red]")
    raise typer.Exit()

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
