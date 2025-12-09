from random import *
from classe_arts import draw_window,term, clear, art_ascii, Cores, mini_mapa_, dialogos, clear_region_a
from classe_do_jogador import *

player_b = jogador(nome="", hp_max=100, atk=15, niv=1, xp_max=100, defesa=10, gold=0, stm_max=100, intt=10, mn_max=100,d_m=20, art_player=art.necro, skin=0,skin_nome='')
mapas = mini_mapa_()

CASAS = [
    [
        '#########........',
        '#:::::::#..‼‼‼‼‼‼',
        '#::::&::#........',
        '#:::::::#........',
        r'##\######........',
    ],
    [
    '########............',
    '#::::::#............',
    '#:&::::#............',
    '#::::::#.¥¥¥¥¥¥¥¥¥¥¥',
    '#::::::#............',
    r'####\###............',
    ],
    [
    '#########',
    '#::V::::#',
    '#:::::::#',
    '#:::::::#',
    '#:::::::#',
    r'##\\#####'
    ]
]
IGREJAS = [
    [
        '...+...',
        '...#...',
        '..#:#..',
        '.#:::#.',
        '#::P::#',
        '#:::::#',
        '#:::::#',
        r'###\### ',
    ]
]
BOSS = [
    [
    '....+....',
    '....O....',
    '...O:O...',
    '..O:::O..',
    '..O:@:O..',
    '..O:::O..',
    '..O:::O..',
    '.O:::::O.',
    '.O:::::O.',
    '.O:::::O.',
    '.OOO/OOO.'
    ],
    [
    '.....+.....',
    '.....O.....',
    '....O:O....',
    '....O:O....',
    '.+.O:::O.+.',
    'O:O:::::O:O',
    'O:::::::::O',
    'O::::W::::O',
    'O:::::::::O',
    'O:::::::::O',
    r'OOOO\\OOOOO'

    ]
]

def colocar_construcao(mapa, estrutura, pos_x, pos_y):
    mapa_altura = len(mapa)
    mapa_largura = len(mapa[0])
    for y, linha in enumerate(estrutura):
        for x, ch in enumerate(linha):
            mapa_y = pos_y + y
            mapa_x = pos_x + x
            if 0 <= mapa_x < mapa_largura and 0 <= mapa_y < mapa_altura:
                mapa[mapa_y][mapa_x] = ch

