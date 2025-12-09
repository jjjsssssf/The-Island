import os
import time
import threading
import random
from jogo import *
from classe_arts import draw_window, term, clear, mini_mapa_
from maps import *
from classe_arts import art_ascii, Cores
from classe_do_inventario import TODOS_OS_ITENS
# -----------------------------------------
# CONFIGURAÇÃO INICIAL
# -----------------------------------------
ascii = art_ascii()
mapas = mini_mapa_()
C = Cores()
jj = jogador(
    nome="", hp_max=100, atk=15, niv=1, xp_max=100, defesa=10,
    gold=0, stm_max=100, intt=10, mn_max=100, d_m=20,
    art_player=ascii.necro, skin="0", skin_nome=''
)
ee = inimigo(nome="", hp_max=0, atk=0, niv=0, xp=0, defesa=0, gold=0, art_ascii="", atk1="", atk2="")

# -----------------------------------------
# FUNÇÕES DE LOADING E MAPA
# -----------------------------------------
def tela_de_loading(term, mensagem="Carregando Mapa..."):
    clear()
    draw_window(term, x=25, y=10, width=40, height=10, title="Aguarde")
    with term.location(30, 14):
        print(mensagem)
    while not getattr(tela_de_loading, "terminar", False):
        time.sleep(0.1)

def gerar_mapa_assincrono(term, largura, altura, seed):
    resultado = {}

    def gerar():
        resultado["mapa"] = mapa_procedural(nome="Mundo", largura=largura, altura=altura, seed=seed)
        tela_de_loading.terminar = True 

    thread = threading.Thread(target=gerar)
    thread.start()
    tela_de_loading.terminar = False
    tela_de_loading(term)  # mostra a tela fixa
    thread.join()
    return resultado["mapa"]

# -----------------------------------------
# MENU INICIAL
# -----------------------------------------
def menu_inicial(x_l, y_l):
    while True:
        clear()
        menu_art = ascii.titulo
        opcoes = "[1] Jogar\n[2] Carregar\n[3] Sair"
        herd = menu_art.count("\n")
        draw_window(term, x=x_l, y=y_l, width=90, height=25, text_content=menu_art)
        draw_window(term, x=x_l+25, y=y_l+herd+1, width=25, height=8, text_content=opcoes)

        with term.location(x=x_l+27, y=y_l+herd+6):
            escolha = input(">")

        if escolha == "1":
            # Limpa saves antigos
            limpar_todos_os_saves()
            limpar_todos_os_player()

            # Escolhas do jogador
            dificuldade_key = escolher_dificudade(x_l, y_l, menu_art)
            nome = solicitar_nome(x_l, y_l, menu_art)
            mapa_x, mapa_y = solicitar_tamanho(x_l, y_l, menu_art)
            skin_arte, cor_final, skin_nome = escolher_personagem(x_l, y_l)


            # Criação do jogador
            jj = jogador(
                nome=nome, hp_max=50, atk=10, niv=1, xp_max=100, defesa=0,
                gold=0, stm_max=100, intt=0, mn_max=50, d_m=10,
                art_player=skin_arte, skin=cor_final, skin_nome=skin_nome,
                mapa_x=mapa_x, mapa_y=mapa_y, volume = jj.volume
            )
            jj.dificuldade_atual = dificuldade_key
            jj.inventario.extend([
                TODOS_OS_ITENS['Bancada'],
                TODOS_OS_ITENS['Tocha'],
                TODOS_OS_ITENS['Pá'],
                TODOS_OS_ITENS['Escada']
            ])

            # Configuração do mapa
            seed_random = random.randint(1, 9999)
            x_random = random.randint(1, jj.mapa_x)
            y_random = random.randint(1, jj.mapa_y)
            jj.seed = seed_random
            config = gerar_mapa_assincrono(term, largura=jj.mapa_x, altura=jj.mapa_y, seed=jj.seed)
            parar_musica()
            mini_mapa(
                x_l=0, y_l=0,
                player=jj,
                mapas_=config["mapa"],
                camera_w=50, camera_h=25,
                x_p=x_random, y_p=y_random,
                menager="",
                cores_custom=config.get("cores"),
                obstaculos_custom=config.get("obstaculos"),
                mapa_nome=config.get("nome")
            )

        elif escolha == "2":
            player_carregado, mapas_carregados = carregar_jogo_global(filename="save_global.json")
            if player_carregado:
                jj = player_carregado
                ESTADO_MAPAS = mapas_carregados
                estado_mapa_salvo = ESTADO_MAPAS.get(jj.mapa_atual)

                if estado_mapa_salvo:
                    mapa_art_para_load = estado_mapa_salvo["mapa_art"]
                    cores_custom = estado_mapa_salvo.get("cores")
                    obstaculos_custom = estado_mapa_salvo.get("obstaculos")
                else:
                    limpar_todos_os_saves()
                    limpar_todos_os_player()
                    config = mapa_procedural(nome=jj.mapa_atual, largura=jj.mapa_x, altura=jj.mapa_y, seed=42)
                    mapa_art_para_load = config["mapa"]
                    cores_custom = config.get("cores")
                    obstaculos_custom = config.get("obstaculos")

                x_p_load = jj.x_mapa
                y_p_load = jj.y_mapa
                mini_mapa(
                    x_l=0,
                    y_l=0,
                    player=jj,
                    mapas_=mapa_art_para_load,
                    camera_w=50, camera_h=25,
                    x_p=x_p_load,
                    y_p=y_p_load,
                    menager="",
                    mapa_nome=jj.mapa_atual,
                    cores_custom=cores_custom,
                    obstaculos_custom=obstaculos_custom,
                    ESTADO_GLOBAL_LOAD=mapas_carregados
                )
            else:
                with term.location(x_l+27, y=y_l+herd+6):
                    print(term.red("Nenhum save encontrado!"))
                    input("Pressione ENTER para continuar...")

        elif escolha == "3":
            parar_musica()
            exit()

