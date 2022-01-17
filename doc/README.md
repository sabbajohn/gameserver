# amz-server

Servidor para jogos HTML5.

## Introdução

O servidor `webingo` é uma solução implementada em Python 3 para dar suporte a jogos web de estilo cassino.

Principais funcionalidades:

+ Gerenciamento de sessões de usuário
+ Gerenciamento de sessões de jogo com transições atômicas de estado
+ Suporte a mútiplas plataformas
+ Suporte a múltiplos sites
+ Perfis de usuário separados por plataforma
+ Interface com Backoffice para gerenciamento e contabilidade









## Conceitos

A seguir, definições de conceitos básicos que guiaram a implementação do servidor:

### Plataforma

Uma plataforma implementada no servidor representa um conjunto de funcionalidades apresentada pela sessão de usuário, rotas para a geração de páginas HTML, e serviços adicionais, como processamento de compras. Atualmente estão definidas no servidor as plataformas `facebook` e `demo`.

### Site

Um site representa um local onde o jogo é disponibilizado, com uma URL específica. A cada site é associada uma plataforma do servidor, uma lista de jogos disponíveis, e configurações de cada jogo. As informações de um site podem ser provenientes do backoffice ou de um arquivo local.

### Usuário

Um usuário no sistema representa o jogador, o usuário final. O mesmo está associado pela plataforma, responsável pela autenticação do usuário e validação de sua sessão. O usuário possui um ID global, campos para informações de registro, e um campo persistente de dados do usuário que pode ser acessado e modificado pelo jogo. Na implementação atual, usuários são associados exclusivamente a uma plataforma de jogo específica.

### Sessão de Usuário

A sessão de usuário é o ponto de entrada principal para as funcionalidades do servidor. O cliente de jogo, após carregado em um navegador web, conecta-se ao servidor. Ao enviar as informações de autenticação de usuário e site, a sessão é inicializada, associada a um usuário, site, e plataforma.

Quando uma sessão de usuário é iniciada, a sessão é registrada junto ao backoffice, e são obtidas as configurações do site definidas pelo backoffice aplicáveis aos jogos e à sessão.

### Sessão de Jogo

A sessão do jogo é um sub-estado da sessão de usuário. Quando um jogo é iniciado, no lobby ou por um jogo exeutando sozinho, uma sessão de jogo é riada especificando o jogo. O jogo é inicializado com definições presentes em seu manifesto, e configurações provenientes do site, definidas pelo backoffice.

### Componente de Sessão

Um componente de sessão é um objeto que encapsula funcionalidades adicionais da sessão de usuário. Por exemplo, o acesso às informações de Jackpot é implementado como um componente de sessão.

A plataforma associada à sessão de usuário pode injetar componentes adicionais à sessão. Por exemplo, para implementar funcionalidades de cassino social, a plataforma `facebook` agrega a cada sessão de usuário o componente `fb_social`.

### Carteira

A carteira é responsável por armazenar, controlar e sincronizar o saldo de cráditos do usuário.
Cada plataforma pode prover ao controlador da sessão de usuário uma implementação de carteira específica.

### Backoffice

O servidor de jogo depende do backoffice para as seguintes funcionalidades:

+ Obter configurações de sites;
+ Registrar usuários e sessões;
+ Enviar contabilidade de jogadas;
+ Enviar informações de jogador como créditos, 






## Estrutura

Essa seção delinea como o servidor está estruturado em termos práticos.

### Módulos e Código-fonte

O servidor está contido em um módulo Python denominado `webingo`. Os submódulos mais relevantes são:

