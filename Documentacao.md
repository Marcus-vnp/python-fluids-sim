## Primeiros Passos 22/10

- Criei a estrutura do projeto
- Criei o loop principal em `main.py`
- Defini constantes RESOLUCAO, FPS, Dx e Dy (Conversao para notacao fisica do mundo real)
- Criei uma grade para simulacao OBS: indexing='ij' convensao para matriz

### Estrutura do Projeto
```
python-fluids-sim/
    | main.py # LOOP PRINCIPAL de EXECUCAO
    | default.py # Configuracoes padroes e Constantes do projeto
    | calcs.py # FUNCOES RESPONSAVEIS POR CALCULAR TRANSFORMACOES NA SIMULACAO
    | render.py # Funcoes responsaveis por desenhar na tela

```

### Loop principal `main.py`
Nesse arquivo contem a importacao das principais bibliotecas usadas `numpy` e `pygame`

Tambem importa os outros arquivos que fazem parte da estrutura do projeto

Faz as declaracoes basicas para criar uma tela no pygame, definindo resolucao e fps

Cria o loop responsavel por rodar todos os eventos do simulador
	Nele ja conta com a verificacao do botao de fechar

### Constantes 
- `HORIZONTAL` Representa a quantidade de pixels na horizontal
- `VERTICAL`   Representa a quantidade de pixels na vertical
- `RESOLUCAO` Uma tupla que representa a resolucao usando a `HORIZONTAL` e a `VERTICAL` como referencia
- `FPS` Defini a taxa de atualizacoes por segundo
- `Dx e Dy` Definem o espacamento entre as celulas da grade

### Funcao que cria a grade `criar_grade`
Utilizando o meshgrid no numpy, cria uma grid com as coordenadas referentes a `HORIZONTAL` e `VERTICAL`
Permite que essa grid sofra alteracoes sem precisar utilizar o `for` para percorrer cada coordenada
Utilizada a indexacao `ij` adequada para matrizes

### Funcao que desenha a grade
`desenhar_grade(tela, X, Y)`
Funcao que desenha linha com os espacamentos corretos, se baseando na grade criada pela funcao criar_grid

tela = superficie que deve ser desenhada
X = array com a posicao x de cada coordenada do grade
Y = array com a posicao y de cada coordenada do grade