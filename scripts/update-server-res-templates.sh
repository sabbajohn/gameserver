#!/usr/bin/env zsh

set -e 
set extglob
setopt +o nomatch

rm -f ./**/*.pyc

ssh gameserve sudo systemctl stop webingo

scp -r res/templates/* gameserve:/opt/webingo-server/res/templates

ssh gameserve sudo systemctl restart webingo
