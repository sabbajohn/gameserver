/*  *************************************************************************
 *  Copyright (C) 2017 Bluechip Studios - All Rights Reserved
 *
 *  Unauthorized copying of this file, via any medium is strictly prohibited
 *
 *  Written by Darcio Pensky <dpensky@gmail.com>, Agosto 2017
 *  *************************************************************************/

#ifndef SRC_MATEMATICA_H_
#define SRC_MATEMATICA_H_

#include <vector>

using std::vector;

class cmatematica {

 public:

     static const int PREMIO_QUE_PIFA = 11;

     cmatematica();
     ~cmatematica() {;}

     vector<int> gerar_extracao(int aposta, int codigo_cartelas);

     bool liberar_gratis();

};

#endif  // SRC_MATEMATICA_H_

