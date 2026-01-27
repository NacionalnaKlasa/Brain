#!/bin/bash
# Kill all VS Code server processes
pkill -f ".vscode-server"
# Optional: Clear the server directory if things are really corrupted
# rm -rf ~/.vscode-server/bin/*
echo "Cleaned up VS Code Server processes."