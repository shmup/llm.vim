#!/usr/bin/env python3
# pyright: reportUndefinedVariable=false, reportGeneralTypeIssues=false, reportMissingImports=false

import signal

plugin_root = vim.eval('PLUGIN_ROOT')
sys.path.append(plugin_root)
from provider_manager import ProviderManager


class LlmInterface:

    def __init__(self, vim):
        self.vim = vim
        self.manager = ProviderManager()
        self.options = vim.eval('get(g:, "llm_options", {})')
        signal.signal(signal.SIGINT, lambda *_: self.vim.command('echo "Llm cancelled"') or exit(1))

    def _update_section(self, section_marker, text):
        buffer = self.vim.current.buffer
        for i in range(len(buffer) - 1, -1, -1):
            if buffer[i] == section_marker:
                buffer[i + 1:] = text.split('\n')
                break
        self.vim.command("normal G")

    def _extract_system_prompt(self):
        buffer = self.vim.current.buffer[:]
        system_lines = []
        in_system = False

        for line in buffer:
            if line.startswith("### system"):
                in_system = True
                continue
            elif in_system and line.startswith("### "):
                break
            elif in_system:
                system_lines.append(line.strip())

        return "\n".join(system_lines) if system_lines else None

    def process_buffer(self):
        if self.manager.api_key_missing:
            self.vim.command(
                'echohl WarningMsg | echo "Please set ANTHROPIC_API_KEY environment variable" | echohl None')
            return

        try:
            content = "\n".join(self.vim.current.buffer[:])
            messages = self.manager.parse_messages(content)
            system_prompt = self._extract_system_prompt()
            thinking_enabled = bool(self.options.get('thinking_enabled', True))

            section = "### thinking" if thinking_enabled else "### assistant"
            self.vim.current.buffer.append([section, ""])
            self.vim.command("redraw | normal G")

            stream = self.manager.get_stream(messages, system_prompt, self.options)
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

        with stream as s:
            for event in s:
                if hasattr(event, 'type'):
                    if thinking_enabled and event.type == "thinking":
                        thinking_text += event.thinking
                        self._update_section("### thinking", thinking_text)
                    elif event.type == "content_block_start" and in_thinking_mode and event.content_block.type == "text":
                        in_thinking_mode = False
                        self.vim.current.buffer.append(["### assistant", ""])
                    elif event.type == "text":
                        assistant_text += event.text
                        self._update_section("### assistant", assistant_text)
                self.vim.command('redraw')


def main():
    LlmInterface(vim).process_buffer()


if __name__ == '__main__':
    main()
