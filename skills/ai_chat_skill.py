import ollama

from core.base_skill import BaseSkill
from speech.speech import speak

from core.memory import (
    add_conversation,
    get_recent_conversations
)


class AIChatSkill(BaseSkill):

    def __init__(self, context):

        self.context = context

    def can_handle(self, query):

        # fallback skill
        return True

    def handle(self, query):

        try:

            messages = [

                {
                    "role": "system",
                    "content": (
                        "You are Jarvis, a smart personal AI assistant "
                        "created by Divyansh."
                    )
                }
            ]


            recent = get_recent_conversations()

            for convo in recent:

                messages.append({

                    "role": "user",
                    "content": convo["user"]
                })

                messages.append({

                    "role": "assistant",
                    "content": convo["assistant"]
                })


            messages.append({

                "role": "user",
                "content": query
            })


            print("Sending request to Ollama...")
            response = ollama.chat(

                model="phi3",

                messages=messages,

            )
            print("Ollama replied")


            reply = response["message"]["content"]
            reply = reply.strip()

            # Remove problematic formatting
            reply = reply.replace("\n", " ")
            reply = reply.replace("*", "")
            reply = reply.replace("#", "")
            add_conversation(query, reply)
            print("Assistant:", reply)

            # Keep response short for TTS
            short_reply = reply[:200]
            print("Speaking:", short_reply)
            speak(str(short_reply))

        except Exception as e:

            print("Ollama Error:", e)

            speak("Local AI is currently unavailable")