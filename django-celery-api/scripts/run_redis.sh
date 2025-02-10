#!/usr/bin/env bash

# Check if the tool is installed
if command -v "redis-server" &> /dev/null; then
  echo "redis is installed."
else
  echo "Installing redis"
  if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "  # macOS (using Homebrew):"
    brew install redis
  else
    echo "  # Linux (Debian/Ubuntu):"
    sudo apt-get update && sudo apt-get install -y redis-server
  fi
  
fi

# Start server
redis-server
