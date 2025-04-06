#!/usr/bin/env python3
# pyright: reportUndefinedVariable=false, reportGeneralTypeIssues=false

from anthropic import Anthropic
from anthropic.types import MessageParam
from typing import List
import signal

DEFAULT_SEED = "Be direct and concise. Maintain context. No hedging or qualifiers."


class LlmInterface:

    def __init__(self, vim):
        self.vim = vim
        try:
            self.client = Anthropic()
            if not self.client.api_key:
                raise ValueError("ANTHROPIC_API_KEY not set")
        except (ValueError, Exception):
            self.api_key_missing = True
        else:
            self.api_key_missing = False
        self.options = vim.eval('exists("g:llm_options") ? g:llm_options : {}')
        self.seed = vim.eval('exists("g:llm_seed") ? g:llm_seed : ""') or DEFAULT_SEED
        signal.signal(signal.SIGINT, self._handle_interrupt)

    def _handle_interrupt(self, *_):
        self.vim.command('echo "Llm cancelled"')
        raise KeyboardInterrupt

    def _parse_messages(self, content) -> List[MessageParam]:
        messages: List[MessageParam] = []
        role, lines = None, []

        for line in content.splitlines():
            if line.startswith("### "):
                if role and lines:
                    messages.append({
                        "role": "user" if role == "user" else "assistant",
                        "content": "\n".join(lines).strip()
                    })
                role, lines = line[4:].lower(), []
            else:
                lines.append(line)

        if role and lines:
            messages.append({"role": "user" if role == "user" else "assistant", "content": "\n".join(lines).strip()})

        return messages

    def process_buffer(self):
        if self.api_key_missing:
            self.vim.command(
                'echohl WarningMsg | echo "Please set ANTHROPIC_API_KEY environment variable" | echohl None')
            return
        try:
            content = self.vim.eval('join(getline(1, "$"), "\n")')
            messages = self._parse_messages(content)

            # Append assistant header once
            self.vim.current.buffer.append("### assistant")
            # Add an empty line that will be replaced with content
            self.vim.current.buffer.append("")
            self.vim.command("redraw | normal G")

            accumulated_text = ""
            with self.client.messages.stream(model=self.options.get('model', 'claude-3-7-sonnet-20250219'),
                                             max_tokens=int(self.options.get('max_tokens', 2000)),
                                             temperature=float(self.options.get('temperature', 0.1)),
                                             top_p=float(self.options.get('top_p', 0.9)),
                                             top_k=int(self.options.get('top_k', 50)),
                                             system=self.seed,
                                             messages=messages) as stream:
                for text in stream.text_stream:
                    accumulated_text += text
                    self._update_buffer(accumulated_text)
                    self.vim.command('redraw')

        except KeyboardInterrupt:
            pass
        except Exception as e:
            self._append_error(str(e))
        finally:
            self._append_user_prompt()

    def _update_buffer(self, text):
        buffer = self.vim.current.buffer
        assistant_line = 0

        # Find the last "### assistant" line
        for i in range(len(buffer) - 1, -1, -1):
            if buffer[i] == "### assistant":
                assistant_line = i
                break

        # Replace everything after the "### assistant" line
        new_lines = text.split('\n')
        buffer[assistant_line+1:] = new_lines

        # Move cursor to end
        self.vim.command("normal G")

    def _append_user_prompt(self):
        self.vim.command('call append("$", "### user")\nnormal G')

    def _append_error(self, error):
        self.vim.command(f'call append("$", "Error: {error}")')


def main():
    LlmInterface(vim).process_buffer()


if __name__ == '__main__':
    main()
