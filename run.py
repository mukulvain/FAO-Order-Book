import multiprocessing
import os
import subprocess
import sys

FILES = 10
DATES = [
    "03012022",
]
INTERVAL = sys.argv[1]

commands = []
for date in DATES:
    os.makedirs(os.path.dirname(f"LOB/{date}/"), exist_ok=True)
    for num in range(FILES):
        commands.append([sys.executable, "main.py", date, str(num+1), INTERVAL])


def run_command(cmd):
    """Runs a shell command and prints the output."""
    process_id = multiprocessing.current_process().pid
    print(f"Executing: {cmd} on Process ID {process_id}")

    # Execute the command
    result = subprocess.run(cmd, shell=False, text=True, capture_output=False)
    if not result.returncode:
        print(f"[Process {process_id}] Success! Output:\n{result.stdout.strip()}")
    else:
        print(f"[Process {process_id}] ERROR (Exit Code {result.returncode})")
        print(f"--- Standard Error ---\n{result.stderr.strip()}")
        print(f"--- Standard Output ---\n{result.stdout.strip()}")


if __name__ == "__main__":
    num_cores = multiprocessing.cpu_count()
    with multiprocessing.Pool(processes=num_cores) as pool:
        pool.map(run_command, commands)  # Distribute commands dynamically

    print("\nAll commands entered.")
