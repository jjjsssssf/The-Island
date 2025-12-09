import random, os, time, json
from classe_arts import draw_window,clear, art_ascii, clear_region_a
from classe_do_inventario import *
from collections import defaultdict
from blessed import Terminal
term = Terminal()
art= art_ascii()
##ARQUIVO DO JOGADOR
class jogador:
    def __init__(self, nome, hp_max, atk, niv, xp_max, defesa, gold, stm_max, intt, mn_max, d_m, art_player,skin, skin_nome,mapa_x = None,mapa_y = None, mana_lit=None):
        self.nome = nome
        self.skin = skin
        self.skin_nome = skin_nome
        self.hp_max = hp_max
        self.hp = self.hp_max
        self.mapa_atual = ""
        self.mana_max = mn_max
        self.mana = self.mana_max
        self.stm_max = stm_max
        self.stm = self.stm_max
        self.atk = atk
        self.andar = 0
        self.intt = intt
        self.mapa_x = mapa_x
        self.mapa_y = mapa_y
        self.fov_bonus = 0
        self.tocha_ultima_contagem = time.time()
        self.tocha_acesa = False
        self.tocha_duracao = 60
        self.niv = niv
        self.buff_atk = 0
        self.buff_def = 0
        self.ponto = 0
        self.tempo_inicio_global = 0.0
        self.limite_inventario_base = 50 
        self.xp_max = xp_max
        self.dano_magico = d_m
        self.xp = 0
        self.defesa = defesa
        self.gold = gold
        self.rodar_jogo = False
        self.aleatorio = 75
        self.art_player = art_player
        self.x_mapa = 0
        self.y_mapa = 0
        self.seed = 0
        self.direcao = "baixo"
        self.retorno = None
        self.seed_caverna = 0
        self.boss = {
        'Suny': False,
        'Serefas': False}
        self.dificuldade = {
            "Facil": {"dif": None, "niv": 0.5},
            "Normal": {"dif": None, "niv": 1},
            "Dificil": {"dif": None, "niv": 2.5}
        }
        self.dificuldade_atual = "Normal"
        self.inventario = []
        self.mana_lit = mana_lit if mana_lit else []
        self.equipa = {
            "m_pri": None,
            "m_seg": None,
            "m_ter": None,
            "m_ter": None,
            "c_cap": None,
            "p_pet": None,
            "mochila": None
        }
        self.matariais = {
            'slots':{
                'slot_1': None,
                'slot_2': None,
                'slot_3': None,
                'slot_4': None,
                'slot_5': None,
                'slot_6': None,
                'slot_7': None,
                'slot_8': None,
                'slot_9': None,
            }
        }
        
        self.itens_coletaodos = {
            "item_1": False,
            "item_2": False,
            "Farol": False,
            "Dentro_Farol": False,
        }
        self.classe = None 

    def menu_status(self, x, y, largura=40):
        pagina = 0
        paginas = [
            "Itens Equipados",
            "Materiais e Equipamentos"
        ]
        slots_legiveis = {
            "m_pri": "Primeira Mão",
            "m_seg": "Segunda Mão",
            "m_ter": "Liminaria",
            "c_cap": "Cabeça",
            "p_pet": "Peito"
        }   

        while True:
            clear_region_a(x=x, start_y=y, end_y=y, width=largura)
            
            if pagina == 0:
                text_content = "Equipamentos:\n"
                for slot_chave, slot_nome in slots_legiveis.items():
                    item_slot = self.equipa.get(slot_chave)
                    nome_item = item_slot.nome if item_slot else "Vazio"
                    text_content += f"{slot_nome}: {nome_item}\n"

            elif pagina == 1:
                text_content = "Materiais Equipados:\n"
                for i in range(1, 10):
                    slot_nome = f"slot_{i}"
                    item_slot = self.matariais['slots'][slot_nome]
                    nome = item_slot.nome if item_slot else "Vazio"
                    text_content += f"[{i}] {nome}\n"

            total_paginas = len(paginas)
            text_content += f"\nPágina {pagina + 1}/{total_paginas}\nUse '<' e '>' ou digite 'sair'."

            draw_window(term, x=x, y=y, width=largura, height=len(text_content.split("\n")) + 4,
                        title=f"Status - {paginas[pagina]}", text_content=text_content)

            with term.location(x=x + 1, y=y + len(text_content.split("\n")) + 2):
                escolha = input("> ").strip().lower()

            if escolha == "sair":
                clear_region_a(x=x, start_y=y, end_y=y, width=largura)
                break
            elif escolha == ">" and pagina < total_paginas - 1:
                pagina += 1
            elif escolha == "<" and pagina > 0:
                pagina -= 1
            else:
                mensagem = "Entrada inválida."
                draw_window(term, x=x, y=y + len(text_content.split("\n")) + 4, width=largura, height=3, text_content=mensagem)
                time.sleep(1)

    def status_art(self ,x_janela, y_janela):
        art_player = self.art_player
        draw_window(term, x=x_janela, y=y_janela, width=31, height=11, text_content=art_player)

    def status_batalha_art(self, x_janela, y_janela, wend, herd):
        art_player = self.art_player
        draw_window(term, x=x_janela, y=y_janela, width=wend, height=herd, text_content=art_player)
        self.status_batalha(x_janela=x_janela, y_janela=y_janela+herd)

    def status_batalha(self, x_janela, y_janela):
        draw_window(term, x=x_janela, y=y_janela, width=31, height=6)
        with term.location(x=x_janela+1, y=y_janela+1):
            print(f"HP: [{term.bold_green(str(self.hp_max))}/{term.green(str(self.hp))}] MP: [{term.bold_blue(str(self.stm_max))}/{term.blue(str(self.stm))}]")
        with term.location(x=x_janela+1, y=y_janela+2):
            print(f"MG: [{term.bold_magenta(str(self.mana_max))}/{term.magenta(str(self.mana))}] MA: [{term.bold_purple(str(self.dano_magico+3))}-{term.purple(str(self.dano_magico-3))}]")
        with term.location(x=x_janela+1, y=y_janela+3):
            print(f"AT: [{term.bold_red(str(self.atk))}-{term.red(str(self.buff_atk))}] DF: [{term.bold_cyan(str(self.defesa))}-{term.cyan(str(self.buff_def))}]")
        with term.location(x=x_janela+1, y=y_janela+4):
            print(f"Nivel: [{term.yellow(str(self.niv))}]")

    def add_xp(self, xp_ganho):
        self.xp += xp_ganho
        while self.xp >= self.xp_max:
            print(term.bold_white("Você subiu de nível!"))
            xp_remaining = self.xp - self.xp_max
            self.xp_max = int(self.xp_max * 1.5)
            self.xp = xp_remaining
            self.niv += 1
            self.ponto += 3
            self.stm = self.stm_max
            time.sleep(1)
        print(f"Você ganhou {xp_ganho} de XP. Total: {self.xp}/{self.xp_max}")
        time.sleep(2)
