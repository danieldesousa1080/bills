from flask import Flask, request
from flask import render_template, make_response, redirect, session, url_for
from datetime import date, datetime
from wtforms import Form, DateField, StringField, PasswordField, SearchField


class RangeDateForm(Form):
    inicio = DateField("inicio", format="%Y-%m-%d")
    fim = DateField("fim", format="%Y-%m-%d")


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

from database import (
    compras_por_periodo,
    valor_total_por_periodo,
    procurar_usuario,
    criar_usuario,
    validar_usuario,
    encontrar_usuario_pelo_token,
)

from mapper import *
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "abc123"
CORS(app)


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
        usuario_encontrado = procurar_usuario(usuario=usuario)

        if usuario_encontrado:
            return redirect(url_for("registro"))
        
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

    form = RangeDateForm(request.args)

    if form.validate() and form.inicio.data and form.fim.data:
        inicio = datetime.fromordinal(form.inicio.data.toordinal())
        fim = datetime.fromordinal(form.fim.data.toordinal())

        compras = compras_por_periodo(inicio, fim).sort("data", -1)
        valor = valor_total_por_periodo(inicio, fim)

    else:
        compras = compras_por_periodo().sort("data", -1)
        valor = valor_total_por_periodo()
    
    compras = mapper_compras(compras)

    data = {"compras": compras, "valor_periodo": valor, "form": form}

    return render_template("compras.html", context=data, user=user)


@app.get("/compra/<protocolo>")
def mostrar_compra(protocolo):
    token = request.cookies["user_token"]
    user = encontrar_usuario_pelo_token(token)

    compra = encontrar_compra(protocolo)
    produtos: list = procurar_produtos_por_compra(compra["_id"])

    data = {"compra": mapper_compra(compra), "produtos": mapper_produtos(produtos)}

    return render_template("compra.html", context=data, user=user)


@app.post("/compra/<protocolo>")
def atrelar_produtos(protocolo):
    produtos = request.form.getlist("produtos")
    token = request.cookies.get("user_token")

    for produto in produtos:
        registrar_pagamento_produto(produto, encontrar_usuario_pelo_token(token)["_id"])
    
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
    data = {"produtos": mapper_produtos(produtos), "nome": nome, "form": form}
    return render_template("produtos.html", context=data, user=user)

@app.get("/registar_pagamento_compra/<id>")
def pagar_compra(id):
    compra = encontrar_compra_pelo_id(id)
    if compra and not compra["pagador"]:
        registrar_pagamento_compra(compra=compra)

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

@app.get("/admin")
def admin_page():
    token = request.cookies["user_token"]
    user = encontrar_usuario_pelo_token(token)

    if user["admin"]:
        return render_template("admin.html", user=user)
    return redirect("/")


if __name__ == "__main__":
    app.run("0.0.0.0")
