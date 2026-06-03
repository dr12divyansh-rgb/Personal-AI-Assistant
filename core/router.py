from skills.music_skill import MusicSkill
from skills.browser_skill import BrowserSkill
from skills.ai_chat_skill import AIChatSkill
from skills.system_skill import SystemSkill
from skills.coding_skill import CodingSkill


class AssistantRouter:

    def __init__(self,context):

        self.context=context
        self.skills = [

            MusicSkill(self.context),
            BrowserSkill(self.context),
            SystemSkill(self.context),
            CodingSkill(self.context),

            # AI should stay last
            AIChatSkill(self.context)
        ]

    def process(self, query):

        query = query.lower()

        for skill in self.skills:

            if skill.can_handle(query):

                skill.handle(query)
                return