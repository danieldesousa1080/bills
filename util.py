def preco_medio_produtos(produtos: list[dict]):
    """Recebe uma lista de produtos e retorna o preço médio dela"""
    total = 0
    contador = 0

    for produto in produtos:
        total += produto["valor"]
        contador += 1

    return total / contador

class Usuario:
    def __init__(self, nome):
        self.nome = nome

class Conta:
    def __init__(self, pagador: Usuario, recebedor: Usuario, valor: float):
        self.pagador = pagador
        self.recebedor = recebedor
        self.valor = valor

class ListaContas:
    def __init__(self):
        self.contas = []
    def adicionar_conta(self, conta):
        self.contas.append(conta)

    def calcular_valor_total(self, usuario1,  usuario2):
        """Calcula o saldo atual de um usuario com outro"""
        saldo = 0
        for conta in self.contas:
            if conta.pagador.nome == usuario1 and conta.recebedor.nome == usuario2:
                saldo-=conta.valor
            if conta.recebedor.nome == usuario1 and conta.pagador.nome == usuario2:
                saldo += conta.valor
        return saldo
