# Modulo redis_change_to_max_level.py

Para rodar o programa, esteja na pasta "tools" e execute o comando "python3 redis_change_to_max_level.py"

Primeiramente o script entrará em um loop while para verificar se a pessoa realmente quer continuar com a alteração do redis.

Caso Digite "N" ou "n" o programa sairá do while e finalizará.

Caso a pessoa informe qualquer coisa diferente de "n", "N", "s" ou "S" o script informará que a opção informada é invalida e perguntará novamente se a pessoa deseja continuar a modificação no redis.

Caso a pessoa informe "S" ou "s", o programa iniciará a modificação.

Primeiro o script lerá o json fb_social_config.json que fica dentro do /res para pegar os spends de cada nível.

Depois conectará ao banco de dados.

Buscará por todos os jogadores com o level máximo.

Então modificará o spend_total de todos os jogadores que tem o último level liberado.

O programa gerará um arquivo log "changedusers.log" com todas as keys que foram modificadas na execução.

# Etapas
- copiar o script para o server
`$ scp -r tools/ gameserve:/opt/webingo-server`
- acessar o servidor
`$ ssh gameserve`
- parar o servidor para evitar conflitos
`$ sudo systemctl stop webingo`
- fazer backup da base de dados
`$ sudo cp /var/lib/redis/dump.rdb /home/ubuntu/dump-antes.rdb`
- rodar o script dentro da pasta tools
`$ ./redis_change_to_max_level.py`
- fazer mais 1 backup da base de dados
`$ sudo cp /var/lib/redis/dump.rdb /home/ubuntu/dump-depois.rdb`
- iniciar o servidor
`$ sudo systemctl restart webingo`