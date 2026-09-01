import time
import ollama

from core.base_skill import BaseSkill
from speech.speech import speak

from core.memory import add_conversation


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
                        "You are September, a concise personal AI assistant "
                        "created by Divyansh. "
                        "Give short, direct answers suitable for voice."
                    )
                },
                {
                    "role": "user",
                    "content": query
                }
            ]

            print("Sending request to Ollama...")

            start_time = time.time()

            response = ollama.chat(
                model="qwen2.5:1.5b",
                messages=messages,
                options={
                    "temperature": 0.7,
                    "num_predict": 60
                },
                keep_alive="30m"
            )

            total = time.time() - start_time
            print(f"Ollama total time: {total:.2f} seconds")

            print(f"Load time: {response.get('load_duration', 0) / 1e9:.2f} sec")
            print(f"Prompt processing: {response.get('prompt_eval_duration', 0) / 1e9:.2f} sec")
            print(f"Generation: {response.get('eval_duration', 0) / 1e9:.2f} sec")

            end_time = time.time()

            print(f"Ollama response time: {end_time - start_time:.2f} seconds")
            print("Ollama replied")

            reply = response["message"]["content"].strip()

            reply = reply.replace("\n", " ")
            reply = reply.replace("*", "")
            reply = reply.replace("#", "")

            add_conversation(query, reply)

            print("Assistant:", reply)

            short_reply = reply[:300]

            print("Speaking:", short_reply)

            speak(short_reply)

        except Exception as e:

            print("Ollama Error:", e)

            speak("Local AI is currently unavailable")