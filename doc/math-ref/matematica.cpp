/*  *************************************************************************
 *  Copyright (C) 2017 Bluechip Studios - All Rights Reserved
 *
 *  Unauthorized copying of this file, via any medium is strictly prohibited
 *
 *  Written by Darcio Pensky <dpensky@gmail.com>, Agosto 2017
 *  *************************************************************************/

#include <stdlib.h>   // rand

#include "./bingo.h"
#include "./matematica.h"

extern cbingo *bingo;

cmatematica::cmatematica() {
}

vector<int> cmatematica::gerar_extracao(int aposta, int codigo_cartelas) {

    vector<int> extracao;
    vector<struct premio> premios;

    int contador = 0;

    bool aprovada = false;

    while (!aprovada) {

        bool premios_altos = false;

        aprovada = true;
        extracao = bingo->gera_extracao();

        premios = bingo->acha_premios_be(codigo_cartelas, cbingo::EXTRACAO_TAMANHO + cbingo::EXTRACAO_EXTRA - 1);

        for (unsigned int i = 0; i < premios.size(); i++) {

            if (!premios[i].quase) {

                if (premios[i].tipo <= 6) {
                    premios_altos = true;
                    break;
                }

            }

        }

        if (premios_altos) {

            int block = 240;

            if (rand() % 1000 < block)
                aprovada = false;

        }

        if (++contador > 1000)
            aprovada = true;

        if (bingo->saiu_jackpot(codigo_cartelas))
            aprovada = false;

    }

    return extracao;

}

bool cmatematica::liberar_gratis() {
    return rand() % 1000 < 200;
}

