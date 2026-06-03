class AssistantContext:

    def __init__(self):

        self.current_project = None

        self.last_song = None

        self.last_app = None

        self.last_command = None

        self.mode = None

    def set(self, key, value):

        setattr(self, key, value)

    def get(self, key):

        return getattr(self, key, None)