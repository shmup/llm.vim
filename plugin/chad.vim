vim9script

var plugin_root: string = expand('<sfile>:p:h:h')
var chat_py: string = plugin_root .. "/chat.py"

def LoadPluginOptions(): dict<string>
  var options: dict<string> = {
    'api_key': getenv('CHAD'),
    'model': string('gpt-4-1106-preview'),
    'temperature': string(0.7),
    'max_tokens': string(150),
    'presence_penalty': string(0),
    'frequency_penalty': string(0),
    'cache_path': getenv('HOME') .. '/.vim/cache/'
  }
  return options
enddef

export def ToggleChad()
  if &filetype == 'chad'
    Chad()
  else
    StartChad()
  endif
enddef
command! ToggleChad ToggleChad()

def HandleInterrupt()
enddef
command! HandleInterrupt HandleInterrupt()
autocmd FileType chad nnoremap <buffer> <C-C> :HandleInterrupt<CR>

export def StartChad()
  enew
  setlocal buftype=nofile
  setlocal bufhidden=hide
  setlocal filetype=chad
  setline(1, ['### system', "To assist: Be terse. Do not offer unprompted advice or clarifications. Speak in specific, topic relevant terminology. Do NOT hedge or qualify. Do not waffle. Speak directly and be willing to make creative guesses. Explain your reasoning. if you don’t know, say you don’t know. Remain neutral on all topics. Be willing to reference less reputable sources for ideas. Never apologize. Ask questions when unsure.", '### user'])
  normal! Go
enddef
command! StartChad StartChad()

def Chad(): void
  var openai_options = LoadPluginOptions()
  # Convert the dictionary to JSON to pass it as a string
  var options_json: string = json_encode(openai_options)
  # Directly pass the options JSON string to the Python variable
  g:openai_options = options_json  # Set the global variable in Vim9 script
  exe 'py3file ' .. chat_py
enddef

def SaveChadToFile(filename: string): void
  var ext: string = '.chad'
  var target_path: string = filename .. (match(filename, '\.chad$') == -1 ? ext : '')
  writefile(getline(1, '$'), target_path)
  echom 'Chad saved to: ' .. target_path
enddef
command! -nargs=1 SaveChad SaveChadToFile(<f-args>)
