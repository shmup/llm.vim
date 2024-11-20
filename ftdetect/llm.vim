vim9script
# ==============================================================================
# buffer interaction with openai chat completion
# file:     ftdetect/llm.vim
# author:   shmup <https://github.com/shmup>
# website:  https://github.com/shmup/llm.vim
# updated:  dec-24-2023
# license:  :h license
# ==============================================================================

autocmd BufRead,BufNewFile *.llm setfiletype markdown.llm
