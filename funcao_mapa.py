import json, os, glob
from classe_do_inventario import TODOS_OS_ITENS
from classe_do_jogador import jogador
from classe_arts import *
import time, random, textwrap
from collections import Counter, deque
ascii = art_ascii()
player = jogador(nome="Joojs", hp_max=30, atk=5000, niv=15, xp_max=100, defesa=0, gold=0, stm_max=100, intt=0, mn_max=100,d_m=15,art_player=ascii.necro, skin="@", skin_nome='')

def adicionar_caracteres_aleatorios(mapa_id, estado_mapa, caracteres_quantidades, seed=None):
    if estado_mapa.get("caracteres_aleatorios"):
        return 

    if seed is not None:
        random.seed(seed)

    mapa_art = estado_mapa["mapa_art"]
    altura = len(mapa_art)
    largura = len(mapa_art[0])
    posicoes_validas = [
        (x, y)
        for y in range(altura)
        for x in range(largura)
        if mapa_art[y][x] == '.'
    ]
    random.shuffle(posicoes_validas)
    total_caracteres = sum(caracteres_quantidades.values())
    total_caracteres = min(total_caracteres, len(posicoes_validas))

    caracteres_colocados = []
    pos_index = 0

    for char, qtd in caracteres_quantidades.items():
        for _ in range(qtd):
            if pos_index >= len(posicoes_validas):
                break
            x, y = posicoes_validas[pos_index]
            pos_index += 1

            linha_antiga = mapa_art[y]
            mapa_art[y] = linha_antiga[:x] + char + linha_antiga[x+1:]
            caracteres_colocados.append((x, y, char))

    estado_mapa["caracteres_aleatorios"] = caracteres_colocados
    estado_mapa["mapa_art"] = mapa_art  # Atualiza o mapa com os novos caracteres

    salvar_mapa_estado(f"save_mapa_{mapa_id}.json", mapa_id, estado_mapa)

def contar_caracteres_no_mapa(mapa_art, caracteres=None):
    if caracteres is None:
        return False
    
    contador = {ch: 0 for ch in caracteres.keys()}

    for linha in mapa_art:
        for ch in linha:
            if ch in contador:
                contador[ch] += 1

    # Verifica se algum caractere atingiu ou ultrapassou o limite
    for ch, limite in caracteres.items():
        if contador[ch] >= limite:
            return True
    
    return False

def adicionar_construcoes_aleatorias(mapa, construcoes_disponiveis,quantidades,zona_segura=(10, 5),player_spawn=(50, 25),distancia_minima=15,seed=None):
    if seed is not None:
        random.seed(seed)

    altura = len(mapa)
    largura = len(mapa[0])
    player_spawn_x, player_spawn_y = player_spawn
    zona_segura_x, zona_segura_y = zona_segura

    construcoes_colocadas = []

    for tipo, qtd in quantidades.items():
        if tipo not in construcoes_disponiveis:
            continue
        for _ in range(qtd):
            estrutura = random.choice(construcoes_disponiveis[tipo])
            alt = len(estrutura)
            larg = len(estrutura[0])

            max_tentativas = 100
            for _ in range(max_tentativas):
                x = random.randint(0, largura - larg - 1)
                y = random.randint(0, altura - alt - 1)

                # Evitar zona segura
                if abs(x - player_spawn_x) < zona_segura_x and abs(y - player_spawn_y) < zona_segura_y:
                    continue

                # Evitar sobreposição com outras construções
                muito_perto = False
                for (cx, cy) in construcoes_colocadas:
                    if abs(x - cx) < distancia_minima and abs(y - cy) < distancia_minima // 2:
                        muito_perto = True
                        break
                if muito_perto:
                    continue

                # Verifica se área é livre
                espaco_livre = True
                for yy in range(alt):
                    for xx in range(larg):
                        if mapa[y + yy][x + xx] != '.':
                            espaco_livre = False
                            break
                    if not espaco_livre:
                        break

                if not espaco_livre:
                    continue

                # Coloca a construção
                for yy, linha in enumerate(estrutura):
                    for xx, ch in enumerate(linha):
                        mapa[y + yy][x + xx] = ch

                construcoes_colocadas.append((x, y))
                break  # sucesso

    return mapa

