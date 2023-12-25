update:
  pip install --upgrade openai

last-changed:
  find . -type f ! -path '*/.git/*' -exec sed -i \
    "/^# Last Change:/c\# Last Change:  $(date +%b\ %d,\ %Y)" {} +
