/*  *************************************************************************
 *  Copyright (C) 2017 Bluechip Studios - All Rights Reserved
 *
 *  Unauthorized copying of this file, via any medium is strictly prohibited
 *
 *  Written by Darcio Pensky <dpensky@gmail.com>, Agosto 2017
 *  *************************************************************************/

#ifndef SRC_BINGO_H_
#define SRC_BINGO_H_

#include <vector>

#include <superclass/lbingo.h>

using std::vector;

enum {
    CARTELA1 = 8,
    CARTELA2 = 16,
    CARTELA3 = 32,
    CARTELA4 = 64
};

class cbingo : public lbingo {

 public:

     cbingo();

     enum {
         BINGO = 0,
         PERIMETRO
     };

     static const int CARTELA_LINHAS     = 3;    // NUMERO DE LINHAS POR CARTELA
     static const int CARTELA_COLUNAS    = 5;    // NUMERO DE COLUNAS POR CARTELA
     static const int CARTELA_QUANTIDADE = 4;    // NUMERO TOTAL DE CARTELAS

     static const int EXTRACAO_EXTRA   = 11;     // NUMERO DE BOLAS EXTRAS
     static const int EXTRACAO_TAMANHO = 30;     // NUMERO DE BOLAS SORTEADAS NA EXTRACAO NORMAL

     static const int INDEX_PREMIO_JACKPOT = 0;  // EH O IDENTIFICADOR DO PREMIO QUE PAGAR O ACUMULADO
     static const int LIMITE_EXTRACAO_JACKPOT = 30;  // EH O INDEX DA EXTRACAO LIMITE PARA A SAIDA DO ACUMULADO

     int verificar_bola_coringa(int numero, int contador_extracao);

     bool saiu_pifado(int tipo, int cartelas, int contador_extracao, bool ignorar_bola = false);
     bool saiu_jackpot(int cartelas, int index = LIMITE_EXTRACAO_JACKPOT);

     void inicia_serie(int universo);  // define o maior numero nas cartelas e nas bolas (60, 75 ou 90)

     vector<struct premio> acha_premios(int cartelas, int bolas_sorteadas);

     vector<struct numero_cartela> encontra_numero(int index, int cartelas);

};

#endif  // SRC_BINGO_H_

