#!/usr/bin/env sh
set -euo pipefail

GIT_BRANCH="main"
FILE_LIST="app.py data.py components/summary.py dockerfile compose.yaml"

if ! command -v wget >/dev/null 2>&1; then
  echo "Error: wget is required but not installed."
  exit 1
fi

BASE_URL="https://raw.githubusercontent.com/vithom/strava-offline-analyzer/refs/heads/${GIT_BRANCH}"

echo "Branch: $GIT_BRANCH"

for FILE in $FILE_LIST; do
  URL="${BASE_URL}/${FILE}"
  echo "Downloading: $URL"
  wget -O "$FILE" "$URL"
done

echo "Done."
