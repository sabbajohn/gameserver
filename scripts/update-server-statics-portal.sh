#!/usr/bin/env zsh

set -e 
set extglob
setopt +o nomatch

rm -f ./**/*.pyc

ssh gameserve sudo systemctl stop webingo

scp -r static/fb_portal_2/ gameserve:/opt/webingo-server/static

ssh gameserve sudo systemctl restart webingo
