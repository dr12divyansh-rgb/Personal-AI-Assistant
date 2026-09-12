import re
import threading
import time
from datetime import datetime, timedelta

from core.base_skill import BaseSkill
from speech.speech import speak


class ReminderSkill(BaseSkill):

    def __init__(self, context):

        self.context = context

        # =================================================
        # START BACKGROUND REMINDER CHECKER
        # =================================================

        self.running = True

        self.thread = threading.Thread(
            target=self._reminder_checker,
            daemon=True
        )

        self.thread.start()

    # =====================================================
    # CAN HANDLE
    # =====================================================

    def can_handle(self, query):

        query = query.lower().strip()

        reminder_keywords = [

            "remind me",
            "set a reminder",
            "reminder"

        ]

        time_keywords = [

            "what time is it",
            "what is the time",
            "tell me the time",
            "current time",

            "what date is it",
            "what is today's date",
            "what date is today",
            "what day is today",
            "today's date",

            "date and time",
            "date & time"

        ]

        # -------------------------------------------------
        # REMINDER COMMAND
        # -------------------------------------------------

        if any(
            keyword in query
            for keyword in reminder_keywords
        ):

            return True

        # -------------------------------------------------
        # DATE / TIME COMMAND
        # -------------------------------------------------

        if any(
            keyword in query
            for keyword in time_keywords
        ):

            return True

        return False

    # =====================================================
    # HANDLE
    # =====================================================

    def handle(self, query):

        query = query.lower().strip()

        # -------------------------------------------------
        # DATE / TIME
        # -------------------------------------------------

        if self._is_time_query(query):

            self._tell_date_time(query)

            return

        # -------------------------------------------------
        # REMINDER
        # -------------------------------------------------

        if "remind me" in query:

            self._create_reminder(query)

            return

        # -------------------------------------------------
        # UNKNOWN
        # -------------------------------------------------

        speak(
            "I can create reminders or tell you "
            "the date and time."
        )

    # =====================================================
    # DATE / TIME DETECTION
    # =====================================================

    def _is_time_query(self, query):

        keywords = [

            "what time is it",
            "what is the time",
            "tell me the time",
            "current time",

            "what date is it",
            "what is today's date",
            "what date is today",
            "what day is today",
            "today's date",

            "date and time",
            "date & time"

        ]

        return any(
            keyword in query
            for keyword in keywords
        )

    # =====================================================
    # TELL DATE / TIME
    # =====================================================

    def _tell_date_time(self, query):

        now = datetime.now()

        # -------------------------------------------------
        # DATE + TIME
        # -------------------------------------------------

        if (
            ("date" in query and "time" in query)
            or "date & time" in query
        ):

            date_string = now.strftime(
                "%A, %d %B %Y"
            )

            time_string = now.strftime(
                "%I:%M %p"
            )

            speak(
                f"Today is {date_string}, "
                f"and the time is {time_string}"
            )

            return

        # -------------------------------------------------
        # TIME ONLY
        # -------------------------------------------------

        if (
            "time" in query
            and "date" not in query
            and "day" not in query
        ):

            time_string = now.strftime(
                "%I:%M %p"
            )

            speak(
                f"The time is {time_string}"
            )

            return

        # -------------------------------------------------
        # DATE / DAY ONLY
        # -------------------------------------------------

        if (
            "date" in query
            or "day" in query
        ):

            date_string = now.strftime(
                "%A, %d %B %Y"
            )

            speak(
                f"Today is {date_string}"
            )

            return

    # =====================================================
    # CREATE REMINDER
    # =====================================================

    def _create_reminder(self, query):

        # -------------------------------------------------
        # REMOVE "REMIND ME"
        # -------------------------------------------------

        reminder_text = query.replace(
            "remind me",
            "",
            1
        ).strip()

        # =================================================
        # "IN X SECONDS / MINUTES / HOURS"
        # =================================================

        match = re.search(
            r"\bin\s+(\d+)\s+(seconds?|minutes?|hours?)\b",
            reminder_text
        )

        if match:

            amount = int(
                match.group(1)
            )

            unit = match.group(2).lower()

            # -------------------------------------------------
            # CALCULATE REMINDER TIME
            # -------------------------------------------------

            if unit.startswith("second"):

                reminder_time = (
                    datetime.now()
                    + timedelta(
                        seconds=amount
                    )
                )

            elif unit.startswith("minute"):

                reminder_time = (
                    datetime.now()
                    + timedelta(
                        minutes=amount
                    )
                )

            else:

                reminder_time = (
                    datetime.now()
                    + timedelta(
                        hours=amount
                    )
                )

            # -------------------------------------------------
            # REMOVE COMPLETE TIME PHRASE
            # -------------------------------------------------

            task = (
                reminder_text[:match.start()]
                + reminder_text[match.end():]
            ).strip()

            # -------------------------------------------------
            # REMOVE OPTIONAL "TO"
            # -------------------------------------------------

            if task.startswith("to "):

                task = task[3:].strip()

            self._save_reminder(
                task,
                reminder_time
            )

            return

        # =================================================
        # "TOMORROW AT X"
        # =================================================

        match = re.search(
            r"\btomorrow\s+at\s+"
            r"(\d{1,2})"
            r"(?::(\d{2}))?"
            r"\s*(am|pm)?\b",
            reminder_text
        )

        if match:

            hour = int(
                match.group(1)
            )

            minute = int(
                match.group(2) or 0
            )

            period = match.group(3)

            # -------------------------------------------------
            # CONVERT 12-HOUR TIME TO 24-HOUR TIME
            # -------------------------------------------------

            if period:

                if (
                    period == "pm"
                    and hour != 12
                ):

                    hour += 12

                elif (
                    period == "am"
                    and hour == 12
                ):

                    hour = 0

            tomorrow = (
                datetime.now()
                + timedelta(days=1)
            )

            reminder_time = tomorrow.replace(

                hour=hour,
                minute=minute,
                second=0,
                microsecond=0

            )

            # -------------------------------------------------
            # REMOVE COMPLETE TIME PHRASE
            # -------------------------------------------------

            task = (
                reminder_text[:match.start()]
                + reminder_text[match.end():]
            ).strip()

            if task.startswith("to "):

                task = task[3:].strip()

            self._save_reminder(
                task,
                reminder_time
            )

            return

        # =================================================
        # "AT X"
        # =================================================

        match = re.search(
            r"\bat\s+"
            r"(\d{1,2})"
            r"(?::(\d{2}))?"
            r"\s*(am|pm)?\b",
            reminder_text
        )

        if match:

            hour = int(
                match.group(1)
            )

            minute = int(
                match.group(2) or 0
            )

            period = match.group(3)

            # -------------------------------------------------
            # CONVERT 12-HOUR TIME TO 24-HOUR TIME
            # -------------------------------------------------

            if period:

                if (
                    period == "pm"
                    and hour != 12
                ):

                    hour += 12

                elif (
                    period == "am"
                    and hour == 12
                ):

                    hour = 0

            now = datetime.now()

            reminder_time = now.replace(

                hour=hour,
                minute=minute,
                second=0,
                microsecond=0

            )

            # -------------------------------------------------
            # IF TIME PASSED, SCHEDULE TOMORROW
            # -------------------------------------------------

            if reminder_time <= now:

                reminder_time += timedelta(
                    days=1
                )

            # -------------------------------------------------
            # REMOVE COMPLETE TIME PHRASE
            # -------------------------------------------------

            task = (
                reminder_text[:match.start()]
                + reminder_text[match.end():]
            ).strip()

            if task.startswith("to "):

                task = task[3:].strip()

            self._save_reminder(
                task,
                reminder_time
            )

            return

        # =================================================
        # NO TIME FOUND
        # =================================================

        speak(
            "When should I remind you?"
        )

    # =====================================================
    # SAVE REMINDER
    # =====================================================

    def _save_reminder(
        self,
        task,
        reminder_time
    ):

        # -------------------------------------------------
        # CHECK TASK
        # -------------------------------------------------

        if not task:

            speak(
                "What should I remind you about?"
            )

            return

        # -------------------------------------------------
        # CREATE REMINDER OBJECT
        # -------------------------------------------------

        reminder = {

            "task": task,

            "time": reminder_time,

            "completed": False

        }

        # -------------------------------------------------
        # GET EXISTING REMINDERS
        # -------------------------------------------------

        reminders = self.context.get(
            "reminders"
        )

        # -------------------------------------------------
        # ADD NEW REMINDER
        # -------------------------------------------------

        reminders.append(
            reminder
        )

        # -------------------------------------------------
        # PRINT INFORMATION
        # -------------------------------------------------

        print("\nReminder added:")

        print(
            "Task:",
            task
        )

        print(
            "Time:",
            reminder_time.strftime(
                "%d-%m-%Y %I:%M %p"
            )
        )

        # -------------------------------------------------
        # SPEAK CONFIRMATION
        # -------------------------------------------------

        speak(
            f"Okay. I'll remind you to {task} "
            f"at {reminder_time.strftime('%I:%M %p')}"
        )

    # =====================================================
    # BACKGROUND REMINDER CHECKER
    # =====================================================

    def _reminder_checker(self):

        while self.running:

            try:

                reminders = self.context.get(
                    "reminders"
                )

                now = datetime.now()

                # -------------------------------------------------
                # CHECK EVERY REMINDER
                # -------------------------------------------------

                for reminder in reminders:

                    # Skip completed reminders
                    if reminder["completed"]:

                        continue

                    # -------------------------------------------------
                    # CHECK WHETHER REMINDER IS DUE
                    # -------------------------------------------------

                    if now >= reminder["time"]:

                        task = reminder[
                            "task"
                        ]

                        print(
                            "\nREMINDER DUE:"
                        )

                        print(
                            task
                        )

                        # -------------------------------------------------
                        # SPEAK REMINDER
                        # -------------------------------------------------

                        speak(
                            f"Reminder: {task}"
                        )

                        # -------------------------------------------------
                        # MARK AS COMPLETED
                        # -------------------------------------------------

                        reminder[
                            "completed"
                        ] = True

            except Exception as e:

                print(
                    "Reminder checker error:",
                    e
                )

            # -------------------------------------------------
            # CHECK EVERY SECOND
            # -------------------------------------------------

            time.sleep(1)