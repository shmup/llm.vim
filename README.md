This is a vim plugin to interact with Simon's llm tool.

https://llm.datasette.io/en/stable/

### CONFIGURE THE DEFAULTS

    let g:llm_seed = "You are a helpful AI assistant."
    let g:llm_options = {
          \ 'model': 'claude-3.5-sonnet-latest',
          \ 'temperature': 0.3,
          \ 'max_tokens': 1000,
          \ 'top_p': 0.7,
          \ 'top_k': 5,
          \ 'thinking_enabled': v:false,
          \ 'thinking_budget': 1600,
          \ }

### EXAMPLE MAPPING

    " used to both open llm buffer and request response
    nnoremap ,c :ToggleLlm<CR>

### REQUIREMENTS

- vim9
- python3
- pip install anthropic

set an ANTHROPIC_API_KEY environment variable

https://console.anthropic.com/settings/keys


