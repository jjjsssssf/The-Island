import random, time
def interagir_com_objeto(px, py, ch, player, mapa_art, mapa_id,interacoes_contagem, ESTADO_MAPAS, TODOS_OS_ITENS,save_filename, mapas_, salvar_mapa_estado, substituir_caractere):
    feedback_message = ""
    pos = (px, py)
    interacoes_contagem[pos] = interacoes_contagem.get(pos, 0) + 1
    tentativas = interacoes_contagem[pos]

    if player.stm <= 1:
        return "Você não tem energia o suficiente"

    item_equipado = player.equipa.get("m_pri")
    nome_item = item_equipado.nome.lower() if item_equipado else "sem_ferramenta"
    BLOCOS = {
        # ÁRVORE
        "♣": {
            "ferramentas": ["machado/madeira", "machado/pedra", "machado/ferro"],
            "energia": {"machado/madeira": 5, "machado/pedra": 5, "machado/ferro": 5, "sem_ferramenta": 5},
            "mensagens": {
                "machado/madeira": ["Você começou a cortar a árvore", "Você continua cortando", "Você quebrou a árvore!"],
                "machado/pedra": ["Você começou a cortar a árvore", "Você quebrou a árvore!"],
                "machado/ferro": ["Você cortou a árvore instantaneamente!"],
                "sem_ferramenta": ["Você bate na árvore... é difícil", "Você ainda tenta...", "Você ainda luta...", "Você quebrou a árvore (na marra)!"],
            },
            "golpes_necessarios": {"machado/madeira": 3, "machado/pedra": 2, "machado/ferro": 1, "sem_ferramenta": 4},
            "drops": [("Madeira", 5), ("Muda/Arvore", 1)],
            "acoes": ["remover_bloco"]
        },

        # PEDRA
        "o": {
            "ferramentas": ["picareta/madeira", "picareta/pedra", "picareta/ferro"],
            "energia": {"picareta/madeira": 5, "picareta/pedra": 5, "picareta/ferro": 5, "sem_ferramenta": 0},
            "mensagens": {
                "picareta/madeira": ["Você iniciou a quebrar a pedra", "Você continua quebrando", "Você quebrou a pedra!"],
                "picareta/pedra": ["Você começou a quebrar", "Você quebrou a pedra!"],
                "picareta/ferro": ["Você destruiu a pedra facilmente!"],
                "sem_ferramenta": ["Você precisa de uma picareta"],
            },
            "golpes_necessarios": {"picareta/madeira": 3, "picareta/pedra": 2, "picareta/ferro": 1, "sem_ferramenta": 999},
            "drops": [("Pedra", 1)],
            "acoes": ["remover_bloco"]
        },
        "c": {
            "ferramentas": ["picareta/madeira", "picareta/pedra", "picareta/ferro"],
            "energia": {"picareta/madeira": 5, "picareta/pedra": 5, "picareta/ferro": 5, "sem_ferramenta": 0},
            "mensagens": {
                "picareta/madeira": ["Você iniciou a quebrar o carvão", "Você continua quebrando", "Você quebrou o carvão!"],
                "picareta/pedra": ["Você começou o carvão", "Você quebrou o carvão!"],
                "picareta/ferro": ["Você destruiu a pedra facilmente!"],
                "sem_ferramenta": ["Você precisa de uma picareta"],
            },
            "golpes_necessarios": {"picareta/madeira": 3, "picareta/pedra": 2, "picareta/ferro": 1, "sem_ferramenta": 999},
            "drops": [("Carvão", 1)],
            "acoes": ["remover_bloco"]
        },
        "u": {
            "ferramentas": ["picareta/madeira", "picareta/pedra", "picareta/ferro"],
            "energia": {"picareta/madeira": 5, "picareta/pedra": 5, "picareta/ferro": 5, "sem_ferramenta": 0},
            "mensagens": {
                "picareta/madeira": ["Você iniciou a quebrar o ferro", "Você continua quebrando", "Você quebrou o ferro!"],
                "picareta/pedra": ["Você começou a quebrar", "Você quebrou o ferro!"],
                "picareta/ferro": ["Você destruiu o ferro facilmente!"],
                "sem_ferramenta": ["Você precisa de uma picareta de pedra"],
            },
            "golpes_necessarios": {"picareta/madeira": 999, "picareta/pedra": 2, "picareta/ferro": 1, "sem_ferramenta": 999},
            "drops": [("Ferro", 1)],
            "acoes": ["remover_bloco"]
        },

        # MADEIRA
        "#": {
            "ferramentas": [],
            "energia": {"sem_ferramenta": 5},
            "mensagens": {"sem_ferramenta": ["Você pegou a madeira."]},
            "golpes_necessarios": {"sem_ferramenta": 1},
            "drops": [("Madeira", 1)],
            "acoes": ["remover_bloco"]
        },

        # BANCADA
        "C": {
            "ferramentas": [],
            "energia": {"sem_ferramenta": 5},
            "mensagens": {"sem_ferramenta": ["Você coletou a bancada."]},
            "golpes_necessarios": {"sem_ferramenta": 1},
            "drops": [("Bancada", 1)],
            "acoes": ["remover_bloco"]
        },

        # BAÚ
        "$": {
            "ferramentas": [],
            "energia": {"sem_ferramenta": 1},
            "mensagens": {"sem_ferramenta": ["Você tenta abrir o baú..."]},
            "golpes_necessarios": {"sem_ferramenta": 1},
            "drops": [("Baú", 1)],
            "acoes": ["interagir_bau"]
        },

        # ARBUSTO
        "♠": {
            "ferramentas": [],
            "energia": {"sem_ferramenta": 2},
            "mensagens": {"sem_ferramenta": ["Você colheu um arbusto."]},
            "golpes_necessarios": {"sem_ferramenta": 1},
            "drops": [("Fruta", lambda: random.randint(1, 5))],
            "acoes": ["transformar_x"]
        },

        # ARBUSTO COLHIDO
        "x": {
            "ferramentas": [],
            "energia": {"sem_ferramenta": 1},
            "mensagens": {"sem_ferramenta": ["Você coletou algumas mudas."]},
            "golpes_necessarios": {"sem_ferramenta": 1},
            "drops": [("Semente/Arbusto", lambda: random.randint(1, 2))],
            "acoes": ["remover_bloco"]
        },

        # TRIGO
        '‼':{
            "ferramentas": [],
            "energia": {"sem_ferramenta": 1},
            "mensagens": {"sem_ferramenta": ["Você coletou um Trigo."]},
            "golpes_necessarios": {"sem_ferramenta": 1},
            "drops": [("Trigo", lambda: random.randint(1, 5))],
            "acoes": ["terra_arada"]
        },
        # Algodão
        "☼":{
            "ferramentas": [],
            "energia": {"sem_ferramenta": 1},
            "mensagens": {"sem_ferramenta": ["Você coletou um Algodão."]},
            "golpes_necessarios": {"sem_ferramenta": 1},
            "drops": [("Algodão", lambda: random.randint(1, 5))],
            "acoes": ["terra_arada"]
        },

        # MILHO
        '¥': {
            "ferramentas": [],
            "energia": {"sem_ferramenta": 1},
            "mensagens": {"sem_ferramenta": ["Você coletou um Milho."]},
            "golpes_necessarios": {"sem_ferramenta": 1},
            "drops": [("Milho", lambda: random.randint(1, 5))],
            "acoes": ["terra_arada"]
        },

        # ABOBORA
        '0': {
            "ferramentas": [],
            "energia": {"sem_ferramenta": 1},
            "mensagens": {"sem_ferramenta": ["Você coletou uma Abobora."]},
            "golpes_necessarios": {"sem_ferramenta": 1},
            "drops": [("Abobora", 1)],
            "acoes": ["transformar_7"]
        },
        
        "♀": {
            "ferramentas": [],
            "energia": {"sem_ferramenta": 1},
            "mensagens": {"sem_ferramenta": ["Você coletou um Morango."]},
            "golpes_necessarios": {"sem_ferramenta": 1},
            "drops": [("Morango", lambda: random.randint(1, 7))],
            "acoes": ["transformar_7"]
        },

        # CERCA
        "!": {
            "ferramentas": [],
            "energia": {"sem_ferramenta": 1},
            "mensagens": {"sem_ferramenta": ["Você pegou a Cerca."]},
            "golpes_necessarios": {"sem_ferramenta": 1},
            "drops": [("Cerca", 1)],
            "acoes": ["remover_bloco"]
        },

        # CHÃO
        ":": {
            "ferramentas": [],
            "energia": {"sem_ferramenta": 1},
            "mensagens": {"sem_ferramenta": ["Você pegou a Chão."]},
            "golpes_necessarios": {"sem_ferramenta": 1},
            "drops": [("Chão", 1)],
            "acoes": ["remover_bloco"]
        },
        # CHÃO
        "%": {
            "ferramentas": [],
            "energia": {"sem_ferramenta": 1},
            "mensagens": {"sem_ferramenta": ["Você pegou a Fornalha."]},
            "golpes_necessarios": {"sem_ferramenta": 1},
            "drops": [("Fornalha", 1)],
            "acoes": ["remover_bloco"]
        },
        "7": {
            "ferramentas": [],
            "energia": {"sem_ferramenta": 1},
            "mensagens": {"sem_ferramenta": ["placeholder"]},
            "golpes_necessarios": {"sem_ferramenta": 1},
            "acoes": ["remover_bloco", "mensagem_muda"]
        },

    }
    bloco = BLOCOS.get(ch)
    if not bloco:
        return f"Não há interação configurada para '{ch}'."

    ferramenta = nome_item if nome_item in bloco["ferramentas"] else "sem_ferramenta"
    mensagens = bloco["mensagens"].get(ferramenta, ["..."])
    energia_custo = bloco["energia"].get(ferramenta, 0)
    golpes_necessarios = bloco.get("golpes_necessarios", {}).get(ferramenta, 1)

    idx_msg = min(tentativas - 1, len(mensagens) - 1)
    feedback_message = mensagens[idx_msg]

    if tentativas >= golpes_necessarios:
        for acao in bloco["acoes"]:
            if acao == "remover_bloco":
                substituir_caractere(mapa_art, px, py, '.')
                ESTADO_MAPAS[mapa_id].get("regeneracoes", {}).pop((px, py), None)
                interacoes_contagem.pop(pos, None)
            elif acao == "interagir_bau":
                bau_handler(px, py, mapa_art, mapa_id, ESTADO_MAPAS, player, salvar_mapa_estado, save_filename)
            elif acao == "transformar_x":
                substituir_caractere(mapa_art, px, py, 'x')
                ESTADO_MAPAS[mapa_id].setdefault("regeneracoes", {})[(px, py)] = {
                    "tempo_inicio": time.time(),
                    "tempo_regeneracao": 30,
                    "tipo_original": "♠"
                }
                interacoes_contagem.pop(pos, None)
            elif acao == 'terra_arada':
                substituir_caractere(mapa_art, px, py, '=')
                interacoes_contagem.pop(pos, None)
            elif acao == "transformar_7":
                substituir_caractere(mapa_art, px, py, '7')
                ESTADO_MAPAS[mapa_id].setdefault("regeneracoes", {})[(px, py)] = {
                    "tempo_inicio": time.time(),
                    "tempo_regeneracao": 15 * 60,
                    "tipo_original": ch
                }
                ESTADO_MAPAS[mapa_id].setdefault("origens_7", {})[(px, py)] = ch
                interacoes_contagem.pop(pos, None)
            elif acao == "mensagem_muda":
                origem = ESTADO_MAPAS[mapa_id].get("origens_7", {}).get((px, py))

                if origem == '0':        # abóbora
                    feedback_message = "Você removeu a muda de Abóbora."

                elif origem == '♀':      # morango
                    feedback_message = "Você removeu a muda de Morango."

                else:
                    feedback_message = "Você removeu uma muda desconhecida."

                # Remove registro após quebrar
                ESTADO_MAPAS[mapa_id].get("origens_7", {}).pop((px, py), None)


        for item_nome, quantidade in bloco.get("drops", []):
            qtd = quantidade() if callable(quantidade) else quantidade
            espaco = player.inventario_espaco_restante()
            
            if espaco <= 0:
                feedback_message += "\nInventário cheio! Não é possível coletar itens."
                break  # não tenta adicionar mais
            elif espaco < qtd:
                feedback_message += f"\nInventário quase cheio! Você só conseguiu pegar {espaco}x {item_nome}."
                qtd = espaco  # só pega o que cabe

            for _ in range(qtd):
                player.inventario.append(TODOS_OS_ITENS[item_nome])

    salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
    player.stm -= energia_custo

    return feedback_message

