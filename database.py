from pymongo import MongoClient
from pymongo.collection import InsertOneResult, ObjectId
from dotenv import dotenv_values
from datetime import datetime
from hashlib import sha256
from uuid import uuid4

config = dotenv_values()

client = MongoClient(config["MONGO_CONNECTION"])

database = client["qr-bills"]
compras = database["compras"]
estabelecimentos = database["estabelecimentos"]
produtos = database["produtos"]
usuarios = database["usuarios"]
sessoes = database["sessoes"]
relatorios = database["relatorios"]

def procurar_estabelecimento(inscricao) -> dict | None:
    """Procura um estabelecimento no banco de dados dado uma inscrição."""
    estabelecimento = estabelecimentos.find_one(
        {"inscricao": {"$eq": inscricao.strip()}}
    )
    exit()
    return estabelecimento


def procurar_usuario_pelo_id(id):
    if type(id) == str:
        id = ObjectId(id)
    return usuarios.find_one({"_id": id})


def criar_estabelecimento(
    nome, cnpj, inscricao, uf, endereco, apelido=None
) -> InsertOneResult | dict:
    """Cria um estabelecimento, caso não haja no banco."""
    estabelecimento = procurar_estabelecimento(inscricao)

    if not estabelecimento:

        data = {
            "nome": nome,
            "cnpj": cnpj,
            "inscricao": inscricao,
            "uf": uf,
            "endereco": endereco,
            "apelido": apelido,
        }

        estabelecimento = estabelecimentos.insert_one(data)

    return estabelecimento


def encontrar_estabelecimento_pelo_id(id):
    id = ObjectId(id)
    return estabelecimentos.find_one({"_id": {"$eq": id}})


def encontrar_compra(protocolo) -> dict | None:
    """encontra uma compra no banco dado um protocolo.
    Retorna o id da compra, ou None
    """
    return compras.find_one({"protocolo": {"$eq": protocolo}})


def encontrar_compra_pelo_id(id):
    if type(id) == str:
        id = ObjectId(id)
    return compras.find_one({"_id": {"$eq": id}})

def encontrar_compras_pendentes():
    return compras.find({
        "editavel": True
    })

def criar_compra(
    protocolo, total_itens, preco, pagamento, data, id_estabelecimento
) -> InsertOneResult | None:
    """cria uma compra no banco de dados e retorna o id ou None, caso a compra ja esteja cadastrada"""
    compra_encontrada = encontrar_compra(protocolo)

    if not compra_encontrada:
        compra = compras.insert_one(
            {
                "protocolo": protocolo,
                "total_itens": total_itens,
                "preco": preco,
                "pagamento": pagamento,
                "data": data,
                "id_estabelecimento": id_estabelecimento,
                "pagador": None,
                "editavel": True,
                "analizada": False
            }
        )
        return compra

def definir_participantes_compra(id_compra, ids_participantes):
    id_compra = ObjectId(id_compra)

    compras.update_one(
        {"_id": id_compra},
        {"$set":{
            "participantes": ids_participantes
        }}
    )

def criar_produto(
    nome: str, quantidade: float, unidade: str, valor: float, id_compra, codigo
) -> InsertOneResult:
    produto = produtos.insert_one(
        {
            "nome": nome,
            "quantidade": quantidade,
            "unidade": unidade,
            "valor": valor,
            "id_compra": id_compra,
            "codigo": codigo,
            "pagador": None,
        }
    )

    return produto


def procurar_produtos_por_compra(id_compra: ObjectId) -> list[dict] | None:
    """Retorna todos os produtos de uma compra
    params:
        id_compra: ObjectId
    """
    return produtos.find({"id_compra": {"$eq": id_compra}})


def procurar_produtos_por_nome(nome_do_produto: str) -> list[dict] | None:
    """Retorna uma lista de produtos dado um nome. Ou None, caso não econtre nenhum produto"""
    return produtos.find({"nome": {"$regex": nome_do_produto, "$options": "i"}})

def produtos_consumidos_pelo_usuario(produtos, id_usuario):
    id_usuario = ObjectId(id_usuario)
    consumidos = []

    for produto in produtos:
        if id_usuario in produto["consumidores"]:
            consumidos.append(produto)
    return consumidos

