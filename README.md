### OVERRIDE THE DEFAULTS

    let g:llm_seed = "You are a helpful AI assistant."
    let g:llm_options = {
        \ 'api_key': $YOUR_EXPORTED_API_KEY,
        \ 'model': "gpt-4-1106-preview",
        \ 'temperature': 0.7,
        \ 'max_tokens': 150,
        \ 'presence_penalty': 0,
        \ 'frequency_penalty': 0
    \ }

### EXAMPLE MAPPING

    " used to both open llm buffer and request response
    nnoremap ,c :ToggleLlm<CR>

### REQUIREMENTS

- vim9
- openai-python https://github.com/openai/openai-python#installation

### ABOUT

I wrote this to spin up a buffer and communicate with GPT-4

The syntax for the buffer was borrowed from a feature rich alternative:

https://github.com/madox2/vim-ai

---

![llm](https://github.com/shmup/llm.vim/assets/118710/83918715-43e7-4d3f-8492-6a09c6ac832f)

