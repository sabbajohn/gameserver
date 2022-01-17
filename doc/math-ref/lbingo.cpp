#include <lbingo.h>
#include <sys/time.h>
#include <stdlib.h>
#include <algorithm>
#include <string.h>
#include <stdio.h>
#include <dicionario.h>
#include <SDL.h>
#include <aleatorio.h>

lbingo::lbingo(){

	//printf("lbingo::lbingo()\n");
	v = new struct lbingo_vars;
	srand(time(NULL));

	v->qtd_cartelas = 0;
	v->numeros_cartela = 0;
	v->linhas_cartela = 0;
	v->colunas_cartela = 0;

	v->total_bolas = 0;
	v->extracao_natural = 0;
	v->extras = 0;

	v->premio_jackpot = 0;
	v->limite_jackpot = 0;

	v->retorna_maior_premio = false;

}

void lbingo::push_cartelas(int qtd, int linhas, int colunas) {

	//	printf("lbingo::push_cartelas(int qtd=%d, int linhas=%d, int colunas=%d)\n", qtd, linhas, colunas);

	v->qtd_cartelas = qtd;
	v->linhas_cartela = linhas;
	v->colunas_cartela = colunas;
	v->numeros_cartela = linhas * colunas;

}

void lbingo::push_bolas(int universo, int bolas_natural, int bolas_extras) {

	//	printf("lbingo::push_bolas(int universo=%d, int bolas_natural=%d, int bolas_extras=%d)\n", universo, bolas_natural, bolas_extras);

	v->total_bolas = universo;
	v->extracao_natural = bolas_natural;
	v->extras = bolas_extras;

}

void lbingo::push_jackpot(int index, int limite) {

	//	printf("lbingo::push_jackpot(int index=%d, int limite=%d)\n", index, limite);

	v->premio_jackpot = index;
	v->limite_jackpot = limite;

}

void lbingo::push_combinacao(string name, int valor, int contagem_marcados, int orientacao, int nr_linhas, int sobreposicao, ...) {
	unsigned pattern = 0;
	va_list list;
	va_start(list, sobreposicao);

	for(int i=0, value; i<v->numeros_cartela; i++){
		value = va_arg(list, int);
		pattern |= (value?1:0)<<i;
	}
	
	va_end(list);
	
	this->push_combinacao2(name, valor, contagem_marcados, orientacao, nr_linhas, sobreposicao, pattern);
}

void lbingo::push_combinacao2(string name, int valor, int contagem_marcados, int orientacao, int nr_linhas, int sobreposicao, unsigned bit_pattern) {

	combinacao tcomb;

	int col = 0;
	int counter = 0;

	tcomb.nome = Dicionario::get(name.c_str());
	tcomb.valor = valor;
	tcomb.contagem_marcados = contagem_marcados;
	tcomb.orientacao = orientacao;
	tcomb.nr_linhas = nr_linhas;
	tcomb.sobreposicao = sobreposicao;

	vector<int> linha;
	linha.clear();

	for(;;) {

		if(counter >= v->numeros_cartela) {
			break;
		}

		int p = bit_pattern & 0x1;
		bit_pattern = bit_pattern >> 1;

		linha.push_back(p);

		counter++;
		col++;

		if(col % v->colunas_cartela == 0) {
			col = 0;
			tcomb.prototipo.push_back(linha);
			linha.clear();
		}

	}

	int index_combinacao = -1;

	for(int i = v->combinacoes.size() - 1; i >= 0; i--) {

		if(valor > v->combinacoes[i].valor)
			index_combinacao = i;

	}

	if(index_combinacao < 0)
		v->combinacoes.push_back(tcomb);
	else
		v->combinacoes.insert(v->combinacoes.begin() + index_combinacao, tcomb);

}

vector<int> lbingo::gera_extracao() {

	//	printf("lbingo::gera_extracao()\n");

	v->bolas_usadas.clear();
	for(int i = 0; i < v->total_bolas; i++) {
		v->bolas_usadas.push_back(false);
	}

	vector<int> bolas_livres;
	bolas_livres.clear();
	v->extracao.clear();

	// CRIA UMA COPIA DA SERIE SEM NUMEROS REPETIDOS (ex.: cartela 5x5)
	// OU SEJA, OS NUMEROS Q PODEM SER SORTEADOS
	vector<int> aux;
	aux = v->serie;
	sort(aux.begin(),aux.end());
	unique_copy(aux.begin(), aux.end(), back_inserter(bolas_livres));

	if((signed)bolas_livres.size() < (v->extracao_natural + v->extras)) {
		bolas_livres.clear();
		for(int i = 0; i < v->total_bolas; i++) {
			bolas_livres.push_back(i+1);
		}
	}

	while((signed)v->extracao.size() < (v->extracao_natural + v->extras)) {
		int posicao = randgen->gen(bolas_livres.size());
		int bola = bolas_livres[posicao];

		v->bolas_usadas[bola-1] = true;
		bolas_livres.erase(bolas_livres.begin()+posicao);

		v->extracao.push_back(bola);
	}

	return v->extracao;

}

