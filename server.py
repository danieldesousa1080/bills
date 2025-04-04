from flask import Flask, request
from flask import render_template, make_response, redirect, url_for, send_file
from datetime import datetime, timedelta
from wtforms import FileField, Form, DateField, StringField, PasswordField, SearchField, SelectField
from mapper import *
from flask_cors import CORS
from database import (
    compras_por_periodo,
    valor_total_por_periodo,
    procurar_usuario,
    criar_usuario,
    validar_usuario,
    encontrar_usuario_pelo_token,
)
from util import escrever_relatorio, remover_relatorio

class RangeDateForm(Form):
    inicio = DateField("inicio", format="%Y-%m-%d")
    fim = DateField("fim", format="%Y-%m-%d")

class FiltroComprasForm(Form):
    inicio = DateField("inicio", format="%Y-%m-%d")
    fim = DateField("fim", format="%Y-%m-%d")
    ordem = SelectField(choices=["decrescente", "crescente"])

class LoginForm(Form):
    usuario = StringField("usuario")
    senha = PasswordField("senha")

class StoreForm(Form):
    apelido = StringField("apelido")

class SearchForm(Form):
    busca = SearchField("busca")

class AdminForm(Form):
    inicio = DateField("inicio", format="%Y-%m-%d")
    fim = DateField("fim", format="%Y-%m-%d")

class RelatorioForm(Form):
    inicio = DateField("inicio", format="%Y-%m-%d")
    fim = DateField("fim", format="%Y-%m-%d")
    titulo = StringField()

app = Flask(__name__)
app.secret_key = "abc123"
cores = CORS(app, resources={r"*": {"origins": "*"}})


@app.before_request
def validar_identidade():
    token = request.cookies.get("user_token")
    usuario = encontrar_usuario_pelo_token(token)["usuario"] if token else None

    rotas_publicas = ["login","registro"]

    if request.endpoint not in rotas_publicas:
        if not usuario:
            return redirect("/login")

@app.route("/")
def home():
    token = request.cookies.get("user_token")
    if token:
        user = encontrar_usuario_pelo_token(token)

    return render_template("home.html", user=user)


@app.route("/login", methods=["POST", "GET"])
def login():

    if request.method == "GET":

        loginForm = LoginForm(request.form)

        data = {"form": loginForm}

        return render_template("login.html", context=data)

    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        usuario_encontrado = procurar_usuario(usuario=usuario)

        if usuario_encontrado:
            usuario_validado = validar_usuario(usuario, senha)
            if usuario_validado:
                resposta = make_response(redirect("/"))
                resposta.set_cookie("user_token", usuario_validado["token"])
                return resposta
        return redirect("/login")


@app.route("/registro", methods=["POST", "GET"])
def registro():

    if request.method == "GET":
        loginForm = LoginForm(request.form)
        data = {"form": loginForm}
        return render_template("registro.html", context=data)
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        criar_usuario(usuario=usuario, senha=senha)

        return redirect(url_for('login'))

@app.get("/logoff")
def logoff():
    resposta = make_response(redirect("/"))
    resposta.delete_cookie("user_token")
    return resposta

@app.get("/compras")
def mostrar_compras():
    token = request.cookies["user_token"]
    user = encontrar_usuario_pelo_token(token)

    form = FiltroComprasForm(request.args)
    
    ordem = -1

    if form.ordem:
        ordem = 1 if form.ordem.data == "crescente" else -1

    if form.validate():        
        if form.inicio.data and form.fim.data:
            inicio = datetime.fromordinal(form.inicio.data.toordinal())
            fim = datetime.fromordinal(form.fim.data.toordinal()) + timedelta(days=1)
            compras = compras_por_periodo(inicio, fim).sort("data", ordem)
            valor = valor_total_por_periodo(inicio, fim)
    else:
        compras = compras_por_periodo().sort("data", ordem)
        valor = valor_total_por_periodo()

    compras = mapper_compras(compras)

    data = {"compras": compras, "valor_periodo": valor, "form": form}

    return render_template("compras.html", context=data, user=user, ordem=ordem)

@app.get("/compras/pendentes")
def mostrar_compras_pendentes():
    token = request.cookies["user_token"]
    user = encontrar_usuario_pelo_token(token)

    compras_pendentes = encontrar_compras_pendentes().sort('data', 1)

    compras_pendentes = mapper_compras(compras_pendentes) if compras_pendentes else None

    return render_template("compras_pendentes.html", compras=compras_pendentes, user=user)

