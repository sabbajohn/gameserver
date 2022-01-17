# Amazonia Games Backend Server

#### Sobre esse repositório
Para uma descrição mais detalhada do servidor, sua estrutura e protocolos, ver o arquivo doc/README.md

#### Instalação das Dependências
    - [Redis](https://redis.io/)
        - Instalação no Linux: usar versão do gerenciador de pacotes (4.0+)
        - Instalação no Windows: usar [esse tutorial](https://redislabs.com/blog/redis-on-windows-10/) (requer WSL)
    - [Python](https://www.python.org/) versão 3.6+
        - No Windows, usar [o instalador](https://www.python.org/downloads/windows/)
    - Pacotes do Python:
        - [redis-py](https://redis.io/)
        - [Tornado](https://www.tornadoweb.org)
        - [PyCurl](http://pycurl.io/)
        
Para a instação dos pacotes do Python, recomenda-se utilizar o programa `pip`, o gerenciador de pacotes do Python. O arquivo `setup.py` utiliza o pacote `setuptools` do python e pode fazer as instalações automaticamente, através de:

    sudo python3 ./setup.py develop

TODO: Instruções de execução no Windows
    
#### Configurações

TODO: o que precisa ser configurado antes de rodar

+ instalações de jogos e arquivos de manifesto
    

#### Instruções para execução

No Linux:
    
    $ python3 -m webingo ?

No Windows:
    
- como executar esse aplicativo localmente (se aplicável)

No servidor:

+ configuração do Redis
+ configuração do systemd para execução do servidor como serviço

#### Instruções para instalação
    - como instalar/atualizar localmente (se aplicável)
    - como instalar/atualizar remotamente (se aplicável)

#### Admin do respositório
    - [Lucas P. Camargo](mailto:lucas@camargo.eng.br)

#### Outros membros
    - [Diego Escorza](mailto:descorza17@gmail.com) - Game Director
    - [Darcio Pensky](mailto:dpensky@gmail.com) - Senior Developer
    - [Nathan Soares](mailto:nathan.soares.ns@gmail.com) - Intern

sudo apt install libcurl4-openssl-dev libssl-dev

pip install redis
pip install tornado
pip install pycurl
pip install user-agents

p.s: Pode ser que seja necessário usar o comando pip3 no lugar depedendo do sistema operacional.