# -----------------------------------------
# FUNÇÕES AUXILIARES
# -----------------------------------------
def solicitar_nome(x_l, y_l, menu_art):
    while True:
        clear()
        prompt = "Qual será seu Nome:\n(max 8 caracteres)"
        num_linhas = prompt.count("\n") + 4
        draw_window(term, x=x_l, y=y_l, width=90, height=25, text_content=menu_art)
        draw_window(term, x=x_l+25, y=y_l+num_linhas+3, width=27, height=num_linhas, text_content=prompt)

        with term.location(x=x_l+26, y=y_l+num_linhas+6):
            nome = input(">")

        if len(nome) > 8:
            mostrar_mensagem(x_l+26, y_l+num_linhas+6, "Nome muito extenso")
        elif len(nome) < 1:
            mostrar_mensagem(x_l+26, y_l+num_linhas+6, "Digite pelo menos 1 letra")
        else:
            return nome

def solicitar_tamanho(x_l, y_l, menu_art):
    while True:
        clear()
        prompt = "Escolha o Tamanho do Mapa\n[1] Pequeno (500x250)\n[2] Médio (800x400)\n[3] Grande (1100x550)"
        num_linhas = prompt.count("\n") + 4        
        draw_window(term, x=x_l, y=y_l, width=90, height=25, text_content=menu_art)
        draw_window(term, x=x_l+25, y=y_l+num_linhas+1, width=30, height=num_linhas, text_content=prompt)

        with term.location(x=x_l+26, y=y_l+num_linhas+6):
            escolha = input(">")

        if escolha == "1":
            return 250, 125
        elif escolha == "2":
            return 500, 250
        elif escolha == "3":
            return 800, 400
        else:
            mostrar_mensagem(x_l+26, y_l+num_linhas+6, "Opção inválida! Escolha 1, 2 ou 3")

def escolher_personagem(x_l, y_l):
    personagens = {
        "1": {"nome": "necro", "arte": ascii.necro},
        "2": {"nome": "guerreiro", "arte": ascii.guerriro},
        "3": {"nome": "mago", "arte": ascii.mago}
    }
    while True:
        clear()
        draw_window(term, x=x_l, y=y_l, width=90, height=25)
        draw_window(term, x=x_l+2, y=y_l+1, width=25, height=11, title="1", text_content=ascii.necro)
        draw_window(term, x=x_l+32, y=y_l+1, width=25, height=11, title="2", text_content=ascii.guerriro)
        draw_window(term, x=x_l+64, y=y_l+1, width=25, height=11, title="3", text_content=ascii.mago)

        with term.location(x=x_l+2, y=y_l+12):
            escolha = input("Escolha uma Skin: ")

        if escolha in personagens:
            skin_data = personagens[escolha]
            skin_arte = skin_data["arte"]
            skin_nome = skin_data["nome"]
            
            caractere = solicitar_caractere(x_l, y_l)
            cor_final = escolher_cor(caractere, x_l, y_l)
            
            return skin_arte, cor_final, skin_nome

def solicitar_caractere(x_l, y_l):
    while True:
        with term.location(x=x_l+2, y=y_l+13):
            print("Escolha um caractere do seu personagem: ")
        with term.location(x=x_l+2, y=y_l+14):
            caractere = input(">")
        if len(caractere) == 1:
            return caractere
        else:
            with term.location(x=x_l+2, y=y_l+15):
                print("Use apenas UM caractere")

def escolher_cor(caractere, x_l, y_l):
    cores = {
        "1": C.AZUL,
        "2": C.AMARELO,
        "3": C.VERDE,
        "4": C.VERMELHO,
        "5": term.magenta,
        "6": term.cyan,
        '7': term.white
    }
    while True:
        with term.location(x=x_l+2, y=y_l+15):
            print("Escolha um Cor: ")
        with term.location(x=x_l+2, y=y_l+16):
            print(f"{C.AZUL}[1]Azul {C.AMARELO}[2]Amarelo {C.VERDE}[3]Verde {C.VERMELHO}[4]Vermelho {term.magenta}[5]Roxo {term.cyan}[6]Ciano {term.white}[7]Branco")
        with term.location(x=x_l+2, y=y_l+17):
            escolha = input(">")
        if escolha in cores:
            return f"{cores[escolha]}{caractere}{C.RESET}"

def escolher_dificudade(x_l, y_l, menu_art):
    while True:
        clear()
        prompt = "Escolha a Dificuldade\n[1] Fácil (x0.5)\n[2] Normal (x1.0)\n[3] Difícil (x2.0)"
        num_linhas = prompt.count("\n") + 4        
        draw_window(term, x=x_l, y=y_l, width=90, height=25, text_content=menu_art)
        draw_window(term, x=x_l+25, y=y_l+num_linhas+1, width=27, height=num_linhas, text_content=prompt)

        with term.location(x=x_l+26, y=y_l+num_linhas+6):
            dif = input(">")
            
        if dif == '1':
            return 'Facil'
        elif dif == '2':
            return 'Normal'
        elif dif == '3':
            return 'Dificil'
        else:
            mostrar_mensagem(x_l+26, y_l+num_linhas+6, "Opção inválida. Use 1, 2 ou 3.")

def mostrar_mensagem(x, y, mensagem):
    with term.location(x, y):
        print(mensagem)

# -----------------------------------------
# INÍCIO DO JOGO
# -----------------------------------------
clear()
menu_inicial(x_l=0, y_l=0)
