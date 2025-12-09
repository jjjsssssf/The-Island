from classe_arts import draw_window, term, clear
import random, time, string
from classe_do_jogador import jogador
from classe_do_inimigo import inimigo
from classe_arts import art_ascii
import msvcrt
def limpar_buffer_teclas():
    while msvcrt.kbhit():
        msvcrt.getch()
ascii = art_ascii()
player_b = jogador(nome="", hp_max=100, atk=15, niv=1, xp_max=100, defesa=10, gold=0, stm_max=100, intt=10, mn_max=100,d_m=20, art_player=ascii.necro, skin=0,skin_nome='')
inimigo_b = inimigo(nome="", hp_max=0, atk=0, niv=0, xp=0, defesa=0, gold=0, art_ascii='',atk1="",atk2="")

def batalha(player_b,inimigo_b):
    with term.fullscreen():
        while True:
            clear()
            x_jogador = 30
            inimigo_b.status_art(x_janela=31, y_janela=0, wend = 31, herd = 11)
            player_b.status_batalha_art(x_janela=0, y_janela=0, wend = 31, herd = 11)
            acoes = "[1]Atacar\n[2]Magias\n[3]Inventario\n[4]Fugir\n"
            acoes_text= acoes.count('\n')+1
            herd = acoes_text + 2
            draw_window(term, x=x_jogador+32, y=0, width=25, height=herd, title="Ações",text_content=acoes)
            with term.location(x=x_jogador+33, y=5):
                escolha = input(">")
            acao_valida = False
            if escolha == "4":
                with term.location(x=x_jogador+32, y=7):
                    print(term.bold_red("Você fugiu da batalha."))
                    player_b.buff_atk = 0
                    player_b.buff_def = 0
                time.sleep(2)
                return True
            elif escolha == "1":
                player_b.atake(inimigo_b, x_janela=0, y_janela=17)
                acao_valida = True
            elif escolha == "2":
                acao_valida = player_b.menu_magias(x_menu=x_jogador+32, y_menu=7, batalha=True, alvo=inimigo_b)
            elif escolha == "3":
                acao_valida = player_b.inventario_(x=x_jogador+32, y=7,werd=35, herd=9,batalha=True)
            else:
                with term.location(x=x_jogador+32, y=7):
                    print("Escolha inválida. Tente novamente.")
                time.sleep(2)
                continue            
            if acao_valida:
                if inimigo_b.hp <= 0:
                    with term.location(x=x_jogador+32, y=7):
                        print(term.clear_eol + f"{player_b.nome} venceu a batalha!")
                    time.sleep(3)
                    player_b.gold += inimigo_b.gold
                    player_b.xp += inimigo_b.xp
                    player_b.buff_atk = 0
                    player_b.buff_def = 0
                    player_b.add_xp(inimigo_b.xp)

                    return True
                inimigo_b.ataque_selec(player_b, x_janela=31, y_janela=17)
                with term.location(x=x_jogador+32, y=7):
                    input(">")
                if player_b.hp <= 0:
                    with term.location(x=x_jogador+32, y=7):
                        print(f"{inimigo_b.nome} venceu a batalha!")
                    time.sleep(3)
                    return False

def batalha_cut(player_b, inimigo_b):
    with term.fullscreen():
        while True:
            print(term.clear)
            x_jogador = 30
            inimigo_b.status_art(x_janela=31, y_janela=0, wend = 31, herd = 11)
            player_b.status_batalha_art(x_janela=0, y_janela=0, wend = 31, herd = 11)
            acoes = "[1]Atacar\n[2]Magias\n[3]Inventario\n"
            acoes_text= acoes.count('\n')+1
            herd = acoes_text + 2
            draw_window(term, x=x_jogador+32, y=0, width=25, height=herd, title="Ações",text_content=acoes)
            with term.location(x=x_jogador+33, y=4):
                escolha = input(">")
            acao_valida = False
            if escolha == "1":
                player_b.atake(inimigo_b, x_janela=0, y_janela=17)
                acao_valida = True
            elif escolha == "2":
                acao_valida = player_b.menu_magias(x_menu=x_jogador+32, y_menu=7, batalha=True, alvo=inimigo_b)
            elif escolha == "3":
                acao_valida = player_b.inventario_(x=x_jogador+32, y=0, werd=35, herd=0, batalha=True)
            else:
                with term.location(x=x_jogador+32, y=7):
                    print("Escolha inválida. Tente novamente.")
                time.sleep(2)
                continue            
            if acao_valida:
                if inimigo_b.hp <= 0:
                    with term.location(x=x_jogador+32, y=7):
                        print(term.clear_eol + f"{player_b.nome} venceu a batalha!")
                    time.sleep(3)
                    player_b.gold += inimigo_b.gold
                    player_b.xp += inimigo_b.xp
                    player_b.buff_atk = 0
                    player_b.buff_def = 0
                    player_b.add_xp(inimigo_b.xp)
                    return True
                inimigo_b.ataque_selec(player_b, x_janela=31, y_janela=17)
                with term.location(x=x_jogador+32, y=7):
                    input(">")
                if player_b.hp <= 0:
                    with term.location(x=x_jogador+32, y=7):
                        print(f"{inimigo_b.nome} venceu a batalha!")
                    time.sleep(3)
                    return False