@app.get("/compra/<protocolo>")
def mostrar_compra(protocolo):
    token = request.cookies["user_token"]
    user = encontrar_usuario_pelo_token(token)

    compra = encontrar_compra(protocolo)
    produtos = list(procurar_produtos_por_compra(compra["_id"]))
    habilitar_analise = True

    consumidores = []

    if not compra["pagador"]:
        habilitar_analise = False

    for produto in produtos:
        if not produto["consumidores"]:
            habilitar_analise = False

        for consumidor in produto["consumidores"]:
            if consumidor not in consumidores:
                consumidores.append(consumidor)
    
    print(consumidores)
    
    definir_participantes_compra(compra["_id"], consumidores)

    participantes = consumidores

    usuario_participou = user["_id"] in participantes

    pagamento_participantes = {}

    for participante_id in participantes:
        nome_participante = procurar_usuario_pelo_id(participante_id)["usuario"]
        pagamento_participantes[nome_participante] = calcular_pagamento_compra_usuario(compra["_id"], participante_id)

    participantes = [procurar_usuario_pelo_id(usuario) for usuario in participantes]

    produtos_consumidos = produtos_consumidos_pelo_usuario(produtos, user["_id"])
    produtos = mapper_produtos(produtos)

    data = {"compra": mapper_compra(compra), "produtos": produtos, "usuario": user["usuario"]}

    return render_template(
        "compra.html", 
        context=data, 
        user=user ,
        usuario_participou=usuario_participou, 
        participantes=participantes, 
        pagamento_participantes=pagamento_participantes,
        habilitar_analise=habilitar_analise,
        produtos_consumidos=mapper_produtos(produtos_consumidos)
    )

@app.get("/compra/<protocolo>/modo/Consumidoresedicao")
def mudar_para_o_modo_de_edicao(protocolo):
    compra = encontrar_compra(protocolo)
    definir_edicao_compra(compra["_id"], True)

    return redirect(url_for('mostrar_compra', protocolo=protocolo))


@app.get("/compra/<protocolo>/modo/visualizacao")
def mudar_para_o_modo_de_visualizacao(protocolo):
    compra = encontrar_compra(protocolo)
    definir_edicao_compra(compra["_id"], False)

    return redirect(url_for('mostrar_compra', protocolo=protocolo))

@app.get("/produto/registrar_dono")
def registrar_dono_do_produto(id):
    produtos = request.form.getlist("produtos")
    token = request.cookies.get("user_token")
    usuario = encontrar_usuario_pelo_token(token)["_id"]

    for produto in produtos:
        registrar_pagamento_produto(produto, usuario)

    return redirect(request.url)

@app.route("/empresa/<id>", methods=["GET","POST"])
def informacoes_empresa(id):
    token = request.cookies["user_token"]
    user = encontrar_usuario_pelo_token(token)
    empresa = encontrar_estabelecimento_pelo_id(id)

    if request.method == "GET":

        form = StoreForm()
        form.apelido.data = empresa["apelido"]
        data = {
            "empresa":mapper_empresa(empresa),
            "form": form
        }

        return render_template("empresa.html", context=data, user=user)

    if request.method == "POST":
        novo_apelido = request.form["apelido"]
        if empresa["apelido"] != novo_apelido:
            mudar_apelido_da_empresa(empresa["_id"], novo_apelido)
        return redirect(request.url)


@app.get("/produtos")
def procurar_produtos():
    token = request.cookies["user_token"]
    user = encontrar_usuario_pelo_token(token)

    form = SearchForm()

    nome = request.args.get("busca")

    form.busca.data = nome

    produtos = procurar_produtos_por_nome(nome if nome else "")
    produtos = mapper_produtos(produtos)

    data = {"produtos": produtos, "nome": nome, "form": form}
    return render_template("produtos.html", context=data, user=user)

@app.get("/registar_pagamento_compra/<id>")
def pagar_compra(id):
    compra = encontrar_compra_pelo_id(id)
    token = request.cookies.get("user_token")
    if compra and not compra["pagador"]:
        registrar_pagamento_compra(usuario=encontrar_usuario_pelo_token(token)["usuario"], compra=compra)

        return redirect(url_for('mostrar_compra', protocolo=compra["protocolo"]))
    return redirect("/")

@app.get("/remover_pagamento_compra/<id>")
def remover_pgto_compra(id):
    token = request.cookies.get("user_token")
    compra = encontrar_compra_pelo_id(id)
    usuario = encontrar_usuario_pelo_token(token)
    if compra and compra["pagador"] == usuario["_id"]:
        remover_pagamento_compra(compra)
        return redirect(url_for('mostrar_compra', protocolo=compra["protocolo"]))
    return redirect("/")

@app.get("/remover_edicoes_compra/<id>")
def remover_edicoes_compra(id):

    compra = encontrar_compra_pelo_id(id)

    remover_todas_edicoes_compra(id)

    return redirect(url_for('mostrar_compra', protocolo=compra["protocolo"]))