def add_boss(mapa_art, player, mapa_id, ESTADO_MAPAS, num=0):
    from maps import BOSS
    CONSTRUCOES = {
        'BOSS': [BOSS[num]]
    }
    quantidades = {
        'BOSS': 1
    }

    mapa_mutavel = [list(linha) for linha in mapa_art]
    mapa_mutavel = adicionar_construcoes_aleatorias(
        mapa=mapa_mutavel,
        construcoes_disponiveis=CONSTRUCOES,
        quantidades=quantidades,
        zona_segura=(10, 5),
        player_spawn=(player.x_mapa, player.y_mapa),
        distancia_minima=20
    )
    mapa_art = [''.join(linha) for linha in mapa_mutavel]
    ESTADO_MAPAS[mapa_id]["mapa_art"] = mapa_art
    return mapa_art

def localizar_caractere(mapa_art, caractere):
    posicoes = []
    for y, linha in enumerate(mapa_art):
        for x, ch in enumerate(linha):
            if ch == caractere:
                posicoes.append((x, y))
    return posicoes

def substituir_caractere(mapa_art, x, y, novo_char):
    if not (0 <= y < len(mapa_art)):
        raise IndexError(f"Linha {y} fora dos limites do mapa.")
    if not (0 <= x < len(mapa_art[y])):
        raise IndexError(f"Coluna {x} fora dos limites da linha {y}.")

    linha_antiga = mapa_art[y]
    mapa_art[y] = linha_antiga[:x] + novo_char + linha_antiga[x + 1:]
    return mapa_art

def mover_inimigos_para_jogador(mapa_art, player, obstaculos, inimigo_chars, estado_mapa, raio_visao=int):
    altura = len(mapa_art)
    largura = len(mapa_art[0])
    destino = (player.x_mapa, player.y_mapa)
    
    if "fundo_inimigos" not in estado_mapa:
        estado_mapa["fundo_inimigos"] = {}
    fundo_inimigos = estado_mapa["fundo_inimigos"]
    inimigos = []

    for y, linha in enumerate(mapa_art):
        for x, ch in enumerate(linha):
            if ch in inimigo_chars:
                inimigos.append((x, y, ch))

    for inimigo_x, inimigo_y, inimigo_tipo in inimigos:
        dx = player.x_mapa - inimigo_x
        dy = player.y_mapa - inimigo_y
        distancia = (dx ** 2 + dy ** 2) ** 0.5
        if distancia > raio_visao:
            continue
        visitados = set()
        fila = deque()
        fila.append(((inimigo_x, inimigo_y), []))
        caminho_encontrado = None

        while fila:
            (x, y), caminho = fila.popleft()
            if (x, y) in visitados:
                continue
            visitados.add((x, y))
            if (x, y) == destino:
                caminho_encontrado = caminho
                break
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < largura and 0 <= ny < altura and (nx, ny) not in visitados:
                    ch = mapa_art[ny][nx]
                    if (nx, ny) == destino or (ch not in obstaculos and ch not in inimigo_chars):
                        fila.append(((nx, ny), caminho + [(nx, ny)]))

        if caminho_encontrado and len(caminho_encontrado) > 0:
            proximo_x, proximo_y = caminho_encontrado[0]
            if (proximo_x, proximo_y) == destino:
                continue
            if mapa_art[proximo_y][proximo_x] not in inimigo_chars:
                fundo_char = fundo_inimigos.get((inimigo_x, inimigo_y), '.')
                mapa_art[inimigo_y] = mapa_art[inimigo_y][:inimigo_x] + fundo_char + mapa_art[inimigo_y][inimigo_x + 1:]
                fundo_inimigos[(proximo_x, proximo_y)] = mapa_art[proximo_y][proximo_x]
                mapa_art[proximo_y] = mapa_art[proximo_y][:proximo_x] + inimigo_tipo + mapa_art[proximo_y][proximo_x + 1:]

def remover_caracteres(mapa_art, caracteres_para_remover):
    for y in range(len(mapa_art)):
        linha = mapa_art[y]
        nova_linha = ""
        for ch in linha:
            if ch in caracteres_para_remover:
                nova_linha += "."
            else:
                nova_linha += ch
        mapa_art[y] = nova_linha

