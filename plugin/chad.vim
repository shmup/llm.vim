vim9script
# ==============================================================================
# buffer interaction with openai chat completion
# file:     plugin/chad.vim
# author:   shmup <https://github.com/shmup>
# website:  https://github.com/shmup/chad.vim
# updated:  dec-24-2023
# license:  :h license
# ==============================================================================

if get(g:, 'loaded_chad')
  finish
endif
g:loaded_chad = 1

import autoload '../autoload/chad.vim'

command ToggleChad chad.ToggleChad()
command HandleInterrupt chad.HandleInterrupt()
command -nargs=1 SaveChad chad.SaveChadToFile(<f-args>)

augroup chad
  autocmd!
  autocmd FileType chad nnoremap <buffer> <C-C> :HandleInterrupt<CR>
augroup END

