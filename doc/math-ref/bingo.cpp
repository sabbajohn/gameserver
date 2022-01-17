/*  *************************************************************************
 *  Copyright (C) 2017 Bluechip Studios - All Rights Reserved
 *
 *  Unauthorized copying of this file, via any medium is strictly prohibited
 *
 *  Written by Darcio Pensky <dpensky@gmail.com>, Agosto 2017
 *  *************************************************************************/

#include <stdio.h>

#include "./bingo.h"

cbingo::cbingo() {

    push_jackpot(INDEX_PREMIO_JACKPOT, LIMITE_EXTRACAO_JACKPOT);
    push_cartelas(CARTELA_QUANTIDADE, CARTELA_LINHAS, CARTELA_COLUNAS);

    push_combinacao("bingo",            // # 0
            1500,
            0,
            get_horizontal(),
            CARTELA_LINHAS,
            get_sim(),
            0, 0, 0, 0, 0,
            0, 0, 0, 0, 0,
            0, 0, 0, 0, 0);

    push_combinacao("perimetro",        // # 1
            750,
            0,
            get_geometrico(),
            0,
            get_sim(),
            1, 1, 1, 1, 1,
            1, 0, 0, 0, 1,
            1, 1, 1, 1, 1);

    push_combinacao("duplotriangulo",   // # 2
            500,
            0,
            get_geometrico(),
            0,
            get_sim(),
            1, 1, 1, 1, 1,
            0, 1, 0, 1, 0,
            1, 1, 1, 1, 1);

    push_combinacao("mw",               // # 3
            200,
            0,
            get_geometrico(),
            0,
            get_sim(),
            1, 0, 1, 0, 1,
            1, 1, 0, 1, 1,
            1, 0, 1, 0, 1);

    push_combinacao("linhadupla",       // # 4
            100,
            0,
            get_horizontal(),
            2,
            get_sim(),
            0, 0, 0, 0, 0,
            0, 0, 0, 0, 0,
            0, 0, 0, 0, 0);

    push_combinacao("m",                // # 5
            100,
            0,
            get_geometrico(),
            0,
            get_sim(),
            1, 0, 0, 0, 1,
            1, 1, 0, 1, 1,
            1, 0, 1, 0, 1);

    push_combinacao("w",                // # 6
            100,
            0,
            get_geometrico(),
            0,
            get_sim(),
            1, 0, 1, 0, 1,
            1, 1, 0, 1, 1,
            1, 0, 0, 0, 1);

    push_combinacao("o",                // # 7
            40,
            0,
            get_geometrico(),
            0,
            get_sim(),
            0, 1, 1, 1, 0,
            0, 1, 0, 1, 0,
            0, 1, 1, 1, 0);

    push_combinacao("duplox",           // # 8
            40,
            0,
            get_geometrico(),
            0,
            get_sim(),
            1, 0, 1, 0, 1,
            0, 1, 0, 1, 0,
            1, 0, 1, 0, 1);

    push_combinacao("triangulo",        // # 9
            10,
            0,
            get_geometrico(),
            0,
            get_sim(),
            0, 0, 1, 0, 0,
            0, 1, 0, 1, 0,
            1, 1, 1, 1, 1);

    push_combinacao("trianguloinvertido",   // # 10
            10,
            0,
            get_geometrico(),
            0,
            get_sim(),
            1, 1, 1, 1, 1,
            0, 1, 0, 1, 0,
            0, 0, 1, 0, 0);

    push_combinacao("cruz",             // # 11
            8,
            0,
            get_geometrico(),
            0,
            get_sim(),
            0, 0, 1, 0, 0,
            1, 1, 1, 1, 1,
            0, 0, 1, 0, 0);

    push_combinacao("v",                // # 12
            3,
            0,
            get_geometrico(),
            0,
            get_sim(),
            1, 0, 0, 0, 1,
            0, 1, 0, 1, 0,
            0, 0, 1, 0, 0);

    push_combinacao("vinvertido",       // # 13
            3,
            0,
            get_geometrico(),
            0,
            get_sim(),
            0, 0, 1, 0, 0,
            0, 1, 0, 1, 0,
            1, 0, 0, 0, 1);

    push_combinacao("linha",            // # 14
            3,
            0,
            get_horizontal(),
            1,
            get_sim(),
            0, 0, 0, 0, 0,
            0, 0, 0, 0, 0,
            0, 0, 0, 0, 0);

}

// define o maior numero nas cartelas e nas bolas (60, 75 ou 90)
// essa informacao vem da classe data, do campo rol_tamanho
// pode ser alterada pelo tecnico na tela de configuracoes
void cbingo::inicia_serie(int universo) {
    push_bolas(universo, EXTRACAO_TAMANHO, EXTRACAO_EXTRA);
}

