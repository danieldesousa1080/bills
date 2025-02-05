from peewee import *

db = SqliteDatabase("bills.db")

class Estabelecimento(Model):
    nome = CharField()
    cnpj = CharField()
    inscricao_estadual = CharField()
    uf = CharField()

    class Meta:
        database = db

class Compra(Model):
    protocolo = CharField()
    total_itens = IntegerField()
    preco = FloatField()
    pagamento = CharField()
    data_hora = DateTimeField()
    estabelecimento = ForeignKeyField(Estabelecimento, backref='compras')

    class Meta:
        database = db

class Produto(Model):
    nome = CharField()
    quantidade = IntegerField()
    unidade = CharField()
    valor_total = FloatField()
    compra = ForeignKeyField(Compra, backref='produtos')
    codigo = CharField()

    class Meta:
        database = db

if __name__ == "__main__":
    db.connect()
    db.create_tables([Estabelecimento, Compra, Produto])