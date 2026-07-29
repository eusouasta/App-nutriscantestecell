"""
nutrition_data.py
==================
Base de conhecimento nutricional local. Mapeia cada uma das 101 classes do
modelo de classificação de comida (dataset Food-101) para uma estimativa de
calorias e macronutrientes por porção típica.

Essa é a "camada de lógica" em Python do NutriScan: o modelo de IA só diz
"o que é" a comida (ex: "pizza"); é esse módulo que sabe "quanto vale" isso
em termos nutricionais, e é aqui que a matemática de agregação do prato
inteiro acontece.

IMPORTANTE: os valores são estimativas aproximadas por porção comum
(não são medições de laboratório nem substituem orientação nutricional
profissional).
"""

from dataclasses import dataclass


@dataclass
class InfoNutricional:
    nome_pt: str
    emoji: str
    kcal: int          # por porção típica
    proteina_g: float
    carboidrato_g: float
    gordura_g: float


# Tabela por classe do Food-101 (chave = label do modelo em inglês)
TABELA_NUTRICIONAL: dict[str, InfoNutricional] = {
    "apple_pie": InfoNutricional("Torta de maçã", "🥧", 296, 2.4, 42.5, 13.7),
    "baby_back_ribs": InfoNutricional("Costelinha suína", "🍖", 470, 33.0, 6.0, 34.0),
    "baklava": InfoNutricional("Baclava", "🍯", 334, 5.0, 29.0, 23.0),
    "beef_carpaccio": InfoNutricional("Carpaccio de carne", "🥩", 190, 22.0, 2.0, 10.0),
    "beef_tartare": InfoNutricional("Tartar de carne", "🥩", 250, 24.0, 3.0, 16.0),
    "beet_salad": InfoNutricional("Salada de beterraba", "🥗", 140, 3.0, 18.0, 6.0),
    "beignets": InfoNutricional("Beignet", "🍩", 350, 5.0, 40.0, 18.0),
    "bibimbap": InfoNutricional("Bibimbap", "🍚", 560, 22.0, 78.0, 17.0),
    "bread_pudding": InfoNutricional("Pudim de pão", "🍮", 340, 7.0, 48.0, 13.0),
    "breakfast_burrito": InfoNutricional("Burrito de café da manhã", "🌯", 450, 20.0, 40.0, 24.0),
    "bruschetta": InfoNutricional("Bruschetta", "🍞", 150, 3.5, 20.0, 6.0),
    "caesar_salad": InfoNutricional("Salada Caesar", "🥗", 470, 15.0, 15.0, 40.0),
    "cannoli": InfoNutricional("Cannoli", "🍰", 300, 6.0, 30.0, 18.0),
    "caprese_salad": InfoNutricional("Salada Caprese", "🥗", 250, 12.0, 8.0, 19.0),
    "carrot_cake": InfoNutricional("Bolo de cenoura", "🍰", 415, 4.5, 52.0, 21.0),
    "ceviche": InfoNutricional("Ceviche", "🐟", 180, 22.0, 12.0, 4.0),
    "cheesecake": InfoNutricional("Cheesecake", "🍰", 400, 6.5, 32.0, 27.0),
    "cheese_plate": InfoNutricional("Tábua de queijos", "🧀", 380, 22.0, 4.0, 30.0),
    "chicken_curry": InfoNutricional("Frango ao curry", "🍛", 430, 28.0, 20.0, 25.0),
    "chicken_quesadilla": InfoNutricional("Quesadilla de frango", "🫓", 480, 27.0, 35.0, 25.0),
    "chicken_wings": InfoNutricional("Asinha de frango", "🍗", 430, 30.0, 4.0, 32.0),
    "chocolate_cake": InfoNutricional("Bolo de chocolate", "🍫", 420, 5.0, 55.0, 20.0),
    "chocolate_mousse": InfoNutricional("Mousse de chocolate", "🍫", 280, 4.5, 28.0, 17.0),
    "churros": InfoNutricional("Churros", "🥖", 300, 3.5, 38.0, 15.0),
    "clam_chowder": InfoNutricional("Sopa de mariscos", "🥣", 300, 12.0, 25.0, 17.0),
    "club_sandwich": InfoNutricional("Sanduíche club", "🥪", 550, 30.0, 40.0, 28.0),
    "crab_cakes": InfoNutricional("Bolinho de caranguejo", "🦀", 290, 15.0, 15.0, 18.0),
    "creme_brulee": InfoNutricional("Crème brûlée", "🍮", 330, 5.0, 25.0, 23.0),
    "croque_madame": InfoNutricional("Croque madame", "🥪", 520, 27.0, 30.0, 32.0),
    "cup_cakes": InfoNutricional("Cupcake", "🧁", 300, 3.0, 40.0, 14.0),
    "deviled_eggs": InfoNutricional("Ovos recheados", "🥚", 180, 8.0, 2.0, 15.0),
    "donuts": InfoNutricional("Rosquinha (donut)", "🍩", 260, 3.0, 30.0, 14.0),
    "dumplings": InfoNutricional("Dumplings", "🥟", 300, 12.0, 35.0, 12.0),
    "edamame": InfoNutricional("Edamame", "🫛", 190, 17.0, 15.0, 8.0),
    "eggs_benedict": InfoNutricional("Ovos benedict", "🍳", 460, 20.0, 25.0, 32.0),
    "escargots": InfoNutricional("Escargot", "🐌", 230, 16.0, 5.0, 16.0),
    "falafel": InfoNutricional("Falafel", "🧆", 330, 13.0, 32.0, 18.0),
    "filet_mignon": InfoNutricional("Filé mignon", "🥩", 380, 36.0, 0.0, 25.0),
    "fish_and_chips": InfoNutricional("Peixe com batata frita", "🐟", 590, 25.0, 55.0, 30.0),
    "foie_gras": InfoNutricional("Foie gras", "🍽️", 460, 11.0, 4.0, 44.0),
    "french_fries": InfoNutricional("Batata frita", "🍟", 365, 4.0, 48.0, 17.0),
    "french_onion_soup": InfoNutricional("Sopa de cebola francesa", "🍲", 310, 12.0, 25.0, 18.0),
    "french_toast": InfoNutricional("Rabanada", "🍞", 350, 10.0, 45.0, 14.0),
    "fried_calamari": InfoNutricional("Lula à dorê", "🦑", 400, 18.0, 30.0, 24.0),
    "fried_rice": InfoNutricional("Arroz frito", "🍚", 420, 10.0, 60.0, 15.0),
    "frozen_yogurt": InfoNutricional("Iogurte gelado", "🍦", 220, 6.0, 38.0, 5.0),
    "garlic_bread": InfoNutricional("Pão de alho", "🍞", 280, 6.0, 32.0, 14.0),
    "gnocchi": InfoNutricional("Nhoque", "🍝", 380, 9.0, 65.0, 9.0),
    "greek_salad": InfoNutricional("Salada grega", "🥗", 300, 8.0, 12.0, 25.0),
    "grilled_cheese_sandwich": InfoNutricional("Sanduíche de queijo quente", "🥪", 400, 15.0, 30.0, 25.0),
    "grilled_salmon": InfoNutricional("Salmão grelhado", "🐟", 350, 34.0, 0.0, 22.0),
    "guacamole": InfoNutricional("Guacamole", "🥑", 230, 3.0, 12.0, 20.0),
    "gyoza": InfoNutricional("Gyoza", "🥟", 280, 11.0, 30.0, 12.0),
    "hamburger": InfoNutricional("Hambúrguer", "🍔", 350, 20.0, 30.0, 17.0),
    "hot_and_sour_soup": InfoNutricional("Sopa agridoce picante", "🍜", 180, 8.0, 18.0, 8.0),
    "hot_dog": InfoNutricional("Cachorro-quente", "🌭", 290, 11.0, 24.0, 17.0),
    "huevos_rancheros": InfoNutricional("Huevos rancheros", "🍳", 400, 18.0, 35.0, 22.0),
    "hummus": InfoNutricional("Homus", "🧆", 220, 8.0, 20.0, 13.0),
    "ice_cream": InfoNutricional("Sorvete", "🍨", 210, 3.5, 24.0, 11.0),
    "lasagna": InfoNutricional("Lasanha", "🍝", 480, 24.0, 38.0, 26.0),
    "lobster_bisque": InfoNutricional("Bisque de lagosta", "🦞", 320, 14.0, 15.0, 23.0),
    "lobster_roll_sandwich": InfoNutricional("Sanduíche de lagosta", "🦞", 430, 22.0, 35.0, 22.0),
    "macaroni_and_cheese": InfoNutricional("Macarrão com queijo", "🧀", 450, 17.0, 45.0, 22.0),
    "macarons": InfoNutricional("Macaron", "🍬", 90, 1.5, 12.0, 4.0),
    "miso_soup": InfoNutricional("Sopa de missô", "🍲", 80, 6.0, 7.0, 3.0),
    "mussels": InfoNutricional("Mexilhões", "🦪", 250, 24.0, 10.0, 12.0),
    "nachos": InfoNutricional("Nachos", "🧀", 550, 15.0, 55.0, 30.0),
    "omelette": InfoNutricional("Omelete", "🍳", 280, 18.0, 3.0, 21.0),
    "onion_rings": InfoNutricional("Anéis de cebola", "🧅", 410, 5.0, 45.0, 24.0),
    "oysters": InfoNutricional("Ostras", "🦪", 110, 12.0, 6.0, 4.0),
    "pad_thai": InfoNutricional("Pad thai", "🍜", 480, 18.0, 60.0, 18.0),
    "paella": InfoNutricional("Paella", "🥘", 520, 28.0, 60.0, 18.0),
    "pancakes": InfoNutricional("Panqueca", "🥞", 350, 8.0, 55.0, 10.0),
    "panna_cotta": InfoNutricional("Panna cotta", "🍮", 290, 4.0, 24.0, 20.0),
    "peking_duck": InfoNutricional("Pato à Pequim", "🦆", 430, 26.0, 12.0, 30.0),
    "pho": InfoNutricional("Pho", "🍜", 400, 25.0, 50.0, 8.0),
    "pizza": InfoNutricional("Pizza (2 fatias)", "🍕", 570, 24.0, 68.0, 22.0),
    "pork_chop": InfoNutricional("Costeleta de porco", "🍖", 350, 35.0, 0.0, 22.0),
    "poutine": InfoNutricional("Poutine", "🍟", 740, 18.0, 65.0, 45.0),
    "prime_rib": InfoNutricional("Prime rib", "🥩", 500, 38.0, 0.0, 38.0),
    "pulled_pork_sandwich": InfoNutricional("Sanduíche de porco desfiado", "🥪", 490, 28.0, 42.0, 22.0),
    "ramen": InfoNutricional("Ramen", "🍜", 470, 20.0, 60.0, 16.0),
    "ravioli": InfoNutricional("Ravioli", "🍝", 400, 16.0, 55.0, 13.0),
    "red_velvet_cake": InfoNutricional("Bolo red velvet", "🍰", 420, 4.5, 55.0, 20.0),
    "risotto": InfoNutricional("Risoto", "🍚", 430, 10.0, 60.0, 15.0),
    "samosa": InfoNutricional("Samosa", "🥟", 260, 5.0, 30.0, 14.0),
    "sashimi": InfoNutricional("Sashimi", "🍣", 180, 28.0, 2.0, 6.0),
    "scallops": InfoNutricional("Vieiras", "🐚", 200, 25.0, 8.0, 7.0),
    "seaweed_salad": InfoNutricional("Salada de algas", "🥗", 120, 3.0, 12.0, 7.0),
    "shrimp_and_grits": InfoNutricional("Camarão com polenta", "🍤", 420, 22.0, 35.0, 22.0),
    "spaghetti_bolognese": InfoNutricional("Espaguete à bolonhesa", "🍝", 460, 22.0, 55.0, 16.0),
    "spaghetti_carbonara": InfoNutricional("Espaguete à carbonara", "🍝", 520, 20.0, 55.0, 24.0),
    "spring_rolls": InfoNutricional("Rolinho primavera", "🥢", 220, 5.0, 25.0, 11.0),
    "steak": InfoNutricional("Bife", "🥩", 420, 40.0, 0.0, 28.0),
    "strawberry_shortcake": InfoNutricional("Bolo de morango", "🍰", 350, 4.0, 48.0, 16.0),
    "sushi": InfoNutricional("Sushi (8 peças)", "🍣", 300, 12.0, 50.0, 5.0),
    "tacos": InfoNutricional("Tacos (3 unidades)", "🌮", 420, 20.0, 35.0, 22.0),
    "takoyaki": InfoNutricional("Takoyaki", "🐙", 280, 10.0, 30.0, 13.0),
    "tiramisu": InfoNutricional("Tiramisu", "🍰", 350, 6.0, 32.0, 22.0),
    "tuna_tartare": InfoNutricional("Tartar de atum", "🐟", 220, 26.0, 4.0, 11.0),
    "waffles": InfoNutricional("Waffle", "🧇", 360, 8.0, 48.0, 15.0),
}