bool cbingo::saiu_jackpot(int cartelas, int index) {

    if (cartelas < CARTELA1)
        cartelas = CARTELA1|CARTELA2|CARTELA3|CARTELA4;

    if (index >= LIMITE_EXTRACAO_JACKPOT || index < 0)
        index = LIMITE_EXTRACAO_JACKPOT - 1;

    vector<struct premio> premios = acha_premios(cartelas, index);

    for (unsigned int i = 0; i < premios.size(); i++) {

        if (premios[i].tipo == INDEX_PREMIO_JACKPOT && !premios[i].quase)
            return true;

    }

    return false;

}

bool cbingo::saiu_pifado(int tipo, int cartelas, int contador_extracao, bool ignorar_bola) {

    if (contador_extracao < EXTRACAO_TAMANHO + EXTRACAO_EXTRA - 5 && !ignorar_bola)
        return false;

    vector<struct premio> premios = acha_premios(cartelas, contador_extracao);

    for (unsigned int i = 0; i < premios.size(); i++) {

        if (premios[i].quase) {

            if (premios[i].tipo <= tipo)
                return true;

        }

    }

    return false;

}

vector<struct premio> cbingo::acha_premios(int cartelas, int bolas_sorteadas) {

    vector<struct premio> premios_validos;

    if (cartelas < CARTELA1) {
        printf("ERRO[cbingo::acha_premios] - Quantidade invalida de cartelas abertas! [%d]\n", cartelas);
        return premios_validos;
    }

    int cartelas_abertas[CARTELA_QUANTIDADE] = {0, 0, 0, 0};

    if (cartelas & CARTELA1)
        cartelas_abertas[0] = 1;

    if (cartelas & CARTELA2)
        cartelas_abertas[1] = 1;

    if (cartelas & CARTELA3)
        cartelas_abertas[2] = 1;

    if (cartelas & CARTELA4)
        cartelas_abertas[3] = 1;

    vector<struct premio> premios = lbingo::acha_premios(CARTELA_QUANTIDADE, bolas_sorteadas);

    for (unsigned int i = 0; i < premios.size();  i++) {

        if (cartelas_abertas[premios[i].cartela])
            premios_validos.push_back(premios[i]);

    }

    return premios_validos;

}

vector<struct numero_cartela> cbingo::encontra_numero(int index, int cartelas) {

    if (index >= (signed)get_extracao().size())
        index = get_extracao().size() - 1;

    vector<struct numero_cartela> posicoes;

    struct numero_cartela posicao;
    posicao.marcado = false;

    if (cartelas < CARTELA1) {
        printf("ERRO[cbingo::encontra_numero] - Quantidade invalida de cartelas abertas! [%d]\n", cartelas);
        return posicoes;
    }

    int limite = CARTELA_QUANTIDADE * CARTELA_LINHAS * CARTELA_COLUNAS;
    int cartelas_abertas[CARTELA_QUANTIDADE] = {0, 0, 0, 0};

    if (cartelas & CARTELA1)
        cartelas_abertas[0] = 1;

    if (cartelas & CARTELA2)
        cartelas_abertas[1] = 1;

    if (cartelas & CARTELA3)
        cartelas_abertas[2] = 1;

    if (cartelas & CARTELA4)
        cartelas_abertas[3] = 1;

    for (int i = 0; i < limite; i++) {

        if (get_extracao(index) == get_serie(i)) {

            int numeros_cartela = CARTELA_LINHAS * CARTELA_COLUNAS;

            if (cartelas_abertas[i / numeros_cartela]) {

                posicao.marcado = true;
                posicao.cartela = i / numeros_cartela;
                posicao.linha = (i / CARTELA_COLUNAS) % CARTELA_LINHAS;
                posicao.coluna = i % CARTELA_COLUNAS;
                posicao.numero = get_serie(i);
                posicao.index = i % numeros_cartela;

                posicoes.push_back(posicao);

            }

        }

    }

    return posicoes;

}

int cbingo::verificar_bola_coringa(int numero, int contador_extracao) {

    vector<int> extracao_jogo = get_extracao();

    for (int i = 0; i < contador_extracao; i++) {

        if (numero == extracao_jogo[i])
            return i;  // Esta bola jah foi sorteada, nao pode ser usada

    }

    bool axou = false;

    int pos = cbingo::EXTRACAO_TAMANHO + cbingo::EXTRACAO_EXTRA;

    for (int i = contador_extracao; i < cbingo::EXTRACAO_TAMANHO + cbingo::EXTRACAO_EXTRA; i++) {

        if (numero == extracao_jogo[i]) {

            extracao_jogo[i] = extracao_jogo[contador_extracao];
            extracao_jogo[contador_extracao] = numero;

            pos = i;
            axou = true;

            break;

        }

    }

    if (!axou)  // A bola nao estava na extracao
        extracao_jogo[contador_extracao] = numero;

    set_extracao(extracao_jogo);

    return pos;

}

