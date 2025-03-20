from database import *
from util import preco_medio_produtos
from datetime import datetime

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
        "editavel": compra["editavel"],
        "analizada": compra["analizada"],
        "participantes": compra["participantes"]
    }

def mapper_produto(produto: dict) -> dict:
    compra = mapper_compra(encontrar_compra_pelo_id(produto["id_compra"]))
    consumidores = [procurar_usuario_pelo_id(consumidor)["usuario"] for consumidor in produto["consumidores"]]

    print(consumidores)

    return {
                    "data_compra": datetime.strptime(compra["data"], "%d/%m/%Y").date(),
                    "id": produto["_id"],
                    "nome": produto["nome"],
                    "preco": produto["valor"],
                    "unidade": produto["unidade"],
                    "quantidade": produto["quantidade"],
                    "preco_real": produto["valor"] / produto["quantidade"],
                    "compra": compra,
                    "consumidores": consumidores
                }

def mapper_produtos(produtos: list[dict]) -> dict:
    # Mapeia os produtos e inclui a compra associada
    produtos_mapeados = []

    def _chave(produto):
        return produto["data_compra"]

    for produto in produtos:
        compra = mapper_compra(encontrar_compra_pelo_id(produto["id_compra"]))
        produtos_mapeados.append(
                {
                    "data_compra": datetime.strptime(compra["data"], "%d/%m/%Y").date(),
                    "id": produto["_id"],
                    "nome": produto["nome"],
                    "preco": produto["valor"],
                    "unidade": produto["unidade"],
                    "quantidade": produto["quantidade"],
                    "preco_real": produto["valor"] / produto["quantidade"],
                    "compra": compra,
                    "pagador": procurar_usuario_pelo_id(produto["pagador"])['usuario'] if produto["pagador"] else None,
                    "consumidores": [procurar_usuario_pelo_id(consumidor)["usuario"] for consumidor in produto["consumidores"]]
                }
            )

    return sorted(produtos_mapeados, key=_chave, reverse=True)

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
