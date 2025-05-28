from pathlib import Path
import os
import subprocess
import sys
import glob

if len(sys.argv) < 2:
    print("ZIP file was not provided")
    exit()

file_name = sys.argv[1]

os.chdir(os.path.dirname(os.path.abspath(__file__)))

current_platform = sys.platform

if not os.path.exists("SecLists"):
    subprocess.run(['git', 'clone', '--depth=1', 'https://github.com/danielmiessler/SecLists.git'])
    subprocess.run(['tar', '-xvzf', 'SecLists/Passwords/Leaked-Databases/rockyou.txt.tar.gz', '-C' ,'SecLists/Passwords/Leaked-Databases/'])

john_the_ripper_folder = glob.glob("john*-win64*/")

if john_the_ripper_folder:
    os.chdir(john_the_ripper_folder[0])
else:
    print("No matching folder found.")
    if current_platform == "win32":
        subprocess.run(['curl', '-O', 'https://www.openwall.com/john/k/john-1.9.0-jumbo-1-win64.zip'])
        subprocess.run(['tar', '-xf', 'john-1.9.0-jumbo-1-win64.zip'])
        john_the_ripper_folder = glob.glob("john*-win64*/")
        if john_the_ripper_folder:
            os.chdir(john_the_ripper_folder[0])

with open('hashfile', 'w') as outfile:
    subprocess.run(['./run/zip2john.exe', file_name], stdout=outfile)

folder_path = Path('../SecLists/Passwords')

for file in folder_path.rglob('*.txt'):
    if file.is_file():
        process = subprocess.Popen(
            ['./run/john.exe', f'--wordlist={str(file)}', './hashfile'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        found_1g = False
        password_line = None

        for line in process.stdout:
            print(line, end='')  # Optional live output

            # Check if the line starts with '1g' followed by space or colon or tab,
            # meaning it's the password line
            if line.startswith('1g ') or line.startswith('1g:') or line.startswith('1g\t'):
                password_line = line.strip()
                print("Detected password line starting with '1g', stopping.")
                process.terminate()
                found_1g = True
                break

        process.wait()

        if password_line:
            print(f"Password found: {password_line}")

        if found_1g:
            break

if not found_1g:
    print("\nNo password found using wordlists. Starting incremental mode...\n")
    process = subprocess.Popen(
        ['./run/john.exe', './hashfile', '--incremental'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    for line in process.stdout:
        print(line, end='')  # Show progress

    process.wait()

    # Show the found password (if any)
    subprocess.run(['./run/john.exe', '--show', './hashfile'])