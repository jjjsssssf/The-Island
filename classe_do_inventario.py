from collections import defaultdict

class Item:
    def __init__(self, nome, tipo, nivel = 0, bonus_hp=0, espaco = 0,bonus_stm = 0,bonus_mana=0, bonus_atk=0, bonus_def=0, bonus_atk_mana=0, bonus_hp_max=0,preco=0, slot_equip=None, vendivel=True, comprável=True, duracao_max=0):
        self.nome = nome
        self.vendivel = vendivel
        self.comprável = comprável
        self.tipo = tipo
        self.bonus_hp = bonus_hp
        self.bonus_hp_max = bonus_hp_max
        self.bonus_mana = bonus_mana
        self.bonus_stm = bonus_stm
        self.bonus_atk = bonus_atk
        self.preco = preco
        self.bonus_atk_mana = bonus_atk_mana
        self.bonus_def = bonus_def
        self.slot_equip = slot_equip
        self.nivel = nivel
        self.duracao_max = duracao_max
        self.espaco = espaco

    def __repr__(self):
        return f"Item(nome='{self.nome}', tipo='{self.tipo}', comprável={self.comprável})"

TODOS_OS_ITENS = {
    ###ARMAS
    "Espada": Item(nome=f"Espada", tipo="Equipavel", preco=100, bonus_atk=10, slot_equip="m_pri", nivel=1),
    "Vara de Pesca": Item(nome=f"Vara de Pesca", tipo="Equipavel", preco=100, bonus_atk=2, slot_equip="m_seg", nivel=1),
    "Picareta/Madeira": Item(nome='Picareta/Madeira', tipo='Equipavel', preco=100, bonus_def=2, slot_equip="m_pri",nivel=1),
    "Picareta/Pedra": Item(nome='Picareta/Pedra', tipo='Equipavel', preco=200, bonus_def=4, slot_equip="m_pri",nivel=1),
    "Pá": Item(nome='Pá', tipo='Equipavel', preco=100, slot_equip="m_seg", nivel=1),
    "Enchada": Item(nome='Enchada', tipo='Equipavel', preco=100, slot_equip="m_seg", nivel=1),
    'Machado/Pedra': Item(nome='Machado/Pedra', tipo='Equipavel', preco=200, bonus_atk=4, slot_equip="m_pri", nivel=1),
    'Machado/Madeira': Item(nome='Machado/Madeira', tipo='Equipavel', preco=100, bonus_atk=2, slot_equip="m_pri", nivel=1),
    'Tocha': Item(nome='Tocha', tipo='Equipavel', preco=100, slot_equip="m_ter", duracao_max=60),
    'Mochila': Item(nome='Mochila', tipo='Equipavel', espaco = 50,preco=100, slot_equip="mochila", duracao_max=60),
    ##CONS
    "Fruta": Item(nome="Fruta", tipo="Consumivel", preco=30, bonus_hp=20, bonus_stm=15),
    "Salada de Frutas": Item(nome="Salada de Frutas", tipo="Consumivel", preco=150, bonus_hp=50, bonus_stm=50),
    "Pão": Item(nome="Pão", tipo="Consumivel", preco=50, bonus_hp=40, bonus_stm=30),
    "Leite": Item(nome="Leite", tipo="Consumivel", preco=60, bonus_hp=25, bonus_stm=25),
    "Ovo": Item(nome="Ovo", tipo="Consumivel", preco=40, bonus_hp=15, bonus_stm=10),
    "Queijo": Item(nome="Queijo", tipo="Consumivel", preco=120, bonus_hp=50, bonus_stm=50),
    "Sopa de Legumes": Item(nome="Sopa de Legumes", tipo="Consumivel", preco=180, bonus_hp=120, bonus_stm=100),
    "Bolo de Milho": Item(nome="Bolo de Milho", tipo="Consumivel", preco=220, bonus_hp=100, bonus_stm=80),
    "Torta de Abobora": Item(nome="Torta de Abobora", tipo="Consumivel", preco=300, bonus_hp=200, bonus_stm=150),
    "Pizza": Item(nome="Pizza", tipo="Consumivel", preco=500, bonus_hp=350, bonus_stm=30),
    "Elixir": Item(nome="Elixir", tipo="Consumivel", preco=400, bonus_mana=200),
    "Poção de Cura": Item(nome="Poção de Cura", tipo="Consumivel", preco=350, bonus_hp=250),
    "Suco": Item(nome="Suco", tipo="Consumivel", preco=250, bonus_stm=150),
    "Ovo Frito": Item(nome="Ovo Frito", tipo="Consumivel", preco=120, bonus_hp=80, bonus_stm=60),
    "Tilapia": Item(nome="Tilapia", tipo="Consumivel", preco=120, bonus_hp=40, bonus_stm=30),
    "Salmão": Item(nome="Salmão", tipo="Consumivel", preco=120, bonus_hp=40, bonus_stm=30),
    ##ARDUR
    "Peitoral": Item(nome="Peitoral", tipo="Equipavel", preco=1500, bonus_def=5, bonus_hp_max=50,slot_equip="p_pet"),
    "Elmo/Ferro": Item(nome="Elmo/Ferro", tipo="Equipavel", preco=1500, bonus_def=2, bonus_hp_max=25,slot_equip="c_cap"),
    ##Chaves
    "Chave": Item(nome='Chave', tipo="Chave", preco=0, vendivel=False, comprável=False),
    "Chave do Dragão": Item(nome='Chave do Dragão', tipo="Chave", preco=0, vendivel=False, comprável=False),
    ##Coletaveis
    "Madeira": Item(nome="Madeira", tipo="Material", slot_equip="slots",vendivel=False, comprável=False),
    "Cerca": Item(nome="Cerca", tipo="Material", slot_equip="slots",vendivel=False, comprável=False),
    "Chão": Item(nome="Chão", tipo="Material", slot_equip="slots",vendivel=False, comprável=False),
    "Escada": Item(nome="Escada", tipo="Material", slot_equip="slots",vendivel=False, comprável=False),
    "Porta": Item(nome="Porta", tipo="Material", slot_equip="slots",vendivel=False, comprável=False),
    "Baú": Item(nome="Baú", tipo="Material", slot_equip="slots", preco = 40),
    "Pedra": Item(nome="Pedra", tipo="Material", slot_equip="slots", preco=25),
    "Bancada": Item(nome="Bancada", tipo="Material", slot_equip="slots", preco=100),
    "Semente/Trigo": Item(nome="Semente/Trigo", tipo="Material", slot_equip="slots", preco=5),
    "Semente/Morango": Item(nome="Semente/Morango", tipo="Material", slot_equip="slots", preco=5),
    "Semente/Algodão": Item(nome="Semente/Algodão", tipo="Material", slot_equip="slots", preco=5),
    "Semente/Abobora": Item(nome="Semente/Abobora", tipo="Material", slot_equip="slots", preco=10),
    "Semente/Milho": Item(nome="Semente/Milho", tipo="Material", slot_equip="slots", preco=5),
    'Muda/Arvore': Item(nome="Muda/Arvore", tipo="Material", slot_equip="slots", preco=10),
    'Semente/Arbusto': Item(nome="Semente/Arbusto", tipo="Material", slot_equip="slots", preco=5),
    'Fornalha': Item(nome="Fornalha", tipo="Material", slot_equip="slots", vendivel=False, comprável=False),
    ##Produtors
    "Trigo": Item(nome="Trigo", tipo="Produto", preco=100),
    "Algodão": Item(nome="Algodão", tipo="Produto", preco=100),
    "Morango": Item(nome="Morango", tipo="Produto", preco=100),
    "Milho": Item(nome="Milho", tipo="Produto", preco=100),
    "Graveto": Item(nome="Graveto", tipo="Produto", preco=2),
    "Carvão": Item(nome="Carvão", tipo="Produto", preco=250),
    "Ferro": Item(nome="Ferro", tipo="Produto",preco=500),
    "Linha": Item(nome="Linha", tipo="Produto",preco=250),
    "Abobora": Item(nome="Abobora", tipo="Produto", preco=200),
    "Barra/Ferro": Item(nome="Barra/Ferro", tipo="Produto", preco=2000),
}

