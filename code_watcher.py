import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from code_checker import check_code
from compiler_checker import compile_check

FILE_TO_WATCH = "test.cpp"

last_run_time = 0   # debounce timer


class CodeHandler(FileSystemEventHandler):

    def on_any_event(self, event):

        global last_run_time

        if event.is_directory:
            return

        filename = os.path.basename(event.src_path)

        # debug: see every event
        print("EVENT:", event.event_type, event.src_path)

        if filename != FILE_TO_WATCH:
            return

        if event.event_type not in ["modified", "created"]:
            return

        current_time = time.time()

        # Ignore repeated events within 1 second
        if current_time - last_run_time < 1:
            return

        last_run_time = current_time

        print("File change detected. Checking code...")

        try:
            with open(FILE_TO_WATCH, "r") as file:
                code = file.read()

            check_code(code)
            compile_check(FILE_TO_WATCH)

        except Exception as e:
            print("File read error:", e)


observer = Observer()
event_handler = CodeHandler()

observer.schedule(event_handler, ".", recursive=False)
observer.start()

print("Watching code file...")

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    observer.stop()

observer.join()