vector<int> lbingo::gera_serie(bool repete_numero) {

	//	printf("lbingo::gera_serie(bool repete_numero=%s)\n", repete_numero ? "true" : "false");

	v->serie.clear();

	int tamanho = v->qtd_cartelas * v->numeros_cartela;
	int numerosporcoluna = v->total_bolas / v->colunas_cartela;
	int numerosporposicao = numerosporcoluna;

	if(v->total_bolas % v->numeros_cartela == 0) {
		numerosporposicao = v->total_bolas / v->numeros_cartela;
	}

	//NAO TEM COMO NAO REPETIR SE O TAMANHO DA SERIE FOR MAIOR Q O UNIVERSO DE SORTEIO
	if(tamanho > v->total_bolas) {
		repete_numero = true;
	}

	vector<int> todos_numeros;
	todos_numeros.clear();
	for(int i = 0; i < v->total_bolas; i++) {
		todos_numeros.push_back(i+1);
	}

	vector<int> temp_cartelas;
	temp_cartelas.clear();
	int contador = 0;

	if(repete_numero) {
		//numeros que foram sorteados e adicionados na serie
		vector<int> numeros_selecionados;
		numeros_selecionados.clear();

		for(int i=0;i<v->total_bolas;i++) {
			numeros_selecionados.push_back(0);
		}
		for(int i=0;i<tamanho;i++)
			temp_cartelas.push_back(0);
		struct timeval aux;
		//variavel que limita a quantidade que um numero repete na serie
		vector<int> controla_repeticao;
		controla_repeticao.clear();
		int conta = 0;
		int cartela = 0;
		int controle = 0;
		//divide os numeros em partes iguais e os adiciona nas cartelas
		while(cartela < v->qtd_cartelas) {
			conta = cartela*v->numeros_cartela;
			controle = conta + (v->total_bolas/v->qtd_cartelas);
			for(;conta < controle ;) {
				gettimeofday(&aux,NULL);
				srand(aux.tv_usec);
				int posicao = randgen->gen(v->total_bolas);
				if(numeros_selecionados[posicao] == 0) {
					numeros_selecionados[posicao] = 1;
					temp_cartelas[conta] = posicao+1;
					contador++;
					conta++;
				}
			}
			cartela++;
		}
		numeros_selecionados.clear();

		for(int i=0;i<v->total_bolas;i++) {
			numeros_selecionados.push_back(0);
		}
		int livre = 0;
		int existe = 0;
		//procura por locais que nao foram setados numeros e coloca numeros repetidos... com o limite de 1 numero repetido
		while(contador < tamanho) {
			gettimeofday(&aux,NULL);
			srand(aux.tv_usec);
			int posicao = randgen->gen(v->total_bolas);
			if(numeros_selecionados[posicao] == 0) {
				while(temp_cartelas[livre] != 0) livre++;
				cartela = livre/v->numeros_cartela;
				conta = cartela*v->numeros_cartela;
				controle = v->numeros_cartela*(cartela+1);
				for(;conta < controle ;conta++) {
					if(temp_cartelas[conta] == posicao+1) existe = 1;
				}
				if(existe == 0) {
					temp_cartelas[livre] = posicao+1;
					numeros_selecionados[posicao] = 1;
					contador++;
				}
				existe = 0;
			}
		}

		/*	
			int numeros_cartelas[v->qtd_cartelas][v->total_bolas];
			int contagem_todos_numeros[v->total_bolas];

			bzero(numeros_cartelas, sizeof(numeros_cartelas));
			bzero(contagem_todos_numeros, sizeof(contagem_todos_numeros));

			while(contador < tamanho) {
			if (contador % v->numeros_cartela == 0) {
			for(int i = 0; i < v->total_bolas; i++) {
			todos_numeros.push_back(i+1);
			}
			}

			int index = contador % v->numeros_cartela;
			int posicao = randgen->gen(numerosporposicao) + (index*numerosporposicao);

			if(contagem_todos_numeros[posicao] == 0 || (contagem_todos_numeros[posicao] == 1 && randgen->gen(3) == 0)){
			temp_cartelas.push_back(todos_numeros[posicao]);
			contagem_todos_numeros[posicao]++;
			todos_numeros.erase(todos_numeros.begin()+posicao);
			contador++;
			}
			}
			*/
	} else {

		bool usado[v->total_bolas];
		memset(&usado, false, sizeof(usado));

		while(contador < tamanho) {
			int index = contador % v->numeros_cartela;
			int posicao = randgen->gen(numerosporposicao) + (index*numerosporposicao);

			if(!usado[posicao]) {
				temp_cartelas.push_back(todos_numeros[posicao]);
				contador++;
				usado[posicao] = true;
			}

		}

	}

	vector<int> temp;

	for(int cartela = 0; cartela < v->qtd_cartelas; cartela++) {

		int cartela_inicio = cartela * v->numeros_cartela;
		int cartela_final = cartela_inicio + v->numeros_cartela;

		temp.clear();
		for(int i = cartela_inicio; i < cartela_final; i++) {
			temp.push_back(temp_cartelas[i]);
		}

		//ORDENA SEQUENCIALMENTE
		sort(temp.begin(), temp.end());

		//ORDENA POR COLUNA
		for(int linha = 0; linha < v->linhas_cartela; linha++) {
			for(int coluna = 0; coluna < v->colunas_cartela; coluna++) {
				v->serie.push_back(temp[coluna * v->linhas_cartela + linha]);
			}
		}

	}

	return v->serie;

}

