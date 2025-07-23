#!/bin/bash

# .envファイルを読み込む
if [ -f "../.env" ]; then
  source "../.env"
fi

PORT=8080 ./mcp-avtool-go --transport http &
PORT=8081 ./mcp-chirp3-go --transport http &
PORT=8082 ./mcp-imagen-go --transport http &
PORT=8083 ./mcp-lyria-go --transport http &
PORT=8084 ./mcp-veo-go --transport http &

sleep 5