+ `webingo.engines` - difinições de motores de jogo, motor de bingo, e matemáticas. Motores de gerenciam o estado do jogo dentro de uma sessão.
+ `webingo.jackpot` - controladores de Jackpot, e componente de sessão correspondente
+ `webingo.platforms` - definição de API e implementações de plataformas, handlers para geração de páginas HTML com JS de cliente correspondente
+ `webingo.platforms.facebook` - especializações de classes para a plataforma facebook (carteira, perfil de usuário), validações de sessão e componente de cassino social (`fb_social`).
+ `webingo.resources` - definições de modelos de dados para sites, registro de sessão no backoffice, e jogos. Fontes de dados para os mesmos (arquivos locais ou backoffice).
+ `webingo.server` - setup do framework `tornado`, handler de conexões ao websocket e controlador de sessão de usuário.
+ `webingo.support` - provê o mecanismo de logging e conexão com o banco de dados Redis.
+ `webingo.transaction`- abstrações de rounds de jogo e operações. financeiras de carteira e envio das informações ao backoffice.
+ `webingo.user` - modelo de dados para perfis de usuário e persistência de dados do mesmo
+ `webingo.wallet` - implementação de carteiras de crédito (em memória e com persistência no Redis), definições de denominações de valores (moedas)

### Arquivo de Configuração

O arquivo `config.json` especifica as configurações básicas do servidor: portas, de backends de plataforma, endereço do backoffice, entre outros. Um exemplo:

    {
        "debug": true,
        "http_port": 8080,
        "backoffice_url": "?????",
        "cert": "/home/camargo/bc/webingo-server-mvp/local-ssl/localhost.crt",
        "certkey": "/home/camargo/bc/webingo-server-mvp/local-ssl/localhost.key",
        "fb_app_id": "354159478852902",
        "fb_app_secret": "hexadeciamlhexadecimal",
        "rgs_base": "http://rgsapi.amazoniagaming.com/rgs-api/"
    }

+ "debug": se o servidor vai executar em modo de depuração (dev) ou produção. Afeta principalmente o volume dos logs e reação a mudanças nos arquivos-fonte.
+ "http_port": porta principal do servidor.
+ "cert" e "certkey": certificados para servir HTTPS ao invés de HTTP (IMPORTANTE, o jogo em produção espera por HTTPS).
+ "fb_app_id": identificador do apicativo para a API do Facebook.
+ "fb_app_secret": chave secreta de acesso server<->server para a API do Facebook.
+ "rgs_base": URL base para o backoffice

### Dependências

O servidor utiliza o framework web `tornado` para implementar o mecanismo de servidor web e requisições a APIs REST. Para executar as requisições REST, o `tornado` utiliza a biblioteca `pycurl`.

O banco de dados no-sql `redis` é utilizado para armazenar todos os dados de usuário, sessão, carteiras e jackpot, que requeiram persistência. Atualamente há apenas uma instância do banco de dados, mas o mesmo pode ser configurado apra ser distribuído em mais de uma máquina no futuro.

### Diretórios

Os seguintes diretórios são os mais relevantes à operação do servidor:

+ `./res` - Arquivos de recurso, definidos na seção "Arquivos de recurso" mais adiante
    + `/games` - Jogos exportados do Godot, acompanhados de um arquivo de manifesto
    + `/local_sites` - Sites definidos localmente, ao invés de serem obtidos do backoffice
    + `/templates` - Templates para geração de páginas HTML
+ `./static` - Arquivos estáticos disponibilizados pelo servidor via HTTP
    + `/games-available` - Pacotes de jogo (*.pck) a serem carregados dinâmicamente pelo cliente/lobby
    + `/splash` - Imagens e recursos da tela de loading e fundo
    + `/webingo-client` - Lobby de jogo exportado do Godot



### Rotas HTTPS

Rotas padrão:

+ `/static` - Assets estáticos como pacotes de jogo
+ `/game/*` - Rota estática para `./res/games`
+ `/session/ws` - Websocket para sessões de usuário

Rotas da plataforma "facebook":

+ `/facebook/portal` - Página principal do jogo instalado no Facebook. Carrega o lobby do cassino social.










## Protocolo de Sessão