vector<premio> lbingo::acha_premios(int cartelas, int bolas_sorteadas) {

	if(cartelas == -1) {
		cartelas = v->qtd_cartelas;
	}

	if(bolas_sorteadas == -1) {
		bolas_sorteadas = v->extracao_natural + v->extras - 1;
	}

	if(bolas_sorteadas >=(int)v->extracao.size()) {
		bolas_sorteadas = v->extracao.size() - 1;
	}

	vector<premio> premios;
	premios.clear();

	int cartela_marcada[v->linhas_cartela][v->colunas_cartela];
	int linha_marcada[v->linhas_cartela];
	int coluna_marcada[v->colunas_cartela];
	int serie_pos = 0;

	vector<numero_cartela> num_boa_linha;
	vector<numero_cartela> num_boa_coluna;

	// transforma a cartela em uma matriz booleana para poder comparar com os padroes de premios
	for(int cont_cartela = 0; cont_cartela < cartelas; cont_cartela++) {                // percorre as cartelas da serie

		// zera a variavel de controle de incidencia de linhas
		memset(&linha_marcada, 0, sizeof(linha_marcada));

		// zera a variavel de controle de incidencia de colunas
		memset(&coluna_marcada, 0, sizeof(coluna_marcada));

		// zerar a cartela matriz referencia de premio
		memset(&cartela_marcada, 0, sizeof(cartela_marcada));

		for(int cont_linha = 0; cont_linha < v->linhas_cartela; cont_linha++) {
			for(int cont_coluna = 0; cont_coluna < v->colunas_cartela; cont_coluna++) {
				int numero = v->serie[serie_pos];

				if(*find(v->extracao.begin(), v->extracao.begin()+bolas_sorteadas, numero) == numero) {
					cartela_marcada[cont_linha][cont_coluna] = 1;
				}

				serie_pos++;
				//printf("estou no acha_premios - 0\n");
			}
		}

		//identifica a marcacoes para linhas
		int pcounter = cont_cartela * v->numeros_cartela;

		for(int cont_linha = 0; cont_linha < v->linhas_cartela; cont_linha++) {                  // percorre as linhas da cartela

			numero_cartela boa;

			for(int cont_coluna = 0; cont_coluna < v->colunas_cartela; cont_coluna++) {     // percorre colunas da cartela

				bool marcado = false;
				int numero = v->serie[pcounter];
				if(*find(v->extracao.begin(), v->extracao.begin()+bolas_sorteadas, numero) == numero) {
					linha_marcada[cont_linha]++;                  // incrementa contador de marcacao
					marcado = true;
				}

				if(!marcado) {
					boa.marcado = false;
					boa.cartela = cont_cartela;
					boa.numero = v->serie[pcounter];
					boa.linha = (pcounter / v->colunas_cartela) % v->linhas_cartela;
					boa.coluna = pcounter % v->colunas_cartela;
					boa.index = pcounter % v->numeros_cartela;
				}

				pcounter++;

			}

			if(linha_marcada[cont_linha] == v->colunas_cartela - 1) {
				num_boa_linha.push_back(boa);
			}

		}

		//printf("estou no acha_premios - 1\n");

		//identifica a marcacoes para colunas
		int numcartela = cont_cartela * v->numeros_cartela;

		for(int cont_coluna = 0; cont_coluna < v->colunas_cartela; cont_coluna++) {               // percorre colunas da cartela

			numero_cartela boa;

			for(int cont_linha = 0; cont_linha < v->linhas_cartela; cont_linha++) {           // percorre as linhas da cartela

				bool marcado = false;
				int numero = v->serie[numcartela + cont_coluna + cont_linha * v->colunas_cartela];

				//printf("procurando %d\n", numero);

				if(*find(v->extracao.begin(), v->extracao.begin()+bolas_sorteadas, numero) == numero) {
					coluna_marcada[cont_coluna]++;                  // incrementa contador de marcacao
					marcado = true;
				}

				if(!marcado) {
					boa.marcado = false;
					boa.cartela = cont_cartela;
					boa.numero = v->serie[numcartela + cont_coluna + cont_linha * v->colunas_cartela];
					boa.linha = cont_linha;
					boa.coluna = cont_coluna;
					boa.index = cont_linha * v->colunas_cartela + cont_coluna;
				}
				//printf("estou no acha_premios - 2 saindo\n");

			}

			if(coluna_marcada[cont_coluna] == v->linhas_cartela - 1) {
				num_boa_coluna.push_back(boa);
			}

		}

		int boa_lin = 0;
		int boa_col = 0;
		bool quase = false;
		bool premio_ok = false;
		bool procurando_linear = true;
		bool procurando_quase = true;

		//printf("estou no acha_premios - 3\n");

		//percorre todos os premios da lista e verifica eles estao contidos na cartela
		for(int i = 0; i <(int)v->combinacoes.size(); i++) {

			//printf("estou no acha_premios - combinacao - %d\n", i);

			premio tpremio;

			if(v->combinacoes[i].contagem_marcados > 0) {

				// caso use premios de marcacao

			} else if(v->combinacoes[i].nr_linhas > 0) {

				if(v->combinacoes[i].orientacao == v->HORIZONTAL && procurando_linear) {

					int linhas_marcadas = 0;
					int linhas_quase = 0;

					for(int p = 0; p < v->linhas_cartela; p++) {
						if(linha_marcada[p] == v->colunas_cartela)
							linhas_marcadas++;
						else if(linha_marcada[p] == v->colunas_cartela - 1)
							linhas_quase++;
					}

					if(linhas_marcadas >= v->combinacoes[i].nr_linhas) {

						tpremio.cartela = cont_cartela;
						tpremio.tipo = i;
						tpremio.nome = v->combinacoes[i].nome;
						tpremio.valor = v->combinacoes[i].valor;
						tpremio.quase = false;

						int linecont = 0;

						for(int p = 0; p < v->linhas_cartela; p++) {
							if(linha_marcada[p] == v->colunas_cartela) {
								//MESMO SE TIVER MAIS LINHAS COMPLETADAS, MARCA APENAS AS PRIMEIRAS
								if(linecont < v->combinacoes[i].nr_linhas) {	
									tpremio.linha_marcada.push_back(p);
									linecont++;
								}
							}
						}

						tpremio.posicoes_marcadas.clear();

						linecont = 0;

						for(int c = 0; c < v->linhas_cartela; c++) {

							//MESMO SE TIVER MAIS LINHAS COMPLETADAS, MARCA APENAS AS PRIMEIRAS
							if(linha_marcada[c] == v->colunas_cartela && linecont < v->combinacoes[i].nr_linhas) {

								for(int d = 0; d < v->colunas_cartela; d++) {

									numero_cartela numero_marcado;

									numero_marcado.cartela = cont_cartela;
									numero_marcado.linha = c;
									numero_marcado.coluna = d;
									numero_marcado.index = c * v->colunas_cartela + d;
									numero_marcado.marcado = true;
									numero_marcado.numero = v->serie[cont_cartela * v->numeros_cartela + numero_marcado.index];

									tpremio.posicoes_marcadas.push_back(numero_marcado);

								}

								linecont++;
							}
						}

						if((v->combinacoes[i].sobreposicao && !verifica_sobreposicao(tpremio, premios)) || !v->combinacoes[i].sobreposicao) {
							premios.push_back(tpremio);
							procurando_linear = false;

							if (v->retorna_maior_premio) {

								break;

							}
						}

						//ENCONTROU PREMIO NA BOA
					} else if(linhas_marcadas == v->combinacoes[i].nr_linhas - 1 && linhas_quase > 0 && (procurando_quase || !v->retorna_maior_premio)) {

						vector<numero_cartela> boas_local;
						boas_local.clear();

						for(unsigned int bb = 0; bb < num_boa_linha.size(); bb++) {
							if(num_boa_linha[bb].cartela == cont_cartela) {
								boas_local.push_back(num_boa_linha[bb]);
							}
						}

						for(unsigned int boa = 0; boa < boas_local.size(); boa++) {

							tpremio.nome = v->combinacoes[i].nome;
							tpremio.tipo = i;
							tpremio.cartela = cont_cartela;
							tpremio.valor = 0;
							tpremio.quase = true;

							tpremio.boa.clear();
							tpremio.linha_marcada.clear();
							tpremio.linha_quase.clear();
							tpremio.posicoes_marcadas.clear();

							tpremio.boa.push_back(boas_local[boa]);

							for(int cont_linha = 0; cont_linha < v->linhas_cartela; cont_linha++) {

								//LINHAS COMPLETADAS
								if(linha_marcada[cont_linha] == v->colunas_cartela) {

									tpremio.linha_marcada.push_back(cont_linha);

									for(int d = 0; d < v->colunas_cartela; d++) {

										numero_cartela numero_marcado;

										numero_marcado.cartela = cont_cartela;
										numero_marcado.linha = cont_linha;
										numero_marcado.coluna = d;
										numero_marcado.index = cont_linha * v->colunas_cartela + d;
										numero_marcado.marcado = true;
										numero_marcado.numero = v->serie[cont_cartela * v->numeros_cartela + numero_marcado.index];

										tpremio.posicoes_marcadas.push_back(numero_marcado);

									}										
									//LINHAS QUASE
								} else if(linha_marcada[cont_linha] == v->colunas_cartela - 1 && cont_linha == tpremio.boa[0].linha) {

									tpremio.linha_quase.push_back(cont_linha);

									for(int d = 0; d < v->colunas_cartela; d++) {

										if(v->serie[cont_cartela * v->numeros_cartela + (cont_linha * v->colunas_cartela) + d] != tpremio.boa[0].numero) {

											numero_cartela numero_marcado;

											numero_marcado.cartela = cont_cartela;
											numero_marcado.linha = cont_linha;
											numero_marcado.coluna = d;
											numero_marcado.index = cont_linha * v->colunas_cartela + d;
											numero_marcado.numero = v->serie[cont_cartela * v->numeros_cartela + numero_marcado.index];
											numero_marcado.marcado = true;

											tpremio.posicoes_marcadas.push_back(numero_marcado);

										}

									}


								}


							}

							if((v->combinacoes[i].sobreposicao && !verifica_sobreposicao(tpremio, premios)) || !v->combinacoes[i].sobreposicao) {
								premios.push_back(tpremio);
								//procurando_quase = false;
							}

						}

					}

				} else if(v->combinacoes[i].orientacao == v->VERTICAL) {

					int colunas_marcadas = 0;
					int colunas_quase = 0;

					for(int p = 0; p < v->colunas_cartela; p++) {
						if(coluna_marcada[p] == v->linhas_cartela)
							colunas_marcadas++;
						else if(coluna_marcada[p] == v->linhas_cartela - 1)
							colunas_quase++;
					}

					if(colunas_marcadas == v->combinacoes[i].nr_linhas) {	//CORRIGIDO PARA MARCAR SE TIVER MAIS LINHAS FECHADAS

						tpremio.cartela = cont_cartela;
						tpremio.tipo = i;
						tpremio.nome = v->combinacoes[i].nome;
						tpremio.valor = v->combinacoes[i].valor;
						tpremio.quase = false;

						int colcont = 0;

						for(int p = 0; p < v->colunas_cartela; p++) {
							if(coluna_marcada[p] == v->linhas_cartela) {
								//MARCA APENAS AS PRIMEIRAS COLUNAS PREENCHIDAS
								if(colcont < v->combinacoes[i].nr_linhas) {
									tpremio.coluna_marcada.push_back(p);
									colcont++;
								}
							} else if(coluna_marcada[p] == v->linhas_cartela - 1) {
								tpremio.coluna_quase.push_back(p);
							}
						}

						colcont = 0;

						for(int d = 0; d < v->colunas_cartela; d++) {
							if(coluna_marcada[d] == v->linhas_cartela && colcont < v->combinacoes[i].nr_linhas) {
								for(int c = 0; c < v->linhas_cartela; c++) {
									numero_cartela numero_marcado;

									numero_marcado.cartela = cont_cartela;
									numero_marcado.linha = c;
									numero_marcado.coluna = d;
									numero_marcado.index = d + c * v->linhas_cartela;
									numero_marcado.marcado = true;
									numero_marcado.numero = v->serie[cont_cartela * v->numeros_cartela + numero_marcado.index];

									tpremio.posicoes_marcadas.push_back(numero_marcado);
								}
								colcont++;
							}
						}

						if((v->combinacoes[i].sobreposicao && !verifica_sobreposicao(tpremio, premios)) || !v->combinacoes[i].sobreposicao) {

							premios.push_back(tpremio);
							if (v->retorna_maior_premio) {

								break;

							}

						}

					} else if(colunas_marcadas == v->combinacoes[i].nr_linhas - 1 && colunas_quase > 0 && (procurando_quase || !v->retorna_maior_premio)) {

						tpremio.tipo = i;
						tpremio.nome = v->combinacoes[i].nome;
						tpremio.valor = 0;
						tpremio.quase = true;
						tpremio.cartela = cont_cartela;

						for(unsigned int c = 0; c < num_boa_coluna.size(); c++)
							if(num_boa_coluna[c].cartela == cont_cartela)
								tpremio.boa.push_back(num_boa_coluna[c]);
						for(int p = 0; p < v->colunas_cartela; p++) {
							if(coluna_marcada[p] == v->linhas_cartela) {
								tpremio.coluna_marcada.push_back(p);
							} else if(coluna_marcada[p] == v->linhas_cartela - 1) {
								tpremio.coluna_quase.push_back(p);
							}
						}

						if((v->combinacoes[i].sobreposicao && !verifica_sobreposicao(tpremio, premios)) || !v->combinacoes[i].sobreposicao) {
							premios.push_back(tpremio);
							//procurando_quase = false;
						}

					}

				}

			} else {

				premio_ok = true;
				quase = false;

				vector<numero_cartela> todos_numeros_marcados;

				todos_numeros_marcados.clear();

				//printf("linhas_cartela=%d\n", linhas_cartela);

				for(int y = 0; y < v->linhas_cartela; y++) {

					for(int x = 0; x < v->colunas_cartela; x++) {

						if(v->combinacoes[i].prototipo[y][x] == 1) {

							if(cartela_marcada[y][x] == 1) {

								numero_cartela numero_marcado;
								numero_marcado.cartela = cont_cartela;
								numero_marcado.linha = y;
								numero_marcado.coluna = x;
								numero_marcado.index = y * v->colunas_cartela + x;
								numero_marcado.marcado = true;
								numero_marcado.numero = v->serie[cont_cartela * v->numeros_cartela + numero_marcado.index];

								todos_numeros_marcados.push_back(numero_marcado);

							} else if(!quase) {
								boa_lin = y;
								boa_col = x;
								quase = true;
							} else {
								premio_ok = false;
							}

							//printf("acha_premios - for\n");		

						}

						//printf("acha_premios - for1\n");		

					}
					//printf("acha_premios - for2\n");		

				}

				//printf("acha_premios - depois do for\n");		

				if(premio_ok) {

					if (quase) {

						if (!procurando_quase && v->retorna_maior_premio) {

							break;

						}
						//procurando_quase = false;

					}

					numero_cartela boa;

					boa.marcado = false;
					boa.cartela = cont_cartela;
					boa.linha = boa_lin;
					boa.coluna = boa_col;
					boa.index = boa_lin * v->colunas_cartela + boa_col;
					boa.numero = v->serie[cont_cartela * v->numeros_cartela + boa.index];

					tpremio.cartela = cont_cartela;
					tpremio.tipo = i;
					tpremio.nome = v->combinacoes[i].nome;
					tpremio.valor = v->combinacoes[i].valor;

					if(quase) {
						tpremio.boa.push_back(boa);
						tpremio.valor = 0;
					}

					tpremio.quase = quase;
					tpremio.posicoes_marcadas = todos_numeros_marcados;

					//printf("acha_premios - combinacoes[i].sobreposicao\n");		
					if((v->combinacoes[i].sobreposicao && !verifica_sobreposicao(tpremio, premios)) || !v->combinacoes[i].sobreposicao) {
						premios.push_back(tpremio);
						if (v->retorna_maior_premio && !quase) {

							break;

						} 

					}
					//printf("acha_premios - combinacoes[i].sobreposicao - saindo\n");		

				}


			}

		}

	}

	//retorna a lista de premios da jogada
	return premios;

}