def gerar_mapa_procedural_unido(largura, altura, seed=None):
    if seed is not None:
        random.seed(seed)
    else:
        random.seed()

    noise = [[random.random() for _ in range(largura)] for _ in range(altura)]

    def suavizar(matriz, vezes=2):
        temp_matriz = matriz
        for _ in range(vezes):
            nova = [[0.0] * largura for _ in range(altura)]
            for y in range(altura):
                for x in range(largura):
                    vizinhos = []
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < largura and 0 <= ny < altura:
                                vizinhos.append(temp_matriz[ny][nx])
                    nova[y][x] = sum(vizinhos) / len(vizinhos)
            temp_matriz = nova
        return temp_matriz

    noise = suavizar(noise, vezes=3)
    total = largura * altura

    qtd_agua = int(total * 0.05)
    qtd_pedras = int(total * 0.1)
    qtd_carvao = int(total * 0.02)

    noise_flat = [(noise[y][x], x, y) for y in range(altura) for x in range(largura)]
    noise_flat.sort(key=lambda t: t[0])

    mapa = [['.'] * largura for _ in range(altura)]

    player_spawn_x = player_b.x_mapa
    player_spawn_y = player_b.y_mapa
    zona_segura_x = 10
    zona_segura_y = 5

    todas_construcoes = []

    idx_atual = 0
    qtd_a_preencher = min(qtd_agua, len(noise_flat) - idx_atual)
    for i in range(qtd_a_preencher):
        _, x, y = noise_flat[idx_atual + i]
        if abs(x - player_spawn_x) < zona_segura_x and abs(y - player_spawn_y) < zona_segura_y:
            continue
        mapa[y][x] = '~'
    idx_atual += qtd_a_preencher

    candidatos_arvore = noise_flat[-qtd_pedras:]
    restante_para_embaralhar = noise_flat[idx_atual : -qtd_pedras if qtd_pedras > 0 else None]
    random.shuffle(restante_para_embaralhar)
    for _, x, y in candidatos_arvore:
        if abs(x - player_spawn_x) < zona_segura_x and abs(y - player_spawn_y) < zona_segura_y:
            continue
        mapa[y][x] = '♣'

    candidatos_idx = 0
    qtd_total_arbusto = min(qtd_carvao, len(restante_para_embaralhar) - candidatos_idx)
    for _ in range(qtd_total_arbusto):
        _, x, y = restante_para_embaralhar[candidatos_idx]
        candidatos_idx += 1
        if abs(x - player_spawn_x) < zona_segura_x and abs(y - player_spawn_y) < zona_segura_y:
            continue
        mapa[y][x] = '♠'

    def longe_de_todas_construcoes(x, y, distancia_x=20, distancia_y=10):
        for (cx, cy) in todas_construcoes:
            if abs(x - cx) < distancia_x and abs(y - cy) < distancia_y:
                return False
        return True

    #Casas
    if total == 25000:
        casa_w = 10
    if total == 125000:
        casa_w = 20
    if total == 320000:
        casa_w = 30
    else:
        casa_w = 0
    qtd_construcoes = casa_w
    for _ in range(qtd_construcoes):
        casa = random.choice(CASAS)
        alt_casa = len(casa)
        lar_casa = len(casa[0])

        for _ in range(100):
            x = random.randint(0, largura - lar_casa - 1)
            y = random.randint(0, altura - alt_casa - 1)

            if abs(x - player_spawn_x) < zona_segura_x and abs(y - player_spawn_y) < zona_segura_y:
                continue
            if not longe_de_todas_construcoes(x, y):
                continue

            colocar_construcao(mapa, casa, x, y)
            todas_construcoes.append((x, y))
            break

    #Igrejas
    if total == 25000:
        igrejas_w = 5
    if total == 125000:
        igrejas_w = 10
    if total == 320000:
        igrejas_w = 15
    else:
        igrejas_w = 0
    qtd_igrejas = igrejas_w
    for _ in range(qtd_igrejas):
        igreja = random.choice(IGREJAS)
        alt = len(igreja)
        lar = len(igreja[0])

        for _ in range(100):
            x = random.randint(0, largura - lar - 1)
            y = random.randint(0, altura - alt - 1)

            if abs(x - player_spawn_x) < zona_segura_x and abs(y - player_spawn_y) < zona_segura_y:
                continue
            if not longe_de_todas_construcoes(x, y):
                continue

            colocar_construcao(mapa, igreja, x, y)
            todas_construcoes.append((x, y))
            break

    if mapa[player_spawn_y][player_spawn_x] == '~':
        mapa[player_spawn_y][player_spawn_x] = '.'

    mapa_final = [''.join(linha) for linha in mapa]
    return mapa_final

def mapa_procedural(nome, largura, altura, seed=None):
    mapa = gerar_mapa_procedural_unido(largura=largura, altura=altura, seed=seed)
    player_b.mapa_atual = 'Mundo'
    cores = {
    '#':term.lightsalmon,
    '♣':term.olivedrab2,
    '&':term.blue,
    "C":term.brown,
    '‼':term.yellow2,
    '¥':term.forestgreen,
    '☼': term.bold_brown_on_gray,
    'o':term.antiquewhite3,
    '0':term.coral,
    '1':term.brown,
    '*':term.olivedrab,
    '♠':term.springgreen4,
    'x':term.chocolate3,
    '$':term.sandybrown,
    '.':term.lawngreen,
    '\\': term.tan4,
    '~': term.bold_white_on_deepskyblue3,
    ':': term.thistle4,
    '+': term.bold_cornsilk3,
    '=': term.lightsalmon3,
    'I': term.rosybrown2,
    'N': term.sienna,
    'G': term.red,
    'F': term.magenta,
    ',': term.bold_white_on_rosybrown2,
    '!': term.lightsalmon,
    '@': term.red_on_purble,
    'O': term.lightgray_on_darkgray,
    '/': term.brown,
    '%': term.orange1_on_darkgray,
    'V': term.darkgreen,
    '♀': term.bold_red2,
    "7": term.lightgreen
    }
    obstaculos = set([
        '#', '♣', '&', "C", '‼', '¥', 'o', '0', '1', '„', '♠', 'x', '$', '+', 'P', 'N', 'I', 'G', 'F', '!', '/', 'O', '@', '%', 'V', '♀', "7", "☼"
    ])

    return {
        "mapa": mapa,
        "cores": cores,
        "obstaculos": obstaculos,
        "nome": nome
    }

