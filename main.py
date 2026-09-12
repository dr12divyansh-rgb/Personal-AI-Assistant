import time

from speech.speech import speak, take_command
from core.router import AssistantRouter
from core.context import AssistantContext


# =========================================================
# ASSISTANT STATE
# =========================================================

assistant_awake = False


# =========================================================
# CONTEXT AND ROUTER
# =========================================================

context = AssistantContext()

router = AssistantRouter(context)


# =========================================================
# START ASSISTANT
# =========================================================

speak("September is now online")


# =========================================================
# DIRECT COMMANDS
# =========================================================

DIRECT_COMMANDS = [

    "play",
    "pause",
    "resume",
    "next",
    "previous",
    "volume"

]


# =========================================================
# MAIN LOOP
# =========================================================

while True:

    # =====================================================
    # SLEEP MODE
    # =====================================================

    if not assistant_awake:

        print(
            "Waiting for wake word..."
        )

        query = take_command(
            silent=True
        )

        if not query:

            continue

        query = query.lower().strip()

        # -------------------------------------------------
        # WAKE SEPTEMBER
        # -------------------------------------------------

        if (
            "september" in query
            or "wake up" in query
        ):

            assistant_awake = True

            if "september" in query:

                speak(
                    "Yes, how can I assist you?"
                )

            else:

                speak(
                    "I am awake now, "
                    "how can I assist you?"
                )

        continue

    # =====================================================
    # AWAKE MODE
    # =====================================================

    query = take_command(
        silent=False
    )

    if not query:

        continue

    query = query.lower().strip()

    print(
        "You said:",
        query
    )

    # =====================================================
    # WAKE-WORD-ONLY QUERIES
    # =====================================================

    wake_phrases = [

        "september",
        "hey september",
        "hi september",
        "okay september",
        "ok september"

    ]

    if query in wake_phrases:

        speak(
            "Yes, how can I assist you?"
        )

        continue

    # =====================================================
    # PROCESS COMMAND
    # =====================================================

    # Reset sleep request before processing
    context.set(
        "sleep_requested",
        False
    )

    router.process(
        query
    )

    # =====================================================
    # CHECK WHETHER SEPTEMBER WAS ASKED TO SLEEP
    # =====================================================

    if context.get(
        "sleep_requested"
    ):

        speak(
            "Going to sleep"
        )

        assistant_awake = False

        context.set(
            "sleep_requested",
            False
        )

        continue