vector<numero_cartela> lbingo::encontra_numero(int index, int cartelas_abertas) {

	//	printf("lbingo::encontra_numero(int index=%d, int cartelas_abertas=%d)\n", index, cartelas_abertas);

	if(index >= (signed)v->extracao.size()) {
		//		printf("lbingo::encontra_numero - erro no indice = %d", index);
		//		printf(" -> corrigido para %d!\n",(int)extracao.size() - 1);
		index = v->extracao.size() - 1;
	}

	vector<numero_cartela> posicoes;
	numero_cartela posicao;

	posicoes.clear();
	posicao.marcado = false;

	//SOH PROCURA NAS CARTELAS ABERTAS
	int limite = cartelas_abertas * v->numeros_cartela;

	for(int i = 0; i < limite; i++) {
		if(v->extracao[index] == v->serie[i]) {
			posicao.marcado = true;
			posicao.cartela = i / v->numeros_cartela;
			posicao.linha =(i / v->colunas_cartela) % v->linhas_cartela;
			posicao.coluna = i % v->colunas_cartela;
			posicao.numero = v->serie[i];
			posicao.index = i % v->numeros_cartela;

			posicoes.push_back(posicao);
		}
	}

	return posicoes;

}

vector<numero_cartela> lbingo::encontra_boas(int cartelas, int indice_extracao) {

	//	printf("lbingo::encontra_boas(int cartelas=%d, int indice_extracao=%d)\n", cartelas, indice_extracao);

	vector<premio> premios;
	vector<numero_cartela> boas;

	premios = acha_premios(cartelas, indice_extracao);

	for(unsigned int i = 0; i < premios.size(); i++) {
		for(unsigned int x = 0; x < premios[i].boa.size(); x++) {

			bool jafoi = false;				
			for(unsigned int w = 0; w < boas.size(); w++) {

				if(premios[i].boa[x].cartela == boas[w].cartela && premios[i].boa[x].linha == boas[w].linha && premios[i].boa[x].coluna == boas[w].coluna && v->retorna_maior_premio) {
					jafoi = true;
				}
			}

			if(!jafoi) {
				boas.push_back(premios[i].boa[x]);
			}
		}
	}

	return boas;

}

