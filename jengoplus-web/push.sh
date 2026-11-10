#!/bin/bash
# Usage (Git Bash): ./push.sh "what you changed"
git add -A && git commit -m "${1:-Update site}" && git push
