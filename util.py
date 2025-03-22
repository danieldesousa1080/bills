import database as db
import csv
from datetime import datetime

def preco_medio_produtos(produtos: list[dict]):
    """Recebe uma lista de produtos e retorna o preço médio dela"""
    total = 0
    contador = 0

    for produto in produtos:
        total += produto["valor"]
        contador += 1

    return total / contador

def valores_compras_por_usuario(inicio: datetime, fim: datetime):
    """Calcula a divisão de valores para cada usuário dado um período e retorna um dicionario

        formato do dicionario: 

        {
            devedor: {
                pagador: valor,
                pagador: valor
            }
        }

    """

    dicionario_despesas = {}

    compras = db.compras_por_periodo(inicio, fim)

    for compra in compras:
        if compra["analizada"] and compra["participantes"]:
            pagador_compra = db.procurar_usuario_pelo_id(compra["pagador"])
            pagador = pagador_compra["usuario"]
            for participante_id in compra["participantes"]:
                usuario = db.procurar_usuario_pelo_id(participante_id)
                usuario = usuario["usuario"]
                valor = db.calcular_pagamento_compra_usuario(compra["_id"], participante_id)
                if valor > 0:
                    print(f" [{compra['data'].date()}] {usuario} deve pagar R$ {valor :.2f} para {pagador} referente à compra {compra['protocolo']}")
                    if dicionario_despesas.get(usuario):
                        if dicionario_despesas.get(usuario).get(pagador):
                            dicionario_despesas[usuario][pagador] += valor
                        else:
                            dicionario_despesas[usuario][pagador] = valor
                    else:
                        dicionario_despesas[usuario] = {pagador: valor}
        return dicionario_despesas

def escrever_relatorio(inicio, fim):
    """escreve o relatorio em um arquivo e cria a referência no banco de dadoss"""
    dividas = valores_compras_por_usuario(inicio, fim)
    texto = ""

    for devedor, conta in dividas.values():
        for recebedor, valor in conta.values():
            texto += f"O usuário {devedor} deve pagar R$ {valor} para {recebedor}\n"
    
    return textos
    