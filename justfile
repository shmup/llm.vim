update:
  pip install --upgrade llm
  llm install llm-claude-3 --upgrade

last-changed:
  find . -type f ! -path '*/.git/*' -exec sed -i \
    "/^# Last Change:/c\# Last Change:  $(date +%b\ %d,\ %Y)" {} +