def serializar_para_json(data):
    if isinstance(data, dict):
        novo_dicionario = {}
        for k, v in data.items():
            if isinstance(k, tuple):
                k = f"{k[0]},{k[1]}"
            novo_dicionario[k] = serializar_para_json(v)
        return novo_dicionario
        
    elif isinstance(data, list):
        return [serializar_para_json(item) for item in data]
        
    elif isinstance(data, set):
        return list(data)

    elif hasattr(data, '__class__') and data.__class__.__name__ == 'Item':
        return {
            "__class__": "Item", 
            "nome": data.nome
        }
    
    else:
        return data

def deserializar_do_json(data):
    if isinstance(data, dict) and data.get("__class__") == "Item":
        item_nome = data.get("nome")
        if item_nome and item_nome in TODOS_OS_ITENS:
            return TODOS_OS_ITENS[item_nome]
        else:
            print(f"⚠️ Aviso: Item '{item_nome}' não encontrado em TODOS_OS_ITENS durante o load.")
            return None

    if isinstance(data, dict):
        novo_dicionario = {}
        for k, v in data.items():
            if isinstance(k, str) and ',' in k and all(part.strip().isdigit() for part in k.split(',')):
                try:
                    k = tuple(map(int, k.split(',')))
                except ValueError:
                    pass                     
            novo_dicionario[k] = deserializar_do_json(v)
        return novo_dicionario
        
    elif isinstance(data, list):
        return [deserializar_do_json(item) for item in data]
        
    else:
        return data

