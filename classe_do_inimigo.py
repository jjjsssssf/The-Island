from classe_arts import draw_window, term, art_ascii
import random, os, time
def clear():
    os.system("cls" if os.name == "nt" else "clear")

class inimigo:
    def __init__(self, nome, hp_max, atk, niv, xp, defesa, gold, art_ascii, atk1, atk2):
        self.nome = nome
        self.hp_max = hp_max
        self.hp = self.hp_max
        self.art_ascii = art_ascii
        self.atk = atk
        self.niv = niv
        self.xp = xp
        self.defesa = defesa
        self.gold = gold
        self.atk1 = atk1
        self.atk2 = atk2
        self.aleatorio_ = 50

    def status_art(self, x_janela, y_janela, wend, herd):
        status_art = self.art_ascii
        draw_window(term, x=x_janela, y=y_janela, width=wend, height=herd, text_content=status_art)
        self.status(x_janela=x_janela, y_janela=y_janela+herd)

    def status_art_boss(self, x_janela, y_janela, wend, herd):
        status_art = self.art_ascii
        draw_window(term, x=x_janela, y=y_janela, width=wend, height=herd, text_content=status_art)

    def status(self, x_janela, y_janela):
        draw_window(term, x=x_janela, y=y_janela, width=31, height=6)
        with term.location(x=x_janela+1, y=y_janela+1):
            print(f"Nome: {term.bold_gray(self.nome)} Niv: [{term.bold_cyan(str(self.niv))}]")
        with term.location(x=x_janela+1, y=y_janela+2):
            print(f"HP: [{term.bold_green(str(self.hp))}]/[{term.green(str(self.hp_max))}]")
        with term.location(x=x_janela+1, y=y_janela+3):
            print(f"ATK: [{term.bold_red(str(self.atk))}] DEF:[{term.bold_purple(str(self.defesa))}]")
        with term.location(x=x_janela+1, y=y_janela+4):
            print(f"[{term.yellow(str(self.atk1))}]-[{term.yellow(str(self.atk2))}]")

    def ataque_1(self, alvo,x_janela,y_janela):
        atak_aleatorio = random.randint(1, 100)
        if self.aleatorio_ > atak_aleatorio:
            dano_ale = random.randint(int(self.atk - 3), int(self.atk + 3))
            meno_defsa = alvo.defesa + alvo.buff_def
            mm = meno_defsa // 4
            dano_final = int(dano_ale - mm)
            if dano_final <= 0:
                dano_final = 1
            mensagem = f"""{str(self.nome)} usou {str(self.atk1)} em {str(alvo.nome)}\ndeu um dano de {str(dano_final)}"""
            alvo.hp -= dano_final
        else:
            mensagem = f"{self.nome} errou o ataque"
        herd = 4
        draw_window(term, x_janela, y_janela, width=len(mensagem)-6, height=herd, text_content=mensagem)

    def ataque_2(self, alvo,x_janela,y_janela):
        atak_aleatorio = random.randint(1, 100)
        if self.aleatorio_ > atak_aleatorio:
            dano_ale = random.randint(int(self.atk - 3), int(self.atk + 3))
            meno_defsa = alvo.defesa + alvo.buff_def // 4 
            dano_final = int(1.5 * dano_ale - meno_defsa)
            if dano_final <= 0:
                dano_final = 1
            mensagem = f"""{str(self.nome)} usou {str(self.atk2)} em {str(alvo.nome)}\ndeu um dano de {str(dano_final)}"""
            alvo.hp -= dano_final
            time.sleep(1)
        else:
            mensagem = f"{self.nome} errou o ataque"
            time.sleep(1)
        herd = 4
        draw_window(term, x_janela, y_janela, width=len(mensagem)-6, height=herd, text_content=mensagem)

    def ataque_selec(self, alvo, x_janela, y_janela):
        atk = ["atk1", "atk2"]
        atk_ = random.choice(atk)
        atk = atk_
        if atk == "atk1":
            self.ataque_1(alvo, x_janela=x_janela, y_janela=y_janela)
        elif atk == "atk2":
            self.ataque_2(alvo, x_janela=x_janela, y_janela=y_janela)
