vim9script

syntax match system /^###\ssystem$/
syntax match user /^###\suser$/
syntax match thinking /^###\sthinking$/
syntax match assistant /^###\sassistant$/

hi link system Comment
hi link user SpecialComment
hi link assistant Todo
hi link thinking Identifier