vector<int> lbingo::gera_premio(string nome, int index_extracao) {

	//printf("lbingo::gera_premio(string nome=%s, int index_extracao=%d)\n", nome.c_str(), index_extracao);

	bool encontrou_combinacao = false;

	v->bolas_usadas.clear();
	for(int i = 0; i < v->total_bolas; i++) {
		v->bolas_usadas.push_back(false);
	}

	v->extracao.clear();

	//encontra a combinacao desejada
	unsigned int cont_combinacoes = 0;

	while(cont_combinacoes < v->combinacoes.size()) {
		if(v->combinacoes[cont_combinacoes].nome == nome) {
			encontrou_combinacao = true;
			break;
		}
		cont_combinacoes++;
	}

	//aloca todas as posicoes da extracao para depois serem preenchidas
	for(int i = 0; i < v->extracao_natural + v->extras; i++) {
		v->extracao.push_back(0);
	}

	if(!encontrou_combinacao) {
		printf("ERRO %s:%d - Nao foi possivel encontrar o premio %s\n", __FILE__, __LINE__, nome.c_str());
		SDL_Quit();
		exit(__LINE__);
	}

	//monta o premio
	if(encontrou_combinacao) {

		int cartela_sorteada = randgen->gen(v->qtd_cartelas);
		int cartela_inicio = cartela_sorteada * v->numeros_cartela;

		if(v->combinacoes[cont_combinacoes].nr_linhas == 0) { //para premios geometricos

			for(int i = cartela_inicio; i < cartela_inicio + v->numeros_cartela; i++) {

				int mylin =(i / v->colunas_cartela) % v->linhas_cartela;
				int mycol = i % v->colunas_cartela;

				if(v->combinacoes[cont_combinacoes].prototipo[mylin][mycol] == 1) {
					bool aprovada = false;

					while(!aprovada){
						int posicao_sorteada = randgen->gen(index_extracao);

						if(!v->bolas_usadas[v->serie[i] - 1] && v->extracao[posicao_sorteada] == 0) {
							v->extracao[posicao_sorteada] = v->serie[i];
							v->bolas_usadas[v->serie[i] - 1] = true;
							aprovada = true;
						}
					}
				}

			}

		} else if(v->combinacoes[cont_combinacoes].nr_linhas > 0) { //para premios lineares

			if(v->combinacoes[cont_combinacoes].orientacao == v->HORIZONTAL) {

				bool linhas_sorteadas[v->linhas_cartela];
				memset(&linhas_sorteadas, false, sizeof(linhas_sorteadas));

				for(int x = 0; x < v->combinacoes[cont_combinacoes].nr_linhas; x++) {
					bool aprovada = false;

					while(!aprovada) {
						int linha_sorteada = randgen->gen(v->linhas_cartela);

						if(!linhas_sorteadas[linha_sorteada]) {
							linhas_sorteadas[linha_sorteada] = true;
							aprovada = true;
						}
					}
				}

				for(int x = 0; x < v->linhas_cartela; x++) {

					if(linhas_sorteadas[x]) {

						int linha_inicio = cartela_inicio +(x * v->colunas_cartela);

						for(int w = linha_inicio; w < linha_inicio + v->colunas_cartela; w++) {

							bool aprovada = false;

							while(!aprovada){

								int posicao_sorteada = randgen->gen(index_extracao);

								if(!v->bolas_usadas[v->serie[w] - 1] && v->extracao[posicao_sorteada] == 0) {
									v->extracao[posicao_sorteada] = v->serie[w];
									v->bolas_usadas[v->serie[w] - 1] = true;
									aprovada = true;
								}
							}
						}
					}
				}

			} else {

				bool colunas_sorteadas[v->colunas_cartela];
				memset(&colunas_sorteadas, false, sizeof(colunas_sorteadas));

				for(int x = 0; x < v->combinacoes[cont_combinacoes].nr_linhas; x++) {
					bool aprovada = false;

					while(!aprovada) {
						int coluna_sorteada = randgen->gen(v->colunas_cartela);
						if(!colunas_sorteadas[coluna_sorteada]) {
							colunas_sorteadas[coluna_sorteada] = true;
							aprovada = true;
						}
					}
				}

				for(int x = 0; x < v->colunas_cartela; x++) {

					if(colunas_sorteadas[x]) {

						int coluna_inicio = cartela_inicio + x;
						int coluna_fim = coluna_inicio +((v->linhas_cartela - 1) * v->colunas_cartela) + 1;

						for(int w = coluna_inicio; w < coluna_fim; w += v->colunas_cartela) {
							bool aprovada = false;

							while(!aprovada){
								int posicao_sorteada = randgen->gen(index_extracao);

								if(!v->bolas_usadas[v->serie[w] - 1] && v->extracao[posicao_sorteada] == 0) {
									v->extracao[posicao_sorteada] = v->serie[w];
									v->bolas_usadas[v->serie[w] - 1] = true;
									aprovada = true;
								}
							}
						}
					}
				}

			}

		}

	}

	if (v->extracao[index_extracao - 1] == 0) {

		bool aprovada = false;
		while (!aprovada) {

			int posicao_sorteada = randgen->gen(index_extracao);
			if (v->extracao[posicao_sorteada] != 0) {

				v->extracao[index_extracao - 1] = v->extracao[posicao_sorteada];
				v->extracao[posicao_sorteada] = 0;
				aprovada = true;

			}

		}

	}

	int bola = 0;
	int counter = 0;

	while(counter < v->extracao_natural + v->extras) {
		if(v->extracao[counter]) {
			counter++;
		} else {
			bola = v->serie[randgen->gen(v->serie.size())];
			if(!v->bolas_usadas[bola - 1]){
				v->extracao[counter] = bola;
				v->bolas_usadas[bola - 1] = true;
				counter++;
			}
		}
	}

	return v->extracao;

}