# Estimativa genérica pra quando o modelo detecta uma classe fora da tabela
PADRAO_DESCONHECIDO = InfoNutricional("Prato não identificado", "🍽️", 350, 15.0, 35.0, 15.0)


def buscar_info(label_modelo: str) -> InfoNutricional:
    """Busca a info nutricional de uma classe do modelo, com fallback seguro."""
    return TABELA_NUTRICIONAL.get(label_modelo, PADRAO_DESCONHECIDO)


def montar_resultado(predicoes: list[dict]) -> dict:
    """
    Recebe uma lista de predições do modelo de visão, no formato:
        [{"label": "pizza", "score": 0.87}, ...]

    Aplica a lógica de negócio:
      - filtra predições com confiança muito baixa (ruído)
      - remove duplicatas mantendo a de maior score
      - cruza cada item com a tabela nutricional
      - agrega o total de calorias e macros do "prato"

    Retorna um dicionário pronto pra virar JSON de resposta da API.
    """
    CONFIANCA_MINIMA = 0.03
    MAX_ITENS = 4

    vistos = set()
    itens_validos = []
    for pred in predicoes:
        label = pred.get("label", "")
        score = float(pred.get("score", 0))
        if score < CONFIANCA_MINIMA:
            continue
        if label in vistos:
            continue
        vistos.add(label)
        itens_validos.append((label, score))

    itens_validos.sort(key=lambda x: x[1], reverse=True)
    itens_validos = itens_validos[:MAX_ITENS]

    if not itens_validos:
        itens_validos = [(predicoes[0]["label"], predicoes[0].get("score", 0))] if predicoes else []

    itens_resultado = []
    total_kcal = 0
    total_proteina = 0.0
    total_carbo = 0.0
    total_gordura = 0.0

    for label, score in itens_validos:
        info = buscar_info(label)
        itens_resultado.append({
            "label": label,
            "nome": info.nome_pt,
            "emoji": info.emoji,
            "confianca": round(score * 100, 1),
            "kcal": info.kcal,
            "proteina_g": info.proteina_g,
            "carboidrato_g": info.carboidrato_g,
            "gordura_g": info.gordura_g,
        })
        total_kcal += info.kcal
        total_proteina += info.proteina_g
        total_carbo += info.carboidrato_g
        total_gordura += info.gordura_g

    return {
        "itens": itens_resultado,
        "total": {
            "kcal": total_kcal,
            "proteina_g": round(total_proteina, 1),
            "carboidrato_g": round(total_carbo, 1),
            "gordura_g": round(total_gordura, 1),
        },
    }
