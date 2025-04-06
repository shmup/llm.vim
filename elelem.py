#!/usr/bin/env python3
# pyright: reportUndefinedVariable=false, reportGeneralTypeIssues=false

from anthropic import Anthropic
from anthropic.types import MessageParam
from anthropic.types import ContentBlock, TextBlock
from typing import List
import signal

DEFAULT_SEED = "Be direct and concise. Maintain context. No hedging or qualifiers."


class LlmInterface:

    def __init__(self, vim):
        self.vim = vim
        self.client = Anthropic()
        self.options = vim.eval('exists("g:llm_options") ? g:llm_options : {}')
        self.seed = vim.eval('exists("g:llm_seed") ? g:llm_seed : ""') or DEFAULT_SEED
        signal.signal(signal.SIGINT, self._handle_interrupt)

    def _handle_interrupt(self, *_):
        self.vim.command('echo "Llm cancelled"')
        raise KeyboardInterrupt

    def process_buffer(self):
        try:
            content = self.vim.eval('join(getline(1, "$"), "\n")')
            messages = self._parse_messages(content)
            response = self.client.messages.create(model=self.options.get('model', 'claude-3-5-sonnet-latest'),
                                                   max_tokens=int(self.options.get('max_tokens', 2000)),
                                                   temperature=float(self.options.get('temperature', 0.1)),
                                                   top_p=float(self.options.get('top_p', 0.9)),
                                                   top_k=int(self.options.get('top_k', 50)),
                                                   system=self.seed,
                                                   messages=messages)
            self._update_buffer(response.content)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self._append_error(str(e))
        finally:
            self._append_user_prompt()

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

    def _update_buffer(self, content_blocks: List[ContentBlock]):
          buffer = self.vim.current.buffer
          buffer.append("### assistant")
          full_response = ""
          for block in content_blocks:
              if isinstance(block, TextBlock):
                  full_response += block.text
          if full_response:
              buffer.append(full_response.split('\n'))
          self.vim.command("redraw | normal G")

    def _append_user_prompt(self):
        self.vim.command('call append("$", "### user")\nnormal G')

    def _append_error(self, error):
        self.vim.command(f'call append("$", "Error: {error}")')


def main():
    LlmInterface(vim).process_buffer()


if __name__ == '__main__':
    main()
