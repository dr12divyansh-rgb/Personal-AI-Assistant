class AssistantContext:

    def __init__(self):

        self.current_project = None

        self.last_song = None

        self.last_app = None

        self.last_command = None

        self.mode = None

        # Store reminders
        self.reminders = []

        # Used when a command asks September to sleep
        self.sleep_requested = False

    def set(self, key, value):

        setattr(self, key, value)

    def get(self, key):

        return getattr(self, key, None)