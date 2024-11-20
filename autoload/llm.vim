vim9script
# ==============================================================================
# buffer interaction with openai chat completion
# file:     autoload/llm.vim
# author:   shmup <https://github.com/shmup>
# website:  https://github.com/shmup/llm.vim
# updated:  dec-24-2023
# license:  :h license
# ==============================================================================

var plugin_root: string = expand('<sfile>:p:h:h')
var llm_py: string = plugin_root .. "/llm.py"

def LoadPluginOptions(): dict<string>
    var options: dict<string> = {
        'model': 'gpt-4',
        'temperature': '0.3'
    }
    if exists('g:llm_options')
        for [key, value] in items(g:llm_options)
            if type(value) == v:t_float || type(value) == v:t_number
                options[key] = string(value)
            elseif type(value) == v:t_string
                options[key] = value
            endif
        endfor
    endif
    return options
enddef

export def ToggleLlm()
  var filetypes = split(&filetype, '\.')
  if index(filetypes, 'llm') >= 0
    Llm()
  else
    StartLlm()
  endif
enddef

export def StartLlm()
  var seed: string = exists('g:llm_seed') ? g:llm_seed : 'You are helpful.'
  enew
  setlocal buftype=nofile
  setlocal bufhidden=hide
  setlocal filetype=markdown.llm
  setline(1, ['### system', seed, '### user'])
  normal! Go
enddef

def Llm(): void
  var openai_options = LoadPluginOptions()
  var options_json: string = json_encode(openai_options)
  g:openai_options = options_json
  exe 'py3file ' .. llm_py
enddef

export def SaveLlmToFile(filename: string): void
  var ext: string = '.llm'
  var target_path: string = filename .. (match(filename, '\.llm$') == -1 ? ext : '')
  writefile(getline(1, '$'), target_path)
  echom 'Llm saved to: ' .. target_path
enddef

export def HandleInterrupt()
enddef
