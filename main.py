import time
from speech.speech import speak, take_command
from core.router import AssistantRouter
from core.context import AssistantContext

assistant_awake = True
context = AssistantContext()
router = AssistantRouter(context)

speak("Jarvis is now online")


DIRECT_COMMANDS = [

    "play",
    "pause",
    "resume",
    "next",
    "previous",
    "volume"
]


assistant_awake = False

speak("Jarvis is now online")


while True:


    # SLEEP MODE
    if not assistant_awake:

        print("Waiting for wake word...")

        query = take_command(silent=True)


        if not query:

            continue


        query = query.lower()


        if "jarvis" in query or "wake up" in query:

            assistant_awake = True

            if "jarvis" in query:
                speak("Yes, how can I assist you?")
            
            else:
                speak("I am awake now, how can I assist you?")


        continue


    # AWAKE MODE
    query = take_command(silent=False)


    if not query:

        continue


    print("You said:", query)


    query = query.lower()


    # Sleep command
    if "sleep" in query:

        speak("Going to sleep")

        assistant_awake = False

        continue

    # Ignore wake-word-only queries
    wake_phrases = [
        "jarvis",
        "hey jarvis",
        "hi jarvis",
        "okay jarvis",
        "ok jarvis"
    ]
    if query in wake_phrases:
        speak("Yes, How can I assist you?")
        continue


    # Process command
    router.process(query)

#Start the voice assistant by running this file (after activating venv) in this Voice_assistant foler.