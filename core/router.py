from skills.music_skill import MusicSkill
from skills.browser_skill import BrowserSkill
from skills.ai_chat_skill import AIChatSkill
from skills.system_skill import SystemSkill
from skills.coding_skill import CodingSkill
from skills.reminder_skill import ReminderSkill
from skills.time_skill import TimeSkill


class AssistantRouter:

    def __init__(self, context):

        self.context = context

        self.skills = [

            ReminderSkill(self.context),
            TimeSkill(self.context),

            MusicSkill(self.context),
            BrowserSkill(self.context),
            SystemSkill(self.context),
            CodingSkill(self.context),

            # AI should stay last
            AIChatSkill(self.context)
        ]

    # =====================================================
    # SPLIT MULTIPLE TASKS
    # =====================================================

    def split_commands(self, query):

        query = query.lower().strip()

        # Normalize punctuation
        query = query.replace(",", " ")

        # Normalize multiple spaces
        query = " ".join(query.split())

        # -------------------------------------------------
        # FIRST:
        # Handle strong task separators
        # -------------------------------------------------

        separators = [
            " and then ",
            " after that ",
            " then "
        ]

        commands = [query]

        for separator in separators:

            new_commands = []

            for command in commands:

                parts = command.split(separator)

                for part in parts:

                    part = part.strip()

                    if part:
                        new_commands.append(part)

            commands = new_commands

        # -------------------------------------------------
        # SECOND:
        # Handle plain "and"
        #
        # We only split if "and" is followed by a
        # recognizable action.
        #
        # Example:
        #
        # "open spotify and play believer"
        #
        # becomes:
        #
        # "open spotify"
        # "play believer"
        #
        # But:
        #
        # "search for tom and jerry"
        #
        # stays as ONE task.
        # -------------------------------------------------

        final_commands = []

        for command in commands:

            words = command.split()

            current_command = []

            i = 0

            while i < len(words):

                word = words[i]

                # -----------------------------------------
                # Check for "and"
                # -----------------------------------------

                if word == "and" and i + 1 < len(words):

                    next_word = words[i + 1]

                    # Commands that indicate a new task
                    action_words = [

                        "open",
                        "search",
                        "play",
                        "close",
                        "exit",
                        "quit",
                        "lock",
                        "sleep",
                        "restart",
                        "shutdown",
                        "start",
                        "launch",
                        "remind"
                    ]

                    # -------------------------------------
                    # "and" followed by a new action
                    # -------------------------------------

                    if next_word in action_words:

                        # Save the current task
                        if current_command:

                            final_commands.append(
                                " ".join(current_command).strip()
                            )

                        # Start a new task
                        current_command = []

                        i += 1

                        continue

                # -----------------------------------------
                # Normal word
                # -----------------------------------------

                current_command.append(word)

                i += 1

            # ---------------------------------------------
            # Save remaining task
            # ---------------------------------------------

            if current_command:

                final_commands.append(
                    " ".join(current_command).strip()
                )

        return final_commands

    # =====================================================
    # PROCESS COMMAND
    # =====================================================

    def process(self, query):

        query = query.lower().strip()

        if not query:

            return

        # Save complete command
        self.context.set(
            "last_command",
            query
        )

        # -------------------------------------------------
        # Split into tasks
        # -------------------------------------------------

        commands = self.split_commands(query)

        print("\n" + "=" * 50)

        print("COMMAND RECEIVED:")
        print(query)

        print("\nTASKS DETECTED:")

        for i, command in enumerate(
            commands,
            1
        ):

            print(
                f"  Task {i}: {command}"
            )

        print("=" * 50)

        # -------------------------------------------------
        # Execute every task
        # -------------------------------------------------

        for i, command in enumerate(
            commands,
            1
        ):

            print(
                f"\nExecuting Task {i}: {command}"
            )

            handled = False

            # ---------------------------------------------
            # Find appropriate skill
            # ---------------------------------------------

            for skill in self.skills:

                try:

                    if skill.can_handle(command):

                        print(
                            f"Skill: "
                            f"{skill.__class__.__name__}"
                        )

                        skill.handle(command)

                        handled = True

                        break

                except Exception as e:

                    print(
                        f"Error in "
                        f"{skill.__class__.__name__}:",
                        e
                    )

                    # One failed task should NOT stop
                    # the remaining tasks.
                    handled = True

                    break

            # ---------------------------------------------
            # No skill found
            # ---------------------------------------------

            if not handled:

                print(
                    f"No skill found for: "
                    f"{command}"
                )

        print("\nAll tasks processed.")