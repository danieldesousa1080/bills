import database as db
import csv
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4
from database import ObjectId
import os

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

    fim += timedelta(days=1)

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
                if valor > 0 and usuario != pagador:
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
    """escreve o relatorio em um arquivo e retorna o caminho para o arquivo"""
    dividas = valores_compras_por_usuario(inicio, fim)

    if not dividas:
        return None

    inicio_txt = inicio.strftime('%d/%m/%Y')
    fim_txt = fim.strftime('%d/%m/%Y')
    texto = f"Relatório de referência {inicio_txt} à {fim_txt}\n"
    texto += "==================================\n"

    for devedor, conta in dividas.items():
        for recebedor, valor in conta.items():
            texto += f"{str(devedor).capitalize()} deve pagar R$ {valor:.2f} para {str(recebedor).capitalize()}\n"
    
    texto+="=================================================\n"
    texto += "Favor conferir as compras referentes a esse período."

    arquivo = Path("relatorios") / f"{str(uuid4())}.txt"

    with open(arquivo, "w") as file:
        file.writelines(texto)
    
    return arquivo
    
def remover_relatorio(id):
    relatorio = db.relatorios.find_one(
        {"_id": ObjectId(id)}
    )

    arquivo = Path(relatorio['arquivo'])
    
    os.remove(arquivo)

    db.relatorios.delete_one(
        {"_id": ObjectId(id)}
    )