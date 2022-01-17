#ifndef __LBINGO_H__
#define __LBINGO_H__
 
#include <vector>
#include <string>
#include <stdarg.h>
#include "libSuperclass.h"

using namespace std;

struct numero_cartela {
	int cartela;
	int numero;
	int linha;
	int coluna;
	int index; 
	bool marcado;
};

struct premio {
	int tipo;					// INDICE DO PREMIO NA LISTA DE COMBINACOES
	int cartela;					// CARTELA ONDE SAIU O PREMIO
	int valor;
	bool quase;					// PREMIO QUASE OU COMPLETO
	string nome;					// NOME DO PREMIO
	vector<numero_cartela> boa;			// LISTA DOS NUMERO PIFADOS PARA O PREMIO
	vector<numero_cartela> posicoes_marcadas;	// LISTA DOS NUMEROS MARCADOS
	vector<int> linha_marcada;			// INDICE DAS LINHAS MARCADAS, UTILIZADO NOS PREMIOS LINEARES
	vector<int> linha_quase;			// INDICE DAS LINHAS PIFADAS, UTILIZADO NOS PREMIOS LINEARES
	vector<int> coluna_marcada;			// INDICE DAS COLUNAS MARCADAS, UTILIZADO NOS PREMIOS LINEARES
	vector<int> coluna_quase;			// INDICE DAS COLUNAS PIFADAS, UTILIZADO NOS PREMIOS LINEARES
};

struct combinacao {

		vector< vector<int> > prototipo;
		int contagem_marcados;
		int orientacao;
		int nr_linhas;
		int sobreposicao;
		int valor;
		string nome;

	};

class lbingo {

public:

	lbingo();
	virtual ~lbingo() {;}
	
	
	int quantidade_premios();
	int maximo_cartelas();
	int bolas_extracao();
	int bolas_extras();
	
	virtual vector<int> gera_serie(bool);				// GERA TODOS OS NUMEROS DAS CARTELAS
	virtual vector<int> gera_extracao();				// GERA TODAS AS BOLAS SORTEADAS NA JOGADA
	virtual vector<int> gera_premio(string, int);
	virtual vector<int> gera_jackpot();
	virtual vector<int> remove_premio(int, int);
	virtual vector<int> coloca_premio_be(int, int);
	virtual vector<int> trocar_bola(int);
	virtual vector<int> remover_superpremio();

	virtual vector<premio> acha_premios(int=-1, int=-1);
	virtual vector<premio> acha_premios_criados(int, int, bool);
	virtual vector<premio> acha_premios_quase(int, int, int);
	virtual vector<premio> acha_premios_be(int, int);
	virtual vector<premio> acha_premios_sequencia(int, int, int);
	virtual vector<numero_cartela> encontra_numero(int, int);
	virtual vector<numero_cartela> encontra_boas(int, int);
	
	virtual bool verifica_sobreposicao(premio, vector<premio>);
	virtual bool saiu_jackpot(int=-1);
	virtual bool saiu_jackpot(int, int);
	virtual bool saiu_premio(string, int=-1, int=-1);
	
	virtual int quantidade_bolas_disponiveis();
	virtual int retorna_bola(int index);
	virtual int retorna_valor_premio(int index);
	virtual int retorna_numero_serie(int index);
	virtual int troca_bola(int,int);
	virtual int saiu_superpremio(int);
	
	virtual string nome_premio(int index);
	
	virtual void define_serie(vector<int>);
	virtual void define_extracao(vector<int>);
	void dump_premios();

protected:

	virtual void push_cartelas(int, int, int);
	virtual void push_bolas(int, int, int);
	virtual void push_jackpot(int, int);


	virtual void push_combinacao(string, int, int, int, int, int, ...);                    // CARREGA PARA DENTRO DA LISTA AS MATRIZES BIN
	virtual void push_combinacao2(string, int, int, int, int, int, unsigned);                    // CARREGA PARA DENTRO DA LISTA AS MATRIZES BIN

	int get_vertical();	
	int get_horizontal();	
	int get_geometrico();	
	int get_sim();	
	int get_nao();	

	int get_retorna_maior_premio();
	void set_retorna_maior_premio(int valor);

	vector<bool>& get_bolas_usadas();
	bool get_bolas_usadas(int valor);

	void set_bolas_usadas(vector<bool> valor);
	void set_bolas_usadas(bool valor, int pos);

	vector<int>& get_extracao();
	int get_extracao(int pos);
	void set_extracao(vector<int> valor);
	void set_extracao(int valor, int pos);

	vector<int>& get_serie();                                                     // TODAS AS CARTELAS POSSIVEIS NA JOGADA
	int get_serie(int pos);
	void set_serie(vector<int> valor);
	void set_serie(int valor, int pos);

	vector<combinacao>& get_combinacoes();                                 // COMBINACOES POSSIVEIS PARA PREMIO NA CARTELA	
	combinacao* get_combinacoes(int pos);
	void set_combinacao(vector<combinacao> valor);
	void set_combinacoes(combinacao valor, int pos);

	struct lbingo_vars {
		int qtd_cartelas;
		int numeros_cartela;
		int linhas_cartela;
		int colunas_cartela;
		int total_bolas;
		int extracao_natural;
		int extras;
		int premio_jackpot;
		int limite_jackpot;

		static const int VERTICAL = 0;		//PREMIOS EM FORMA DE COLUNA
		static const int HORIZONTAL = 1;	//PREMIOS EM FORMA DE LINHA
		static const int GEOMETRICO = 2;	//PREMIOS EM FORMA GEOMETRICA

		static const bool NAO = false;		//NAO VERIFICA SOBREPOSICAO
		static const bool SIM = true;		//VERIFICA SOBREPOSICAO

		int retorna_maior_premio;

		vector<bool> bolas_usadas;
		vector<int> extracao;                                                  // TODAS AS BOLAS REFERENTES A JOGADA
		vector<int> serie;                                                     // TODAS AS CARTELAS POSSIVEIS NA JOGADA
		vector<combinacao> combinacoes;                                 // COMBINACOES POSSIVEIS PARA PREMIO NA CARTELA	
	};
	struct lbingo_vars *v;

};

#endif
