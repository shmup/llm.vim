vim9script

const PLUGIN_ROOT = expand('<sfile>:p:h:h')
const LLM_PY = PLUGIN_ROOT .. "/python/elelem.py"

export def Toggle()
    if &filetype =~ 'llm'
        Process()
    else
        Start()
    endif
enddef

export def ToggleThinking()
    g:llm_options.thinking_enabled = !g:llm_options.thinking_enabled
enddef

export def ThinkingStatus(): string
    return get(g:llm_options, 'thinking_enabled', v:false) ? '🧠' : ''
enddef

export def Start()
    const seed = get(g:, 'llm_seed', 'You are helpful.')
    enew
    setlocal buftype=nofile bufhidden=hide filetype=markdown.llm
    setline(1, ['### system', seed, "", '### user'])
    normal! G
enddef

def Process(): void
    exe 'py3file ' .. LLM_PY
enddef

export def SaveToFile(filename: string): void
    const ext = '.llm'
    const target = filename .. (filename =~ '\.llm$' ? '' : ext)
    writefile(getline(1, '$'), target)
    echom 'chat saved to: ' .. target
enddef
