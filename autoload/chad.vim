vim9script
# ==============================================================================
# buffer interaction with openai chat completion
# file:     autoload/chad.vim
# author:   shmup <https://github.com/shmup>
# website:  https://github.com/shmup/chad.vim
# updated:  dec-24-2023
# license:  :h license
# ==============================================================================

var plugin_root: string = expand('<sfile>:p:h:h')
var chad_py: string = plugin_root .. "/chad.py"

def LoadPluginOptions(): dict<string>
  var options: dict<string> = {
    'api_key': string(getenv('CHAD')),
    'model': 'gpt-4-1106-preview',
    'temperature': '0.3',
    'top_p': '0.5',
    'max_tokens': '150',
    'presence_penalty': '0.1',
    'frequency_penalty': '0.6'
  }
  if exists('g:chad_options')
    for [key, value] in items(g:chad_options)
      if type(value) == v:t_float || type(value) == v:t_number
        options[key] = string(value)
      elseif type(value) == v:t_string
        options[key] = value
      endif
    endfor
  endif
  return options
enddef

export def ToggleChad()
  if &filetype == 'chad'
    Chad()
  else
    StartChad()
  endif
enddef

export def StartChad()
  var seed: string = exists('g:chad_seed') ? g:chad_seed : 'You are helpful.'
  enew
  setlocal buftype=nofile
  setlocal bufhidden=hide
  setlocal filetype=chad
  setline(1, ['### system', seed, '### user'])
  normal! Go
enddef

def Chad(): void
  var openai_options = LoadPluginOptions()
  var options_json: string = json_encode(openai_options)
  g:openai_options = options_json
  exe 'py3file ' .. chad_py
enddef

export def SaveChadToFile(filename: string): void
  var ext: string = '.chad'
  var target_path: string = filename .. (match(filename, '\.chad$') == -1 ? ext : '')
  writefile(getline(1, '$'), target_path)
  echom 'Chad saved to: ' .. target_path
enddef

export def HandleInterrupt()
enddef
