from typing import List, Dict
import importlib


class ProviderManager:

    def __init__(self, provider_name="anthropic"):
        try:
            provider_module = importlib.import_module(f"providers.{provider_name}")
            provider_class = getattr(provider_module, f"{provider_name.capitalize()}Provider")
            self.provider = provider_class()
            self.api_key_missing = getattr(self.provider, "api_key_missing", False)
        except Exception:
            self.api_key_missing = True

    def parse_messages(self, content: str) -> List[Dict[str, str]]:
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
        if role and lines and role != "system":
            messages.append({"role": "user" if role == "user" else "assistant", "content": "\n".join(lines).strip()})
        return messages

    def get_stream(self, messages, system_prompt, options):
        return self.provider.get_stream(messages, system_prompt, options)