vector<int> lbingo::remove_premio(int tipo, int extracao_tamanho) {

	//	printf("lbingo::remove_premio(int tipo=%d, int extracao_tamanho=%d)\n", tipo, extracao_tamanho);

	int index_premio = 0;

	vector<premio> lista_premios;

	index_premio = tipo;

	lista_premios = acha_premios();

	for(unsigned int i = 0; i < lista_premios.size(); i++) {

		if(lista_premios[i].tipo == index_premio && !lista_premios[i].quase) {

			if(v->combinacoes[index_premio].contagem_marcados > 0) {

				//para premios de incidencia

			} else if(v->combinacoes[index_premio].nr_linhas > 0) {

				//para premios lineares

				if(v->combinacoes[index_premio].orientacao == v->HORIZONTAL) {
					int linha_escolhida = 0;

					if(lista_premios[i].linha_marcada.size() > 1) {
						int index_selecionado = randgen->gen(lista_premios[i].linha_marcada.size());
						linha_escolhida = lista_premios[i].linha_marcada[index_selecionado];
					} else {
						linha_escolhida = lista_premios[i].linha_marcada[0];
					}

					int coluna_escolhida = randgen->gen(v->colunas_cartela);
					int posicao_selecionada = lista_premios[i].cartela * v->numeros_cartela + linha_escolhida * v->colunas_cartela + coluna_escolhida;
					int numero_encontrado = v->serie[posicao_selecionada];

					for(int x = 0; x < extracao_tamanho; x++) {
						if(v->extracao[x] == numero_encontrado) {
							v->extracao[x] = 0;
							break;
						}
					}

					bool aprovada = false;

					while(!aprovada) {

						vector<numero_cartela> lista_boas;
						lista_boas = encontra_boas(v->qtd_cartelas, extracao_tamanho);

						int nova_bola_sorteada = v->serie[randgen->gen(v->serie.size())];
						bool eh_boa = false;

						for(unsigned int q = 0; q < lista_boas.size(); q++) {
							if(lista_boas[q].numero == nova_bola_sorteada)
								eh_boa = true;
						}

						if(!v->bolas_usadas[nova_bola_sorteada - 1] && !eh_boa){
							for(unsigned int w = 0; w < v->extracao.size(); w++) {
								if(v->extracao[w] == 0) {
									v->extracao[w] = nova_bola_sorteada;
								}
							}

							aprovada = true;
							v->bolas_usadas[nova_bola_sorteada - 1] = true;
						}

					}

				} else {
					//para premios de coluna
				}

			} else {

				//para premios geometricos

				int linha_sorteada = 0;
				int coluna_sorteada = 0;
				bool aprovada = false;

				while(!aprovada) {
					linha_sorteada = randgen->gen(v->linhas_cartela);
					coluna_sorteada = randgen->gen(v->colunas_cartela);

					if(v->combinacoes[index_premio].prototipo[linha_sorteada][coluna_sorteada] == 1)
						aprovada = true;
				}

				int posicao_selecionada = lista_premios[i].cartela * v->numeros_cartela + linha_sorteada * v->colunas_cartela + coluna_sorteada;
				int numero_encontrado = v->serie[posicao_selecionada];

				for(int x = 0; x < extracao_tamanho; x++) {
					if(v->extracao[x] == numero_encontrado) {
						v->extracao[x] = 0;
						break;
					}
				}

				aprovada = false;

				while(!aprovada) {

					vector<numero_cartela> lista_boas;
					lista_boas = encontra_boas(v->qtd_cartelas, extracao_tamanho);

					int nova_bola_sorteada = v->serie[randgen->gen(v->serie.size())];
					bool eh_boa = false;

					for(unsigned int q = 0; q < lista_boas.size(); q++) {
						if(lista_boas[q].numero == nova_bola_sorteada)
							eh_boa = true;
					}

					if(!v->bolas_usadas[nova_bola_sorteada - 1] && !eh_boa){
						for(unsigned int w = 0; w < v->extracao.size(); w++) {
							if(v->extracao[w] == 0) {
								v->extracao[w] = nova_bola_sorteada;
							}
						}

						aprovada = true;
						v->bolas_usadas[nova_bola_sorteada - 1] = true;
					}

				}

			}

		}

	}

	return v->extracao;

}

vector<premio> lbingo::acha_premios_criados(int index_bola, int cartelas, bool maior_premio) {

	//	printf("lbingo::acha_premios_criados(int index_bola=%d, int cartelas=%d, bool maior_premio=%s)\n", index_bola, cartelas, maior_premio ? "true" : "false");

	vector<premio> premios_antigos;
	vector<premio> premios_atuais;
	vector<premio> premios_diferenca;

	premios_antigos.clear();
	premios_atuais.clear();
	premios_diferenca.clear();

	if(index_bola <= 0 || index_bola >= v->extracao_natural + v->extras) {
		return premios_diferenca;
	}

	premios_antigos = acha_premios(cartelas, index_bola - 1);
	premios_atuais = acha_premios(cartelas, index_bola);

	for(unsigned int i = 0; i < premios_atuais.size(); i++) {

		bool axou = false;

		for(unsigned int x = 0; x < premios_antigos.size(); x++) {

			if(premios_atuais[i].tipo == premios_antigos[x].tipo			//VERIFICA SE O CODIGO DO PREMIO EH O MESMO
					&& premios_atuais[i].quase == premios_antigos[x].quase		//VERIFICA SE O ESTADO DO PREMIO EH O MESMO
					&& premios_atuais[i].cartela == premios_antigos[x].cartela) {	//VERIFICA SE A CARTELA DO PREMIO EH O MESMO

				unsigned int posicoes = 0;

				if(premios_atuais[i].quase) {
					for(unsigned int y = 0; y < premios_atuais[i].boa.size(); y++) {
						for(unsigned int w = 0; w < premios_antigos[x].boa.size(); w++) {
							if(premios_atuais[i].boa[y].numero == premios_antigos[x].boa[w].numero) {
								posicoes++;
							}
						}
					}					
					if(posicoes == premios_atuais[i].boa.size()) {
						axou = true;
						break;	//COMO JAH AXOU, NAUM PRECISA MAIS PROCURAR NOS OUTROS
					}
				} else {
					for(unsigned int y = 0; y < premios_atuais[i].posicoes_marcadas.size(); y++) {
						for(unsigned int w = 0; w < premios_antigos[x].posicoes_marcadas.size(); w++) {
							if(premios_atuais[i].posicoes_marcadas[y].numero == premios_antigos[x].posicoes_marcadas[w].numero) {
								posicoes++;
							}
						}
					}					
					if(posicoes == premios_atuais[i].posicoes_marcadas.size()) {
						axou = true;
						break;	//COMO JAH AXOU, NAUM PRECISA MAIS PROCURAR NOS OUTROS
					}
				}



			}

		}

		//SE O PREMIO OU QUASE PREMIO NAUM EXISTIA NA BOLA ANTERIOR,
		//ADICIONA A LISTA DE PREMIOS CRIADOS OU PIFADOS POR AKELA BOLA
		if(!axou) {
			premios_diferenca.push_back(premios_atuais[i]);
		}

	}

	//somente retorna o premio maior que bola "gerou"
	if(maior_premio) {

		if(premios_diferenca.size() > 1) {

			premio premio_temp;
			premio quase_temp;

			premio_temp.tipo = v->combinacoes.size() + 1;
			quase_temp.tipo = v->combinacoes.size() + 1;

			for(unsigned int i = 0; i < premios_diferenca.size(); i++) {

				if(premios_diferenca[i].quase) {
					if(premios_diferenca[i].tipo < premio_temp.tipo) {
						premio_temp = premios_diferenca[i];
					}
				} else {
					if(premios_diferenca[i].tipo < quase_temp.tipo) {
						quase_temp = premios_diferenca[i];
					}
				}

			}

			premios_diferenca.clear();

			if(premio_temp.tipo != (signed)(v->combinacoes.size()+1)) {
				premios_diferenca.push_back(premio_temp);
			}

			if(quase_temp.tipo != (signed)(v->combinacoes.size()+1)) {
				premios_diferenca.push_back(quase_temp);
			}

		}

	}

	return premios_diferenca;

}

vector<premio> lbingo::acha_premios_quase(int bola, int cartelas, int index) {

	//	printf("lbingo::acha_premios_quase(int bola=%d, int cartelas=%d, int index=%d)\n", bola, cartelas, index);

	vector<premio> premios_antigos;
	vector<premio> premios_diferenca;

	premios_antigos.clear();
	premios_diferenca.clear();

	if(bola <= 0 || bola > v->total_bolas)
		return premios_diferenca;

	premios_antigos = acha_premios(cartelas, index);

	//procura algum premio que esteja na "boa" esperando a bola informada
	for(int i = 0; i <(int)premios_antigos.size(); i++) {
		if(premios_antigos[i].quase) {
			for(int x = 0; x <(int)premios_antigos[i].boa.size(); x++) {
				if(premios_antigos[i].boa[x].numero == bola) {
					premios_diferenca.push_back(premios_antigos[i]);
				}
			}
		}
	}

	return premios_diferenca;

}