O protocolo busca sincronizar o estado de jogo entre um cliente e um servidor. Cada estado de jogo possui um nome, id único, ações possíveis do jogador e informações de carteira de créditos.
O cliente do jogo deve sincronizar a exibição do jogo de acordo com o estado atual, e permitir ao usuário interagir com o jogo através das ações que os estado permite.

### Camada de Rede

A pilha de rede na qual se baseia o protocolo é a tecnologia WebSockets (RFC 6455), que permite a criação de um túnel TCP através de proxies HTTP. O próprio protocolo WebSockets, e a pilha de rede associada, provê as seguintes garantias:

+ Mensagens discretizadas binárias e de texto
+ Entrega de mensagens em ordem
+ Verificação por checksum
+ Pings automáticos e manuais
+ Verificação do estado de conexão e timeouts

### Início de sessão

Na primeira conexão, o servidor espera uma mensagem contendo informações do usuário e site do jogo, para autenticação e construção das informações da sessão. O objeto tem o seguinte formato:


    {
        "auth":{
            "uid":"3201401476538110",
            "token":"EAAFCGy3uTS[...]BHpwZDZD",
            "userinfo":{...}
        },
        "platform":"facebook",
        "site":"demo"
    }

+ "auth": informações de autenticação do usuário na plataforma
+ "auth/uid": identificador do usuário
+ "auth/token": token de autenticação da plataforma de terceiro
+ "auth/userinfo": informações do usuário, dependentes da plataforma/site
+ "site": site correspondente à instalação
    
Para a plataforma facebook, os dados de autenticação do usuário (userinfo) seguem esse formato, direto da API do Facebook:

    {
    "id":"3201401476538110",
    "name":"Lucas Camargo",
    "picture":{
        "data":{
            "height":50,
            "is_silhouette":false,
            "url":"https://platform-lookaside.fbsbx.com/platform/profilepic/?as…8110&height=50&width=50&ext=1597083747&hash=AeS89W82iUIl148x",
            "width":50
        }
    },
    "email":"lucaspcamargo@gmail.com"
    }

### Mensagens do Servidor para o Cliente

Todas as mensagens são um objeto JSON, que em sua raiz possuem um campo "t", uma string que denota o tipo da mensagem. O tipo de mensagem determina os outros campos presentes no objeto. Os tipo sde mensagem são descritos a seguir.

#### 'state'

Essas mensagens representam o estado atual da sessão, incluindo o estado de jogo se houver um jogo em execução. Uma mensagem de estado de sessão sem um estado de jogo denota o fim da execução do jogo. A sessão de usuário continua válida.

O servidor envia o estado da sessão completo ao cliente sempre que há uma transição. Não necessariamente tudo o que é enviado representa uma mudança, a ideia é que o cliente tenha em uma mensagem de estado tudo o que é necessário para manter a sincronia entre o estado interno da sessão no servidor, e o que é apresentado ao jogador.

Um exemplo de mensagem de estado da sessão:

    {
        "t":"state",
        "curr_game":"joker_bingo",
        "gamestate":{...},
        "wallet":{
            "credits":38334,
            "denom":"credit",
            "denom_info":{
                "prefix":"",
                "suffix":"",
                "integer":true,
                "money_multiplier":1,
                "rgs_id":"CRE"
            }
        },
        "userdata":{
            "first_time":true,
            "soc_level":2,
            "soc_level_prog":0.18000000000000008,
            "spend_total":88
        }
    }

+ "curr_game": jogo atualmente em execução, se houver 
+ "gamestate": estado atual do jogo, ver "Estado de Jogo" mais adiante
+ "wallet": informações da carteira do usuário, valor, denominação, e apresentação em dinheiro
+ "userdata": campo de dados persistentes do usuário, no escopo do site e plataforma. Pode ser manipulado pelo cliente livremente


### Mensagens do Cliente para o Servidor

#### 'action'

Uma mensagem que representa uma ação do jogador que muda o estado do jogo. Geralmente uma aposta ou compra.
As mensagens do tipo "action" devem apresentar três campos adicionais:,

