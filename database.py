from models import db, Estabelecimento, Produto, Compra

def criar_estabelecimento(nome, cnpj, inscricao, uf):
    try:
        estabelecimento = procurar_estabelecimento(inscricao=inscricao)
    except:
        estabelecimento = Estabelecimento.create(
            nome=nome, 
            cnpj=cnpj, 
            inscricao_estadual = inscricao, 
            uf = uf
        )

        estabelecimento.save()
    return estabelecimento

def criar_compra(protocolo, total_itens, preco, pagamento, data, estabelecimento):
    try:
        compra = procurar_compra(protocolo=protocolo)
        print("compra já existe na base de dados!")
        return None
    except:
        compra = Compra.create(
            protocolo = protocolo,
            total_itens = total_itens,
            preco = preco,
            pagamento = pagamento,
            data_hora = data,
            estabelecimento = estabelecimento
        )

        compra.save()

    return compra

def criar_produto(nome, quantidade, unidade, valor, compra, codigo):
    produto = Produto.create(
        nome = nome,
        quantidade = quantidade,
        unidade = unidade,
        valor_total = valor,
        compra = compra,
        codigo = codigo
    )

    produto.save()

    return produto

def procurar_compra(protocolo):
    compra = Compra.select().where(Compra.protocolo == protocolo).get()

    if compra:
        return compra

def procurar_estabelecimento(inscricao):
    estabelecimento = Estabelecimento.select().where(Estabelecimento.inscricao_estadual == inscricao).get()

    if estabelecimento:
        return estabelecimento

