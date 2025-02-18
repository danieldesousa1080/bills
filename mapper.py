from database import *
from util import preco_medio_produtos

def mapper_compras(compras):
    return [
        mapper_compra(compra)
        for compra in compras
    ]

def mapper_compra(compra):
    pagador = procurar_usuario_pelo_id(compra["pagador"]) 
    return {
        "id": compra["_id"],
        "protocolo": compra["protocolo"],
        "data": compra["data"].strftime("%d/%m/%Y"),
        "estabelecimento":mapper_empresa(encontrar_estabelecimento_pelo_id(compra["id_estabelecimento"])),
        "preco":compra["preco"],
        "total_itens":int (compra["total_itens"]),
        "preco_por_produto": preco_medio_produtos(encontrar_produtos_por_compra(compra["_id"])),
        "pagador": pagador["usuario"] if pagador else None,
        "editavel": compra["editavel"]
    }

def mapper_produtos(produtos: list[dict]) -> dict:
    # Mapeia os produtos e inclui a compra associada
    produtos_mapeados = [
        {
            "id": produto["_id"],
            "nome": produto["nome"],
            "preco": produto["valor"],
            "unidade": produto["unidade"],
            "quantidade": produto["quantidade"],
            "preco_real": produto["valor"] / produto["quantidade"],
            "compra": mapper_compra(encontrar_compra_pelo_id(produto["id_compra"])),
            "pagador": procurar_usuario_pelo_id(produto["pagador"])['usuario'] if produto["pagador"] else None
        }
        for produto in produtos
    ]

    # Ordena os produtos pela data da compra (assumindo que a compra tem um campo "data")
    produtos_ordenados = sorted(
        produtos_mapeados,
        key=lambda x: x["compra"]["data"],  # Acessa a data dentro da compra
        reverse=True  # Ordena do mais recente para o mais antigo
    )

    return produtos_ordenados

def mapper_empresa(empresa: dict) -> dict:

    produtos = encontrar_produtos_por_empresa(empresa["_id"])

    return {
        "id": empresa["_id"],
        "nome_real": empresa["nome"],
        "endereco": empresa["endereco"],
        "apelido": empresa["apelido"],
        "uf": empresa["uf"],
        "inscricao": empresa["inscricao"],
        "total_produtos": len(produtos),
        "preco_por_produto": preco_medio_produtos(produtos),
        "nome": empresa["apelido"] if empresa["apelido"] else empresa["nome"]
    }