from openai import OpenAI
import signal
import json
# pyright: reportUndefinedVariable=false, reportGeneralTypeIssues=false


class InterruptedError(Exception):
  pass


def signal_handler(_, __):
  raise InterruptedError()


signal.signal(signal.SIGINT, signal_handler)


def get_streamed_response(messages, options):
  client = OpenAI(api_key=options['api_key'])
  completion_params = {
      "model": options['model'],
      "messages": messages,
      "stream": True,
      "temperature": float(options.get('temperature',
                                       1)),  # Default to 1 if not set
      "presence_penalty": float(options.get('presence_penalty',
                                            0)),  # Default to 0 if not set
      "frequency_penalty": float(options.get('frequency_penalty',
                                             0)),  # Default to 0 if not set
  }
  try:
    with open('debug.log', 'a') as debug_file:
      debug_file.write("completion_params before API call: " +
                       repr(completion_params) + '\n')

    stream = client.chat.completions.create(**completion_params)

    # Log the raw stream data before any processing
    with open('debug.log', 'a') as debug_file:
      debug_file.write("Raw stream data: " + repr(stream) + '\n')

    return stream
  except Exception as e:
    error_message = str(e)
    if isinstance(e, bytes):
      error_message = e.decode('utf-8')
    # Log the error message
    with open('debug.log', 'a') as debug_file:
      debug_file.write("Exception: " + error_message + '\n')
    return error_message


def parse_chat_messages(chat_content):
  lines = chat_content.splitlines()
  messages = []
  current_role = None
  content_buffer = []

  def add_message(role, content):
    if role:
      # Ensure content is a str, decode if it's bytes
      if isinstance(content, bytes):
        content = content.decode('utf-8')  # or the appropriate encoding
      messages.append({"role": role, "content": content.strip()})

  for line in lines:
    if line.startswith("### "):  # Detects system, user, and assistant tags
      # Add the current message to messages list before switching roles
      add_message(current_role, "\n".join(content_buffer))
      # Clear the content buffer for the next message
      content_buffer.clear()
      # Update the current role according to the tag
      current_role = line[4:].lower()
    else:
      # Add line to content buffer
      content_buffer.append(line)

  # Add the last message if there is one
  add_message(current_role, "\n".join(content_buffer))

  # Log the chat_content and messages for debugging
  with open('debug.log', 'a') as debug_file:
    debug_file.write("chat_content: " + chat_content + '\n')
    debug_file.write("messages: " + json.dumps(messages, default=str) + '\n')

  return messages


def render_text_chunks(stream):
  buffer = vim.current.buffer
  line_number = len(buffer) - 1

  try:
    for chunk in stream:
      text = chunk.choices[0].delta.content
      # Log the text for debugging
      with open('debug.log', 'a') as debug_file:
        debug_file.write("text: " + json.dumps(text, default=str) + '\n')

      if isinstance(text, bytes):  # Add this check
        text = text.decode('utf-8')
      if text:
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        lines = text.split('\n')

        if buffer[line_number].startswith("### "):
          buffer[line_number + 1:line_number + 1] = lines[0:1]
          line_number += 1
        else:
          buffer[line_number] += lines[0]
        if len(lines) > 1:
          buffer[line_number + 1:line_number + 1] = lines[1:]
          line_number += len(lines) - 1

        vim.command("redraw")
        vim.command("normal G")
  except InterruptedError:
    vim.command('echo "Stream cancelled"')


def vim_chat():
  openai_options = json.loads(vim.eval('g:openai_options'))
  openai_options = {
      k: (v.decode('utf-8') if isinstance(v, bytes) else v).strip("'")
      for k, v in openai_options.items()
  }
  buffer_content = vim.eval('join(getline(1, "$"), "\n")')
  messages = parse_chat_messages(buffer_content)
  try:
    response = get_streamed_response(messages, openai_options)
    vim.command('call append("$", "### assistant")')
    if isinstance(response, str):  # Check if response is an error message
      escaped_response = response.replace('"', '\\"').replace("\n", '\\n')
      vim.command(f'call append("$", "{escaped_response}")')
    elif hasattr(response, '__iter__'):
      render_text_chunks(response)
    else:
      vim.command('call append("$", "Error: Unexpected response type")')
  except KeyboardInterrupt:
    vim.command('echo "Chat cancelled"')
  except InterruptedError:
    vim.command('echo "Stream cancelled by user"')
  finally:
    vim.command('call append("$", "### user")')
    vim.command("normal G")


def main():
  vim_chat()


if __name__ == '__main__':
  main()
