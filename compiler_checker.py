import subprocess
import re
from text_to_speech import speak

def compile_check(file):

    result = subprocess.run(
        ["g++", "-fsyntax-only", file],
        capture_output=True,
        text=True
    )

    if result.stderr:

        errors = result.stderr.split("\n")

        for line in errors:

            if "error:" in line:

                print(line)

                # Extract line number
                match = re.search(r":(\d+):\d+:", line)

                if match:
                    line_no = match.group(1)
                else:
                    line_no = "unknown"

                # Convert compiler message to human message
                if "expected ';'" in line:
                    message = f"Divyansh, you forgot a semicolon on line {line_no}"

                elif "was not declared in this scope" in line:
                    message = f"Divyansh, there is an undeclared variable on line {line_no}"

                else:
                    message = f"Divyansh, there is a syntax error on line {line_no}"

                speak(message)

    else:

        message = "Code compiled successfully with no errors."
        print(message)
        speak(message)