#r
    def up(self, x, y, werd, herd, x_i):
        STATUS_MAP = {
            "HP": ("hp_max", "HP"),
            "MP": ("stm_max", "MP"),
            "ATK": ("atk", "ATK"),
            "DEF": ("defesa", "DEF"),
            "MG": ("mana_max", "Poder Mágico (MG)"),
            "MA": ("dano_magico", "Dano Mágico (MA)"),
            "INT": ("intt", "INT"),
            "SAIR": ("sair", "Sair do menu")
        }

        while True:
            clear_region_a(x=x, start_y=herd, end_y=herd-1, width=werd)
            mensagem = f"""Pontos: [{self.ponto}]
HP: [{self.hp_max}]
MP: [{self.stm_max}]
ATK: [{self.atk}]
DEF: [{self.defesa}]
MG: [{self.mana_max}]
MA: [{self.dano_magico}]
INT: [{self.intt}]
Digite Nome e Quantidade
                """

            draw_window(term, x=x, y=y, width=werd, height=herd, text_content=mensagem)

            if self.ponto >= 1:
                with term.location(x=werd+x_i+10, y=herd-6):
                    up_input = input(">").strip().upper()
            else:
                with term.location(x=werd+x_i+10, y=herd-6):
                    print("Você não tem Pontos")
                    input()
                    break

            if up_input == "SAIR":
                break

            parts = up_input.split()
            if len(parts) == 2:
                stat_name, amount_str = parts
                if stat_name in STATUS_MAP and amount_str.isdigit():
                    amount = int(amount_str)
                    if amount <= 0:
                        msg = "Digite um número maior que zero."
                    elif amount > self.ponto:
                        msg = f"Você só tem {self.ponto} ponto(s)."
                    else:
                        attr_name, display_name = STATUS_MAP[stat_name]
                        current_value = getattr(self, attr_name)
                        setattr(self, attr_name, current_value + (amount * 2))
                        self.ponto -= amount
                        msg = f"Você melhorou seu {display_name}"
                else:
                    msg = "Comando inválido.Tente algo como: HP 5"
            else:
                msg = "Formato inválido.Use: STATUS QUANTIDADE"

            with term.location(x=werd+x_i, y=herd-6):
                print(" " * 50)
            with term.location(x=werd+x_i, y=herd-6):
                print(msg)
            time.sleep(2)
