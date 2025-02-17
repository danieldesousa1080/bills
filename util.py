def preco_medio_produtos(produtos: list[dict]):
    """Recebe uma lista de produtos e retorna o preço médio dela"""
    total = 0
    contador = 0

    for produto in produtos:
        total += produto["valor"]
        contador += 1
    
    return total / contador