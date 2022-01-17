#!/usr/bin/env zsh

set -e 
set extglob
setopt +o nomatch

rm -f ./**/*.pyc

ssh gameserve sudo systemctl stop webingo

scp -r static/ gameserve:/opt/webingo-server/

ssh gameserve sudo systemctl restart webingo
