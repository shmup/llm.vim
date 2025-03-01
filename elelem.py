#!/usr/bin/env python3
# pyright: reportUndefinedVariable=false, reportGeneralTypeIssues=false

import signal
from typing import List, Dict
import os
import json

import llm


class LlmInterface:

    def __init__(self, vim, model_name: str):
        self.vim = vim
        self.model = llm.get_model(model_name)

        # Get buffer ID to use as conversation identifier
        self.buffer_id = str(self.vim.current.buffer.number)

        # Path to store conversation IDs
        self.storage_path = os.path.join(llm.user_dir(), "vim_conversations.json")

        # Load or create the conversation
        self.conversation = self._get_or_create_conversation()

        signal.signal(signal.SIGINT, self._handle_interrupt)

    def _handle_interrupt(self, *_):
        self.vim.command('echo "Llm cancelled"')
        raise KeyboardInterrupt

    def _get_or_create_conversation(self):
        # Load existing conversation IDs
        conversation_ids = {}
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    conversation_ids = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        # Check if we have a conversation ID for this buffer
        if self.buffer_id in conversation_ids:
            try:
                # Try to load the existing conversation
                return self.model.conversation(id=conversation_ids[self.buffer_id])
            except Exception:
                # If loading fails, create a new conversation
                pass

        # Create a new conversation
        conversation = self.model.conversation()

        # Save the conversation ID
        conversation_ids[self.buffer_id] = conversation.id
        with open(self.storage_path, 'w') as f:
            json.dump(conversation_ids, f)

        return conversation

    def process_buffer(self) -> None:
        try:
            content = self.vim.eval('join(getline(1, "$"), "\n")')
            messages = self._parse_messages(content)
            response = self._get_response(messages)
            self._update_buffer(response)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self._append_error(str(e))
        finally:
            self._append_user_prompt()

    def _parse_messages(self, content: str) -> List[Dict[str, str]]:
        messages, role, lines = [], None, []
        for line in content.splitlines():
            if line.startswith("### "):
                if role:
                    messages.append({"role": role, "content": "\n".join(lines).strip()})
                role, lines = line[4:].lower(), []
            else:
                lines.append(line)
        if role and lines:
            messages.append({"role": role, "content": "\n".join(lines).strip()})
        return messages

    def _get_response(self, messages: List[Dict[str, str]]) -> str:
        # Extract system message if present
        system_msg = next((m['content'] for m in messages if m['role'] == 'system'), None)

        # Get the most recent user message
        user_messages = [m for m in messages if m['role'] == 'user']
        if not user_messages:
            return "Error: No user message found"

        user_msg = user_messages[-1]['content']

        # Send the prompt to the model
        return self.conversation.prompt(user_msg, system=system_msg).text()

    def _update_buffer(self, response: str) -> None:
        buffer = self.vim.current.buffer
        buffer.append("### assistant")
        buffer.append(response.split('\n'))
        self.vim.command("redraw | normal G")

    def _append_user_prompt(self) -> None:
        self.vim.command('call append("$", "### user")\nnormal G')

    def _append_error(self, error: str) -> None:
        self.vim.command(f'call append("$", "Error: {error}")')


def main():
    model_name = vim.eval('get(g:llm_options, "model", "claude-3.5-sonnet")')
    LlmInterface(vim, model_name).process_buffer()


if __name__ == '__main__':
    main()
