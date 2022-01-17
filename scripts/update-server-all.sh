#!/usr/bin/env zsh

#
# THIS SCRIPT WILL UPDATE ALL SERVER RELATED FILES
# INCLUDING:
# - PYTHON FILES (webingo folder)
# - GAME CONFIGS (res folder)
# - HTML FILES   (static folder)
# WILL NOT UPDATE GAMES (pck) files
#

set -e 
set extglob
setopt +o nomatch

rm -f ./**/*.pyc

if $1 != "--dont-touch-service"; then
    echo "Stoping game server service"
    ssh gameserve sudo systemctl stop webingo
fi

echo "Copying game resources"
scp -r res/ gameserve:/opt/webingo-server

echo "Copying server source code"
scp -r webingo/ gameserve:/opt/webingo-server

echo "Copying static files"
scp -r static/splash/       gameserve:/opt/webingo-server/static
scp -r static/fb_portal_2/  gameserve:/opt/webingo-server/static

if $1 != "--dont-touch-service"; then
    echo "Restarting game server service"
    ssh gameserve sudo systemctl restart webingo
fi

echo "Done!"