def procurar_estabelecimento(inscricao: str) -> dict | None:
    """Retorna um estabelecimento dada uma inscrição. Ou None caso não encontre"""
    return estabelecimentos.find_one({"inscricao": {"$eq": inscricao}})


def compras_por_periodo(inicio: datetime = None, fim: datetime = None):
    """Retorna uma lista de compras dado um tempo de início e fim.
    formato do período: datetime"""
    if not inicio or not fim:
        return compras.find()
    return compras.find({"data": {"$gte": inicio, "$lte": fim}}).sort("data", -1)


def valor_total_por_periodo(inicio: datetime = None, fim: datetime = None) -> float:
    """Calcula o valor de todas as compras feitas em um intervalo de tempo"""
    if not inicio or not fim:
        pipeline = [{"$group": {"_id": None, "total": {"$sum": "$preco"}}}]
    else:
        pipeline = [
            {"$match": {"data": {"$gte": inicio, "$lte": fim}}},
            {"$group": {"_id": None, "total": {"$sum": "$preco"}}},
        ]

    return compras.aggregate(pipeline).next()["total"]


def procurar_usuario(usuario):
    """Procura um usuario no banco dado um nome de usuario.
    Retorna None caso nenhum usuario seja encontrado."""
    return usuarios.find_one({"usuario": {"$eq": usuario}})


def criar_usuario(usuario: str, senha: str) -> None:
    """Cria um usuario no banco
    parametros:
        usuario: str
        senha: str
    """
    h = sha256()
    h.update(str.encode(senha))

    if not procurar_usuario(usuario):
        usuarios.insert_one(
            {"usuario": usuario, "senha": h.hexdigest(), "token": str(uuid4())}
        )


def validar_usuario(usuario, senha):
    """Valida o username e senha de um usuario e o retorna, caso passe na validação"""
    h = sha256()
    h.update(str.encode(senha))

    usuario_encontrado = usuarios.find_one(
        {"usuario": {"$eq": usuario}, "senha": {"$eq": h.hexdigest()}}
    )
    return usuario_encontrado


def encontrar_usuario_pelo_token(token: str) -> dict | None:
    """encontra um usuario através de um token, caso contrário, retorna None"""
    usuario = usuarios.find_one({"token": {"$eq": token}})

    return usuario


def encontrar_produtos_por_compra(id_compra):
    return produtos.find({"id_compra": {"$eq": id_compra}})


def encontrar_produtos_por_empresa(id_empresa) -> list[dict]:
    produtos_empresa = []
    for compra in compras.find({"id_estabelecimento": {"$eq": ObjectId(id_empresa)}}):
        produtos_empresa += produtos.find({"id_compra": {"$eq": compra["_id"]}})

    return produtos_empresa


def mudar_apelido_da_empresa(id_empresa, apelido):
    empresa = estabelecimentos.update_one(
        {"_id": {"$eq": id_empresa}}, {"$set": {"apelido": apelido}}
    )


def registrar_pagamento_compra(usuario, compra):
    """Registra o pagamento de uma compra"""
    usuario = usuarios.find_one({"usuario": usuario})

    if usuario:
        query = {"_id": compra["_id"]}

        operacao = {"$set": {"pagador": usuario["_id"]}}

        compras.update_one(query, operacao)


def remover_pagamento_compra(compra):
    """remove o pagamento de uma compra"""
    query = {"_id": compra["_id"]}

    operacao = {"$set": {"pagador": None}}

    compras.update_one(query, operacao)


def registrar_pagamento_produto(id_produto, id_pagador):
    if type(id_produto) == str:
        id_produto = ObjectId(id_produto)
    if type(id_pagador) == str:
        id_pagador = ObjectId(id_pagador)

    return produtos.update_one({"_id": id_produto}, {"$set": {"pagador": id_pagador}})

def remover_pagamento_produto(id_produto, id_pagador):
    if type(id_produto) == str:
        id_produto = ObjectId(id_produto)
    if type(id_pagador) == str:
        id_pagador = ObjectId(id_pagador)

    return produtos.update_one({"_id": id_produto}, {"$set": {"pagador": None}})

