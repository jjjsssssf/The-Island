# eventos_mundo
from funcao_mapa import *
from batalha import *
from classe_do_inimigo import inimigo

def processar_eventos_mundo(player, mapa_art, periodo_atual, ESTADO_MAPAS, mapa_id, save_filename):
    total = player.x_mapa * player.y_mapa
    if periodo_atual == "noite":
        adicionar_caracteres_aleatorios(mapa_id,ESTADO_MAPAS[mapa_id],caracteres_quantidades={'G': int(total * 0.0006), 'F': int(total * 0.0003)})
        inimigo_chars = ['F', 'R']
        obstaculos_inimigo = {'#', '♣', '&', "C", '‼', '¥', 'o', '0', '1', '„', '♠', 'x', '$', '+', 'P', 'N', 'I', 'G', 'F', '!', '/', 'O', '@', '%', '\\'}
        mover_inimigos_para_jogador(mapa_art,player=player,obstaculos=obstaculos_inimigo,inimigo_chars=inimigo_chars,estado_mapa=ESTADO_MAPAS[mapa_id],raio_visao=7)

    elif periodo_atual == "dia":
        remover_caracteres(mapa_art, caracteres_para_remover=['F', 'G'])
    salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])

def processar_eventos_caverna(player, mapa_art, periodo_atual, ESTADO_MAPAS, mapa_id, save_filename):
    obstaculos_inimigo = ['o', 'G', 'F', 'B', f'{player.skin}','u',"#",'c', "@", '\\']
    inimigo_chars = ["F","G"]
    boss = ['@']
    mover_inimigos_para_jogador(mapa_art, player=player, obstaculos=obstaculos_inimigo, inimigo_chars=boss, estado_mapa=ESTADO_MAPAS[mapa_id], raio_visao=10)
    mover_inimigos_para_jogador(mapa_art, player=player, obstaculos=obstaculos_inimigo, inimigo_chars=inimigo_chars, estado_mapa=ESTADO_MAPAS[mapa_id], raio_visao=5)
    salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
