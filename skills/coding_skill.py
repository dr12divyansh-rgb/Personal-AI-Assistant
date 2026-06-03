from core.base_skill import BaseSkill
from speech.speech import speak

from code_checker import check_code
from compiler_checker import compile_check


class CodingSkill(BaseSkill):

    def __init__(self, context):
        self.context = context
    
    def can_handle(self, query):

        keywords = [

            "code",
            "compile",
            "program",
            "syntax"
        ]

        return any(word in query for word in keywords)

    def handle(self, query):

        query = query.lower()

        if "check" in query:

            speak("Checking your code")

            with open("test.cpp", "r") as file:

                code = file.read()

            check_code(code)

        elif "compile" in query:

            speak("Compiling your code")

            compile_check("test.cpp")

        else:

            speak("Coding command not recognized")