def definir_edicao_compra(id_compra, editavel: bool):
    """Define se a compra é editavel ou não"""
    compras.update_one(
        {
            "_id": id_compra
        },
        {
            "$set": {
                "editavel": editavel
            }
        }
    )

def verificar_compras_editaveis():
    """Retorna verdadeiro caso haja compras editaveis"""
    return bool(compras.find_one({
        "editavel": True
    }))

def finalizar_sessão_aberta():
    return compras.update_many(
        {
            "editavel": True
        },
        {
            "$set": {
                "editavel": False,
                "analizada": True
            }
        }
    )

def criar_nova_sessao(inicio: datetime.date, fim: datetime.date):
    return compras.update_many(
        {
            "$and": [
                {
                    "data": {
                        "$lt":fim,
                        "$gte":inicio
                    },
                    "analizada": {
                        "$eq": False
                    }
                }
            ]
                   },
            {
            "$set": {
                "editavel": True
            }
            }
    )

def finalizar_compra(id, valor: bool):
    return compras.update_one(
        {
            "_id": ObjectId(id)
        },
        {
            "$set": {
                "analizada": valor
            }
        }
    )


def adicionar_consumidor_produto(id_produto, id_usuario):
    '''Adiciona um consumidor na lista de consumidores do produto'''
    id_produto = ObjectId(id_produto)
    id_usuario = ObjectId(id_usuario)

    consumidores = produtos.find_one({
        "_id": id_produto
    })["consumidores"]

    if id_usuario not in consumidores:

        produtos.update_one(
            {"_id": id_produto},
            {"$push": {
                "consumidores": id_usuario
            }}
        )

def remover_consumidor_produto(id_produto, id_usuario):
    id_produto = ObjectId(id_produto)
    id_usuario = ObjectId(id_usuario)

    consumidores = produtos.find_one({
        "_id": id_produto
    })["consumidores"]

    if id_usuario in consumidores:

        produtos.update_one(
            {"_id": id_produto},
            {"$pull": {
                "consumidores": id_usuario
            }}
        )


def adicionar_participante_compra(id_compra, id_paricipante):
    id_compra = ObjectId(id_compra)
    id_paricipante = ObjectId(id_paricipante)

    compras.update_one(
        {"_id": id_compra},
        {"$push": {
            "participantes": id_paricipante
        }}
    )

def remover_participante_compra(id_compra, id_paricipante): 
    id_compra = ObjectId(id_compra)
    id_paricipante = ObjectId(id_paricipante)
    
    compras.update_one(
        {"_id": id_compra},
        {"$pull": 
            {
                "participantes": id_paricipante
            }
        }
    )

def remover_todos_participantes_compra(id_compra):
    id_compra = ObjectId(id_compra)

    compras.update_one(
        {
            "_id": id_compra
        },
        {
            "$set": {
                "participantes": []
            }
        }
    )


def criar_relatorio(nome:str, arquivo: str,inicio: datetime, fim: datetime):
    return relatorios.insert_one(
            {
                "inicio": inicio,
                "fim": fim,
                "nome": nome,
                "arquivo": arquivo
            }
    )

def obter_relatorios():
    encontrados = relatorios.find({})

    return list(encontrados)

def encontrar_relatorio_pelo_id(id):
    id = ObjectId(id)

    relatorio =  relatorios.find_one(
        {"_id": id}
    )

    return relatorio

def calcular_pagamento_compra_usuario(id_compra, id_usuario):
    id_compra = ObjectId(id_compra)
    id_usuario = ObjectId(id_usuario)
    
    compra = encontrar_compra_pelo_id(id_compra)

    total_usuario = 0

    produtos = encontrar_produtos_por_compra(id_compra)
    usuario = procurar_usuario_pelo_id(id_usuario)

    if compra["pagador"] == usuario["_id"]:
        return 0

    for produto in produtos:
        if usuario["_id"] in produto["consumidores"]:
            total_usuario += produto["valor"] / len(produto["consumidores"])
    
    return total_usuario



