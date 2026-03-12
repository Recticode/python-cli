import typer
import subprocess
from rich import print

app = typer.Typer()

challenges = {"python": {"example-python": "https://github.com/Recticode/example-python"}}
challenge_names = {"example-python": challenges['python']['example-python']}

@app.command()
def start(challenge_name):
    if challenge_name in challenge_names:
        cmd = ["git", "clone", challenge_names[challenge_name]]
        subprocess.run(cmd, check=True)
        print("cloned repo")
    else:
        print("not a challenge name")

@app.command()
def list_challenges():
    print("[bold][yellow]All Challenges[/yellow][/bold]")
    for language in challenges:
        print(f"[bold][green]{language.title()}[/bold][/green]")
        for challenge in challenges[language]:
            print(challenge)

if __name__ == "__main__":
    app()
