from quebrar import *
from collections import deque
from maps import *
from inimigo_batalha import *
from eventos_mundo import *
##ARQUIVO DO MAPA
mapas = mini_mapa_()
dialogo = dialogos()
C = Cores()
from pynput import keyboard
import msvcrt

def limpar_buffer_teclas():
    while msvcrt.kbhit():
        msvcrt.getch()

def mini_mapa(x_l, y_l, player, mapas_, camera_w, camera_h, x_p, y_p, menager,cores_custom=None, obstaculos_custom=None, mapa_anterior=None, interacoes_custom=None, mapa_nome=None, ESTADO_GLOBAL_LOAD=None ):
##saves
    ESTADO_MAPAS = ESTADO_GLOBAL_LOAD if ESTADO_GLOBAL_LOAD is not None else {}
    mapa_id = mapa_nome or id(mapas_)
    if mapa_nome:
        player.mapa_atual = mapa_nome

    estado_carregado = ESTADO_MAPAS.get(mapa_id)
    save_filename = f"save_mapa_{mapa_id}.json"

    if estado_carregado is None:
        estado_carregado = carregar_mapa_estado(save_filename)

    if estado_carregado:
        ESTADO_MAPAS[mapa_id] = {
            "mapa_art": estado_carregado["mapa_art"],
            "inimigos_derrotados": estado_carregado.get("inimigos_derrotados", set()),
            "baus_abertos": estado_carregado.get("baus_abertos", set()),
            "interacoes": estado_carregado.get("interacoes", {}),
            "obstaculos": estado_carregado.get("obstaculos", set()),
            "cores": estado_carregado.get("cores", {}),
            "caracteres_aleatorios": estado_carregado.get("caracteres_aleatorios", []),
            "chaves_pegas": estado_carregado.get("chaves_pegas", set()),
            "abrir_porta": estado_carregado.get("abrir_porta", set()),
            "plantacoes": estado_carregado.get("plantacoes", {}),
            "regeneracoes":estado_carregado.get("regeneracoes", {}),
            "baus_armazenamento": estado_carregado.get("baus_armazenamento", {}),
            "tempo_inicio": estado_carregado.get("tempo_inicio"),
            "tempo_decorrido": estado_carregado.get("tempo_decorrido", 0),
        }

        mapa_art = ESTADO_MAPAS[mapa_id]["mapa_art"]
        max_width = max(len(l) for l in mapa_art)
    else:
        raw_map_lines = mapas_
        max_width = max(len(l) for l in raw_map_lines if l.strip())
        mapa_art = [l.ljust(max_width) for l in raw_map_lines if l.strip()]

        ESTADO_MAPAS[mapa_id] = {
            "mapa_art": mapa_art,
            "inimigos_derrotados": set(),
            "baus_abertos": set(),
            "interacoes": {},
            "obstaculos": obstaculos_custom or set(),
            "cores": cores_custom or {},
            "caracteres_aleatorios": [],
            "chaves_pegas": set(),
            "abrir_porta": set(),
            "plantacoes": {},
            "regeneracoes": {},
            "baus_armazenamento": {}, 
        }

    player.x_mapa = x_p
    player.y_mapa = y_p
    OBSTACULOS = obstaculos_custom or ESTADO_MAPAS[mapa_id]["obstaculos"]
    INTERACOES = interacoes_custom or {}
    CORES_DO_ESTADO = ESTADO_MAPAS[mapa_id].get("cores", {})
    CORES = cores_custom or CORES_DO_ESTADO or {}
    plantacoes_ativas = ESTADO_MAPAS[mapa_id].get("plantacoes", {})
    for (px, py), dados in plantacoes_ativas.items():
        if mapa_art[py][px] in ('*', '=', "1", "7"): 
            cor_plantio = dados.get("cor")
            if cor_plantio:
                CORES[(px, py)] = cor_plantio
    interacoes_contagem = {}
    feedback_message = ""
    MAP_WIDTH = max_width
    MAP_HEIGHT = len(mapa_art)
    CAMERA_WIDTH = camera_w
    CAMERA_HEIGHT = camera_h
    tempo_decorrido = 0
    if estado_carregado:
        tempo_decorrido = estado_carregado.get("tempo_decorrido", 0)
    if not hasattr(player, "tempo_inicio_global"):
        player.tempo_inicio_global = time.time()

    TEMPO_TOTAL_DIA = 15 * 60
    PERIODOS = {
        "dia": (0, TEMPO_TOTAL_DIA / 3),
        "tarde": (TEMPO_TOTAL_DIA / 3, 2 * TEMPO_TOTAL_DIA / 3),
        "noite": (2 * TEMPO_TOTAL_DIA / 3, TEMPO_TOTAL_DIA)
    }

    tempo_atual = (time.time() - player.tempo_inicio_global) % TEMPO_TOTAL_DIA

    if PERIODOS["dia"][0] <= tempo_atual < PERIODOS["dia"][1]:
        periodo_atual = "dia"
    elif PERIODOS["tarde"][0] <= tempo_atual < PERIODOS["tarde"][1]:
        periodo_atual = "tarde"
    else:
        periodo_atual = "noite"

    if "plantacoes" not in ESTADO_MAPAS[mapa_id]:
        ESTADO_MAPAS[mapa_id]["plantacoes"] = {}

    camera_x = max(0, player.x_mapa - CAMERA_WIDTH // 2)
    camera_y = max(0, player.y_mapa - CAMERA_HEIGHT // 2)

    def atualizar_camera():
        nonlocal camera_x, camera_y
        camera_x = max(0, min(MAP_WIDTH - CAMERA_WIDTH, player.x_mapa - CAMERA_WIDTH // 2))
        camera_y = max(0, min(MAP_HEIGHT - CAMERA_HEIGHT, player.y_mapa - CAMERA_HEIGHT // 2))

    clear()
    def calcular_fov(player, mapa_largura, mapa_altura, raio_fov):
        visiveis = set()
        for dy in range(-raio_fov, raio_fov + 1):
            for dx in range(-raio_fov, raio_fov + 1):
                x = player.x_mapa + dx
                y = player.y_mapa + dy
                if 0 <= x < mapa_largura and 0 <= y < mapa_altura:
                    if dx*dx + dy*dy <= raio_fov*raio_fov:
                        visiveis.add((x, y))
        return visiveis
##fim
    while True:
##plantas e outras funções
        if player.tocha_acesa:
            agora = time.time()
            delta = agora - player.tocha_ultima_contagem
            player.tocha_ultima_contagem = agora

            player.tocha_duracao -= delta

            if player.tocha_duracao <= 0:
                feedback_message = "Sua tocha apagou."
                remover_equipamento(player, "m_ter")

        if player.hp <= 0:
            player_carregado, mapas_carregados = carregar_jogo_global(filename="save_global.json")
            if player_carregado:
                player = player_carregado
                ESTADO_MAPAS = mapas_carregados
                estado_mapa_salvo = ESTADO_MAPAS.get(player.mapa_atual)
                if estado_mapa_salvo:
                    mapa_art_para_load = estado_mapa_salvo["mapa_art"]
                    cores_custom = estado_mapa_salvo.get("cores", None)
                    obstaculos_custom = estado_mapa_salvo.get("obstaculos", None)
                else:
                    limpar_todos_os_saves()
                    limpar_todos_os_player()
                    config = mapa_procedural(nome=player.mapa_atual, largura=250, altura=10, seed=player.seed)
                    mapa_art_para_load = config["mapa"]
                    cores_custom = config.get("cores", None)
                    obstaculos_custom = config.get("obstaculos", None)
                x_p_load = player.x_mapa
                y_p_load = player.y_mapa
                mini_mapa(
                    x_l=0,
                    y_l=0,
                    player=player,
                    mapas_=mapa_art_para_load,
                    camera_w=35,
                    camera_h=15,
                    x_p=x_p_load,
                    y_p=y_p_load,
                    menager="",
                    mapa_nome=player.mapa_atual,
                    cores_custom=cores_custom,
                    obstaculos_custom=obstaculos_custom,
                    ESTADO_GLOBAL_LOAD=mapas_carregados
                )
                status_ale_menor = random.choice('atk', 'def', 'atk/mn', 'int')
                if status_ale_menor == 'atk':
                    player.atk -= 2
                elif status_ale_menor == 'def':
                    player.defesa -= 2
                elif status_ale_menor == 'atk/mn':
                    player.d_m -= 2
                elif status_ale_menor == 'int':
                    player.intt -= 2
            else:
                exit()
        
        tempo_atual = (time.time() - player.tempo_inicio_global) % TEMPO_TOTAL_DIA

        if PERIODOS["dia"][0] <= tempo_atual < PERIODOS["dia"][1]:
            periodo_atual = "dia"
        elif PERIODOS["tarde"][0] <= tempo_atual < PERIODOS["tarde"][1]:
            periodo_atual = "tarde"
        else:
            periodo_atual = "noite"
        
        regeneracoes = ESTADO_MAPAS[mapa_id].get("regeneracoes", {})
        tempo_atual = time.time()
        
        for (px, py), dados in list(regeneracoes.items()):
            tipo_original = dados.get("tipo_original")
            tempo_passado = tempo_atual - dados["tempo_inicio"]

            # Se o tile NO MOMENTO não for mais um 'x' ou '7', não regenera!
            if mapa_art[py][px] != 'x' and mapa_art[py][px] != '7':
                del regeneracoes[(px, py)]
                continue

            if tempo_passado >= dados["tempo_regeneracao"]:
                substituir_caractere(mapa_art, px, py, tipo_original)
                del regeneracoes[(px, py)]

        plantacoes = ESTADO_MAPAS[mapa_id].get("plantacoes", {})
        tempo_atual = time.time()
        for (px, py), dados in list(plantacoes.items()):
            tempo_passado = tempo_atual - dados["tempo_plantio"]
            tempo_crescimento = dados.get("tempo_crescimento", 10)
            tipo = dados.get("item", "desconhecido")

            if tempo_passado >= tempo_crescimento and mapa_art[py][px] in ('*', "1", ','):
                if tipo == "trigo":
                    substituir_caractere(mapa_art, px, py, "‼")
                elif tipo == "milho":
                    substituir_caractere(mapa_art, px, py, "¥")
                elif tipo == 'abobora':
                    substituir_caractere(mapa_art, px, py, '0')
                elif tipo == 'arvore':
                    substituir_caractere(mapa_art, px, py, '♣')
                elif tipo == 'arbusto':
                    substituir_caractere(mapa_art, px, py, '♠')
                elif tipo == 'terra':
                    substituir_caractere(mapa_art, px, py, '.')
                elif tipo == 'morrango':
                    substituir_caractere(mapa_art, px,py, "♀")
                elif tipo == 'algodão':
                    substituir_caractere(mapa_art, px,py, "☼")
                else:
                    substituir_caractere(mapa_art, px, py, "¶")
                
                del plantacoes[(px, py)]
                salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])

        inimigo_chars = []
        mobs_chars = []
        boss = []
        def bau(pos_bau):
            if pos_bau in ESTADO_MAPAS[mapa_id]["baus_abertos"]:
                return
            ESTADO_MAPAS[mapa_id]["baus_abertos"].add(pos_bau)
            itens = ['Suco', 'Poção de Cura', 'Elixir', 'Moedas']
            selec = random.choice(itens)
            if selec == 'Moedas':
                quantia = (player.niv * 10)
                moedas = f"Você Encontrou um Baú\nVocê conseguiu um {selec}\nquantidade ({quantia})x"
                falas(moedas)
                quantia += player.gold
            else:
                item_ = f"Você Encontrou um Baú\nVocê conseguiu um {selec}"
                falas(item_)
                player.inventario.append(TODOS_OS_ITENS[f"{selec}"])
            bx, by = pos_bau
            linha_antiga = mapa_art[by]
            mapa_art[by] = linha_antiga[:bx] + '.' + linha_antiga[bx + 1:]
            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])

        def chave(pos_chave):
            if pos_chave in ESTADO_MAPAS[mapa_id]["chaves_pegas"]:
                return
            ESTADO_MAPAS[mapa_id]["chaves_pegas"].add(pos_chave)

            chave_item = TODOS_OS_ITENS.get('Chave')
            if chave_item:
                player.inventario.append(chave_item)
            else:
                feedback_message = "Item 'Chave' não encontrado em TODOS_OS_ITENS."
                return
            feedback_message = "Você Encontrou uma Chave"

            bx, by = pos_chave
            linha_antiga = mapa_art[by]
            mapa_art[by] = linha_antiga[:bx] + '.' + linha_antiga[bx + 1:]

            ESTADO_MAPAS[mapa_id]["mapa_art"] = mapa_art
            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])

        def abrir_portas(pos_porta):
            if pos_porta in ESTADO_MAPAS[mapa_id]["abrir_porta"]:
                return

            possui_chave = any(item.nome == 'Chave' for item in player.inventario)
            if possui_chave:
                ESTADO_MAPAS[mapa_id]["abrir_porta"].add(pos_porta)
                bx, by = pos_porta
                linha_antiga = mapa_art[by]
                mapa_art[by] = linha_antiga[:bx] + '\\' + linha_antiga[bx + 1:]

                for i, item in enumerate(player.inventario):
                    if item.nome == 'Chave':
                        del player.inventario[i]
                        break

                ESTADO_MAPAS[mapa_id]["mapa_art"] = mapa_art
                salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
            else:
                feedback_message= "Você precisa de uma chave para abrir esta porta."

        def falas(menager, velocidade=0.03):
            max_width = 35 
            lines = menager.split('\n')
            wrapped_lines = []

            for line in lines:
                wrapped_lines.extend(textwrap.wrap(line, max_width))

            draw_window(
                term,
                x=x_l + CAMERA_WIDTH + 2,
                y=y_l,
                width=35,
                height=15,
                text_content=''
            )

            for i, line in enumerate(wrapped_lines):
                with term.location(x_l + CAMERA_WIDTH + 3, y_l + 1 + i):
                    for char in line:
                        print(char, end='', flush=True)
                        time.sleep(velocidade)

            with term.location(x_l + CAMERA_WIDTH + 2, y_l + 15):
                input(term.bold_cyan("[Pressione Enter para continuar]"))
            clear()

        def bau_armazenamento(pos_bau):
            ESTADO = ESTADO_MAPAS[mapa_id]
            baus_armazenamento = ESTADO.setdefault("baus_armazenamento", {})
            bau_inventario = baus_armazenamento.setdefault(pos_bau, [])

            def exibir_telas_bau():
                clear()
                contagem_player = Counter(item.nome for item in player.inventario)
                conteudo_player = []
                for i, item_nome in enumerate(sorted(contagem_player.keys())):
                    quantidade = contagem_player[item_nome]
                    conteudo_player.append(f"{i+1}. {item_nome} ({quantidade}x)")
                
                conteudo_player_str = "\n".join(conteudo_player) or "Inventário vazio."

                draw_window(
                    term, 
                    x=x_l - 35, 
                    y=y_l, 
                    width=30, 
                    height=15, 
                    title=f"Inventário de {player.nome}",
                    text_content=conteudo_player_str
                )
                menu_texto = term.bold_yellow("[1]") + " Guardar\n" + \
                             term.bold_yellow("[2]") + " Pegar\n" + \
                             term.bold_yellow("[3]") + " Sair"
                draw_window(
                    term, 
                    x=x_l, 
                    y=y_l, 
                    width=30, 
                    height=15, 
                    title=term.bold_cyan("Baú de Armazenamento"),
                    text_content=menu_texto
                )
                contagem_bau = Counter(item.nome for item in bau_inventario)
                conteudo_bau = []
                for i, item_nome in enumerate(sorted(contagem_bau.keys())):
                    quantidade = contagem_bau[item_nome]
                    conteudo_bau.append(f"{i+1}. {item_nome} ({quantidade}x)")
                
                conteudo_bau_str = "\n".join(conteudo_bau) or "Baú vazio."

                draw_window(
                    term, 
                    x=x_l + 35, 
                    y=y_l, 
                    width=30, 
                    height=15, 
                    title=term.bold_green("Itens do Baú"),
                    text_content=conteudo_bau_str
                )

            def processar_transferencia(origem_lista, destino_lista, titulo_escolha):
                """Gerencia a transferência de itens (Guardar/Pegar) com controle exato de quantidades."""
                if not origem_lista:
                    falas(f"A lista de origem ({titulo_escolha}) está vazia.")
                    return

                clear()
                contagem_origem = Counter(item.nome for item in origem_lista)
                itens_unicos = sorted(contagem_origem.keys())
                mapeamento_escolha = {i + 1: item_nome for i, item_nome in enumerate(itens_unicos)}

                # Mostra os itens disponíveis
                linhas_display = [
                    f"{i}. {nome} ({contagem_origem[nome]}x)"
                    for i, nome in mapeamento_escolha.items()
                ]
                draw_window(
                    term,
                    x=x_l,
                    y=y_l,
                    width=40,
                    height=15,
                    title=titulo_escolha,
                    text_content="\n".join(linhas_display)
                )

                with term.location(x=x_l, y=y_l + 16):
                    entrada = input(term.bold("Digite [Nº Item] [Quantia] ou 0 para cancelar: ")).strip().split()

                if not entrada or entrada[0].upper() == '0':
                    return

                # Processa a entrada
                try:
                    idx_escolhido = int(entrada[0])
                    quantia_desejada = int(entrada[1]) if len(entrada) > 1 else 1
                except ValueError:
                    falas("Entrada inválida. Use o formato: [Nº Item] [Quantia].")
                    return

                if idx_escolhido not in mapeamento_escolha:
                    falas("Número de item inválido.")
                    return

                item_nome_selecionado = mapeamento_escolha[idx_escolhido]
                quantidade_disponivel = contagem_origem[item_nome_selecionado]

                if quantia_desejada <= 0:
                    falas("A quantidade deve ser maior que zero.")
                    return
                if quantia_desejada > quantidade_disponivel:
                    falas(f"Você só tem {quantidade_disponivel}x de {item_nome_selecionado}.")
                    return

                # Transfere exatamente a quantia pedida
                itens_transferidos = 0
                novos_itens = []
                for item_obj in origem_lista[:]:  # cópia para evitar modificação durante iteração
                    if item_obj.nome == item_nome_selecionado:
                        destino_lista.append(item_obj)
                        origem_lista.remove(item_obj)
                        itens_transferidos += 1
                        if itens_transferidos >= quantia_desejada:
                            break

                if itens_transferidos > 0:
                    acao = "guardados no baú" if destino_lista is bau_inventario else "retirados do baú"
                    falas(f"{itens_transferidos}x {item_nome_selecionado} foram {acao}.")
                    salvar_mapa_estado(save_filename, mapa_id, ESTADO)
                else:
                    falas("Nenhum item foi transferido.")

            while True:
                exibir_telas_bau()
                
                with term.location(x=x_l, y=y_l + 16):
                    escolha = input(term.bold_cyan("Escolha uma opção: ")).strip()

                if escolha == "1":  # Guardar
                    processar_transferencia(
                        player.inventario, 
                        bau_inventario, 
                        "Escolha o item para guardar no Baú:"
                    )

                elif escolha == "2":  # Pegar
                    processar_transferencia(
                        bau_inventario, 
                        player.inventario, 
                        "Escolha o item para pegar do Baú:"
                    )

                elif escolha == "3":  # Sair
                    break
                    
                else:
                    falas("Opção inválida. Escolha 1, 2 ou 3.")