class CraftRecipe:
    def __init__(self, nome_item, materiais, quantidade=1):
        self.nome_item = nome_item
        self.materiais = materiais
        self.quantidade = quantidade

RECEITAS_EQUIPAMENTOS = {
    'Espada': CraftRecipe('Espada',{'Madeira': 2, 'Graveto': 1}),
    'Vara de Pesca': CraftRecipe('Vara de Pesca',{'Linha': 3, 'Graveto': 4}),
    'Pá': CraftRecipe('Pá',{'Madeira': 1, 'Graveto': 4}),
    'Enchada': CraftRecipe('Enchada',{'Pedra':2 , 'Graveto': 4}),
    'Tocha': CraftRecipe('Tocha',{'Graveto':2 , 'Carvão': 1}, quantidade=2),
    'Picareta/Madeira': CraftRecipe('Picareta/Madeira',{'Madeira': 3, 'Graveto': 4}),
    'Machado/Madeira': CraftRecipe('Machado/Madeira',{'Madeira': 3, 'Graveto': 4}),
    'Picareta/Pedra': CraftRecipe('Picareta/Pedra',{'Pedra': 3, 'Graveto': 4}),
    'Machado/Pedra': CraftRecipe('Machado/Pedra',{'Pedra': 3, 'Graveto': 4}),
    'Elmo/Ferro': CraftRecipe('Elmo/Ferro', {'Barra/Ferro': 10}),
    'Peitoral': CraftRecipe('Peitoral', {'Barra/Ferro': 25}),
    'Mochila': CraftRecipe("Mochila", {"Linha": 5})
}

