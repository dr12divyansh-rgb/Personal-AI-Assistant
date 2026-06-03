import json
import os


MEMORY_FILE = "memory/conversations.json"


def load_memory():

    if not os.path.exists(MEMORY_FILE):

        return []

    with open(MEMORY_FILE, "r") as file:

        return json.load(file)


def save_memory(memory):

    with open(MEMORY_FILE, "w") as file:

        json.dump(memory, file, indent=4)


def add_conversation(user, assistant):

    memory = load_memory()

    memory.append({

        "user": user,
        "assistant": assistant
    })

    save_memory(memory)


def get_recent_conversations(limit=1):

    memory = load_memory()

    return memory[-limit:]