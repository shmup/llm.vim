vim9script
# ==============================================================================
# buffer interaction with openai chat completion
# file:     plugin/llm.vim
# author:   shmup <https://github.com/shmup>
# website:  https://github.com/shmup/llm.vim
# updated:  dec-24-2023
# license:  :h license
# ==============================================================================

import autoload '../autoload/llm.vim'

command ToggleLlm llm.ToggleLlm()
command -nargs=1 SaveLlm llm.SaveLlmToFile(<f-args>)

augroup llm
  autocmd!
  autocmd FileType llm nnoremap <buffer> <C-C> :HandleInterrupt<CR>
augroup END
