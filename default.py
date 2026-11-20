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

TAMANHO_CELULA_X = HORIZONTAL / (Nx - 1)
TAMANHO_CELULA_Y = VERTICAL   / (Ny - 1)