RECEITAS_MATERIAIS = {
    'Bau': CraftRecipe('Bau', {'Madeira': 5, 'Pedra': 1}),
    'Porta': CraftRecipe('Porta', {'Madeira': 6}),
    'Chão': CraftRecipe('Chão', {'Madeira': 2}, quantidade=4),
    'Fornalha': CraftRecipe('Forja', {'Pedra': 9}),
    'Graveto': CraftRecipe('Graveto', {'Madeira': 2}, quantidade=4),
    'Linha': CraftRecipe('Linha', {"Algodão":2}),
    'Semente/Trigo': CraftRecipe('Semente/Trigo', {'Trigo':1}, quantidade=3),
    'Semente/Abobora': CraftRecipe('Semente/Abobora', {'Abobora':1}, quantidade=3),
    'Semente/Milho': CraftRecipe('Semente/Milho', {'Milho':1}, quantidade=3),
    "Salada de Frutas": CraftRecipe("Salada de Frutas", {'Frutas': 5, "Morango":2})
}

RECEITAS_CONSUMIVEIS = {
    'Pão': CraftRecipe('Pão',{'Trigo':3, 'Carvão':1}),
    'Bolo de Milho': CraftRecipe('Bolo de Milho',{'Milho':5, 'Carvão':1}),
    'Torta de Abobora': CraftRecipe('Torta de Abobora',{'Trigo':3, 'Abobora':1, 'Carvão':1}),
    'Pizza': CraftRecipe('Pizza',{'Trigo':5, 'Queijo': 1, 'Ovo': 2, 'Carvão ': 1}),
    'Queijo': CraftRecipe('Queijo',{'Leite':5, 'Carvão':1}),
    'Sopa de Legumes': CraftRecipe('Sopa de Legumes',{'Abobora':1, 'Milho':3, 'Trigo':2, 'Carvão': 1}),
    'Ovo Frito': CraftRecipe('Ovo Frito',{'Ovo':1, 'Carvão': 1}),
}

RECEITAS_MINERIOS = {
    "Carvão": CraftRecipe('Carvão',{'Madeira':5}),
    "Barra/Ferro": CraftRecipe('Barra/Ferro',{'Ferro':10, 'Carvão':5}),
}

class magias:
    def __init__(self, nome, tipo, bonus_hp=0, bonus_atk=0, bonus_def=0, bonus_stm=0, batalhas=False, mana_gasta=0, xp=0):
        self.nome = nome
        self.tipo = tipo
        self.bonus_hp = bonus_hp
        self.bonus_atk = bonus_atk
        self.bonus_def = bonus_def
        self.bonus_stm = bonus_stm
        self.batalhas = batalhas
        self.mana_gasta = mana_gasta
        self.xp = xp

    def __repr__(self):
        return f"magias(nome='{self.nome}', tipo='{self.tipo}')"

TODAS_AS_MAGIAS = {
    "Cura Leve": magias(nome="Cura Leve", tipo="Cura", bonus_hp=20, mana_gasta=10, xp=5),
    "Benção da Natureza": magias(nome="Benção da Natureza", tipo="Cura", bonus_hp=50, bonus_stm=10, mana_gasta=25, xp=10),
    "Tempestade de Raios": magias(nome="Tempestade de Raios", tipo="Ataque", bonus_atk=30, batalhas=True, mana_gasta=30, xp=10),
    "Bola de Fogo": magias(nome="Bola de Fogo", tipo="Ataque", bonus_atk=15, batalhas=True, mana_gasta=15, xp=5),
}