def bau_handler(px, py, mapa_art, mapa_id, ESTADO_MAPAS, player, salvar_mapa_estado, save_filename):
    baus = ESTADO_MAPAS[mapa_id].setdefault("baus_armazenamento", {})
    pos = (px, py)

    if pos in baus:
        conteudo = baus[pos]
        if not conteudo:
            substituir_caractere(mapa_art, px, py, '.')
            del baus[pos]
            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
            player.stm -= 1
            print("Você quebrou um baú vazio.")
        else:
            print("O baú ainda contém itens. Esvazie-o antes de quebrar.")
    else:
        print("Este baú não está mais registrado no mapa.")

def regenerar_blocos(mapa_art, mapa_id, ESTADO_MAPAS, salvar_mapa_estado, save_filename):
    tempo_atual = time.time()
    regeneracoes = ESTADO_MAPAS[mapa_id].get("regeneracoes", {})

    for (px, py), dados in list(regeneracoes.items()):
        tempo_passado = tempo_atual - dados["tempo_inicio"]
        if tempo_passado >= dados["tempo_regeneracao"]:
            substituir_caractere(mapa_art, px, py, dados.get("tipo_original", '♠'))
            del regeneracoes[(px, py)]
            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])

def usar_item(player, entrada, mapa_art, mapa_id, ESTADO_MAPAS, TODOS_OS_ITENS,save_filename, mapas_, salvar_mapa_estado, substituir_caractere):
    feedback_message = ""

    # Verifica se o jogador digitou apenas um número (1–9)
    if len(entrada) == 1 and entrada[0].isdigit():
        indice = int(entrada[0]) - 1
        if 0 <= indice < 9:  # agora temos 9 slots
            slot_nome = f"slot_{indice + 1}"
            material_slot = player.matariais['slots'].get(slot_nome)
            if not material_slot:
                return f"O slot {indice + 1} está vazio."

            item_escolhido = material_slot
            if item_escolhido not in player.inventario:
                player.matariais['slots'][slot_nome] = None
                return f"O item {item_escolhido.nome} não está mais no inventário. Slot liberado."

            nome = item_escolhido.nome

            # === DIREÇÃO DO PLAYER ===
            dir_map = {
                "cima": (0, -1),
                "baixo": (0, 1),
                "esquerda": (-1, 0),
                "direita": (1, 0)
            }
            dx, dy = dir_map.get(player.direcao, (0, 0))
            x_frente = player.x_mapa + dx
            y_frente = player.y_mapa + dy

            # Verifica se está dentro dos limites do mapa
            if not (0 <= x_frente < len(mapa_art[0]) and 0 <= y_frente < len(mapa_art)):
                return "Você não pode usar o item fora dos limites do mapa."

            # === CONSTRUÇÕES ===
            construcoes = {
                "Madeira": ("#", "Você colocou Madeira."),
                "Bancada": ("C", "Você colocou uma Bancada."),
                "Pedra": ("#", "Você colocou Pedra."),
                "Bau": ("$", "Você colocou um Baú."),
                "Chão": (":", "Você colocou um chão."),
                "Fornalha": ("%", "Você colocou uma Fornalha."),
                "Porta": ("\\", "Você colocou uma Porta."),
                "Cerca": ("!", "Você colocou uma Cerca."),
                "Escada": ("W", "Você colocou uma Escada.")
            }

            if nome in construcoes:
                char, msg = construcoes[nome]

                if mapa_art[y_frente][x_frente] == '.':  # só coloca se estiver livre
                    substituir_caractere(mapa_art, x_frente, y_frente, char)
                    player.inventario.remove(item_escolhido)
                    salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                    feedback_message = msg
                else:
                    feedback_message = "O local à frente está ocupado."

            # === PLANTIO SEM DIREÇÃO ===
            elif nome in ['Semente/Arbusto', 'Semente/Abobora', 'Semente/Milho', 'Semente/Trigo', 'Muda/Arvore', "Semente/Algodão"]:
                tipo_map = {
                    "Semente/Trigo": ("trigo", 3 * 60),
                    "Semente/Milho": ("milho", 3 * 60),
                    "Semente/Abobora": ("abobora", 15 * 60),
                    "Muda/Arvore": ("arvore", 20 * 60),
                    "Semente/Algodão": ("algodão", 5 * 60),
                    "Semente/Arbusto": ("arbusto", 1000),
                    "Semente/Morrango": ("morango", 15 * 60)
                }

                tipo, tempo_crescimento = tipo_map[nome]

                terreno_atual = mapa_art[player.y_mapa][player.x_mapa]

                # Verifica se o local é válido para plantar
                if tipo in ('trigo', 'milho', 'abobora', 'morrango', "algodão"):
                    if terreno_atual != '=':
                        return "Você precisa estar sobre o solo arado ('=') para plantar sementes."
                    char = '*'

                elif tipo in ('arvore', 'arbusto'):
                    if terreno_atual != '.':
                        return "Você precisa estar sobre terra ('.') para plantar mudas."
                    char = '1'

                # Planta no local do player
                substituir_caractere(mapa_art, player.x_mapa, player.y_mapa, char)
                ESTADO_MAPAS[mapa_id]["plantacoes"][(player.x_mapa, player.y_mapa)] = {
                    "item": tipo,
                    "tempo_plantio": time.time(),
                    "tempo_crescimento": tempo_crescimento,
                }

                player.inventario.remove(item_escolhido)
                salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                feedback_message = f"Você plantou {tipo.capitalize()} aqui!"

            # === OUTROS ITENS ===
            else:
                feedback_message = f"Você usou o material {item_escolhido.nome}!"

            tem_mais = any(i.nome == item_escolhido.nome for i in player.inventario)
            if not tem_mais:
                player.matariais['slots'][slot_nome] = None

        else:
            feedback_message = "Número de slot inválido (use 1–9)."
    else:
        feedback_message = "Digite apenas o número do slot (1–9) para usar o item."

    return feedback_message







