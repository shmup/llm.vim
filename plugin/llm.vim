vim9script

import autoload '../autoload/llm.vim'

command! ToggleLlm llm.Toggle()
command! -nargs=1 SaveLlm llm.SaveToFile(<f-args>)
command! ToggleThink llm.ToggleThinking()
command! ThinkingStatus llm.ThinkingStatus()
