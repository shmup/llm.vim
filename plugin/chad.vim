vim9script

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

