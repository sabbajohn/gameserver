#!/bin/bash

reset='\033[0m'
green='\033[0;32m'
yellow='\033[1;33m'
backupdate=$(date '+%Y%m%d')
destination=webingo-server-${backupdate}.tar.gz

printf "\n$green%s" "Esse script vai fazer uma copia de:"
printf "\n$green%s" "- toda pasta /opt/webingo-server"
printf "\n$green%s" "- o arquivo /var/lib/redis/dump.rdb"
printf "\n$green%s$reset\n\n" "depois compacta todos eles em um arquivo zipado nomeado com a data do backup";

read -p "Deseja continuar? " -n 1 -r
if [[ $REPLY =~ ^[YySs]$ ]]
then
    echo "fazendo copia do redis"
    ssh gameserve sudo cp /var/lib/redis/dump.rdb /home/ubuntu/dump.rdb
    ssh gameserve sudo chown ubuntu:ubuntu dump.rdb
    echo "fazendo tar de tudo no server"
    # -z gzip, -c create, -f save to file
    ssh gameserve tar --exclude='*.pyc' -zcf $destination /home/ubuntu/dump.rdb /opt/webingo-server
    echo "copiando tar"
    scp gameserve:/home/ubuntu/$destination .
    echo "apagando arquivos no remoto"
    ssh gameserve rm /home/ubuntu/$destination
    ssh gameserve rm /home/ubuntu/dump.rdb
else
    printf "\n$yellow%s$reset\n\n" "Backup cancelado!!!";
fi

printf "\n$green%s$reset\n\n" "Script Finalizado!!!";