##fim
        atualizar_camera()

        def render_frame(term, x_l, y_l, mapa_art, player, camera_x, camera_y, CAMERA_WIDTH, CAMERA_HEIGHT, menager, feedback_message, cores, raio_fov=5, obstaculos=None):
            frame = []
            frame.append(term.home)

            if obstaculos is None:
                obstaculos = set()

            # -------------------
            # Calcula FOV
            # -------------------
            visiveis = set()
            altura = len(mapa_art)
            largura = len(mapa_art[0])

            aspect = 0.5  # ajuste conforme proporção do terminal

            for dy in range(-raio_fov, raio_fov + 1):
                for dx in range(-raio_fov, raio_fov + 1):
                    x = player.x_mapa + dx
                    y = player.y_mapa + dy
                    if 0 <= x < largura and 0 <= y < altura:
                        dist = (dx*dx) + (dy*dy) / (aspect*aspect)
                        if dist <= raio_fov * raio_fov:
                            visiveis.add((x, y))

            # -------------------
            # Janela do Mapa
            # -------------------
            frame.append(term.move_xy(x_l, y_l) + "╔" + "═" * CAMERA_WIDTH + "╗")
            for j in range(CAMERA_HEIGHT):
                y_terminal = y_l + j + 1
                if camera_y + j >= len(mapa_art):
                    linha_raw = " " * CAMERA_WIDTH
                else:
                    linha_raw = mapa_art[camera_y + j][camera_x:camera_x + CAMERA_WIDTH]
                linha_raw = linha_raw.ljust(CAMERA_WIDTH)

                linha = []
                for i, ch in enumerate(linha_raw):
                    mapa_x = camera_x + i
                    mapa_y = camera_y + j
                    if (mapa_x, mapa_y) not in visiveis:
                        linha.append(term.gray("·"))  # célula fora do FOV
                    elif mapa_y == player.y_mapa and mapa_x == player.x_mapa:
                        linha.append(term.bold_yellow(player.skin))
                    else:
                        linha.append(CORES.get(ch, '') + ch + term.normal)
                linha = "".join(linha)
                frame.append(term.move_xy(x_l, y_terminal) + "║" + linha + "║")
            frame.append(term.move_xy(x_l, y_l + CAMERA_HEIGHT + 1) + "╚" + "═" * CAMERA_WIDTH + "╝")

            # -------------------
            # Janela do Painel de Status
            # -------------------
            painel_width = 20
            painel_height = 14
            painel_x = x_l + CAMERA_WIDTH + 2  # lateral ao mapa
            painel_y = y_l

            frame.append(term.move_xy(painel_x, painel_y) + "╔" + "═" * painel_width + "╗")
            for j in range(painel_height):
                y_terminal = painel_y + j + 1
                if j == 0:
                    painel_text = " DIREÇÃO".ljust(painel_width)
                elif j == 1:
                    linha_cima = " " * ((painel_width - 1)//2) + "▲" + " " * (painel_width - (painel_width - 1)//2 - 1)
                    linha_cima = term.green(linha_cima) if player.direcao == "cima" else term.red(linha_cima)
                    painel_text = linha_cima
                elif j == 2:
                    linha_baixo = "◄ ▼ ►".center(painel_width)
                    linha_baixo = linha_baixo.replace("◄", term.green("◄") if player.direcao == "esquerda" else term.red("◄"))
                    linha_baixo = linha_baixo.replace("▼", term.green("▼") if player.direcao == "baixo" else term.red("▼"))
                    linha_baixo = linha_baixo.replace("►", term.green("►") if player.direcao == "direita" else term.red("►"))
                    painel_text = linha_baixo
                elif j == 3:
                    painel_text = f"Nome: [{player.nome}]".ljust(painel_width)
                elif j == 4:
                    painel_text = f"HP[{player.hp_max}/{player.hp}]".ljust(painel_width)
                elif j == 5:
                    painel_text = f"STM[{player.stm_max}/{player.stm}]".ljust(painel_width)
                elif j == 6:
                    painel_text = f"MG[{player.mana_max}/{player.mana}]".ljust(painel_width)
                elif j == 7:
                    painel_text = f"ATK[{player.atk}]".ljust(painel_width)
                elif j == 8:
                    painel_text = f"DEF[{player.defesa}]".ljust(painel_width)
                elif j == 9:
                    painel_text = f"INT[{player.intt}]".ljust(painel_width)
                elif j == 10:
                    painel_text = f"MA[{player.dano_magico}]".ljust(painel_width)
                elif j == 11:
                    painel_text = f"X[{player.x_mapa}] Y[{player.y_mapa}]".ljust(painel_width)
                elif j == 12:
                    painel_text = f"Tempo".ljust(painel_width)
                elif j == 13:
                    painel_text = f"{periodo_atual}".ljust(painel_width)
                else:
                    painel_text = " " * painel_width

                frame.append(term.move_xy(painel_x, y_terminal) + "║" + painel_text + "║")
            frame.append(term.move_xy(painel_x, painel_y + painel_height + 1) + "╚" + "═" * painel_width + "╝")

            # -------------------
            # Mensagens
            # -------------------
            y_menager = y_l + CAMERA_HEIGHT + 2
            frame.append(term.move_xy(x_l, y_menager) + " " * (CAMERA_WIDTH + painel_width + 1))
            frame.append(term.move_xy(x_l, y_menager) + menager)

            if feedback_message:
                y_feedback = y_menager + 1
                frame.append(term.move_xy(x_l, y_feedback) + " " * (CAMERA_WIDTH + painel_width + 1))
                frame.append(term.move_xy(x_l, y_feedback) + term.red(feedback_message))

            print("".join(frame), end="")

        item_equipado = player.equipa.get("m_ter")
        fov_bonus = 0
        if (item_equipado and 
            item_equipado.nome.lower() == "tocha" and 
            player.tocha_acesa and 
            player.tocha_duracao > 0):
            fov_bonus = 5
        else:
            fov_bonus = -3  # escuro
        if player.mapa_atual.startswith('Caverna'):
            raio_fov = 7
        elif player.mapa_atual == 'Mundo':
            if periodo_atual in ['tarde', 'dia']:
                raio_fov = 30
            elif periodo_atual == 'noite':
                raio_fov = 20
        else:
            raio_fov = 30

        raio_fov += fov_bonus
        raio_fov = max(1, raio_fov)

        render_frame(term, x_l, y_l, mapa_art, player,camera_x, camera_y, CAMERA_WIDTH, CAMERA_HEIGHT,menager, feedback_message, CORES,raio_fov=raio_fov)

        def verificar_proximidade_cruz(x, y, mapa_art):
            direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            proximidades = []
            for dx, dy in direcoes:
                nx, ny = x + dx, y + dy
                if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                    ch = mapa_art[ny][nx]
                    proximidades.append((nx, ny, ch))
            return proximidades

        proximos = verificar_proximidade_cruz(player.x_mapa, player.y_mapa, mapa_art)

        def verificar_frente(x, y, direcao, mapa_art):
            dir_map = {
                "cima": (0, -1),
                "baixo": (0, 1),
                "esquerda": (-1, 0),
                "direita": (1, 0)
            }
            dx, dy = dir_map[direcao]
            nx, ny = x + dx, y + dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                return [(nx, ny, mapa_art[ny][nx])]
            return []

        for px, py, ch in proximos:
            if ch == "B":
                if (px, py) not in ESTADO_MAPAS[mapa_id]["baus_abertos"]:
                    bau((px, py))
                    break
            elif ch == 'K':
                if (px, py) not in ESTADO_MAPAS[mapa_id]["chaves_pegas"]:
                    chave((px, py))
                    break
            if ch == '/':
                if (px, py) not in ESTADO_MAPAS[mapa_id]["abrir_porta"]:
                    abrir_portas((px, py))
                    break
            if ch in ["G", "F"]:
                if ch == "G":
                    status = esqueleto(player_b=player, art=ascii)
                    inimigo_b = inimigo(
                        nome=status['nome'],
                        hp_max = status["hp"],
                        atk=status['atk'],
                        niv=status['niv'],
                        xp=status['xp'],
                        defesa=status['defesa'],
                        gold = status['gold'],
                        atk1 = status['atk_1'],
                        atk2= status['atk_2'],
                        art_ascii=status['art']
                    )
                elif ch == "F":
                    status = zumbi(player_b=player, art=ascii)
                    inimigo_b = inimigo(
                        nome=status['nome'],
                        hp_max = status["hp"],
                        atk=status['atk'],
                        niv=status['niv'],
                        xp=status['xp'],
                        defesa=status['defesa'],
                        gold = status['gold'],
                        atk1 = status['atk_1'],
                        atk2= status['atk_2'],
                        art_ascii=status['art']
                    )
                batalha(player_b=player, inimigo_b=inimigo_b)
                if inimigo_b.hp <= 0:
                    ESTADO_MAPAS[mapa_id]["inimigos_derrotados"].add((px, py))
                    linha_antiga = mapa_art[py]
                    mapa_art[py] = linha_antiga[:px] + '.' + linha_antiga[px + 1:]
                    salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])

        if player.mapa_atual == f'Caverna - [{player.andar}]':
            processar_eventos_caverna(player, mapa_art, periodo_atual, ESTADO_MAPAS, mapa_id, save_filename)
            
        if player.mapa_atual == 'Mundo':
            processar_eventos_mundo(player, mapa_art, periodo_atual, ESTADO_MAPAS, mapa_id, save_filename)

        with term.location(x=x_l, y=CAMERA_HEIGHT + y_l + 2):
            pressed_key = None

            def on_press(key):
                nonlocal pressed_key
                try:
                    pressed_key = key.char.lower()
                except AttributeError:
                    if key == keyboard.Key.up:
                        pressed_key = "Keyup"
                    elif key == keyboard.Key.down:
                        pressed_key = "Keydown"
                    elif key == keyboard.Key.left:
                        pressed_key = "Keyleft"
                    elif key == keyboard.Key.right:
                        pressed_key = "Keyright"
                    else:
                        pressed_key = None
                return False

            with keyboard.Listener(on_press=on_press) as listener:
                listener.join()

            movi = pressed_key
            if movi is None:
                continue

            direcoes = {
                "w": (0, -1),
                "s": (0, 1),
                "a": (-1, 0),
                "d": (1, 0),
            }

            tecla_para_direcao = {
                "w": "cima",
                "s": "baixo",
                "a": "esquerda",
                "d": "direita",
            }
            cetinas = {
            "Keyup": "cima",
            "Keydown": "baixo",
            "Keyright": "direita",
            "Keyleft": "esquerda"

            }

            # Movimento
            if movi in direcoes:
                if movi in direcoes:
                    dx, dy = direcoes[movi]
                player.direcao = tecla_para_direcao[movi]

                passo_x = player.x_mapa + dx
                passo_y = player.y_mapa + dy

                if 0 <= passo_x < MAP_WIDTH and 0 <= passo_y < MAP_HEIGHT:
                    caractere = mapa_art[passo_y][passo_x]
                    if caractere not in OBSTACULOS and caractere not in inimigo_chars:
                        player.x_mapa = passo_x
                        player.y_mapa = passo_y
                        feedback_message = f"Movendo para {player.direcao}"
                    else:
                        feedback_message = f"Movimento bloqueado por: {caractere}"
                else:
                    feedback_message = "Limite do mapa atingido."

            else:
                limpar_buffer_teclas()
                px, py = player.x_mapa, player.y_mapa
                caractere_atual = mapa_art[py][px]

                if movi == "i":
                    player.inventario_(x=x_l + CAMERA_WIDTH + 2, y=y_l, werd=40, herd=0, batalha=False)
                    clear()
                    feedback_message = "Inventário fechado."

                elif movi in cetinas:
                    player.direcao = cetinas[movi]

                elif movi == 'h':
                    def tutorail():
                        clear()
                        penis = '''
[W, A, S, D]: Mover 1 passo.
[I]: Abrir Inventário.
[X]: Interagir (Bau, Conversar, Entrar em Buraco 'Caverna' se equipado).
[R]: Quebrar Blocos (Requer item).
[E]: Cavar Buraco ou Arar a Terra (Requer pá ou enxada equipado).
[U]: Melhorar Status (Upgrade).
[J]: Sair da Caverna/Pular.
[Q]: Ver Status Equipados (Equip).
[V]: Salvar Jogo.
[K]: Sair do Jogo.
[1-9]: Usar Item do Slot Rápido (Se equipado).
                        '''
                        draw_window(term, x=x_l, y=y_l, width=90, height=27, text_content=penis)
                        with term.location(x=x_l+1, y= 22):
                            input("Pressione ENTER para continuar...") # Usar input() aqui é OK para comandos que pausam o jogo
                        clear()
                    tutorail()
                    feedback_message = "Menu de ajuda fechado."
                    
                elif movi == "k":
                    exit()
                    
                elif movi == "u": 
                    player.up(x=x_l + CAMERA_WIDTH + 2, y=y_l, werd=40, herd=17, x_i = 1)
                    clear()
                    
                elif movi == 'j':
                    if player.mapa_atual == "Mundo":
                        pass
                    else:
                        player.andar = 0
                        salvar_jogo_player(player)
                        config_player = carregar_jogo_player()
                        if hasattr(player, "retorno"):
                            ret_x, ret_y = player.retorno
                        else:
                            feedback_message = "Erro: nenhuma posição de W salva!"
                            continue
                        if config_player is None:
                            feedback_message = "Erro ao carregar o save para retornar."
                            continue

                        config = mapa_procedural(
                            nome="Mundo",
                            largura=player.mapa_x,
                            altura=player.mapa_y,
                            seed=config_player.seed
                        )

                        mini_mapa(
                            x_l=0, y_l=0,
                            player=config_player,
                            mapas_=config["mapa"],
                            camera_w=50,
                            camera_h=25,
                            x_p=ret_x,      # ← Volta ao X do W
                            y_p=ret_y,      # ← Volta ao Y do W
                            menager="Voltando pelo portal W",
                            cores_custom=config["cores"],
                            obstaculos_custom=config["obstaculos"],
                            mapa_nome=config["nome"]
                        )

                        break

                elif movi == 'r':
                    if player.mapa_atual == "Mundo" or player.mapa_atual == "Caverna":
                        frente = verificar_frente(player.x_mapa, player.y_mapa, player.direcao, mapa_art)
                        for px, py, ch in frente:
                            feedback_message = interagir_com_objeto(
                                px, py, ch, player, mapa_art, mapa_id, interacoes_contagem,
                                ESTADO_MAPAS, TODOS_OS_ITENS, save_filename, mapas_,
                                salvar_mapa_estado, substituir_caractere
                            )
                            if feedback_message:
                                break
                    else:
                        pass

                elif movi == "o":
                    if player.mapa_atual == "Mundo" or player.mapa_atual == "Caverna":
                        chao_atual = mapa_art[player.y_mapa][player.x_mapa]
                        item_equipado = player.equipa.get("m_seg")
                        # Lógica de Arar
                        if chao_atual == "." and item_equipado and item_equipado.nome.lower() == "enchada":
                            feedback_message = 'Você arou o chão'
                            substituir_caractere(mapa_art, player.x_mapa, player.y_mapa, '=')
                            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                        
                        # Lógica de Cavar (Buraco/Caverna)
                        elif chao_atual == '.' and item_equipado and item_equipado.nome.lower() == 'pá':
                            tipo = 'terra'
                            tempo_crescimento = 50
                            substituir_caractere(mapa_art, player.x_mapa, player.y_mapa, ",")
                            ESTADO_MAPAS[mapa_id]["plantacoes"][(player.x_mapa, player.y_mapa)] = {
                            "item": tipo,
                            "tempo_plantio": time.time(),
                            "tempo_crescimento": tempo_crescimento,}
                            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                            itens_ale = random.choice(["Semente/Trigo", "Semente/Milho", "Semente/Algodão",'Nada','Nada','Nada',
                                                        'Nada','Nada','Nada','Nada'])
                            if itens_ale == 'Nada':
                                pass
                            else:
                                player.inventario.append(TODOS_OS_ITENS[f"{itens_ale}"])
                                feedback_message = f'Você cavou um buraco conseguio um {itens_ale}'
                        
                        # Feedback de Buraco/Terra Arada
                        elif chao_atual == ',':
                            feedback_message = 'Você já existe um buraco aqui'
                        elif chao_atual == '=':
                            feedback_message = 'Você transformou a terra arada em terra normal'
                            substituir_caractere(mapa_art, player.x_mapa, player.y_mapa, ".")

                        # Lógica de Pesca
                        frente = verificar_frente(player.x_mapa, player.y_mapa, player.direcao, mapa_art)
                        for px, py, ch in frente:
                            if ch == "~":
                                if item_equipado and item_equipado.nome.lower() == "vara de pesca":
                                    # Esta pausa com time.sleep() irá congelar o programa, mas é o que o código original faz.
                                    # Em um jogo de blessed, você usaria um contador dentro do loop principal.
                                    feedback_message = "Você jogou uma isca..."
                                    time.sleep(2)
                                    feedback_message = "Alguma coisa foi pegar!!"
                                    time.sleep(2)
                                    pesca = random.choice(["Tilapia", "Nada", "Salmão", "Nada", "Camarão", "Nada"])
                                    if pesca == "Nada":
                                        feedback_message = "Sem sorte não veio nada"
                                        player.stm -= 5
                                    else:
                                        feedback_message = f"Você pescou um {pesca}"
                                        player.inventario.append(TODOS_OS_ITENS[f"{pesca}"])
                                        player.stm -= 5
                                break
                    else:
                        pass

                elif movi == 'x':
                    if caractere_atual == ',':
                        if player.mapa_atual == "Mundo":
                            posicoes_W = localizar_caractere(mapa_art, ",")
                            w_x, w_y = posicoes_W[0]
                            player.retorno= (w_x, w_y) 
                            player.andar += 1
                            limpar_todas_caverna()
                            ale_seed = random.randint(1, 9999)
                            player.seed_caverna = ale_seed
                            config = mapa_caverna(nome=f"Caverna - [{player.andar}]", largura=player.mapa_x, altura=player.mapa_y, player_b=player,seed=player.seed_caverna)
                            mini_mapa(
                                x_l=0, y_l=0,
                                player=player,
                                mapas_=config["mapa"],
                                camera_w=50, camera_h=25,
                                x_p=player.x_mapa, y_p=player.y_mapa,
                                menager="",
                                cores_custom=config["cores"],
                                obstaculos_custom=config["obstaculos"],
                                mapa_nome=config["nome"]
                            )
                            break
                        else:
                            player.andar += 1
                            limpar_todas_caverna()
                            ale_seed = random.randint(1, 9999)
                            player.seed_caverna = ale_seed
                            config = mapa_caverna(nome=f"Caverna - [{player.andar}]", largura=player.mapa_x, altura=player.mapa_y, player_b=player,seed=player.seed_caverna)
                            mini_mapa(
                                x_l=0, y_l=0,
                                player=player,
                                mapas_=config["mapa"],
                                camera_w=50, camera_h=25,
                                x_p=player.x_mapa, y_p=player.y_mapa,
                                menager="",
                                cores_custom=config["cores"],
                                obstaculos_custom=config["obstaculos"],
                                mapa_nome=config["nome"]
                            )
                            break
        
                    proximos = verificar_frente(player.x_mapa, player.y_mapa, player.direcao, mapa_art)
                    for px, py, ch in proximos:
                        if ch == "$":
                            bau_armazenamento((px, py))
                            break
                        if ch == 'C':
                            player.craft(x=x_l, y=y_l, werd=CAMERA_WIDTH + 10, herd=CAMERA_HEIGHT + 2)
                            break
                        if ch == '%':
                            player.forja(x=x_l, y=y_l, werd=CAMERA_WIDTH + 10, herd=CAMERA_HEIGHT + 2)
                            break
                        if ch == 'x': # Arbusto Regenerativo
                            pos = (px, py)
                            reg = ESTADO_MAPAS[mapa_id].get("regeneracoes", {}).get(pos) 
                            if reg and time.time() - reg["tempo_inicio"] < reg["tempo_regeneracao"]:
                                feedback_message = "O arbusto ainda não deu frutos novamente."
                            else:
                                substituir_caractere(mapa_art, px, py, '*') # Mudar para o caractere de fruta
                                ESTADO_MAPAS[mapa_id]["regeneracoes"].pop(pos, None)
                                feedback_message = "O arbusto voltou a dar frutos! (Use 'R' para colher)"
                            break
                        if ch == 'P': # Padre
                            if player.boss['Suny'] == False:
                                padres = localizar_caractere(mapa_art, '@')
                                fala = random.choice([dialogo.padre_1, dialogo.padre_2, dialogo.padre_3])
                                falas(fala)
                            else:
                                falas(dialogo.padre_4)
                                player.aprender_magias(term ,x_menu=x_l + CAMERA_WIDTH + 5, y_menu=y_l, wend=CAMERA_WIDTH + 5, herd=CAMERA_HEIGHT)
                            break
                        if ch == '&': # Aldeão
                            if player.boss['Suny']== False:
                                fala = random.choice([dialogo.aldao_1, dialogo.aldao_2,dialogo.aldao_3])
                                falas(fala)
                            else:
                                fala = random.choice([dialogo.aldao_1, dialogo.aldao_2,dialogo.aldao_3,dialogo.aldao_4,dialogo.aldao_5])
                                falas(fala)
                                posicoes_alvo = localizar_caractere(mapa_art, '@')
                                if posicoes_alvo:
                                    x_alvo, y_alvo = posicoes_alvo[0]
                                    feedback_message = f"O Padre Argos está localizado em X: {x_alvo}, Y: {y_alvo}!"
                                else:
                                    pass
                            break
                        if ch == 'V': # Loja
                            player.gerenciar_loja(x=0, y=0, largura=30)
                            break
                    else:
                        feedback_message = "Nada para interagir na sua frente."
                
                elif movi == "f":
                    item_equipado_1 = player.equipa.get("m_ter")

                    if item_equipado_1 and item_equipado.nome.lower() == "tocha":
                        if not player.tocha_acesa:
                            feedback_message = "Você acendeu uma tocha"
                            player.tocha_acesa = True
                            player.tocha_duracao = item_equipado.duracao_max
                            player.tocha_ultima_contagem = time.time()
                        else:
                            feedback_message = "A tocha já está acesa"

                elif movi == "m":
                    def solicitar_volume(x_l, y_l, player):
                        while True:
                            clear()
                            prompt = "Escolha o Volume do jogo\ndigite um numero de 0 a 100"
                            num_linhas = prompt.count("\n") + 4
                            draw_window(term, x=x_l, y=y_l, width=32, height=num_linhas, text_content=prompt)
                            with term.location(x=x_l+1, y=y_l+4):
                                try:
                                    escolha = int(input(">"))
                                    if 0 <= escolha <= 100:
                                        volume = escolha / 100.0
                                        player.volume = volume
                                        set_volume_global(player.volume)  # aplica o volume corretamente

                                        break
                                    else:
                                        mostrar_mensagem(x_l+26, y_l+num_linhas+6, "Escolha entre 1 e 100")
                                except ValueError:
                                    mostrar_mensagem(x_l+26, y_l+num_linhas+6, "Digite apenas números!")
                    solicitar_volume(x_l=x_l, y_l=y_l, player=player)

                elif movi.isdigit():
                    if player.mapa_atual == "Mundo" or player.mapa_atual == "Caverna":
                        entrada = [movi]
                        feedback_message = usar_item(
                            player, entrada, mapa_art, mapa_id, ESTADO_MAPAS,
                            TODOS_OS_ITENS, save_filename, mapas_,
                            salvar_mapa_estado, substituir_caractere
                        )
                    else:
                        pass

                elif movi == "e":
                    player.menu_status(x=x_l + CAMERA_WIDTH +2, y=y_l, largura=40)
                    feedback_message = "Status e equipamentos verificados."
                    clear()

                elif movi == "z":
                    salvar_jogo_global(player, ESTADO_MAPAS)
                    feedback_message = "Jogo salvo com sucesso."
                    
                else:
                    feedback_message = f"Comando '{movi}'."
