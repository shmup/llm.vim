from anthropic import Anthropic


class AnthropicProvider:

    def __init__(self):
        try:
            self.client = Anthropic()
            self.api_key_missing = not self.client.api_key
        except Exception:
            self.api_key_missing = True

    def get_stream(self, messages, system_prompt, options):
        thinking_enabled = bool(options.get('thinking_enabled', True))
        stream_params = {
            "model": 'claude-3-7-sonnet-latest',
            "max_tokens": int(options.get('max_tokens', 2000)),
            "temperature": 1.0 if thinking_enabled else float(options.get('temperature', 0.1)),
            "messages": messages
        }

        if system_prompt:
            stream_params["system"] = system_prompt

        if not thinking_enabled:
            stream_params.update({
                "top_p": float(options.get('top_p', 0.9)),
                "top_k": int(options.get('top_k', 50)),
            })
        else:
            stream_params["thinking"] = {
                "type": "enabled",
                "budget_tokens": int(options.get('thinking_budget', 1600)),
            }

        return self.client.messages.stream(**stream_params)
