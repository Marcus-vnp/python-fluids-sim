# Configuracoes padroes e Constantes do projeto

HORIZONTAL = 1280
VERTICAL   = 720
RESOLUCAO  = (HORIZONTAL, VERTICAL)
FPS = 60


Nx, Ny = 128, 72           # número de células
LARGURA_FISICA = 1.0
ALTURA_FISICA  = 1.0
Dx = LARGURA_FISICA / (Nx - 1)
Dy = ALTURA_FISICA  / (Ny - 1)

TAMANHO_CELULA_X = (HORIZONTAL - 1) / (Nx - 1)
TAMANHO_CELULA_Y = (VERTICAL - 1) / (Ny - 1)

# O domínio físico usa metros. O tempo simulado avança em s por s real.
DIFUSAO = 0.0005
ESCALA_TEMPO = 0.375
DT_MAXIMO = 0.012
INTERVALO_REAL_MAXIMO = 0.05
MAX_SUBPASSOS = 12

# O raio em pixels mede o suporte completo da gaussiana (três sigmas).
RAIO_INICIAL = 144
RAIO_MINIMO = 36
RAIO_MAXIMO = 240
PASSO_RAIO = 12
GANHO_MOUSE = 24.0        # s real / (s simulado)²
ACELERACAO_MAXIMA = 48.0  # m / (s simulado)²
PERTURBACAO_MAXIMA = 2.0  # m / s simulado
AMORTECIMENTO = 3.2       # 1 / s simulado
MAX_SEGMENTOS = 128
MAX_AMOSTRAS = 96

# Visualização do campo de velocidades
TEMPO_VISUAL = 0.024       # segundos simulados representados por uma seta
COMPRIMENTO_MAXIMO = 38.0  # pixels
FRACAO_ESPACAMENTO = 0.85
VELOCIDADE_MINIMA = 0.02   # m/s simulado
COR_VETOR = (111, 224, 247)
COR_CONTORNO_VETOR = (13, 49, 63)
FUNDO_VETORES = (8, 16, 22)