bool lbingo::saiu_jackpot(int index) {

	//	printf("lbingo::saiu_jackpot(int index=%d)\n", index);

	if(index == -1) {
		index = v->limite_jackpot;
	}

	if(index < 0) {
		return false;
	}

	if(index >= v->limite_jackpot) {
		index = v->limite_jackpot-1;
	}

	vector<premio> premios_encontrados;

	premios_encontrados.clear();
	premios_encontrados = acha_premios(v->qtd_cartelas, index);

	for(unsigned int i = 0; i < premios_encontrados.size(); i++) {
		if(premios_encontrados[i].tipo == v->premio_jackpot && !premios_encontrados[i].quase) {
			return true;
		}
	}

	return false;

}

bool lbingo::saiu_jackpot(int index, int cartelas) {

	if(index == -1) {
		index = v->limite_jackpot;
	}

	if(index < 0) {
		return false;
	}

	if(index >= v->limite_jackpot) {
		index = v->limite_jackpot-1;
	}

	vector<premio> premios_encontrados;

	premios_encontrados.clear();
	premios_encontrados = acha_premios(cartelas, index);

	for(unsigned int i = 0; i < premios_encontrados.size(); i++) {
		if(premios_encontrados[i].tipo == v->premio_jackpot && !premios_encontrados[i].quase) {
			return true;
		}
	}

	return false;

}

vector<int> lbingo::gera_jackpot() {

	//	printf("lbingo::gera_jackpot()\n");

	v->extracao.clear();
	v->extracao = gera_premio(nome_premio(v->premio_jackpot), v->limite_jackpot);

	return v->extracao;

}

bool lbingo::saiu_premio(string nome, int cartelas, int contador_extracao) {

	//	printf("lbingo::saiu_premio(string nome=%s)\n", nome.c_str());

	if(cartelas == -1) {

		cartelas = v->qtd_cartelas;

	}

	if(contador_extracao == -1) {

		contador_extracao = v->extracao.size() - 1;

	}

	vector<premio> premios;
	premios.clear();
	premios = acha_premios(cartelas, contador_extracao);

	for(unsigned int i = 0; i < premios.size(); i++) {

		if(!premios[i].quase) {
			if(premios[i].nome == nome) {
				return true;
			}
		}
	}

	return false;

}

bool lbingo::verifica_sobreposicao(premio premio_analisado, vector<premio> premios_encontrados) {

	//	printf("lbingo::verifica_sobreposicao(premio premio_analisado=%x, vector<premio> premios_encontrados=%x)\n", &premio_analisado, & premios_encontrados);

	if(!premio_analisado.posicoes_marcadas.size()) {
		return false;
	}

	int marcacoes_coincidentes = 0;
	int posicao[v->linhas_cartela][v->colunas_cartela];

	for(int i = 0; i < v->linhas_cartela; i++) {
		for(int x = 0; x < v->colunas_cartela; x++) {
			posicao[i][x] = false;
		}
	}

	for(unsigned int i = 0; i < premios_encontrados.size(); i++) {	

		if(((premio_analisado.quase) ||
					(!premio_analisado.quase && !premios_encontrados[i].quase)) && 
				(premios_encontrados[i].cartela == premio_analisado.cartela) &&
				(premio_analisado.tipo != premios_encontrados[i].tipo)) {

			for(unsigned int x = 0; x < premios_encontrados[i].posicoes_marcadas.size(); x++) {

				for(unsigned int y = 0; y < premio_analisado.posicoes_marcadas.size(); y++) {

					if((premio_analisado.posicoes_marcadas[y].cartela == premios_encontrados[i].posicoes_marcadas[x].cartela) &&
							(premio_analisado.posicoes_marcadas[y].linha == premios_encontrados[i].posicoes_marcadas[x].linha) &&
							(premio_analisado.posicoes_marcadas[y].coluna == premios_encontrados[i].posicoes_marcadas[x].coluna) &&
							(!posicao[premio_analisado.posicoes_marcadas[y].linha][premio_analisado.posicoes_marcadas[y].coluna])) {

						marcacoes_coincidentes++;
						posicao[premio_analisado.posicoes_marcadas[y].linha][premio_analisado.posicoes_marcadas[y].coluna] = true;	//soh analiza uma vez cada posicao

					}

				}

			}

			int posicoes = premio_analisado.posicoes_marcadas.size();

			if(premio_analisado.quase) {

				posicoes += premio_analisado.boa.size();

				for(unsigned int i = 0; i < premios_encontrados.size(); i++) {

					if(premios_encontrados[i].quase && (premio_analisado.tipo != premios_encontrados[i].tipo)) {

						for(unsigned int x = 0; x < premios_encontrados[i].boa.size(); x++) {

							for(unsigned int y = 0; y < premio_analisado.boa.size(); y++) {

								if((premio_analisado.boa[y].cartela == premios_encontrados[i].boa[x].cartela) &&
										(premio_analisado.boa[y].linha == premios_encontrados[i].boa[x].linha) &&
										(premio_analisado.boa[y].coluna == premios_encontrados[i].boa[x].coluna) &&
										(!posicao[premio_analisado.boa[y].linha][premio_analisado.boa[y].coluna])) {

									marcacoes_coincidentes++;
									posicao[premio_analisado.posicoes_marcadas[y].linha][premio_analisado.posicoes_marcadas[y].coluna] = true;	//soh analiza uma vez cada posicao

								}

							}

						}

					}

				}

			}

			if(marcacoes_coincidentes >= posicoes) {
				return true;
			}

		}

	}

	return false;
}

int lbingo::quantidade_bolas_disponiveis() {

	//	printf("lbingo::quantidade_bolas_disponiveis()\n");

	int quantidade = 0;

	for(int i = 0; i < v->qtd_cartelas * v->numeros_cartela; i++) {
		if(!v->bolas_usadas[v->serie[i] - 1]) {
			quantidade++;
		}
	}

	return quantidade;

}

void lbingo::define_serie(vector<int> nova_serie) {

	//	printf("lbingo::define_serie(vector<int> nova_serie=%x(%d itens))\n", &nova_serie, nova_serie.size());

	v->serie.clear();
	for(unsigned int i = 0; i < nova_serie.size(); i++) {
		v->serie.push_back(nova_serie[i]);
	}

}

void lbingo::define_extracao(vector<int> nova_extracao) {

	//	printf("lbingo::define_extracao(vector<int> nova_extracao=%x(%d itens))\n", &nova_extracao, nova_extracao.size());

	v->bolas_usadas.clear();
	for(int i = 0; i < v->total_bolas; i++) {
		v->bolas_usadas.push_back(false);
	}

	v->extracao.clear();

	for(unsigned int i = 0; i < nova_extracao.size(); i++) {
		int bola = nova_extracao[i];
		v->extracao.push_back(bola);
		v->bolas_usadas[bola - 1] = true;
	}

}