def salvar_jogo_player(player, filename="save_player.json"):
    try:
        # Serializa o inventário e equipamento apenas pelos nomes
        inventario_nomes = [item.nome for item in player.inventario]
        equipa_nomes = {slot: item.nome if item else None for slot, item in player.equipa.items()}

        player_data = {
            "nome": player.nome,
            "hp_max": player.hp_max,
            "hp": player.hp,
            "atk": player.atk,
            "niv": player.niv,
            "xp_max": player.xp_max,
            "defesa": player.defesa,
            "gold": player.gold,
            "stm_max": player.stm_max,
            "stm": player.stm,
            "intt": player.intt,
            "mana_max": player.mana_max,
            "mana": player.mana,
            "d_m": player.dano_magico,
            "xp": player.xp,
            "aleatorio": player.aleatorio,
            "inventario": inventario_nomes,
            "equipa": equipa_nomes,
            "itens_coletados": player.itens_coletaodos,
            "rodar": player.rodar_jogo,
            "classe": player.classe,
            "pos_x": player.x_mapa,
            "pos_y": player.y_mapa,
            "mapa_atual": player.mapa_atual,
            "skin": player.skin,
            "skin_nome": player.skin_nome,
            "pontos": player.ponto,
            "andar": player.andar,
            "seed": player.seed,
            'seed_caverna': player.seed_caverna,
            "fov_bonus": player.fov_bonus,
            "tocha_acesa": player.tocha_acesa,
            "mapa_x": player.mapa_x,
            "mapa_y": player.mapa_y,
            "retorno": player.retorno
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(player_data, f, indent=4)
    except Exception as e:
        pass

def carregar_jogo_player(filename="save_player.json"):
    if not os.path.exists(filename):
        return None
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            player_data = json.load(f)

        # Reconstrói o jogador
        SKIN_MAP = {
            "necro": ascii.necro,
            "guerreiro": ascii.guerriro,
            "mago": ascii.mago
        }
        skin_nome_carregado = player_data.get("skin_nome")
        skin_arte_carregada = SKIN_MAP.get(skin_nome_carregado) or None

        player = jogador(
            nome=player_data["nome"],
            hp_max=player_data["hp_max"],
            atk=player_data["atk"],
            niv=player_data["niv"],
            xp_max=player_data["xp_max"],
            defesa=player_data["defesa"],
            gold=player_data["gold"],
            stm_max=player_data["stm_max"],
            intt=player_data["intt"],
            mn_max=player_data["mana_max"],
            d_m=player_data["d_m"],
            art_player=skin_arte_carregada,
            skin=player_data.get("skin", "@"),
            skin_nome=skin_nome_carregado,
            mapa_x = player_data["mapa_x"],
            mapa_y = player_data["mapa_y"]
        )

        # Restaura atributos
        player.hp = player_data["hp"]
        player.mana = player_data["mana"]
        player.xp = player_data["xp"]
        player.stm = player_data["stm"]
        player.ponto = player_data["pontos"]
        player.andar = player_data["andar"]
        player.retorno = player_data["retorno"]
        player.x_mapa = player_data["pos_x"]
        player.y_mapa = player_data["pos_y"]
        player.fov_bonus = player_data.get("fov_bonus", 0)
        player.tocha_acesa = player_data.get("tocha_acesa", False)
        player.seed_caverna = player_data['seed_caverna']
        player.seed = player_data["seed"]
        player.mapa_atual = player_data["mapa_atual"]
        player.inventario = [TODOS_OS_ITENS[n] for n in player_data.get("inventario", []) if n in TODOS_OS_ITENS]
        player.equipa = {slot: TODOS_OS_ITENS[n] if n and n in TODOS_OS_ITENS else None
                         for slot, n in player_data.get("equipa", {}).items()}
        player.itens_coletaodos = player_data.get("itens_coletados", {})
        player.rodar_jogo = player_data.get("rodar")
        player.classe = player_data.get("classe")
        return player

    except Exception as e:
        return None

def salvar_mapa_estado(filename, mapa_id, estado_mapa):
    try:
        dados_salvar = {
            "mapa_id": mapa_id,
            "mapa_art": estado_mapa["mapa_art"],
            # Campos que são SETs
            "inimigos_derrotados": estado_mapa.get("inimigos_derrotados", set()),
            "baus_abertos": estado_mapa.get("baus_abertos", set()),
            "obstaculos": estado_mapa.get("obstaculos", set()),
            "chaves_pegas": estado_mapa.get("chaves_pegas", set()),
            "abrir_porta": estado_mapa.get("abrir_porta", set()),
            # Campos com chaves de TUPLA
            "cores": estado_mapa.get("cores", {}),
            "plantacoes": estado_mapa.get("plantacoes", {}),
            "regeneracoes": estado_mapa.get("regeneracoes", {}),
            "interacoes": estado_mapa.get("interacoes", {}),
            "caracteres_aleatorios": estado_mapa.get("caracteres_aleatorios", []),
            "baus_armazenamento": estado_mapa.get("baus_armazenamento", {}),
            "tempo_inicio": estado_mapa.get("tempo_inicio"),
            "tempo_decorrido": estado_mapa.get("tempo_decorrido", 0)
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializar_para_json(dados_salvar), f, indent=4)

    except IOError as e:
        print(f"❌ Erro ao salvar mapa em {filename}: {e}")
    except Exception as e:
        print(f"⚠️ Erro inesperado ao salvar mapa {mapa_id}: {e}")

def carregar_mapa_estado(filename):
    if not os.path.exists(filename):
        print(f"Nenhum save encontrado para {filename}. Será criado um novo mapa.")
        return None

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            dados_carregados = json.load(f)
            estado_deserializado = deserializar_do_json(dados_carregados)
            # Conversões de volta para SETs
            estado_deserializado["inimigos_derrotados"] = set(estado_deserializado.get("inimigos_derrotados", []))
            estado_deserializado["baus_abertos"] = set(estado_deserializado.get("baus_abertos", []))
            estado_deserializado["obstaculos"] = set(estado_deserializado.get("obstaculos", []))
            estado_deserializado["chaves_pegas"] = set(estado_deserializado.get("chaves_pegas", []))
            estado_deserializado["abrir_porta"] = set(estado_deserializado.get("abrir_porta", [])) 
            # Corrige baús com chaves de string em vez de tupla
            baus_finais = {}
            baus_armazenamento_carregados = estado_deserializado.get("baus_armazenamento", {})
            for pos_str, lista_itens in baus_armazenamento_carregados.items():
                if isinstance(pos_str, tuple):
                    pos_tuple = pos_str
                else:
                    try:
                        pos_tuple = tuple(map(int, pos_str.strip("()").split(",")))
                    except Exception:
                        pos_tuple = pos_str  # fallback se não for uma tupla válida
                baus_finais[pos_tuple] = lista_itens

            estado_deserializado["baus_armazenamento"] = baus_finais

            # Garante que todos os campos esperados existam
            if "regeneracoes" not in estado_deserializado:
                estado_deserializado["regeneracoes"] = {}
            if "plantacoes" not in estado_deserializado:
                estado_deserializado["plantacoes"] = {}
            if "cores" not in estado_deserializado:
                estado_deserializado["cores"] = {}
            estado_deserializado.setdefault("tempo_inicio", None)
            estado_deserializado.setdefault("tempo_decorrido", 0)

            print(f"✅ Estado do mapa '{filename}' carregado com sucesso.")
            return estado_deserializado

    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON do arquivo {filename}: {e}")
        return None
    except Exception as e:
        print(f"Erro inesperado ao carregar estado do mapa {filename}: {e}")
        return None

def limpar_todos_os_saves():
    """Remove todos os arquivos de save de qualquer mapa."""
    for save_file in glob.glob("save_mapa_Mundo.json"):
        try:
            os.remove(save_file)
            print(f"Save removido: {save_file}")
        except Exception as e:
            print(f"Erro ao remover {save_file}: {e}")

def limpar_todos_os_player():
    """Remove todos os arquivos de save de qualquer mapa."""
    for save_file in glob.glob("save_player.json"):
        try:
            os.remove(save_file)
            print(f"Save removido: {save_file}")
        except Exception as e:
            print(f"Erro ao remover {save_file}: {e}")

def limpar_todas_caverna():
    for save_file in glob.glob("save_mapa_Caverna - *.json"):
        try:
            os.remove(save_file)
            print(f"Save de caverna removido: {save_file}")
        except Exception as e:
            print(f"Erro ao remover {save_file}: {e}")

def salvar_jogo_global(player, ESTADO_MAPAS, filename="save_global.json"):
    try:
        inventario_nomes = [item.nome for item in player.inventario]
        equipa_nomes = {slot: item.nome if item else None for slot, item in player.equipa.items()}
        player_data = {
            "nome": player.nome,
            "hp_max": player.hp_max,
            "hp": player.hp,
            "atk": player.atk,
            "niv": player.niv,
            "xp_max": player.xp_max,
            "defesa": player.defesa,
            "gold": player.gold,
            "stm_max": player.stm_max,
            "stm": player.stm,
            "intt": player.intt,
            "mn_max": player.mana_max,
            "mana": player.mana,
            "d_m": player.dano_magico,
            "xp": player.xp,
            "aleatorio": player.aleatorio,
            "inventario": inventario_nomes,
            "mana_lit": player.mana_lit,
            "equipa": equipa_nomes,
            "itens_coletaodos": player.itens_coletaodos,
            "rodar": player.rodar_jogo,
            "classes": player.classe,
            "pos_x": player.x_mapa,
            "pos_y": player.y_mapa,
            "mapa_atual": player.mapa_atual,
            "char_skin": player.skin,
            "art_player_nome": player.skin_nome,
            "pontos": player.ponto,
            "andar": player.andar,
            'seed': player.seed,
            'seed_caverna': player.seed_caverna,
            "fov_bonus": player.fov_bonus,
            "tocha_acesa": player.tocha_acesa,
            "mapa_x": player.mapa_x,
            "mapa_y": player.mapa_y,
        }

        mapas_serializados = {}
        for mapa_id, estado in ESTADO_MAPAS.items():
            mapas_serializados[mapa_id] = serializar_para_json({
                "mapa_art": estado["mapa_art"],
                "inimigos_derrotados": estado["inimigos_derrotados"],
                "baus_abertos": estado["baus_abertos"],
                "interacoes": estado.get("interacoes", {}),
                "obstaculos": estado["obstaculos"],
                "cores": estado.get("cores", {}),
                "caracteres_aleatorios": estado.get("caracteres_aleatorios", []),
                "chaves_pegas": estado["chaves_pegas"],
                "abrir_porta": estado["abrir_porta"],
                "plantacoes": estado.get("plantacoes", {}),
                "regeneracoes": estado.get("regeneracoes", {}), 
                "baus_armazenamento": estado.get("baus_armazenamento", {}),
                "tempo_inicio": estado.get("tempo_inicio"),
                "tempo_decorrido": estado.get("tempo_decorrido", 0),
            })

        save_data = {
            "player": player_data,
            "mapas": mapas_serializados
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=4)

        print(f"✅ Jogo global salvo com sucesso em '{filename}'")

    except Exception as e:
        print(f"❌ Erro ao salvar jogo global: {e}")

def carregar_jogo_global(filename="save_global.json"):
    if not os.path.exists(filename):
        print(f"❌ Nenhum save global encontrado em '{filename}'")
        return None, {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            save_data = json.load(f)

        # --- PLAYER ---
        player_data = save_data["player"]
        SKIN_MAP = {
            "necro": ascii.necro,
            "guerreiro": ascii.guerriro,
            "mago": ascii.mago
        }
        skin_nome_carregado = player_data.get("art_player_nome")
        skin_arte_carregada = SKIN_MAP.get(skin_nome_carregado) or None

        player = jogador(
            nome=player_data["nome"],
            hp_max=player_data["hp_max"],
            atk=player_data["atk"],
            niv=player_data["niv"],
            xp_max=player_data["xp_max"],
            defesa=player_data["defesa"],
            gold=player_data["gold"],
            stm_max=player_data["stm_max"],
            intt=player_data["intt"],
            mn_max=player_data["mn_max"],
            d_m=player_data["d_m"],
            art_player=skin_arte_carregada,
            skin=player_data.get("char_skin", "@"),
            skin_nome=skin_nome_carregado,
            mapa_x = player_data["mapa_x"],
            mapa_y = player_data["mapa_y"]
        )

        player.hp = player_data["hp"]
        player.mana = player_data["mana"]
        player.xp = player_data["xp"]
        player.stm = player_data["stm"]
        player.ponto = player_data["pontos"]
        player.andar = player_data["andar"]
        player.fov_bonus = player_data.get("fov_bonus", 0)
        player.tocha_acesa = player_data.get("tocha_acesa", False)
        player.x_mapa = player_data["pos_x"]
        player.seed = player_data['seed']
        player.y_mapa = player_data["pos_y"]
        player.mapa_atual = player_data["mapa_atual"]
        player.inventario = [TODOS_OS_ITENS[n] for n in player_data.get("inventario", []) if n in TODOS_OS_ITENS]
        player.equipa = {slot: TODOS_OS_ITENS[n] if n and n in TODOS_OS_ITENS else None for slot, n in player_data.get("equipa", {}).items()}
        player.mana_lit = player_data.get("mana_lit", [])
        player.itens_coletaodos = player_data.get("itens_coletaodos", {})
        player.rodar_jogo = player_data["rodar"]
        player.classe = player_data["classes"]
        player.seed_caverna = player_data['seed_caverna']

        mapas_carregados = {}
        for mapa_id, estado_serializado in save_data.get("mapas", {}).items():
            estado_deserializado = deserializar_do_json(estado_serializado)
            baus_armazenamento_carregados = estado_deserializado.get("baus_armazenamento", {})
            baus_finais = {}
            for pos_str, lista_itens in baus_armazenamento_carregados.items():
                if isinstance(pos_str, str) and pos_str.startswith('(') and pos_str.endswith(')'):
                    try:
                        pos_tuple = tuple(map(int, pos_str.strip('()').split(', ')))
                    except ValueError:
                        pos_tuple = pos_str
                else:
                    pos_tuple = pos_str
                baus_finais[pos_tuple] = lista_itens

            mapas_carregados[mapa_id] = {
                "mapa_art": estado_deserializado["mapa_art"],
                "inimigos_derrotados": set(tuple(p) for p in estado_deserializado.get("inimigos_derrotados", [])),
                "baus_abertos": set(tuple(p) for p in estado_deserializado.get("baus_abertos", [])),
                "interacoes": estado_deserializado.get("interacoes", {}),
                "obstaculos": set(estado_deserializado.get("obstaculos", [])),
                "cores": estado_deserializado.get("cores", {}),
                "plantacoes": estado_deserializado.get("plantacoes", {}),
                "regeneracoes": estado_deserializado.get("regeneracoes", {}),  # <-- adicionado aqui também
                "explorado": set(tuple(p) for p in estado_deserializado.get("explorado", [])),
                "caracteres_aleatorios": estado_deserializado.get("caracteres_aleatorios", []),
                "chaves_pegas": set(tuple(p) for p in estado_deserializado.get("chaves_pegas", [])),
                "abrir_porta": set(tuple(p) for p in estado_deserializado.get("abrir_porta", [])),
                "baus_armazenamento": baus_finais,
                "tempo_inicio": estado_deserializado.get("tempo_inicio"),
                "tempo_decorrido": estado_deserializado.get("tempo_decorrido", 0),
            }

        print(f"✅ Save global carregado com sucesso de '{filename}'")
        return player, mapas_carregados

    except Exception as e:
        print(f"❌ Erro ao carregar save global: {e}")
        return None, {}

