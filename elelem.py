#!/usr/bin/env python3
# pyright: reportUndefinedVariable=false, reportGeneralTypeIssues=false

from anthropic import Anthropic
from typing import List, Dict
import signal

DEFAULT_SEED = "Be direct and concise. Maintain context. No hedging or qualifiers."


class LlmInterface:

    def __init__(self, vim):
        self.vim = vim
        self.api_key_missing = False

        try:
            self.client = Anthropic()
            if not self.client.api_key:
                raise ValueError("ANTHROPIC_API_KEY not set")
        except Exception:
            self.api_key_missing = True

        self.options = vim.eval('get(g:, "llm_options", {})')
        self.seed = vim.eval('get(g:, "llm_seed", "")') or DEFAULT_SEED
        signal.signal(signal.SIGINT, lambda *_: self.vim.command('echo "Llm cancelled"') or exit(1))

    def _parse_messages(self, content) -> List[Dict[str, str]]:
        messages, role, lines = [], None, []

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
            content = "\n".join(self.vim.current.buffer[:])
            messages = self._parse_messages(content)
            self.vim.current.buffer.append(["### assistant", ""])
            self.vim.command("redraw | normal G")

            accumulated_text = ""
            stream_params = {
                "model": self.options.get('model', 'claude-3-7-sonnet-20250219'),
                "max_tokens": int(self.options.get('max_tokens', 2000)),
                "temperature": float(self.options.get('temperature', 0.1)),
                "top_p": float(self.options.get('top_p', 0.9)),
                "top_k": int(self.options.get('top_k', 50)),
                "system": self.seed,
                "messages": messages
            }

            with self.client.messages.stream(**stream_params) as stream:
                for text in stream.text_stream:
                    accumulated_text += text
                    self._update_buffer(accumulated_text)
                    self.vim.command('redraw')
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.vim.current.buffer.append(f"Error: {str(e)}")
        finally:
            self.vim.current.buffer.append("### user")
            self.vim.command("normal G")

    def _update_buffer(self, text):
        buffer = self.vim.current.buffer
        for i in range(len(buffer) - 1, -1, -1):
            if buffer[i] == "### assistant":
                buffer[i + 1:] = text.split('\n')
                break
        self.vim.command("normal G")


def main():
    LlmInterface(vim).process_buffer()


if __name__ == '__main__':

    main()
