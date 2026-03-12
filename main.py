import typer
import subprocess

app = typer.Typer()

@app.command()
def start(challenge_name):
    challenges = {"example-python": "https://github.com/Recticode/example-python"}
    if challenge_name in challenges:
        cmd = ["git", "clone", challenges[challenge_name]]

        subprocess.run(cmd, check=True)
        print("cloned repo")
    else:
        print("not a challenge name")

@app.command()
def hi():
    print("hi!")

if __name__ == "__main__":
    app()
