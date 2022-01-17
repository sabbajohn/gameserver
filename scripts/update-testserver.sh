#!/usr/bin/env zsh

set -e 
set extglob
setopt +o nomatch

rm -f update.log
rm -f ./**/*.pyc

echo -n "Stoping service..."
ssh gameservetest sudo systemctl stop webingo
echo -e "Ok\n"

echo -n "Copying res folder..."
scp -qr res/ gameservetest:/opt/webingo-server >> update.log
echo -e "Ok\n"

echo -n "Copying static folder..."
scp -q  static/favicon.*     gameservetest:/opt/webingo-server/static/. >> update.log
scp -qr static/splash/       gameservetest:/opt/webingo-server/static/. >> update.log
scp -qr static/fb_portal_2/  gameservetest:/opt/webingo-server/static/. >> update.log
echo -e "Ok\n"

echo -n "Copying webingo folder..."
scp -qr webingo/ gameservetest:/opt/webingo-server >> update.log
echo -e "Ok\n"

echo -n "Starting service..."
ssh gameservetest sudo systemctl restart webingo
echo -e "OK!\n"

echo "Done!!!"