vector<premio> lbingo::acha_premios_be(int cartelas, int limite) {

	//	printf("lbingo::acha_premios_be(int cartelas=%d, int limite=%d)\n", cartelas, limite);

	vector<premio> premios_natural;
	vector<premio> premios;
	vector<premio> premios_be;

	premios_be.clear();
	premios_natural = acha_premios(cartelas, v->extracao_natural-1);
	premios = acha_premios(cartelas, limite);

	for(unsigned int i = 0; i < premios.size(); i++) {

		bool axou = false;

		for(unsigned int j = 0; j < premios_natural.size(); j++) {

			if(premios[i].tipo == premios_natural[j].tipo &&
					premios[i].quase == premios_natural[j].quase &&
					premios[i].cartela == premios_natural[j].cartela) {

				axou = true;

			}

		}

		if(!axou) {
			premios_be.push_back(premios[i]);
		}

	}

	return premios_be;

}

vector<premio> lbingo::acha_premios_sequencia(int index, int cartelas, int qtd) {

	//	printf("lbingo::acha_premios_sequencia(int index=%d, int cartelas=%d, int qtd=%d)\n", index, cartelas, qtd);

	vector<premio> premios;
	premios.clear();

	if(index + qtd >= v->extracao_natural + v->extras) {
		//printf("ERRO[cbingo::acha_premios_sequencia()- index invalido]\n");
		return premios;
	}

	vector<premio> premios_bola;

	for(int i = 0; i < qtd; i++) {
		premios_bola.clear();
		premios_bola = acha_premios_criados(index+i, cartelas, true);

		//REMOVE OS PIFADOS
		for(unsigned int x = 0; x < premios_bola.size(); x++) {
			if(!premios_bola[x].quase) {
				premios.push_back(premios_bola[x]);		
			}
		}

	}

	return premios;

}

int lbingo::troca_bola(int cartelas, int index) {

	//printf("lbingo::troca_bola(int cartelas=%d, int index=%d)\n", cartelas, index);

	int trocada = -1;
	int bola = v->extracao[index];
	int dezena = (bola / 10) * 10;
	//	int unidade = bola % 10;

	bool aprovada = false;
	int contador = 0;
	int menor = 0;
	int maior = 0;

	while(!aprovada) {
		aprovada = true;
		contador++;

		if(contador == 1) {
			trocada = bola - 1;
		} else if(contador == 2) {
			trocada = bola + 1;
		} else if(contador < 12) {
			if(contador % 2 == 1) {
				menor++;
				trocada = bola - (10 * menor);
			} else {
				maior++;
				trocada = bola + (10 * menor);
			}
		} else if(contador < 22) {
			trocada = dezena + (contador - 12);
		} else {
			trocada = v->serie[randgen->gen(v->serie.size())];
		}

		if(trocada < 0 || trocada > v->total_bolas) {
			aprovada = false;
		}

		if(trocada == bola) {
			aprovada = false;
		}

		if(*find(v->serie.begin(), v->serie.end(), trocada) != trocada) {
			aprovada = false;
		}

		vector<numero_cartela> boas;
		boas.clear();
		boas = encontra_boas(cartelas, index);
		for(unsigned int i = 0; i < boas.size(); i++) {
			if(boas[i].numero == trocada) {
				aprovada = false;
			}
		}

		if(*find(v->extracao.begin(), v->extracao.end(), trocada) == trocada) {
			aprovada = false;
		}

		if(contador > 100 && !aprovada) {
			trocada = bola;
			aprovada = true;
		}

	}

	return trocada;

}

int lbingo::saiu_superpremio(int contador_extracao) {

	return -1;

}

vector<int> lbingo::coloca_premio_be(int cartelas, int range) {

	return get_extracao();

}

vector<int> lbingo::trocar_bola(int index) {

	return get_extracao();

}

vector<int> lbingo::remover_superpremio() {

	return get_extracao();

}

void lbingo::dump_premios() {

	for(unsigned int i = 0; i < v->combinacoes.size(); i++) {

		printf("Premio: %02d - Nome: %20s - Valor: %6d - Orientacao: %s\n", i, v->combinacoes[i].nome.c_str(), v->combinacoes[i].valor, v->combinacoes[i].orientacao==0 ? "Vertical" : v->combinacoes[i].orientacao==1 ? "Horizontal" : "Geometrico");

	}

}


int lbingo::quantidade_premios() { return v->combinacoes.size(); }
int lbingo::maximo_cartelas() { return v->qtd_cartelas; }
int lbingo::bolas_extracao() { return v->extracao_natural; }
int lbingo::bolas_extras() { return v->extras; }

	int lbingo::retorna_bola(int index) { 
		if(index >= 0 && index < (signed)v->extracao.size())
			return v->extracao[index]; 
		return -1;
	}
int lbingo::retorna_valor_premio(int index) { return v->combinacoes[index].valor; }
int lbingo::retorna_numero_serie(int index) { return v->serie[index]; }

string lbingo::nome_premio(int index) { return v->combinacoes[index].nome; }

int lbingo::get_vertical() { return v->VERTICAL; }	
int lbingo::get_horizontal() { return v->HORIZONTAL; }	
int lbingo::get_geometrico() { return v->GEOMETRICO; }	
int lbingo::get_sim() { return v->SIM; }	
int lbingo::get_nao() { return v->NAO; }	

int lbingo::get_retorna_maior_premio() { return v->retorna_maior_premio; }
void lbingo::set_retorna_maior_premio(int valor) { v->retorna_maior_premio = valor; }

vector<bool>& lbingo::get_bolas_usadas() { return v->bolas_usadas; }
bool lbingo::get_bolas_usadas(int valor) { return v->bolas_usadas[valor]; }

void lbingo::set_bolas_usadas(vector<bool> valor) { v->bolas_usadas = valor; }
	void lbingo::set_bolas_usadas(bool valor, int pos) { 
		if(pos >=0 && (signed)v->bolas_usadas.size() > pos)
			v->bolas_usadas[pos] = valor; 
	}

vector<int>& lbingo::get_extracao() { return v->extracao; }
int lbingo::get_extracao(int pos) { return v->extracao[pos]; }
void lbingo::set_extracao(vector<int> valor) { 
	v->extracao = valor; 
}
	void lbingo::set_extracao(int valor, int pos) { 
		if(pos >=0 && (signed)v->extracao.size() > pos)
			v->extracao[pos] = valor; 
	}

vector<int>& lbingo::get_serie() { return v->serie; }                                                     // TODAS AS CARTELAS POSSIVEIS NA JOGADA
	int lbingo::get_serie(int pos) { 
		if(pos >= 0 && pos < (signed)v->serie.size())
			return v->serie[pos]; 
		return -1;
	}
void lbingo::set_serie(vector<int> valor) { v->serie = valor; }
	void lbingo::set_serie(int valor, int pos) { 
		if(pos >= 0 && pos < (signed)v->serie.size())
			v->serie[pos] = valor; 
	}

vector<combinacao>& lbingo::get_combinacoes() { return v->combinacoes; }                                 // COMBINACOES POSSIVEIS PARA PREMIO NA CARTELA	
combinacao* lbingo::get_combinacoes(int pos) { return &v->combinacoes[pos]; }
void lbingo::set_combinacao(vector<combinacao> valor) { v->combinacoes = valor; }
	void lbingo::set_combinacoes(combinacao valor, int pos) { 
		if(pos >= 0 && (signed)v->combinacoes.size() > pos)
			v->combinacoes[pos] = valor; 
	}
