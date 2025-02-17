from database import *
from util import preco_medio_produtos

def mapper_compras(compras):
    return [
        mapper_compra(compra)
        for compra in compras
    ]

def mapper_compra(compra):
    return {
        "protocolo": compra["protocolo"],
        "data": compra["data"].strftime("%d/%m/%Y"),
        "estabelecimento":mapper_empresa(encontrar_estabelecimento_pelo_id(compra["id_estabelecimento"])),
        "preco":compra["preco"],
        "total_itens":int (compra["total_itens"]),
        "preco_por_produto": preco_medio_produtos(encontrar_produtos_por_compra(compra["_id"]))
    }

def mapper_produtos(produtos: list[dict]) -> dict:
    return [
        {
            "nome": produto["nome"],
            "preco": produto["valor"],
            "unidade": produto["unidade"],
            "quantidade": produto["quantidade"],
            "preco_real": produto["valor"] / produto["quantidade"],
            "compra": mapper_compra(encontrar_compra_pelo_id(produto["id_compra"])),
        }
        for produto in produtos
    ]

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