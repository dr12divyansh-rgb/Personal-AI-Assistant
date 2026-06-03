class BaseSkill:

    def can_handle(self, query):
        """
        Return True if skill can handle query
        """
        raise NotImplementedError

    def handle(self, query):
        """
        Execute the skill
        """
        raise NotImplementedError