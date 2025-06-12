#!/usr/bin/env python3

from pathlib import Path
import os
import subprocess
import sys
import glob
import locale

if len(sys.argv) < 2:
    print("ZIP file was not provided")
    exit()

file_name = sys.argv[1]

current_language = locale.getlocale()[0]

base_name = os.path.basename(file_name)
name_no_ext = os.path.splitext(base_name)[0]
clean_name = name_no_ext.replace(" ", "_")

hash_filename = f"hashfile_{clean_name}"

os.chdir(os.path.dirname(os.path.abspath(__file__)))
current_platform = sys.platform

if not os.path.exists("SecLists"):
    subprocess.run(['git', 'clone', '--depth=1', 'https://github.com/danielmiessler/SecLists.git'])
    subprocess.run(['tar', '-xvzf', 'SecLists/Passwords/Leaked-Databases/rockyou.txt.tar.gz', '-C', 'SecLists/Passwords/Leaked-Databases/'])
    subprocess.run(['tar', '-xvzf', 'SecLists/Passwords/Leaked-Databases/rockyou-withcount.txt.tar.gz', '-C', 'SecLists/Passwords/Leaked-Databases/'])

if current_platform == "win32":
    john_the_ripper_folder = glob.glob("john*-win64*/")

    if john_the_ripper_folder:
        os.chdir(john_the_ripper_folder[0])
    else:
        if current_language == "pt_BR":
            print("Nenhuma pasta contendo John the Ripper foi encontrada.")
        else:
            print("No matching John the Ripper folder found.")
        subprocess.run(['curl', '-O', 'https://www.openwall.com/john/k/john-1.9.0-jumbo-1-win64.zip'])
        subprocess.run(['tar', '-xf', 'john-1.9.0-jumbo-1-win64.zip'])
        os.remove("john-1.9.0-jumbo-1-win64.zip")
        john_the_ripper_folder = glob.glob("john*-win64*/")
        if john_the_ripper_folder:
            os.chdir(john_the_ripper_folder[0])

    with open(hash_filename, 'w') as outfile:
        subprocess.run(['./run/zip2john.exe', file_name], stdout=outfile, stderr=subprocess.DEVNULL)

    password_folder_path = Path('../SecLists/Passwords')
    miscellaneous_folder_path = Path('../SecLists/Miscellaneous')
    found_1g = False
    password_line = None

    def run_john_with_wordlists(wordlist_paths, hash_filename, current_language):
        for file in wordlist_paths:
            if not file.is_file():
                continue

            process = subprocess.Popen(
                ['./run/john.exe', f'--wordlist={str(file)}', f'./{hash_filename}'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )

            previous_line = ""
            password_line = ""

            for line in process.stdout:
                if "No password hashes loaded" in line:
                    print("No file has been found." if current_language != "pt_BR" else "Nenhuma arquivo foi encontrado.")
                    sys.exit(0)

                if "No password hashes left to crack" in line:
                    process.terminate()
                    result = subprocess.run(
                        ['./run/john.exe', '--show', f'./{hash_filename}'],
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        errors='ignore'
                    )
                    if result.stdout:
                        for show_line in result.stdout.strip().splitlines():
                            parts = show_line.split(':')
                            if len(parts) >= 2:
                                password = parts[1].strip()
                                print("Password already found: " + password if current_language != "pt_BR" else f"Senha já encontrada: {password}")
                                break
                    os.remove(f'./{hash_filename}')
                    sys.exit(0)

                if line.startswith(('1g ', '1g:', '1g\t')):
                    password_line = previous_line.strip()
                    process.terminate()
                    if current_language == "pt_BR":
                        print(f"Senha encontrada: {password_line}")
                    else:
                        print(f"Password found: {password_line}")
                    os.remove(f'./{hash_filename}')
                    return True  # <<< password found

                previous_line = line

            process.wait()

        return False  # <<< no password found

    all_wordlists = list(password_folder_path.rglob('*.txt')) + list(miscellaneous_folder_path.rglob('*.txt'))

    found_1g = run_john_with_wordlists(all_wordlists, hash_filename, current_language)

    if not found_1g:
        print("\nNo password found using wordlists. Starting incremental mode...\n")
        process = subprocess.Popen(
            ['./run/john.exe', f'./{hash_filename}', '--incremental'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        for line in process.stdout:
#            print(line, end='')

            if "No password hashes loaded" in line:
                print("No file has been found.")
                sys.exit(0)

            if "No password hashes left to crack" in line:
                process.terminate()
                result = subprocess.run(
                    ['./run/john.exe', '--show', f'./{hash_filename}'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )
                if result.stdout:
                    for show_line in result.stdout.strip().splitlines():
                        parts = show_line.split(':')
                        if len(parts) >= 2:
                            password = parts[1].strip()
                            print(f"Password already found: {password}")
                            break
                else:
                    print("No output received from john --show.")
#                print("Exiting.")
                os.remove(f'./{hash_filename}')
                sys.exit(0)

        process.wait()

        # Show the found password (if any)
        result = subprocess.run(
            ['./run/john.exe', '--show', f'./{hash_filename}'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        if result.stdout:
            for show_line in result.stdout.strip().splitlines():
                parts = show_line.split(':')
                if len(parts) >= 2:
                    password = parts[1].strip()
                    print(f"Password already found: {password}")
                    break
        else:
            print("No output received from john --show.")