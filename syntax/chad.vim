vim9script
# ==============================================================================
# buffer interaction with openai chat completion
# file:     syntax/chad.vim
# author:   shmup <https://github.com/shmup>
# website:  https://github.com/shmup/chad.vim
# updated:  dec-24-2023
# license:  :h license
# ==============================================================================

syntax match system /^###\ssystem$/
syntax match user /^###\suser$/
syntax match assistant /^###\sassistant$/

hi link system Comment
hi link user SpecialComment
hi link assistant Todo