+ "action": nome da ação que se deseja executar (ex: bet)
+ "params": parâmetros da ação (ex: bet_amount)
+ "sid": UUID do estado *de jogo( ao qual a ação se refere

A exemplo:

    {"t":"action", "action": “bet”, "params": {“amount”: 4}, "sid": “<<UUID>>”}

#### 'gameload'

Pede ao servidor que inicie uma sessão de jogo dentro da sessão de usuário. Deve possuir um único campo "gameid" com o id do jogo a ser carregado. Exemplo:

    {"t": "gameload", "gameid": "joker-bingo"}

O carregamento do jogo não é garantido. A presença de um estado de jogo na sessão é o que determina se o jogo foi iniciado no servidor ou não.


#### 'gamefinish'

Pede ao servidor que encerre o jogo atualmente em execução. Não possui nenhum argumento adicional:

    {"t": "gamefinish"}
    
Note que o controlador de sessão só vai encerrar o jogo se o motor de jogo atualmente em execução permitir. Se o jogo estiver em um estado transiente (compra de bola extra, por exemplo), o jogo não será encerrado. Portanto, da mesma maneira que para o início de sessão de jogo, o término não é garantido, e a presença de um estado de jogo na sessão é o que determina se o jogo foi encerrado.

(A implementação atual do lobby reage automaticamente a uma sessão sem estado de jogo e fecha um jogo executando no cliente, se houver).


#### 'component'

Uma mensagem direcionada a um componente de sessão. O componente pode ser "jackpot", "fb_social", ou eventualmente qualquer outro istalado na sessão pela plataforma.
Um exemplo de mensagem direcionada a um componente:

    {
        "t": "component",
        "which": "jackpot"
        "message": 
        {
            "what": "subscribe", "to": "jp_joker_bingo"
        }
        
    }

+ "which": componente-alvo da mensagem
+ "message": conteúdo da mensagem, espeífico do componente

    
### Estado de jogo - geral

Embora os atributos de estado de jogo possam variar entre jogos diferentes (bingo, slots, etc), algumas propriedades são comuns.
São elas:

+ "id": GUID que identifica o estado atual
+ "name": nome do estado atual, dependente do tipo de jogo
+ "data": dados do estado atual (exemplo: série, extração, bolas extra)
+ "actions": nome das ações de cliente possíveis no estado atual

A exemplo:

    "gamestate":{
        "id":"82f304a9-8fd6-4c29-a513-e084b8769df9",
        "name":"idle",
        "data":{
            "cards": [
                [1, 14, 17, 35, 45, 11, 15, 26, 38, 47, 13, 16, 29, 44, 51], 
                [2, 21, 34, 49, 58, 7, 31, 42, 53, 59, 12, 32, 43, 54, 60], 
                [6, 20, 24, 39, 50, 9, 22, 33, 40, 55, 18, 23, 36, 48, 57], 
                [3, 8, 25, 30, 46, 4, 10, 27, 37, 52, 5, 19, 28, 41, 56]
                ], 
            "balls": []
        },
        "actions":[ "bet", "cards" ]
    }

    
### Motor de jogo: "bingo"

A engine de bingo implementa a mecânica do jogo de bingo no servidor. COmo motor de jogo, é responsável por manter o estado de jogo, e definir e executar as transições de estados, atraves de ações do cliente de jogo.

Estados possíveis:

+ "idle": jogo não está em andamento
+ "game": jogo em andamento

Ações possíves:

+ "bet": iniciar um jogo, com a aposta especificada
+ "extra": comprar bola extra, pelo valor estipulado pelo servidor
+ "end": finalizar jogo atual

Um jogo em andamento pode ser automaticamente finalizado, e outro jogo iniciado, com uma ação "bet". Nesse caso, o jogo transiciona do estado "game" para "game", com um id de estado diferente e outra extração. Ocorrerá uma transição intermediária pro estado "idle".

O estado possui os seguintes artibutos:

+ "cards": série de cartões de bingo, um array de arrays
+ "balls": bolas da extração atual, inclui as bolas extras no final
+ "extra_cost": custo da bola extra
+ "winnings": ganhos da rodada, por cartão
+ "total_winnings": ganhos totais da jogada


### Motor de jogo: "slots"

**TBD, desenvolvimento futuro**



### Componente de sessão: "fb_social"

Esse componente centralia as operações na sessão referentes ao cassino social. No momento, duas operações são suportadas, "manual_buy", um acréscimo de créditos manual na carteira do usuário, e "set_credits", que sobrescreve a quantidade de créditos na carteira do usuário. Exemplo:

    {
        "what": "manual_buy", "amount": 500
    }

Esse componente também é responsável por gerenciar o nível de jogador, em campos no `userdata`. Esses campos são:

+ "soc_level": nível do jogador, um número inteiro
+ "soc_level_progress": progresso do jogador em direção ao próximo nível, número float entre 0.0 e 1.0
+ "spend_total": total gasto pelo jogador em apostas e compras de bola extra, etc., para cálculo do nível e progresso





## Jackpots

Os jackpots são objetos independentes de sessão no servidor. No entanto, estão atrelados ao site. Os jackpots são parametrizados em:

+ id: string nome do jackpot
+ denominação: string, tipo de valor armazenado no jackpot, segue denominações das carteiras ("CRE", "USD", etc)
+ storage_multiplier: int, multiplicador do valor de jackpot no BD para lidar com frações de centavo. 1000 por default.
+ valor mínimo: int, valor mínimo do jackpot em unidades de armazenamento
+ valor máximo: int, valor máximodo jackpot em unidades de armazenamento

Uma unidade de armazenamento é o menor valor armazenável em um registro de jackpot. Seu valor é uma unidade de denominação (um crédito, um centavo),
dividida pelo multiplicador de armazenamento.


### Componente de sessão: "jackpot"

O componente de sessão "jackpot" é o responsável por enviar informações de jackpot ao cliente. Aceita dois tipos de mensagem, "subscribe" e "unsubscribe_all".
A mensagem "subscribe" anuncia interesse o valor de um jackpot, a mensagem "unsubscribe_all" cancela todos. Exemplo:
    
    {
        "what": "subscribe", "to": "jp_joker_bingo"
    }
    

## Arquivos de Recurso

Na pasta `./res`, como apresentado anteriormente, há arquivos que descrevem jogos e sites, além de templates.

As definições de jogo precisam estar disponíveis localmente no servidor, embora possam ser sobrescritas pelas configurações do site provenientes do backoffice. Dependo do cliente, o jogo pode estar localizado no servidor como um ".pck" em `./static/games-available`, mas isso não é obrigatório, nem uma garantia. Os jogos em .pck são para carregamento pelo lobby, os jogos em `./res/games`.

A possibilidade de definir sites localmente através de arquivos JSON é uma conveniência para desenvolvimento. Em produção, todos os sites e suas configurações devem ser conhecidos pelo backoffice no momento do registro da sessão.





## Notas

+ Ainda há no servidor várias referências ao conceito de instalação/installation. Isso não vai mais existir e será eliminado do código. Antes havia uma diferença entre sie e installation. Agora, operacionamente, a diferença entre site e installation foi eliminada e tudo está concentrado no conceito de site, o backoffice não trabalha mais com installation.

+ Pode parecer supérfluo enviar o estado completo de sessão o tempo todo, mas isso foi pensado para facilitar a implementação de clientes *stateless*, e diminuir complexidades de sincronização de dados e a lógica necessária no cliente.
    + É o mesmo motivo pelo qual o estado de jogo possui um UUID, que precisa ser explicitado no momento da execução de uma ação, para garantir que a ação seja executada sobre um estado bem-definido sobre o qual o cliente tem total conhecimento.
