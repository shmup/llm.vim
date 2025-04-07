#!/usr/bin/env python3
# pyright: reportUndefinedVariable=false, reportGeneralTypeIssues=false

from anthropic import Anthropic
from typing import List, Dict
import signal

DEFAULT_SEED = "Be direct and concise. Maintain context. No hedging or qualifiers."


class LlmInterface:

    def __init__(self, vim):
        self.vim = vim
        try:
            self.client = Anthropic()
            self.api_key_missing = not self.client.api_key
        except Exception:
            self.api_key_missing = True

        self.options = vim.eval('get(g:, "llm_options", {})')
        signal.signal(signal.SIGINT, lambda *_: self.vim.command('echo "Llm cancelled"') or exit(1))

    def _parse_messages(self, content) -> List[Dict[str, str]]:
        messages, role, lines = [], None, []
        for line in content.splitlines():
            if line.startswith("### "):
                if role and lines and role != "system":
                    messages.append({
                        "role": "user" if role == "user" else "assistant",
                        "content": "\n".join(lines).strip()
                    })
                role, lines = line[4:].lower(), []
            else:
                lines.append(line)
        if role and lines and role != "system":  # Skip system messages
            messages.append({"role": "user" if role == "user" else "assistant", "content": "\n".join(lines).strip()})
        return messages

    def _update_section(self, section_marker, text):
        buffer = self.vim.current.buffer
        for i in range(len(buffer) - 1, -1, -1):
            if buffer[i] == section_marker:
                buffer[i + 1:] = text.split('\n')
                break
        self.vim.command("normal G")

    def _extract_system_prompt(self) -> str | None:
        """Extract multiline system prompt from buffer if it exists, otherwise return None"""
        buffer = self.vim.current.buffer[:]
        system_lines = []
        in_system = False

        for _, line in enumerate(buffer):
            if line.startswith("### system"):
                in_system = True
                continue
            elif in_system and line.startswith("### "):
                break
            elif in_system:
                system_lines.append(line.strip())

        return "\n".join(system_lines) if system_lines else None

    def process_buffer(self):
        if self.api_key_missing:
            self.vim.command(
                'echohl WarningMsg | echo "Please set ANTHROPIC_API_KEY environment variable" | echohl None')
            return
        system_prompt = self._extract_system_prompt()
        thinking_enabled = bool(self.options.get('thinking_enabled', True))
        try:
            content = "\n".join(self.vim.current.buffer[:])
            messages = self._parse_messages(content)

            stream_params = {
                "model": 'claude-3-7-sonnet-latest',
                "max_tokens": int(self.options.get('max_tokens', 2000)),
                "temperature": 1.0 if thinking_enabled else float(self.options.get('temperature', 0.1)),
                "messages": messages
            }

            if system_prompt is not None:
              stream_params["system"] = system_prompt

            if not thinking_enabled:
                stream_params.update({
                    "top_p": float(self.options.get('top_p', 0.9)),
                    "top_k": int(self.options.get('top_k', 50)),
                })
            else:
                stream_params["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": int(self.options.get('thinking_budget', 1600)),
                }

            # Add initial section
            section = "### thinking" if thinking_enabled else "### assistant"
            self.vim.current.buffer.append([section, ""])
            self.vim.command("redraw | normal G")

            with self.client.messages.stream(**stream_params) as stream:
                self._handle_stream(stream, thinking_enabled)

        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.vim.current.buffer.append(f"Error: {str(e)}")
        finally:
            self.vim.current.buffer.append("### user")
            self.vim.command("normal G")

    def _handle_stream(self, stream, thinking_enabled):
        thinking_text = ""
        assistant_text = ""
        in_thinking_mode = thinking_enabled

        for event in stream:
            if hasattr(event, 'type'):
                if thinking_enabled and event.type == "thinking":
                    thinking_text += event.thinking
                    self._update_section("### thinking", thinking_text)
                elif event.type == "content_block_start" and in_thinking_mode and event.content_block.type == "text":
                    in_thinking_mode = False
                    self.vim.current.buffer.append(["### assistant", ""])
                    self.vim.command("redraw | normal G")
                elif event.type == "text":
                    assistant_text += event.text
                    self._update_section("### assistant", assistant_text)
            elif hasattr(stream, 'text_stream'):  # Legacy API support
                for text in stream.text_stream:
                    assistant_text += text
                    self._update_section("### assistant", assistant_text)
                    self.vim.command('redraw')
                return

            self.vim.command('redraw')


def main():
    LlmInterface(vim).process_buffer()


if __name__ == '__main__':
    main()
