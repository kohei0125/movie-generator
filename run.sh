#!/usr/bin/env bash
set -eux

# 1) .env をまとめて読み込む
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

# 2) （任意）MCP サーバーを CLI 経由で起動
# gemini << 'EOF'
# /mcp start all
# /exit
# EOF

# 3) Python スクリプトを実行
python3 generate_video.py
