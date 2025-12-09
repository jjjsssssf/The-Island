from classe_do_inimigo import *
from classe_do_jogador import *
from classe_arts import *
player_b = jogador(nome="", hp_max=100, atk=15, niv=1, xp_max=100, defesa=10, gold=0, stm_max=100, intt=10, mn_max=100,d_m=20, art_player=art.necro, skin=0,skin_nome='')
art = art_ascii()
def esqueleto(player_b, art):
    try:
        multiplicador_dif = player_b.dificuldade[player_b.dificuldade_atual]["niv"]
    except KeyError:
        multiplicador_dif = 1
    nome = 'Esqueleto'
    atk_1 = 'Soco'
    atk_2 = 'Espadada'
    hp = int(20 * multiplicador_dif * player_b.niv)
    atk = int(5 * multiplicador_dif * player_b.niv)
    defesa = int(3 * multiplicador_dif * player_b.niv)
    xp = int(35 * player_b.niv // 2)
    gold = int(0 * player_b.niv )
    niv = int(1 * multiplicador_dif * player_b.niv)
    art = art.esqueleto
    return{
        'nome': nome,
        'atk_1': atk_1,
        'atk_2': atk_2,
        'hp': hp,
        'atk': atk,
        'defesa': defesa,
        'xp': xp,
        'niv': niv,
        'gold':gold,
        'art': art
    }

def zumbi(player_b, art):
    try:
        multiplicador_dif = player_b.dificuldade[player_b.dificuldade_atual]["niv"]
    except KeyError:
        multiplicador_dif = 1
    nome = 'Zumbi'
    atk_1 = 'Arranharr'
    atk_2 = 'Morder'
    hp = int(20 * multiplicador_dif * player_b.niv)
    atk = int(5 * multiplicador_dif * player_b.niv)
    defesa = int(4 * multiplicador_dif * player_b.niv)
    niv = int(1 * multiplicador_dif * player_b.niv)
    xp = int(40 * player_b.niv // 2)
    gold = int(0 * player_b.niv)
    art = art.zombie
    return{
        'nome': nome,
        'atk_1': atk_1,
        'atk_2': atk_2,
        'hp': hp,
        'atk': atk,
        'defesa': defesa,
        'xp': xp,
        'niv': niv,
        'gold':gold,
        'art': art
    }

def sun(player_b, art):
    try:
        multiplicador_dif = player_b.dificuldade[player_b.dificuldade_atual]["niv"]
    except KeyError:
        multiplicador_dif = 1
    nome = 'Suny'
    atk_1 = 'Morder'
    atk_2 = 'Bola de Fogo'
    hp = int(60 * multiplicador_dif * player_b.niv)
    atk = int(10 * multiplicador_dif * player_b.niv)
    defesa = int(5 * multiplicador_dif * player_b.niv)
    niv = int(1 * multiplicador_dif * player_b.niv)
    xp = int(50 * player_b.niv // 2)
    gold = int(0 * player_b.niv)
    art = art.suny
    return{
        'nome': nome,
        'atk_1': atk_1,
        'atk_2': atk_2,
        'hp': hp,
        'atk': atk,
        'defesa': defesa,
        'xp': xp,
        'niv': niv,
        'gold':gold,
        'art': art
    }

def sers(player_b, art):
    try:
        multiplicador_dif = player_b.dificuldade[player_b.dificuldade_atual]["niv"]
    except KeyError:
        multiplicador_dif = 1
    nome = 'Serafas'
    atk_1 = 'Espiritos'
    atk_2 = 'Maldição'
    hp = int(50 * multiplicador_dif * player_b.niv)
    atk = int(20 * multiplicador_dif * player_b.niv)
    defesa = int(2 * multiplicador_dif * player_b.niv)
    niv = int(1 * multiplicador_dif * player_b.niv)
    xp = int(50 * player_b.niv // 2)
    gold = int(0 * player_b.niv)
    art = art.serafas
    return{
        'nome': nome,
        'atk_1': atk_1,
        'atk_2': atk_2,
        'hp': hp,
        'atk': atk,
        'defesa': defesa,
        'xp': xp,
        'niv': niv,
        'gold':gold,
        'art': art
    }