@app.get("/produto/registrar_pagamento/<protocolo_compra>/<id>")
def adicionar_pgto_produto(protocolo_compra, id):
    token = request.cookies["user_token"]
    user = encontrar_usuario_pelo_token(token)

    registrar_pagamento_produto(id, user["_id"])

    return redirect(url_for('mostrar_compra', protocolo=protocolo_compra))

@app.get("/produto/remover_pagamento/<protocolo_compra>/<id>")
def remover_pgto_produto(protocolo_compra, id):
    token = request.cookies["user_token"]
    user = encontrar_usuario_pelo_token(token)

    remover_pagamento_produto(id, user["_id"])

    return redirect(url_for('mostrar_compra', protocolo=protocolo_compra))

@app.get("/admin")
def admin_page():
    token = request.cookies["user_token"]
    user = encontrar_usuario_pelo_token(token)

    if user["admin"]:
        return render_template("admin.html", user=user)
    return redirect("/")

@app.route("/admin/sessao", methods=["GET", "POST"])
def sessoes():
    token = request.cookies["user_token"]
    user = encontrar_usuario_pelo_token(token)
    
    form = RangeDateForm(request.args)

    if request.method == "GET":
        sessao_aberta = not verificar_compras_editaveis()

        return render_template("admin/sessoes.html", user=user, form=form, sessao_aberta=sessao_aberta)
    
    if request.method == "POST":
        inicio = datetime.strptime(request.form["inicio"], "%Y-%m-%d")
        fim = datetime.strptime(request.form["fim"], "%Y-%m-%d") + timedelta(days=1)

        criar_nova_sessao(inicio, fim)

        return redirect(url_for("sessoes"))

@app.get("/admin/sessao/finalizar")
def finalizar_sessao():
    #finalizar_sessão_aberta()
    return redirect(url_for("sessoes"))

@app.route("/admin/relatorios", methods=["GET","POST"])
def gerar_relatorios():

    form = RelatorioForm()

    if request.method == "GET":
        token = request.cookies["user_token"]
        user = encontrar_usuario_pelo_token(token)
    
        return render_template("admin/gerar_relatorio.html", user=user, form=form)

    if request.method == "POST":

        if form.validate() and form.inicio and form.fim and form.titulo:
            inicio = request.form.get("inicio")
            fim = request.form.get("fim")
            titulo = request.form.get("titulo")

            inicio = datetime.strptime(inicio, "%Y-%m-%d")
            fim = datetime.strptime(fim, "%Y-%m-%d")

            relatorio = escrever_relatorio(inicio, fim)

            if relatorio:
                arquivo = str(relatorio.relative_to("."))
                criar_relatorio(titulo, arquivo, inicio, fim)

                return redirect(url_for('mostrar_relatorios'))
            return redirect(request.url)
        else:
            return redirect(request.url)

@app.get("/compra/definir_analizada/<id>")
def definir_compra_analizada(id):
    compra = encontrar_compra_pelo_id(id)
    finalizar_compra(id, True)

    return redirect(url_for('mostrar_compra', protocolo=compra["protocolo"]))

@app.post("/compra/produto/consumo")
def enviar_consumo_produtos():
    data = request.get_json()

    token = request.cookies["user_token"]
    user = encontrar_usuario_pelo_token(token)

    produtos_selecionados = data["selecionados"]
    produtos_nao_selecionados = data["nao_selecionados"]

    for id_produto in produtos_selecionados:
        adicionar_consumidor_produto(id_produto, user["_id"])
    for id_produto in produtos_nao_selecionados:
        remover_consumidor_produto(id_produto, user["_id"])

    return data

@app.get("/compra/definir_nao_analizada/<id>")
def definir_compra_nao_analizada(id):
    compra = encontrar_compra_pelo_id(id)
    finalizar_compra(id, False)

    return redirect(url_for('mostrar_compra', protocolo=compra["protocolo"]))

@app.get("/relatorios")
def mostrar_relatorios():
    token = request.cookies["user_token"]
    user = encontrar_usuario_pelo_token(token)

    relatorios = obter_relatorios()

    return render_template("relatorio.html", user=user, relatorios=relatorios)

@app.get("/relatorio/download/<id>")
def download_relatorio(id):
    
    relatorio = encontrar_relatorio_pelo_id(id)

    return send_file(relatorio["arquivo"], as_attachment=True, download_name=str(relatorio['nome']+'.txt'))

@app.get("/relatorios/excluir/<id>")
def excluir_relatorio(id):
    remover_relatorio(id)
    return redirect(url_for("mostrar_relatorios"))

if __name__ == "__main__":
    app.run("0.0.0.0")


