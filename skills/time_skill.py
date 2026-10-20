import re
import time
import subprocess
from datetime import datetime

from pywinauto import Desktop

from core.base_skill import BaseSkill
from speech.speech import speak


class TimeSkill(BaseSkill):

    def __init__(self, context):
        self.context = context

    # =========================================================
    # COMMAND DETECTION
    # =========================================================

    def can_handle(self, query):
        query = query.lower().strip()

        time_words = [
            "what time",
            "current time",
            "tell me the time",
            "time now",
            "time"
        ]

        date_words = [
            "what date",
            "today's date",
            "todays date",
            "current date",
            "what day",
            "today"
        ]

        timer_words = [
            "set a timer",
            "start a timer",
            "timer for",
            "timer"
        ]

        if any(word in query for word in timer_words):
            return True

        if any(word in query for word in time_words):
            return True

        if any(word in query for word in date_words):
            return True

        return False

    # =========================================================
    # MAIN HANDLER
    # =========================================================

    def handle(self, query):
        query = query.lower().strip()

        # -----------------------------------------------------
        # TIMER
        # -----------------------------------------------------

        if (
            "set a timer" in query
            or "start a timer" in query
            or "timer for" in query
            or query == "timer"
        ):
            self._handle_timer(query)
            return

        # -----------------------------------------------------
        # TIME
        # -----------------------------------------------------

        if (
            "what time" in query
            or "current time" in query
            or "tell me the time" in query
            or "time now" in query
            or query == "time"
        ):
            self._tell_time()
            return

        # -----------------------------------------------------
        # DATE
        # -----------------------------------------------------

        if (
            "what date" in query
            or "today's date" in query
            or "todays date" in query
            or "current date" in query
            or "what day" in query
            or query == "today"
        ):
            self._tell_date()
            return

    # =========================================================
    # TIME
    # =========================================================

    def _tell_time(self):
        current_time = datetime.now()

        hour = current_time.strftime("%I").lstrip("0")
        minute = current_time.strftime("%M")
        period = current_time.strftime("%p")

        speak(
            f"The time is {hour} {minute} {period}"
        )

    # =========================================================
    # DATE
    # =========================================================

    def _tell_date(self):
        current_date = datetime.now()

        day = current_date.strftime("%d").lstrip("0")
        month = current_date.strftime("%B")
        year = current_date.strftime("%Y")
        weekday = current_date.strftime("%A")

        speak(
            f"Today is {weekday}, {day} {month} {year}"
        )

    # =========================================================
    # TIMER COMMAND PARSING
    # =========================================================

    def _handle_timer(self, query):

        hours = 0
        minutes = 0
        seconds = 0

        # -----------------------------------------------------
        # Hours
        # -----------------------------------------------------

        hour_match = re.search(
            r"(\d+)\s*(?:hour|hours|hr|hrs)",
            query
        )

        if hour_match:
            hours = int(hour_match.group(1))

        # -----------------------------------------------------
        # Minutes
        # -----------------------------------------------------

        minute_match = re.search(
            r"(\d+)\s*(?:minute|minutes|min|mins)",
            query
        )

        if minute_match:
            minutes = int(minute_match.group(1))

        # -----------------------------------------------------
        # Seconds
        # -----------------------------------------------------

        second_match = re.search(
            r"(\d+)\s*(?:second|seconds|sec|secs)",
            query
        )

        if second_match:
            seconds = int(second_match.group(1))

        # -----------------------------------------------------
        # If no duration was understood
        # -----------------------------------------------------

        if hours == 0 and minutes == 0 and seconds == 0:
            speak(
                "Please tell me the timer duration."
            )
            return

        print(
            f"Timer requested: "
            f"{hours} hours, "
            f"{minutes} minutes, "
            f"{seconds} seconds"
        )

        # -----------------------------------------------------
        # Open and control actual Windows Clock
        # -----------------------------------------------------

        success = self._create_windows_timer(
            hours,
            minutes,
            seconds
        )

        if success:

            duration_text = self._format_duration(
                hours,
                minutes,
                seconds
            )

            speak(
                f"Timer set for {duration_text}"
            )

        else:

            speak(
                "I couldn't create the timer in Windows Clock."
            )

    # =========================================================
    # FORMAT TIMER DURATION
    # =========================================================

    def _format_duration(
        self,
        hours,
        minutes,
        seconds
    ):

        parts = []

        if hours:
            if hours == 1:
                parts.append("1 hour")
            else:
                parts.append(f"{hours} hours")

        if minutes:
            if minutes == 1:
                parts.append("1 minute")
            else:
                parts.append(f"{minutes} minutes")

        if seconds:
            if seconds == 1:
                parts.append("1 second")
            else:
                parts.append(f"{seconds} seconds")

        if len(parts) == 1:
            return parts[0]

        if len(parts) == 2:
            return f"{parts[0]} and {parts[1]}"

        return (
            f"{parts[0]}, "
            f"{parts[1]} and "
            f"{parts[2]}"
        )

    # =========================================================
    # FIND WINDOWS CLOCK
    # =========================================================

    def _find_clock(self):

        try:

            windows = Desktop(
                backend="uia"
            ).windows(
                title="Clock"
            )

            for window in windows:

                try:

                    if window.exists():
                        print(
                            "Windows Clock found."
                        )
                        return window

                except Exception:
                    pass

        except Exception as e:

            print(
                "Clock search error:",
                e
            )

        return None

    # =========================================================
    # OPEN WINDOWS CLOCK
    # =========================================================

    def _open_clock(self):

        clock = self._find_clock()

        if clock is not None:
            return clock

        print(
            "Windows Clock is not open."
        )

        print(
            "Opening Windows Clock..."
        )

        try:

            subprocess.Popen(
                [
                    "explorer.exe",
                    "shell:AppsFolder\\"
                    "Microsoft.WindowsAlarms_8wekyb3d8bbwe!"
                ]
            )

        except Exception as e:

            print(
                "Could not launch Clock:",
                e
            )

            return None

        # -----------------------------------------------------
        # Wait for Clock window
        # -----------------------------------------------------

        for attempt in range(20):

            time.sleep(0.5)

            clock = self._find_clock()

            if clock is not None:
                return clock

            print(
                f"Waiting for Clock "
                f"({attempt + 1}/20)..."
            )

        print(
            "Windows Clock did not open."
        )

        return None

    # =========================================================
    # OPEN TIMER PAGE
    # =========================================================

    def _open_timer_page(self, clock):

        print(
            "Opening Timer..."
        )

        timer_button = None

        # -----------------------------------------------------
        # STEP 1:
        # Find Timer navigation button
        # -----------------------------------------------------

        for attempt in range(15):

            try:

                # Always obtain a fresh Clock wrapper.
                clock = self._find_clock()

                if clock is None:

                    print(
                        "Clock window disappeared."
                    )

                    time.sleep(0.5)
                    continue

                list_items = clock.descendants(
                    control_type="ListItem"
                )

                for item in list_items:

                    try:

                        automation_id = (
                            item.element_info
                            .automation_id
                        )

                        if automation_id == "TimerButton":

                            timer_button = item
                            break

                    except Exception:
                        pass

                if timer_button is not None:

                    print(
                        "Timer button found."
                    )

                    break

                print(
                    f"Timer button not found - "
                    f"retry {attempt + 1}/15"
                )

            except Exception as e:

                print(
                    f"Timer search error on "
                    f"attempt {attempt + 1}:",
                    e
                )

            time.sleep(0.5)

        # -----------------------------------------------------
        # Timer button not found
        # -----------------------------------------------------

        if timer_button is None:

            print(
                "Timer button could not be found."
            )

            return False

        # -----------------------------------------------------
        # STEP 2:
        # Click Timer navigation
        # -----------------------------------------------------

        try:

            timer_button.set_focus()

        except Exception:
            pass

        time.sleep(0.3)

        try:

            print(
                "Clicking Timer button..."
            )

            timer_button.click_input()

            print(
                "Timer button clicked."
            )

        except Exception as e:

            print(
                "Timer button click failed:",
                e
            )

            return False

        # -----------------------------------------------------
        # STEP 3:
        # Wait for Timer page
        #
        # We deliberately scan the LIVE UI tree instead
        # of relying on a potentially stale Clock wrapper.
        # -----------------------------------------------------

        print(
            "Waiting for Timer page to load..."
        )

        for attempt in range(30):

            time.sleep(0.5)

            try:

                # Get a completely fresh Clock wrapper.
                clock = self._find_clock()

                if clock is None:
                    continue

                # Search all current buttons.
                buttons = clock.descendants(
                    control_type="Button"
                )

                for button in buttons:

                    try:

                        automation_id = (
                            button.element_info
                            .automation_id
                        )

                        name = button.window_text()

                        if (
                            automation_id
                            == "AddTimerButton"
                        ):

                            print(
                                "Timer page loaded."
                            )

                            print(
                                "Add Timer button found:",
                                name,
                                "| AutomationId:",
                                automation_id
                            )

                            return True

                    except Exception:
                        pass

                # -------------------------------------------------
                # Periodic diagnostics
                # -------------------------------------------------

                if attempt in [
                    4,
                    9,
                    14,
                    19,
                    24,
                    29
                ]:

                    print(
                        f"Still waiting for Timer page "
                        f"({attempt + 1}/30)..."
                    )

                    list_items = clock.descendants(
                        control_type="ListItem"
                    )

                    for item in list_items:

                        try:

                            automation_id = (
                                item.element_info
                                .automation_id
                            )

                            if automation_id in [
                                "TimerButton",
                                "AlarmButton",
                                "StopwatchButton"
                            ]:

                                print(
                                    "Navigation:",
                                    item.window_text(),
                                    "|",
                                    automation_id
                                )

                        except Exception:
                            pass

            except Exception as e:

                print(
                    "Timer page check error:",
                    e
                )

        print(
            "Timer page did not finish loading."
        )

        return False

    # =========================================================
    # CREATE WINDOWS TIMER
    # =========================================================

    def _create_windows_timer(
        self,
        hours,
        minutes,
        seconds
    ):

        # -----------------------------------------------------
        # Open Clock
        # -----------------------------------------------------

        clock = self._open_clock()

        if clock is None:

            print(
                "Could not access Windows Clock."
            )

            return False

        # -----------------------------------------------------
        # Open Timer page
        # -----------------------------------------------------

        if not self._open_timer_page(clock):

            return False

        # -----------------------------------------------------
        # Refresh Clock wrapper
        # -----------------------------------------------------

        clock = self._find_clock()

        if clock is None:
            return False

        # -----------------------------------------------------
        # Find Add New Timer button
        # -----------------------------------------------------

        add_button = None

        try:

            buttons = clock.descendants(
                control_type="Button"
            )

            for button in buttons:

                try:

                    automation_id = (
                        button.element_info
                        .automation_id
                    )

                    if automation_id == "AddTimerButton":

                        add_button = button
                        break

                except Exception:
                    pass

        except Exception as e:

            print(
                "Error finding Add Timer button:",
                e
            )

        if add_button is None:

            print(
                "Add Timer button not found."
            )

            return False

        # -----------------------------------------------------
        # Click Add New Timer
        # -----------------------------------------------------

        try:

            print(
                "Clicking Add new timer..."
            )

            add_button.click_input()

        except Exception as e:

            print(
                "Add Timer click failed:",
                e
            )

            return False

        # -----------------------------------------------------
        # Wait for timer dialog
        # -----------------------------------------------------

        dialog = None

        print(
            "Waiting for Add New Timer dialog..."
        )

        for attempt in range(20):

            time.sleep(0.3)

            try:

                windows = Desktop(
                    backend="uia"
                ).windows(
                    title="Popup"
                )

                for window in windows:

                    try:

                        if window.exists():

                            popup_text = (
                                window.window_text()
                            )

                            if (
                                "Popup"
                                in popup_text
                                or popup_text == ""
                            ):

                                dialog = window
                                break

                    except Exception:
                        pass

                if dialog is not None:
                    break

            except Exception:
                pass

        if dialog is None:

            print(
                "Add New Timer dialog not found."
            )

            return False

        print(
            "Add New Timer dialog found."
        )

        # -----------------------------------------------------
        # Set duration
        # -----------------------------------------------------

        if not self._set_timer_duration(
            dialog,
            hours,
            minutes,
            seconds
        ):

            return False

        # -----------------------------------------------------
        # Save timer
        # -----------------------------------------------------

        if not self._save_timer(dialog):

            return False

        # -----------------------------------------------------
        # Give Clock time to update
        # -----------------------------------------------------

        time.sleep(1)

        # -----------------------------------------------------
        # IMPORTANT:
        # Refresh Clock wrapper after saving.
        # -----------------------------------------------------

        clock = self._find_clock()

        if clock is None:

            print(
                "Clock disappeared after saving timer."
            )

            return False

        # -----------------------------------------------------
        # Find newly created timer
        # -----------------------------------------------------

        timer_card = self._find_new_timer(
            clock,
            hours,
            minutes,
            seconds
        )

        if timer_card is None:

            print(
                "New timer could not be found."
            )

            return False

        # -----------------------------------------------------
        # Start timer
        # -----------------------------------------------------

        if not self._start_timer(
            timer_card
        ):

            return False

        return True

    # =========================================================
    # SET TIMER DURATION
    # =========================================================

    def _set_timer_duration(
        self,
        dialog,
        hours,
        minutes,
        seconds
    ):

        print(
            "Setting timer duration..."
        )

        try:

            duration_picker = None

            customs = dialog.descendants(
                control_type="Custom"
            )

            for custom in customs:

                try:

                    automation_id = (
                        custom.element_info
                        .automation_id
                    )

                    if automation_id == "DurationPicker":

                        duration_picker = custom
                        break

                except Exception:
                    pass

            if duration_picker is None:

                print(
                    "Duration picker not found."
                )

                return False

            # -------------------------------------------------
            # Set hours
            # -------------------------------------------------

            if not self._set_picker_value(
                duration_picker,
                "hours",
                hours
            ):

                return False

            # -------------------------------------------------
            # Set minutes
            # -------------------------------------------------

            if not self._set_picker_value(
                duration_picker,
                "minutes",
                minutes
            ):

                return False

            # -------------------------------------------------
            # Set seconds
            # -------------------------------------------------

            if not self._set_picker_value(
                duration_picker,
                "seconds",
                seconds
            ):

                return False

            print(
                "Timer duration set successfully."
            )

            return True

        except Exception as e:

            print(
                "Duration setting error:",
                e
            )

            return False

    # =========================================================
    # SET INDIVIDUAL PICKER
    # =========================================================

    def _set_picker_value(
        self,
        duration_picker,
        unit_name,
        target_value
    ):

        if target_value <= 0:
            return True

        try:

            unit_control = None

            customs = duration_picker.descendants(
                control_type="Custom"
            )

            for custom in customs:

                try:

                    name = (
                        custom.window_text()
                        .strip()
                        .lower()
                    )

                    if name == unit_name:

                        unit_control = custom
                        break

                except Exception:
                    pass

            if unit_control is None:

                print(
                    f"{unit_name} picker not found."
                )

                return False

            buttons = unit_control.descendants(
                control_type="Button"
            )

            if len(buttons) < 1:

                print(
                    f"No buttons found for "
                    f"{unit_name} picker."
                )

                return False

            # -------------------------------------------------
            # Based on the discovered Windows Clock UI:
            #
            # Button 0 = Increase
            # Button 1 = Decrease
            # -------------------------------------------------

            increase_button = buttons[0]

            print(
                f"Setting {unit_name}: "
                f"{target_value}"
            )

            for _ in range(target_value):

                try:

                    increase_button.click_input()

                except Exception:

                    try:
                        increase_button.invoke()

                    except Exception as e:

                        print(
                            f"Could not increase "
                            f"{unit_name}:",
                            e
                        )

                        return False

                time.sleep(0.05)

            return True

        except Exception as e:

            print(
                f"Picker error for {unit_name}:",
                e
            )

            return False

    # =========================================================
    # SAVE TIMER
    # =========================================================

    def _save_timer(self, dialog):

        print(
            "Saving timer..."
        )

        try:

            buttons = dialog.descendants(
                control_type="Button"
            )

            save_button = None

            for button in buttons:

                try:

                    automation_id = (
                        button.element_info
                        .automation_id
                    )

                    name = (
                        button.window_text()
                        .strip()
                        .lower()
                    )

                    if (
                        automation_id
                        == "PrimaryButton"
                        or name == "save"
                    ):

                        save_button = button
                        break

                except Exception:
                    pass

            if save_button is None:

                print(
                    "Save button not found."
                )

                return False

            try:

                save_button.invoke()

                print(
                    "Save button invoked."
                )

            except Exception:

                save_button.click_input()

                print(
                    "Save button clicked."
                )

            time.sleep(1)

            return True

        except Exception as e:

            print(
                "Save timer error:",
                e
            )

            return False

    # =========================================================
    # FIND NEW TIMER
    # =========================================================

    def _find_new_timer(
        self,
        clock,
        hours,
        minutes,
        seconds
    ):

        print(
            "Finding newly created timer..."
        )

        # -----------------------------------------------------
        # Expected duration text
        # -----------------------------------------------------

        expected_parts = []

        if hours:
            expected_parts.append(
                f"{hours} hour"
            )

        if minutes:
            expected_parts.append(
                f"{minutes} minute"
            )

        if seconds:
            expected_parts.append(
                f"{seconds} second"
            )

        expected_text = " ".join(
            expected_parts
        ).lower()

        # -----------------------------------------------------
        # Give Clock time to update UI
        # -----------------------------------------------------

        for attempt in range(15):

            time.sleep(0.5)

            try:

                clock = self._find_clock()

                if clock is None:
                    continue

                data_items = clock.descendants(
                    control_type="DataItem"
                )

                matching_cards = []

                for item in data_items:

                    try:

                        name = (
                            item.window_text()
                            .strip()
                            .lower()
                        )

                        automation_id = (
                            item.element_info
                            .automation_id
                        )

                        if automation_id != "TimerViewGrid":
                            continue

                        # -------------------------------------------------
                        # Look for "Not Started" and duration.
                        # -------------------------------------------------

                        if (
                            "not started" in name
                            and expected_text in name
                        ):

                            matching_cards.append(
                                item
                            )

                            print(
                                "Matching timer found:",
                                item.window_text()
                            )

                    except Exception:
                        pass

                if matching_cards:

                    # Use the last matching timer.
                    # This is normally the newly-created timer.
                    timer_card = matching_cards[-1]

                    print(
                        "New timer selected."
                    )

                    return timer_card

            except Exception as e:

                print(
                    "Timer search error:",
                    e
                )

        print(
            "Could not find the newly created timer."
        )

        return None

    # =========================================================
    # START TIMER
    # =========================================================

    def _start_timer(self, timer_card):

        print(
            "Finding Start button..."
        )

        try:

            # -------------------------------------------------
            # IMPORTANT:
            # Get a fresh wrapper before clicking.
            # -------------------------------------------------

            clock = self._find_clock()

            if clock is not None:

                # Try to find the same timer again.
                fresh_cards = clock.descendants(
                    control_type="DataItem"
                )

                for card in fresh_cards:

                    try:

                        automation_id = (
                            card.element_info
                            .automation_id
                        )

                        if automation_id != "TimerViewGrid":
                            continue

                        name = (
                            card.window_text()
                            .strip()
                            .lower()
                        )

                        old_name = (
                            timer_card.window_text()
                            .strip()
                            .lower()
                        )

                        # Match using timer name/duration.
                        if (
                            name == old_name
                            or (
                                "not started" in name
                                and "timer" in name
                            )
                        ):

                            if name == old_name:
                                timer_card = card
                                break

                    except Exception:
                        pass

            # -------------------------------------------------
            # Find TimerPlayPauseButton
            # -------------------------------------------------

            buttons = timer_card.descendants(
                control_type="Button"
            )

            start_button = None

            for button in buttons:

                try:

                    automation_id = (
                        button.element_info
                        .automation_id
                    )

                    print(
                        "Button:",
                        button.window_text(),
                        "| AutomationId:",
                        automation_id
                    )

                    if (
                        automation_id
                        == "TimerPlayPauseButton"
                    ):

                        start_button = button
                        break

                except Exception:
                    pass

            if start_button is None:

                print(
                    "Timer Start button not found."
                )

                return False

            # -------------------------------------------------
            # Focus
            # -------------------------------------------------

            try:
                start_button.set_focus()
            except Exception:
                pass

            time.sleep(0.3)

            # -------------------------------------------------
            # First attempt:
            # UI Automation Invoke
            # -------------------------------------------------

            print(
                "Trying UI Automation invoke..."
            )

            try:

                start_button.invoke()

                print(
                    "Invoke completed."
                )

            except Exception as e:

                print(
                    "Invoke failed:",
                    e
                )

            time.sleep(1)

            # -------------------------------------------------
            # Check timer status
            # -------------------------------------------------

            if self._timer_is_running(
                timer_card
            ):

                print(
                    "Timer confirmed RUNNING."
                )

                return True

            # -------------------------------------------------
            # Second attempt:
            # Mouse click
            # -------------------------------------------------

            print(
                "Timer did not start after invoke."
            )

            print(
                "Trying mouse click..."
            )

            try:

                start_button.click_input(
                    button="left",
                    double=False
                )

            except Exception as e:

                print(
                    "Mouse click failed:",
                    e
                )

            time.sleep(1)

            # -------------------------------------------------
            # Check again
            # -------------------------------------------------

            if self._timer_is_running(
                timer_card
            ):

                print(
                    "Timer confirmed RUNNING."
                )

                return True

            # -------------------------------------------------
            # Third attempt:
            # Refresh UI and try fresh button
            # -------------------------------------------------

            print(
                "Refreshing timer UI..."
            )

            clock = self._find_clock()

            if clock is not None:

                data_items = clock.descendants(
                    control_type="DataItem"
                )

                for card in data_items:

                    try:

                        automation_id = (
                            card.element_info
                            .automation_id
                        )

                        if automation_id != "TimerViewGrid":
                            continue

                        name = (
                            card.window_text()
                            .strip()
                            .lower()
                        )

                        if "not started" in name:

                            buttons = card.descendants(
                                control_type="Button"
                            )

                            for button in buttons:

                                try:

                                    automation_id = (
                                        button.element_info
                                        .automation_id
                                    )

                                    if (
                                        automation_id
                                        == "TimerPlayPauseButton"
                                    ):

                                        print(
                                            "Found fresh "
                                            "Start button."
                                        )

                                        try:
                                            button.invoke()
                                        except Exception:
                                            button.click_input()

                                        time.sleep(1)

                                        if self._timer_is_running(
                                            card
                                        ):

                                            print(
                                                "Timer confirmed "
                                                "RUNNING."
                                            )

                                            return True

                                except Exception:
                                    pass

                    except Exception:
                        pass

            print(
                "Timer was created, but Windows Clock "
                "did not confirm that it started."
            )

            return False

        except Exception as e:

            print(
                "Start timer error:",
                e
            )

            return False

    # =========================================================
    # CHECK WHETHER TIMER IS RUNNING
    # =========================================================

    def _timer_is_running(
        self,
        timer_card
    ):

        try:

            buttons = timer_card.descendants(
                control_type="Button"
            )

            for button in buttons:

                try:

                    automation_id = (
                        button.element_info
                        .automation_id
                    )

                    if (
                        automation_id
                        != "TimerPlayPauseButton"
                    ):
                        continue

                    name = (
                        button.window_text()
                        .strip()
                        .lower()
                    )

                    print(
                        "Current timer button:",
                        button.window_text()
                    )

                    # Windows Clock changes the button
                    # from Start to Pause when running.
                    if "pause" in name:
                        return True

                except Exception:
                    pass

        except Exception as e:

            print(
                "Timer status error:",
                e
            )

        return False