#@
    def aprender_magias(self, term, x_menu, y_menu, wend, herd):
        term = Terminal()
        tipos_magias = sorted(set(magia.tipo for magia in TODAS_AS_MAGIAS.values()))
        
        while True:
            clear_region_a(x=x_menu, start_y=y_menu, end_y=y_menu + 10, width=wend)
            menu_text = "Escolha o tipo de magia para aprender:\n"
            for i, tipo in enumerate(tipos_magias, start=1):
                menu_text += f"[{i}] {tipo}\n"
            menu_text += "[0] Voltar"
            draw_window(term, x_menu, y_menu, wend, herd+2, text_content=menu_text)

            with term.location(x=x_menu+1, y=y_menu+herd):
                escolha = input(">").strip()

            if escolha == '0':
                break

            if escolha.isdigit() and 1 <= int(escolha) <= len(tipos_magias):
                tipo_escolhido = tipos_magias[int(escolha) - 1]
                magias_disponiveis = [
                    m for m in TODAS_AS_MAGIAS.values()
                    if m.tipo == tipo_escolhido and m.nome not in self.mana_lit
                ]

                if not magias_disponiveis:
                    draw_window(term, x_menu, y_menu, wend, herd+2, text_content="Nenhuma magia disponível.")
                    time.sleep(2)
                    continue

                while True:
                    clear_region_a(x_menu, y_menu, y_menu + 10, wend)
                    conteudo = f"Magias de tipo: {tipo_escolhido}\n"
                    for i, magia in enumerate(magias_disponiveis, 1):
                        conteudo += f"[{i}] {magia.nome} - Requer {magia.xp} Pontos\n"
                    conteudo += "[0] Voltar"
                    draw_window(term, x_menu, y_menu, wend, herd+2, text_content=conteudo)

                    with term.location(x=x_menu+1, y=y_menu+herd):
                        escolha_magia = input(">").strip()

                    if escolha_magia == '0':
                        break

                    if escolha_magia.isdigit() and 1 <= int(escolha_magia) <= len(magias_disponiveis):
                        magia = magias_disponiveis[int(escolha_magia) - 1]

                        if magia.nome in self.mana_lit:
                            draw_window(term, x_menu, y_menu, wend, herd+2, text_content="Você já aprendeu essa magia.")
                            with term.location(x=x_menu+1, y=y_menu+herd):
                                input("Pressione Enter para continuar...")
                            continue
                        if self.ponto >= magia.xp:
                            self.ponto -= magia.xp
                            self.mana_lit.append(magia.nome)
                            draw_window(term, x_menu, y_menu, wend, herd+2, text_content=f"Você aprendeu: {magia.nome}")
                        else:
                            draw_window(term, x_menu, y_menu, wend, herd+2, text_content="XP insuficiente.")
                            with term.location(x=x_menu+1, y=y_menu+herd):
                                input("Pressione Enter para continuar...")
                        break

    def menu_magias(self, x_menu, y_menu, batalha, alvo):
        term = Terminal()
        text_content = ""

        if not self.mana_lit:
            text_content = "Você não conhece nenhuma magia."
        else:
            for nome_magia in self.mana_lit:
                magia_obj = TODAS_AS_MAGIAS.get(nome_magia)
                if magia_obj:
                    text_content += f"{magia_obj.nome} (Custo: {magia_obj.mana_gasta} Mana)\n"
        
        text_content += "Para usar uma magia, digite o nome dela.\nPara sair, digite 'sair'."
        num_linhas_texto = text_content.count('\n') + 1
        herd = num_linhas_texto + 3
        draw_window(term, x_menu, y_menu, width=45, height=herd, title="Livro de Magias", text_content=text_content)
        
        x_input = x_menu + 2
        y_input = y_menu + herd - 2

        with term.location(x_input, y_input):
            escolha = input(">")

        if escolha.lower() == "sair":
            return False
            
        if escolha in self.mana_lit:
            magia_escolhida = TODAS_AS_MAGIAS[escolha]
            if magia_escolhida.batalhas and not batalha:
                feedback_message = "Você só pode usar esta magia em batalha!"
                draw_window(term, x=x_menu, y=y_menu + herd, width=len(feedback_message) + 5, height=5, text_content=feedback_message)
                time.sleep(2)
                return False
            else:
                return self.usar_magia(magia_escolhida, x_menu, y_menu + herd, alvo=alvo)
        else:
            feedback_message = "Magia inválida ou não conhecida."
            draw_window(term, x=x_menu, y=y_menu + herd, width=len(feedback_message) + 5, height=5, text_content=feedback_message)
            time.sleep(2)
            return False

    def usar_magia(self, magia, x_janela, y_janela, alvo):
        text_content = ""
        herd = 3
        sucesso = False       
        if self.mana < magia.mana_gasta:
            text_content = "Mana insuficiente!"
            sucesso = False
        else:
            self.mana -= magia.mana_gasta            
            if magia.tipo == "Cura":
                self.hp += magia.bonus_hp
                if self.hp > self.hp_max:
                    self.hp = self.hp_max
                text_content = f"Você usou {magia.nome} e curou {magia.bonus_hp} de HP."
                sucesso = True
            elif magia.tipo == "Ataque":
                div = self.intt // 4
                soma = self.dano_magico + div
                dano = soma + magia.bonus_atk
                alvo.hp -= dano
                text_content = f"Você lançou {magia.nome} e causou {dano} de dano."
                sucesso = True
            elif magia.tipo == "Ajudante":
                self.buff_def += magia.bonus_def
                self.buff_atk += magia.bonus_atk
                text_content =f"""Você chamou {magia.nome}
ele ira te ajudar na batalhas
ATK: [{magia.bonus_atk}]
DEF: [{magia.bonus_def}]
                """
                herd = 6
                sucesso = True
        draw_window(term, x_janela, y_janela, width=35, height=herd, text_content=text_content)
        time.sleep(2)
        return sucesso

    @property
    def limite_inventario(self):
        return self.limite_inventario_base

    def inventario_cheio(self):
        return len(self.inventario) >= self.limite_inventario

    def inventario_espaco_restante(self):
        return self.limite_inventario - len(self.inventario)

    def inventario_(self, x, y, werd, herd, batalha):
        altura_janela = 0
        sucesso_uso = False
        pagina = 0
        itens_por_pagina = 8

        while True:
            text_content = ""
            contagem_itens = defaultdict(int)
            lista_itens = []
            indice_para_item = {}
            if not self.inventario:
                text_content = "Não tem nada no inventário.\n"
            else:
                # Conta todos os itens
                for item_obj in self.inventario:
                    contagem_itens[item_obj.nome] += 1

                todos_itens = list(contagem_itens.items())
                total_paginas = (len(todos_itens) - 1) // itens_por_pagina + 1
                inicio = pagina * itens_por_pagina
                fim = inicio + itens_por_pagina
                itens_visiveis = todos_itens[inicio:fim]
                index = 1
                for item_nome, quantidade in itens_visiveis:
                    item_obj_ref = TODOS_OS_ITENS[item_nome]
                    estado = ""
                    if (item_obj_ref.slot_equip and
                        self.equipa.get(item_obj_ref.slot_equip) and
                        self.equipa[item_obj_ref.slot_equip].nome == item_obj_ref.nome):
                        estado = "[Equipado]"

                    text_content += f"[{index}] {item_obj_ref.nome} (x{quantidade}) {estado}\n"
                    lista_itens.append(item_obj_ref)
                    indice_para_item[index - 1] = item_obj_ref
                    index += 1
                text_content += f"\nLimite do Inventário: [{self.limite_inventario_base}]"
                text_content += f"\nPágina {pagina + 1}/{total_paginas}\n"
                text_content += "Escolha um número,\n'<', '>', ou 'sair'"
            num_linhas_texto = text_content.count('\n') + 1
            altura_janela = num_linhas_texto + 4 
            clear_region_a(x=x, start_y=y, end_y=y, width=werd)
            draw_window(term, x, y, width=werd, height=altura_janela, title="Inventário", text_content=text_content)
            x_input = x + 1
            y_input = y + altura_janela - 2
            with term.location(x_input, y_input):
                print(" " * (werd - 4), end='\r')
            with term.location(x_input, y_input):
                escolha = input("> ").strip().lower()
            if escolha == "sair":
                return sucesso_uso
            if escolha == ">":
                if pagina < total_paginas - 1:
                    pagina += 1
                else:
                    mensagem = "Você já está na última página."
                    draw_window(term, x, y + altura_janela, width=werd, height=3, text_content=mensagem)
                    time.sleep(1.2)
                continue

            if escolha == "<":
                if pagina > 0:
                    pagina -= 1
                else:
                    mensagem = "Você já está na primeira página."
                    draw_window(term, x, y + altura_janela, width=werd, height=3, text_content=mensagem)
                    time.sleep(1.2)
                continue
            if escolha.isdigit():
                escolha_index = int(escolha) - 1
                if 0 <= escolha_index < len(lista_itens):
                    item_escolhido = lista_itens[escolha_index]
                    if batalha:
                        if item_escolhido.tipo == "Consumivel":
                            sucesso_uso_local = self.usar_consumivel(item_escolhido, x, y + altura_janela + 1, werd)
                            if sucesso_uso_local:
                                sucesso_uso = True
                                return True 
                        elif item_escolhido.tipo == "Equipavel":
                            mensagem = "Você não pode usar\num equipamento em batalha!"
                            draw_window(term, x=x, y=y + altura_janela, width=werd, height=4, text_content=mensagem)
                            time.sleep(3)
                            clear_region_a(x=x, start_y=y, end_y=y, width=werd)
                    else:
                        if item_escolhido.tipo == "Consumivel":
                            sucesso_uso = self.usar_consumivel(item_escolhido, x, y + altura_janela, werd) or sucesso_uso
                        elif item_escolhido.tipo == "Equipavel":
                            alteracao_equip = self.gerenciar_equipavel(item_escolhido, x, y + altura_janela, werd)
                            if alteracao_equip:
                                sucesso_uso = True
                        elif item_escolhido.tipo == "Produto":
                            interacoes_produto = self.usar_produtos(item_escolhido, x, y + altura_janela, werd) or sucesso_uso
                        elif item_escolhido.tipo == "Material":
                            alteracao_material = self.gerenciar_material(item_escolhido, x, y + altura_janela, werd)
                            if alteracao_material:
                                sucesso_uso = True
                else:
                    mensagem = "Número inválido nesta página."
                    draw_window(term, x, y + altura_janela, width=werd, height=3, text_content=mensagem)
                    time.sleep(2)
            else:
                mensagem = "Entrada inválida."
                draw_window(term, x, y + altura_janela, width=werd, height=3, text_content=mensagem)
                time.sleep(2)

    def usar_produtos(self, item, x_janela, y_janela, werd):
        altura_mensagem = 3
        clear_region_a(x=x_janela, start_y=y_janela, end_y=y_janela + altura_mensagem, width=werd)
        if item.tipo != "Produto":
            mensagem = "Esse item não pode ser usado!"
        else:
            mensagem = f"{item.nome}: esse item é um Produto."
        draw_window(term, x_janela, y_janela, width=werd, height=altura_mensagem, text_content=mensagem)
        time.sleep(2)
        clear_region_a(x=x_janela, start_y=y_janela, end_y=y_janela + altura_mensagem, width=werd)
        sucesso = True
        return sucesso

    def usar_consumivel(self, item, x_janela, y_janela, werd):
        """Usa um item consumível genérico, aplicando todos os bônus definidos nele."""
        altura_mensagem = 3
        clear_region_a(x=x_janela, start_y=y_janela, end_y=y_janela + altura_mensagem, width=werd)
        sucesso = False

        if item.tipo != "Consumivel":
            mensagem = "Esse item não pode ser usado!"
        else:
            efeitos_aplicados = []
            
            # HP
            if getattr(item, "bonus_hp", 0) > 0:
                if self.hp < self.hp_max:
                    ganho = min(item.bonus_hp, self.hp_max - self.hp)
                    self.hp += ganho
                    efeitos_aplicados.append(f"+{ganho} HP")
                    sucesso = True
                else:
                    efeitos_aplicados.append("HP já está cheio")

            # Stamina
            if getattr(item, "bonus_stm", 0) > 0:
                if self.stm < self.stm_max:
                    ganho = min(item.bonus_stm, self.stm_max - self.stm)
                    self.stm += ganho
                    efeitos_aplicados.append(f"\n+{ganho} Stamina")
                    sucesso = True
                else:
                    efeitos_aplicados.append("Stamina já está cheia")

            # Mana
            if getattr(item, "bonus_mana", 0) > 0:
                if self.mana < self.mana_max:
                    ganho = min(item.bonus_mana, self.mana_max - self.mana)
                    self.mana += ganho
                    efeitos_aplicados.append(f"+{ganho} Mana")
                    sucesso = True
                else:
                    efeitos_aplicados.append("Mana já está cheia")

            if sucesso:
                self.inventario.remove(item)
                mensagem = f"Você usou {item.nome}: " + ", ".join(efeitos_aplicados)
            else:
                # Nenhum atributo pôde ser restaurado
                mensagem = f"{item.nome} não teve efeito.\n(Tudo já está cheio)"

        draw_window(term, x_janela, y_janela, width=werd, height=altura_mensagem+1, text_content=mensagem)
        time.sleep(2)
        clear_region_a(x=x_janela, start_y=y_janela, end_y=y_janela + altura_mensagem, width=werd)
        return sucesso

    def gerenciar_material(self, item, x_janela, y_janela, werd):
        altura_feedback = 4
        clear_region_a(x_janela, y_janela, y_janela + altura_feedback, werd)
        slots = self.matariais['slots']
        alteracao_efetuada = False

        if any(v and v.nome == item.nome for v in slots.values()):
            for k, v in slots.items():
                if v and v.nome == item.nome:
                    slots[k] = None
                    feedback = f"{item.nome} foi removido de {k}."
                    alteracao_efetuada = True
                    break
        else:
            slot_livre = next((k for k, v in slots.items() if v is None), None)
            if slot_livre:
                slots[slot_livre] = item
                feedback = f"{item.nome} foi equipado no {slot_livre}."
                alteracao_efetuada = True
            else:
                feedback = "Todos os slots de materiais estão ocupados."

        draw_window(term, x_janela, y_janela, width=werd, height=altura_feedback, text_content=feedback)
        time.sleep(1.8)
        clear_region_a(x_janela, y_janela, y_janela + altura_feedback, werd)
        return alteracao_efetuada

    def gerenciar_equipavel(self, item, x_janela, y_janela, werd):
        altura_feedback = 4
        clear_region_a(x_janela, y_janela, y_janela + altura_feedback, werd)

        slot = item.slot_equip
        alteracao_efetuada = False

        if self.equipa.get(slot) and self.equipa[slot].nome.lower() == "tocha":
            feedback = "A tocha não pode ser desequipada."
            draw_window(term, x_janela, y_janela, width=werd, height=altura_feedback, text_content=feedback)
            time.sleep(1.8)
            clear_region_a(x_janela, y_janela, y_janela + altura_feedback, werd)
            return False
        if self.equipa.get(slot) and self.equipa[slot].nome.lower() == "mochila":
            feedback = "A mochila não pode ser desequipada."
            draw_window(term, x_janela, y_janela, width=werd, height=altura_feedback, text_content=feedback)
            time.sleep(1.8)
            clear_region_a(x_janela, y_janela, y_janela + altura_feedback, werd)
            return False

        if not self.equipa.get(slot):
            self.equipa[slot] = item
            self.atk += item.bonus_atk
            self.defesa += item.bonus_def
            self.hp_max += item.bonus_hp_max
            self.dano_magico += item.bonus_atk_mana
            self.limite_inventario_base += item.espaco
            feedback = f"Você equipou {item.nome}."
            alteracao_efetuada = True

        elif self.equipa[slot].nome == item.nome:
            equipado = self.equipa[slot]
            self.equipa[slot] = None
            self.atk -= equipado.bonus_atk
            self.defesa -= equipado.bonus_def
            self.hp_max -= equipado.bonus_hp_max
            self.dano_magico -= equipado.bonus_atk_mana
            self.limite_inventario_base -= item.espaco
            feedback = f"Você desequipou {equipado.nome}."
            alteracao_efetuada = True

        else:
            equipado = self.equipa[slot]
            self.atk -= equipado.bonus_atk
            self.defesa -= equipado.bonus_def
            self.hp_max -= equipado.bonus_hp_max
            self.dano_magico -= equipado.bonus_atk_mana
            self.limite_inventario_base -= item.espaco

            self.equipa[slot] = item
            self.atk += item.bonus_atk
            self.defesa += item.bonus_def
            self.limite_inventario_base += item.espaco
            self.hp_max += item.bonus_hp_max
            self.dano_magico += item.bonus_atk_mana
            feedback = f"{equipado.nome} foi substituído por {item.nome}."
            alteracao_efetuada = True

        draw_window(term, x_janela, y_janela, width=werd, height=altura_feedback, text_content=feedback)
        time.sleep(1.8)
        clear_region_a(x_janela, y_janela, y_janela + altura_feedback, werd)

        return alteracao_efetuada

    def gerenciar_loja(self, x, y, largura):
        while True:
            clear()
            text_content = f"Gold: [{term.bold_yellow(str(self.gold))}]\n"
            text_content += "[1] Comprar Itens\n"
            text_content += "[2] Vender Itens\n"
            text_content += "[3] Sair da Loja"
            
            draw_window(term, x, y, width=largura, height=7, title="Loja", text_content=text_content)
            
            with term.location(x + 2, y + 5):
                escolha = input("> ")
            
            if escolha == "1":
                self.comprar_itens(x+largura, y, largura)
            elif escolha == "2":
                self.vender_itens(x+y, y, largura+25)
            elif escolha == "3":
                clear()
                return
            else:
                print("Opção inválida.", x, y + 8, largura)

    def comprar_itens(self, x, y, largura):
        while True:
            text_content = f"Gold: [{term.bold_yellow(str(self.gold))}]\n"
            text_content += "[1] Itens Consumíveis\n"
            text_content += "[2] Itens Produto\n"
            text_content += "[3] Itens Material\n"
            text_content += "[4] Voltar"
            
            draw_window(term, x, y, width=largura, height=9, title="Comprar", text_content=text_content)

            with term.location(x + 2, y + 6):
                escolha = input("> ")
            
            if escolha == "1":
                self.exibir_itens_por_tipo("Consumivel", x-largura, y + 7, largura)
            elif escolha == "2":
                self.exibir_itens_por_tipo("Produto", x-largura, y + 7, largura)
            elif escolha == "3":
                self.exibir_itens_por_tipo("Material", x-largura, y + 7, largura)
            elif escolha == '4':
                return
            else:
                pass

    def exibir_itens_por_tipo(self, tipo, x, y, largura):
        while True:
            itens = [i for i in TODOS_OS_ITENS.values() if i.tipo == tipo and i.comprável]
            text_content = f"Gold: [{term.bold_yellow(str(self.gold))}]\n"

            if not itens:
                text_content += f"Nenhum item do tipo '{tipo}' disponível.\n[0] Voltar"
            else:
                for idx, item in enumerate(itens, 1):
                    text_content += f"[{idx}] {item.nome} - [{item.preco}]\n"
                text_content += "[0] Voltar"

            altura = text_content.count("\n") + 4
            draw_window(term, x, y, width=largura, height=altura, title=f"Comprar {tipo}", text_content=text_content)

            with term.location(x + 2, y + altura - 2):
                try:
                    escolha = int(input(">"))
                    if escolha == 0:
                        return
                    item_escolhido = itens[escolha - 1]
                    if self.inventario_cheio():
                        with term.location(x + largura, y + 1):
                            print("Inventário cheio!")
                        time.sleep(1.5)
                        continue
                    if self.gold >= item_escolhido.preco:
                        self.gold -= item_escolhido.preco
                        self.inventario.append(item_escolhido)
                        with term.location(x=x+largura, y=y + 1):
                            print(f"Você comprou {item_escolhido.nome}.",)
                    else:
                        with term.location(x+largura, y+1):
                            print("Dinheiro insuficiente.")
                except (ValueError, IndexError):
                    pass
    
    def vender_itens(self, x, y, largura):
        while True:
            itens_vendaveis = [item for item in self.inventario if item.vendivel]
            contagem = defaultdict(int)
            for item in itens_vendaveis:
                contagem[item.nome] += 1

            nomes_unicos = list(contagem.keys())

            text_content = f"Gold: [{term.bold_yellow(str(self.gold))}]\n"
            if not nomes_unicos:
                text_content += "Você não tem itens vendáveis.\n[0] Voltar"
                altura = 6
            else:
                for i, nome in enumerate(nomes_unicos, 1):
                    item = TODOS_OS_ITENS[nome]
                    preco = item.preco // 2
                    text_content += f"[{i}] {nome} (x{contagem[nome]}) - [{preco}]\n"
                text_content += "[0] Voltar"
                altura = text_content.count("\n") + 4

            clear_region_a(x, y, y + altura + 4, largura)
            draw_window(term, x, y, width=largura, height=altura, title="Vender Itens", text_content=text_content)

            with term.location(x + 2, y + altura - 2):
                try:
                    escolha = int(input("> "))
                    if escolha == 0:
                        return
                    item_nome = nomes_unicos[escolha - 1]
                    item = TODOS_OS_ITENS[item_nome]
                    preco = item.preco // 2
                    self.gold += preco
                    self.inventario.remove(item)
                    with term.location(x=0, y=altura+1):
                        print(f"Você vendeu {item.nome} por {preco} moedas.")
                except (ValueError, IndexError):
                    with term.location(x=largura, y=y):
                        ("Opção inválida.", x, y + altura, largura)

    def hospital(self, x_, y_):
        with term.location(x=x_, y=y_):
            print("Você dormil essa noite")
        self.hp = self.hp_max
        self.stm = self.stm_max
        self.mana = self.mana_max
        time.sleep(3)

    def atake(self, alvo, x_janela, y_janela):
        atak_aleatorio = random.randint(1, 100)
        if self.stm >= 10:
            if self.aleatorio > atak_aleatorio:
                self.stm -= 10
                dano_ale = random.randint(int(self.atk - 3), int(self.atk + 3))
                meno_defsa = alvo.defesa // 4
                dano_final = int(self.buff_atk + dano_ale - meno_defsa)
                if dano_final <= 0:
                    dano_final = 1
                mensagem = f"{str(self.nome)} deu um dano de {str(dano_final)}\nno {str(alvo.nome)}"
                alvo.hp -= dano_final
                time.sleep(1)
            else:
                mensagem = f"{self.nome} errou o ataque"
                time.sleep(1)
        else:
            mensagem = "Você não tem ST suficiente"
            time.sleep(1)
        herd = 4
        draw_window(term, x_janela, y_janela, width=len(mensagem)-5, height=herd, text_content=mensagem)

    def craft(self, x, y, werd, herd=None):
        receitas = escolher_tipo_receita(0, 0, 35, 8)
        if receitas is None:
            return None

        receitas_lista = list(receitas.items())
        receitas_por_pagina = 5
        pagina = 0
        total_paginas = (len(receitas_lista) - 1) // receitas_por_pagina + 1

        while True:
            clear()
            inicio = pagina * receitas_por_pagina
            fim = inicio + receitas_por_pagina
            receitas_visiveis = receitas_lista[inicio:fim]

            # Montar menu
            linhas = [""]
            for i, (nome_item, receita) in enumerate(receitas_visiveis, start=1):
                requisitos = ", ".join(
                    f"{mat} x{qtd}" for mat, qtd in receita.materiais.items() if mat != "Quantidade"
                )
                linhas.append(f"[{i}] {nome_item}")
                linhas.append(f"   {requisitos}")

            linhas.append(f"\nPágina {pagina + 1}/{total_paginas}")
            linhas.append("Digite: '<' ou '>' para navegar páginas")
            linhas.append("Digite 'sair' para voltar")
            linhas.append("OU digite: número [quantidade] (ex: 2 4)")

            text_content = "\n".join(linhas)
            linhas_contadas = len(linhas)
            herd_auto = max(10, min(linhas_contadas + 4, 25))
            altura_janela = herd_auto if herd is None else herd_auto

            draw_window(term, x=x, y=y, width=werd, height=altura_janela + 1,
                        title="Crafting", text_content=text_content)

            with term.location(x + 2, y + altura_janela - 1):
                entrada = input("> ").strip().lower()

            if entrada == "sair":
                clear()
                return None

            if entrada == ">":
                if pagina < total_paginas - 1:
                    pagina += 1
                else:
                    draw_window(term, x, y + altura_janela, width=werd, height=3,
                                text_content="Você já está na última página.")
                    time.sleep(1.2)
                continue

            if entrada == "<":
                if pagina > 0:
                    pagina -= 1
                else:
                    draw_window(term, x, y + altura_janela, width=werd, height=3,
                                text_content="Você já está na primeira página.")
                    time.sleep(1.2)
                continue

            partes = entrada.split()
            if not partes or not partes[0].isdigit():
                draw_window(term, x, y + altura_janela, width=werd, height=3,
                            text_content="Entrada inválida.")
                time.sleep(1.2)
                continue

            indice_local = int(partes[0]) - 1
            qtd_fazer = int(partes[1]) if len(partes) > 1 and partes[1].isdigit() else 1

            if indice_local < 0 or indice_local >= len(receitas_visiveis):
                draw_window(term, x, y + altura_janela, width=werd, height=3,
                            text_content="Número inválido nesta página.")
                time.sleep(1.2)
                continue

            nome_item, receita = receitas_visiveis[indice_local]
            materiais = receita.materiais
            quantidade_por_receita = getattr(receita, "quantidade", 1)
            total_produzir = qtd_fazer * quantidade_por_receita

            faltando = []
            for mat, qtd in materiais.items():
                if mat == "Quantidade":
                    continue
                count = sum(1 for i in self.inventario if i.nome == mat)
                if count < qtd * qtd_fazer:
                    faltando.append(f"{mat} ({count}/{qtd * qtd_fazer})")

            if faltando:
                mensagem = "Materiais insuficientes:\n" + "\n".join(faltando)
                draw_window(term, x, y + altura_janela, width=werd,
                            height=len(faltando) + 5, text_content=mensagem)
                time.sleep(2)
                continue

            for mat, qtd in materiais.items():
                if mat == "Quantidade":
                    continue
                removidos = 0
                for item in list(self.inventario):
                    if item.nome == mat:
                        self.inventario.remove(item)
                        removidos += 1
                        if removidos >= qtd * qtd_fazer:
                            break

            if nome_item in TODOS_OS_ITENS:
                novo_item = TODOS_OS_ITENS[nome_item]
                espaco = self.inventario_espaco_restante()
                if espaco <= 0:
                    mensagem = "Inventário cheio! Não é possível fabricar."
                elif espaco < total_produzir:
                    mensagem = f"Espaço insuficiente! Você só tem {espaco} espaço(s)."
                else:
                    for _ in range(total_produzir):
                        self.inventario.append(novo_item)
                    mensagem = f"Você fabricou {total_produzir}x {nome_item}!"
            else:
                mensagem = f"Item '{nome_item}' não encontrado em TODOS_OS_ITENS."
                novo_item = None

            draw_window(term, x, y + altura_janela, width=werd, height=4,
                        text_content=mensagem)
            time.sleep(2)
            continue

    def forja(self, x, y, werd, herd=None):
        receitas = escolher_tipo_receita_for(0, 0, 35, 8)
        if receitas is None:
            return None

        receitas_lista = list(receitas.items())
        receitas_por_pagina = 5
        pagina = 0
        total_paginas = (len(receitas_lista) - 1) // receitas_por_pagina + 1

        while True:
            clear()
            inicio = pagina * receitas_por_pagina
            fim = inicio + receitas_por_pagina
            receitas_visiveis = receitas_lista[inicio:fim]
            linhas = [""]
            for i, (nome_item, receita) in enumerate(receitas_visiveis, start=1):
                requisitos = ", ".join(
                    f"{mat} x{qtd}" for mat, qtd in receita.materiais.items() if mat != "Quantidade"
                )
                linhas.append(f"[{i}] {nome_item}")
                linhas.append(f"   {requisitos}")

            linhas.append(f"\nPágina {pagina + 1}/{total_paginas}")
            linhas.append("Digite: '<' ou '>' para navegar páginas")
            linhas.append("Digite 'sair' para voltar")
            linhas.append("OU digite: número [quantidade] (ex: 2 4)")

            text_content = "\n".join(linhas)
            linhas_contadas = len(linhas)
            herd_auto = max(10, min(linhas_contadas + 4, 25))
            altura_janela = herd_auto if herd is None else herd_auto

            draw_window(term, x=x, y=y, width=werd, height=altura_janela + 1,
                        title="Crafting", text_content=text_content)

            with term.location(x + 2, y + altura_janela - 1):
                entrada = input("> ").strip().lower()

            if entrada == "sair":
                clear()
                return None

            if entrada == ">":
                if pagina < total_paginas - 1:
                    pagina += 1
                else:
                    draw_window(term, x, y + altura_janela, width=werd, height=3,
                                text_content="Você já está na última página.")
                    time.sleep(1.2)
                continue

            if entrada == "<":
                if pagina > 0:
                    pagina -= 1
                else:
                    draw_window(term, x, y + altura_janela, width=werd, height=3,
                                text_content="Você já está na primeira página.")
                    time.sleep(1.2)
                continue

            partes = entrada.split()
            if not partes or not partes[0].isdigit():
                draw_window(term, x, y + altura_janela, width=werd, height=3,
                            text_content="Entrada inválida.")
                time.sleep(1.2)
                continue

            indice_local = int(partes[0]) - 1
            qtd_fazer = int(partes[1]) if len(partes) > 1 and partes[1].isdigit() else 1

            if indice_local < 0 or indice_local >= len(receitas_visiveis):
                draw_window(term, x, y + altura_janela, width=werd, height=3,
                            text_content="Número inválido nesta página.")
                time.sleep(1.2)
                continue

            nome_item, receita = receitas_visiveis[indice_local]
            materiais = receita.materiais
            quantidade_por_receita = getattr(receita, "quantidade", 1)
            total_produzir = qtd_fazer * quantidade_por_receita

            faltando = []
            for mat, qtd in materiais.items():
                if mat == "Quantidade":
                    continue
                count = sum(1 for i in self.inventario if i.nome == mat)
                if count < qtd * qtd_fazer:
                    faltando.append(f"{mat} ({count}/{qtd * qtd_fazer})")

            if faltando:
                mensagem = "Materiais insuficientes:\n" + "\n".join(faltando)
                draw_window(term, x, y + altura_janela, width=werd,
                            height=len(faltando) + 5, text_content=mensagem)
                time.sleep(2)
                continue

            for mat, qtd in materiais.items():
                if mat == "Quantidade":
                    continue
                removidos = 0
                for item in list(self.inventario):
                    if item.nome == mat:
                        self.inventario.remove(item)
                        removidos += 1
                        if removidos >= qtd * qtd_fazer:
                            break

            if nome_item in TODOS_OS_ITENS:
                novo_item = TODOS_OS_ITENS[nome_item]
                espaco = self.inventario_espaco_restante()
                if espaco <= 0:
                    mensagem = "Inventário cheio! Não é possível fabricar."
                elif espaco < total_produzir:
                    mensagem = f"Espaço insuficiente! Você só tem {espaco} espaço(s)."
                else:
                    for _ in range(total_produzir):
                        self.inventario.append(novo_item)
                    mensagem = f"Você fabricou {total_produzir}x {nome_item}!"
            else:
                mensagem = f"Item '{nome_item}' não encontrado em TODOS_OS_ITENS."
                novo_item = None

            draw_window(term, x, y + altura_janela, width=werd, height=4,
                        text_content=mensagem)
            time.sleep(2)
            continue


