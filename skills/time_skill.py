import threading
import time
from datetime import datetime, timedelta

from core.base_skill import BaseSkill
from speech.speech import speak


class TimeSkill(BaseSkill):

    def __init__(self, context):

        self.context = context

        # Active timers
        self.timers = []

        # Active alarms
        self.alarms = []

        # Stopwatch state
        self.stopwatch_running = False
        self.stopwatch_start = None
        self.stopwatch_elapsed = 0

        # Focus session state
        self.focus_running = False

        # Background checker
        self.running = True

        self.thread = threading.Thread(
            target=self._background_checker,
            daemon=True
        )

        self.thread.start()

    # =====================================================
    # CAN HANDLE
    # =====================================================

    def can_handle(self, query):

        query = query.lower().strip()

        keywords = [
            "alarm",
            "set an alarm",
            "set alarm",

            "timer",
            "set a timer",
            "set timer",

            "stopwatch",
            "stop watch",

            "focus session",
            "focus mode",
            "pomodoro"
        ]

        return any(
            keyword in query
            for keyword in keywords
        )

    # =====================================================
    # HANDLE
    # =====================================================

    def handle(self, query):

        query = query.lower().strip()

        # -------------------------
        # ALARM
        # -------------------------

        if "alarm" in query:

            self._set_alarm(query)
            return

        # -------------------------
        # STOPWATCH
        # -------------------------

        if (
            "stopwatch" in query
            or "stop watch" in query
        ):

            self._handle_stopwatch(query)
            return

        # -------------------------
        # FOCUS SESSION
        # -------------------------

        if (
            "focus session" in query
            or "focus mode" in query
            or "pomodoro" in query
        ):

            self._start_focus_session(query)
            return

        # -------------------------
        # TIMER
        # -------------------------

        if "timer" in query:

            self._set_timer(query)
            return

    # =====================================================
    # TIMER
    # =====================================================

    def _set_timer(self, query):

        import re

        match = re.search(
            r"(\d+)\s*(seconds?|minutes?|hours?)",
            query
        )

        if not match:

            speak(
                "How long should I set the timer for?"
            )

            return

        amount = int(match.group(1))
        unit = match.group(2)

        if unit.startswith("second"):

            duration = amount

        elif unit.startswith("minute"):

            duration = amount * 60

        else:

            duration = amount * 3600

        end_time = (
            datetime.now()
            + timedelta(seconds=duration)
        )

        timer = {
            "end_time": end_time,
            "duration": duration,
            "completed": False
        }

        self.timers.append(timer)

        speak(
            f"Timer set for {amount} {unit}"
        )

        print(
            f"Timer will finish at "
            f"{end_time.strftime('%I:%M:%S %p')}"
        )

    # =====================================================
    # ALARM
    # =====================================================

    def _set_alarm(self, query):

        import re

        match = re.search(
            r"(\d{1,2})"
            r"(?::(\d{2}))?"
            r"\s*(am|pm)?",
            query
        )

        if not match:

            speak(
                "What time should I set the alarm for?"
            )

            return

        hour = int(match.group(1))
        minute = int(match.group(2) or 0)

        period = match.group(3)

        if period:

            if period == "pm" and hour != 12:
                hour += 12

            elif period == "am" and hour == 12:
                hour = 0

        now = datetime.now()

        alarm_time = now.replace(
            hour=hour,
            minute=minute,
            second=0,
            microsecond=0
        )

        # If the requested time has already passed,
        # set it for tomorrow.

        if alarm_time <= now:

            alarm_time += timedelta(
                days=1
            )

        alarm = {
            "time": alarm_time,
            "completed": False
        }

        self.alarms.append(alarm)

        speak(
            f"Alarm set for "
            f"{alarm_time.strftime('%I:%M %p')}"
        )

        print(
            "Alarm:",
            alarm_time.strftime(
                "%d-%m-%Y %I:%M:%S %p"
            )
        )

    # =====================================================
    # STOPWATCH
    # =====================================================

    def _handle_stopwatch(self, query):

        # START

        if (
            "start" in query
            or "begin" in query
        ):

            if self.stopwatch_running:

                speak(
                    "The stopwatch is already running."
                )

                return

            self.stopwatch_running = True

            self.stopwatch_start = time.time()

            speak(
                "Stopwatch started."
            )

            return

        # STOP

        if (
            "stop" in query
            or "pause" in query
        ):

            if not self.stopwatch_running:

                speak(
                    "The stopwatch is not running."
                )

                return

            self.stopwatch_elapsed += (
                time.time()
                - self.stopwatch_start
            )

            self.stopwatch_running = False

            speak(
                self._format_stopwatch()
            )

            return

        # RESET

        if "reset" in query:

            self.stopwatch_running = False

            self.stopwatch_start = None

            self.stopwatch_elapsed = 0

            speak(
                "Stopwatch reset."
            )

            return

        # TIME

        if (
            "how long" in query
            or "time" in query
            or "elapsed" in query
        ):

            speak(
                self._format_stopwatch()
            )

            return

        speak(
            "You can start, stop, pause, "
            "reset, or check the stopwatch."
        )

    # =====================================================
    # FORMAT STOPWATCH
    # =====================================================

    def _get_stopwatch_seconds(self):

        elapsed = self.stopwatch_elapsed

        if self.stopwatch_running:

            elapsed += (
                time.time()
                - self.stopwatch_start
            )

        return int(elapsed)

    def _format_stopwatch(self):

        total_seconds = (
            self._get_stopwatch_seconds()
        )

        hours = total_seconds // 3600

        minutes = (
            total_seconds % 3600
        ) // 60

        seconds = (
            total_seconds % 60
        )

        if hours > 0:

            return (
                f"Stopwatch: "
                f"{hours} hours "
                f"{minutes} minutes "
                f"{seconds} seconds."
            )

        if minutes > 0:

            return (
                f"Stopwatch: "
                f"{minutes} minutes "
                f"{seconds} seconds."
            )

        return (
            f"Stopwatch: "
            f"{seconds} seconds."
        )

    # =====================================================
    # FOCUS SESSION
    # =====================================================

    def _start_focus_session(self, query):

        import re

        match = re.search(
            r"(\d+)\s*(minutes?|hours?)",
            query
        )

        if not match:

            duration = 25

        else:

            amount = int(match.group(1))

            unit = match.group(2)

            if unit.startswith("hour"):

                duration = amount * 60

            else:

                duration = amount

        if self.focus_running:

            speak(
                "A focus session is already running."
            )

            return

        self.focus_running = True

        end_time = (
            datetime.now()
            + timedelta(minutes=duration)
        )

        self.context.set(
            "focus_session",
            {
                "end_time": end_time,
                "duration": duration,
                "completed": False
            }
        )

        speak(
            f"Focus session started for "
            f"{duration} minutes."
        )

    # =====================================================
    # BACKGROUND CHECKER
    # =====================================================

    def _background_checker(self):

        while self.running:

            try:

                now = datetime.now()

                # -------------------------
                # CHECK TIMERS
                # -------------------------

                for timer in self.timers:

                    if (
                        not timer["completed"]
                        and now >= timer["end_time"]
                    ):

                        timer["completed"] = True

                        speak(
                            "Timer finished."
                        )

                # -------------------------
                # CHECK ALARMS
                # -------------------------

                for alarm in self.alarms:

                    if (
                        not alarm["completed"]
                        and now >= alarm["time"]
                    ):

                        alarm["completed"] = True

                        speak(
                            "Alarm! The alarm time has arrived."
                        )

                # -------------------------
                # CHECK FOCUS SESSION
                # -------------------------

                focus = self.context.get(
                    "focus_session"
                )

                if (
                    focus
                    and not focus["completed"]
                    and now >= focus["end_time"]
                ):

                    focus["completed"] = True

                    self.focus_running = False

                    speak(
                        "Your focus session is complete."
                    )

            except Exception as e:

                print(
                    "TimeSkill error:",
                    e
                )

            time.sleep(1)