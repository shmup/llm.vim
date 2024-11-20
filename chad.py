#!/usr/bin/env python3
# ==============================================================================
# buffer interaction with llm
# file:     chad.py
# author:   shmup <https://github.com/shmup>
# website:  https://github.com/shmup/chad.vim
# updated:  dec-24-2023
# license:  :h license
# ==============================================================================
# pyright: reportUndefinedVariable=false, reportGeneralTypeIssues=false

import json
import signal
import llm


class InterruptedError(Exception):
    pass


def signal_handler(_, __):
    raise InterruptedError()


signal.signal(signal.SIGINT, signal_handler)


class ChatInterface:

    def __init__(self, vim, model_name):
        self.vim = vim
        self.model = llm.get_model(model_name)
        self.conversation = self.model.conversation()

    def run(self):
        buffer_content = self.vim.eval('join(getline(1, "$"), "\n")')
        messages = self.parse_buffer(buffer_content)
        try:
            response = self.fetch_response(messages)
            self.vim.command('call append(line("$"), "### assistant")')
            self.update_buffer(response)
        except (InterruptedError, KeyboardInterrupt):
            self.vim.command('echo "Chad cancelled"')
        except Exception as e:
            error_message = str(e)
            self.vim.command(f'call append("$", "Error: {error_message}")')
        finally:
            self.vim.command('call append("$", "### user")\nnormal G')

    def parse_buffer(self, buffer_content):
        messages, role, content = [], None, []
        for line in buffer_content.splitlines():
            if line.startswith("### "):
                if role:
                    messages.append({
                        "role": role,
                        "content": "\n".join(content).strip()
                    })
                role, content = line[4:].lower(), []
            else:
                content.append(line)
        if role:
            messages.append({
                "role": role,
                "content": "\n".join(content).strip()
            })
        return messages

    def fetch_response(self, messages):
        system_msg = next(
            (m['content'] for m in messages if m['role'] == 'system'), None)
        last_msg = messages[-1]['content']
        response = self.conversation.prompt(last_msg, system=system_msg)
        return response.text()

    def update_buffer(self, response):
        buffer = self.vim.current.buffer
        lines = response.split('\n')
        buffer.append(lines, len(buffer))
        self.vim.command("redraw | normal G")

    def _refresh_display(self):
        self.vim.command("redraw")
        self.vim.command("normal G")


def main():
    options = json.loads(vim.eval('g:openai_options'))
    model_name = 'claude-3.5-sonnet'  # hardcode for testing
    chat_interface = ChatInterface(vim, model_name)
    chat_interface.run()

if __name__ == '__main__':
    main()
