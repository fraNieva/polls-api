#!/bin/bash
path=$(python3 -c "import os,json; d=json.loads(os.environ.get('CLAUDE_TOOL_INPUT','{}')); print(d.get('file_path',''))")
if echo "$path" | grep -q "/app/"; then
    module=$(basename "$path" .py)
    ./venv/bin/python -m pytest tests/ -k "$module" -q --no-header --tb=short 2>&1 | tail -10
fi