def gerar_caverna(largura, altura, player_b, seed=None):
    if seed is not None:
        random.seed(seed)
    else:
        random.seed()

    player_x = player_b.x_mapa
    player_y = player_b.y_mapa

    # Cria mapa cheio de pedra
    mapa = [['o' for _ in range(largura)] for _ in range(altura)]

    # Posição inicial
    x, y = player_x, player_y
    mapa[y][x] = '.'

    num_tuneis = 100
    comprimento_tunel = 40
    direcoes = [(0,1), (1,0), (0,-1), (-1,0)]

    for _ in range(num_tuneis):
        dx, dy = random.choice(direcoes)
        for _ in range(random.randint(5, comprimento_tunel)):
            x += dx
            y += dy

            if x < 1 or x >= largura-1 or y < 1 or y >= altura-1:
                break
            mapa[y][x] = '.'

            # 🔹 Chance de abrir uma sala ao redor
            if random.random() < 0.05:
                for dy2 in range(-2, 3):
                    for dx2 in range(-2, 3):
                        if 0 < y+dy2 < altura and 0 < x+dx2 < largura:
                            mapa[y+dy2][x+dx2] = '.'

            # Pequena chance de mudar de direção
            if random.random() < 0.2:
                dx, dy = random.choice(direcoes)

    total = largura * altura
    qtd_ferro = int(total * 0.03)
    qtd_carvao = int(total * 0.05)
    qtd_esqueleto = random.randint(5, 30)
    qtd_zumbi = random.randint(5, 30)
    qtd_bau = random.randint(1, 15)

    pos_pedras = [(x, y) for y in range(altura) for x in range(largura) if mapa[y][x] == 'o']
    pos_terra = [(x, y) for y in range(altura) for x in range(largura) if mapa[y][x] == '.']
    random.shuffle(pos_pedras)

    # Ferro
    if player_b.andar >= 5:
        for i in range(min(qtd_ferro, len(pos_pedras))):
            x, y = pos_pedras[i]
            mapa[y][x] = 'u'
    else:
        pass
    # Carvão
    random.shuffle(pos_pedras)
    colocados = 0
    for x, y in pos_pedras:
        if mapa[y][x] == 'o':
            mapa[y][x] = 'c'
            colocados += 1
            if colocados >= qtd_carvao:
                break

    random.shuffle(pos_terra)
    colocados = 0
    for x, y in pos_terra:
        if mapa[y][x] == '.':
            mapa[y][x] = 'F'
            colocados += 1
            if colocados >= qtd_zumbi:
                break
    colocados = 0
    for x, y in pos_terra:
        if mapa[y][x] == '.':
            mapa[y][x] = 'B'
            colocados += 1
            if colocados >= qtd_bau:
                break

    colocados = 0
    for x, y in pos_terra:
        if mapa[y][x] == '.':
            mapa[y][x] = 'G'
            colocados += 1
            if colocados >= qtd_esqueleto:
                break

    if player_b.andar == 10:
        direcoes_possiveis = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0),           (1, 0),
            (-1, 1),  (0, 1),  (1, 1),
        ]
        random.shuffle(direcoes_possiveis)
        colocado = False

        for dx, dy in direcoes_possiveis:
            bx, by = player_x + dx, player_y + dy
            if 0 <= bx < largura and 0 <= by < altura and mapa[by][bx] == '.':
                mapa[by][bx] = '@'
                colocado = True
                break

        # Se não conseguiu nas posições próximas, tenta achar outro ponto livre aleatório
        if not colocado:
            for _ in range(1000):
                bx, by = random.randint(1, largura-2), random.randint(1, altura-2)
                if mapa[by][bx] == '.':
                    mapa[by][bx] = '@'
                    break

    mapa_final = [''.join(linha) for linha in mapa]
    return mapa_final

def mapa_caverna(nome, largura, altura, player_b ,seed=None):
    mapa = gerar_caverna(largura=largura, altura=altura, player_b = player_b,seed=seed)
    player_b.mapa_atual = f'Caverna - [{player_b.andar}]'
    cores = {
        'o': term.bold_antiquewhite3,
        'u': term.rosybrown2,
        '.': term.seashell2,
        'c': term.darkslategray,
        '~': term.bold_white_on_deepskyblue3,
        'B': term.sandybrown,
        'F': term.magenta,
        'G': term.red
    }

    obstaculos = set([
        '&', 'o', 'u', 'c'
    ])

    return {
        "mapa": mapa,
        "cores": cores,
        "obstaculos": obstaculos,
        "nome": nome
    }