def escolher_tipo_receita(x, y, largura, altura):
    while True:
        clear()
        menu = '''Escolha o Tipo de item que você quer fazer\n[1] Equipamentos\n[2] Materiais'''
        draw_window(term, x=x, y=y, width = largura, height = altura, text_content=menu)
        with term.location(x=x+1, y=y+5):
            escolha = input("> ").strip()
        if escolha == "1":
            return RECEITAS_EQUIPAMENTOS
        elif escolha == "2":
            return RECEITAS_MATERIAIS
        elif escolha.lower() == "sair":
            clear()
            return None
        else:
            with term.location(x=x+1, y=y+5):
                print("Escolha inválida, tente novamente.")

def escolher_tipo_receita_for(x, y, largura, altura):
    while True:
        clear()
        menu = '''Escolha o Tipo de item que você quer fazer\n[1] Consumiveis\n[2] Minerios'''
        draw_window(term, x=x, y=y, width = largura, height = altura, text_content=menu)
        with term.location(x=x+1, y=y+5):
            escolha = input("> ").strip()
        if escolha == "2":
            return RECEITAS_MINERIOS
        elif escolha == "1":
            return RECEITAS_CONSUMIVEIS
        elif escolha.lower() == "sair":
            clear()
            return None
        else:
            with term.location(x=x+1, y=y+5):
                print("Escolha inválida, tente novamente.")

def remover_equipamento(player, slot):
    item = player.equipa.get(slot)
    if item:
        # Remove do equipamento
        player.equipa[slot] = None
        # Remove do inventário se estiver lá
        if item in player.inventario:
            player.inventario.remove(item)
        # Caso seja tocha, apagar efeitos
        if item.nome.lower() == "tocha":
            player.tocha_acesa = False
            player.tocha_duracao = 0
