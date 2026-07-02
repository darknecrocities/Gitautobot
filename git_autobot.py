import subprocess
import time
import sys
import os

# --- Configuration ---
REPO_PATH = os.getcwd()
FILE_TO_MODIFY = "README.md"
COMMIT_MESSAGE = "commit"
REVERT_MESSAGE = "random message it will go back to original"
DELAY = 1  # Seconds between pushes

def run_command(command):
    """Executes a shell command and returns the output."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Stderr: {e.stderr}")
        return None

def get_original_content():
    """Reads the current content of the file."""
    if os.path.exists(FILE_TO_MODIFY):
        with open(FILE_TO_MODIFY, "r") as f:
            return f.read()
    return ""

def git_push():
    """Tries to push to remote. If it fails, pulls with rebase and retries."""
    if run_command("git push origin main") is None:
        print("[!] Push rejected. Pulling latest changes from remote and rebasing...")
        run_command("git pull --rebase origin main")
        print("[!] Retrying push...")
        run_command("git push origin main")

def restore_original(content):
    """Restores the file to its original content and pushes."""
    print("\n[!] Interrupt caught. Restoring original state...")
    with open(FILE_TO_MODIFY, "w") as f:
        f.write(content)
    
    run_command("git add .")
    run_command(f'git commit -m "{REVERT_MESSAGE}"')
    git_push()
    print("[+] Successfully reverted and pushed. Exiting.")

def main():
    print("--- Git Auto-Commit Bot Started ---")
    print(f"Modifying: {FILE_TO_MODIFY}")
    print("Press Ctrl+C to stop and revert.")

    # Pull latest changes from remote at startup to ensure clean state
    print("[+] Syncing with remote repository...")
    run_command("git pull --rebase origin main")

    original_content = get_original_content()

    try:
        count = 1
        while True:
            # Add a white space to the end of the file
            with open(FILE_TO_MODIFY, "a") as f:
                f.write(" ")
            
            # Git steps
            print(f"[{count}] Adding, committing, and pushing...")
            run_command("git add .")
            run_command(f'git commit -m "{COMMIT_MESSAGE}"')
            git_push()
            
            count += 1
            time.sleep(DELAY)

    except KeyboardInterrupt:
        restore_original(original_content)
        sys.exit(0)

if __name__ == "__main__":
    main()
