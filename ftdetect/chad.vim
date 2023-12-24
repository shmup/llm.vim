vim9script
# ==============================================================================
# buffer interaction with openai chat completion
# file:     ftdetect/chad.vim
# author:   shmup <https://github.com/shmup>
# website:  https://github.com/shmup/chad.vim
# updated:  dec-24-2023
# license:  :h license
# ==============================================================================

autocmd BufRead,BufNewFile *.chad setfiletype markdown.chad
