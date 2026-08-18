import json

from . import prompts


class PromptBuilder:
    def build_prompt(self, selected_context, user_message, chat_history=""):
        """
        Build a prompt for the AI model based on the selected context and user message.
        """

        history_section = ""

        if chat_history:
            history_section = f"""

        ==================================================
        Conversation History
        ==================================================
        
        {chat_history}
        
        """

        # Add selected context to the prompt
        return f"""
        {prompts.prompt_main_model}
        ==================================================
        PLANNER OUTPUT
        ==================================================

        Action: {selected_context['action']}
        Confidence: {selected_context['confidence']}
        

        ==================================================
        Selected Context
        ==================================================

        {json.dumps(selected_context, default=str)}
        
        {history_section}

        ==================================================
        Current User Message

        {user_message}

        ==================================================
        Assistant's Response
        ==================================================
        """
