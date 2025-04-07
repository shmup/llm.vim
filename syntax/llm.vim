vim9script

syntax match system /^###\ssystem$/
syntax match user /^###\suser$/
syntax match thinking /^###\sthinking$/
syntax match assistant /^###\sassistant$/

hi link system NonText
hi link thinking Folded
hi link user SpecialComment
hi link assistant Constant
