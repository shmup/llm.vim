#!/usr/bin/env python3
# pyright: reportUndefinedVariable=false, reportGeneralTypeIssues=false

import signal
from typing import List, Dict

import llm


class LlmInterface:

    def __init__(self, vim, model_name: str):
        self.vim = vim
        self.model = llm.get_model(model_name)
        self.conversation = self.model.conversation()
        signal.signal(signal.SIGINT, self._handle_interrupt)

    def _handle_interrupt(self, *_):
        self.vim.command('echo "Llm cancelled"')
        raise KeyboardInterrupt

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
                    messages.append({
                        "role": role,
                        "content": "\n".join(lines).strip()
                    })
                role, lines = line[4:].lower(), []
            else:
                lines.append(line)
        if role and lines:
            messages.append({
                "role": role,
                "content": "\n".join(lines).strip()
            })
        return messages

    def _get_response(self, messages: List[Dict[str, str]]) -> str:
        system_msg = next(
            (m['content'] for m in messages if m['role'] == 'system'), None)
        user_msg = messages[-1]['content']
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
