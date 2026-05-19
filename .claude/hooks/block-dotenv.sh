#!/bin/bash
path=$(python3 -c "import os,json; d=json.loads(os.environ.get('CLAUDE_TOOL_INPUT','{}')); print(d.get('file_path',''))")
if [ "$(basename "$path")" = ".env" ]; then
    echo "Blocked: direct edits to .env are not allowed. Update .env.example instead."
    exit 1
fi
