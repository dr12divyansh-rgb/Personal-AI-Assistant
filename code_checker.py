import difflib
import re
from text_to_speech import speak

keywords = {
    "int","float","double","char","bool","string","long","short",
    "if","else","for","while","do","switch","case","break","continue",
    "return","void","cout","cin","endl",
    "include","using","namespace","std","main","printf","scanf","iostream"
}

def check_code(code):

    lines = code.split("\n")

    for line_no, line in enumerate(lines, start=1):

        # remove text inside quotes
        line = re.sub(r'".*?"', '', line)

        words = re.findall(r'[A-Za-z_]+', line)

        for word in words:

            word = word.lower()

            # ignore small variable names
            if len(word) <= 2:
                continue

            # ignore known keywords
            if word in keywords:
                continue

            # ignore words that look like function names
            if re.search(rf"{word}\s*\(", line):
                continue

            suggestion = difflib.get_close_matches(word, keywords, n=1)

            if suggestion:
                message = f"Error on line {line_no}. Unknown word {word}. Did you mean {suggestion[0]}?"
                print(message)
                speak(message)