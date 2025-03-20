// O que acontece aqui? Aqui nós iremos fazer a lógica da seleção de produtos

var produtos = document.querySelectorAll("#selecao-produto")

btn_selecionar_tudo = document.querySelector("#selecionar-tudo")
btn_desmarcar_todos_os_produtos = document.querySelector("#desmarcar-tudo")
btn_enviar = document.querySelector("#enviar")

function selecionar_todos_os_produtos(valor_bool) {
    produtos.forEach(
        (p) => {
            p.checked = valor_bool
        }
    )
}


btn_selecionar_tudo.addEventListener("click", () => {
    selecionar_todos_os_produtos(true)
})

btn_desmarcar_todos_os_produtos.addEventListener("click", () => {
    selecionar_todos_os_produtos(false)
})

function get_produtos_nao_selecionados(){
    let nao_selecionados = []

    let tags_nao_selecionados = document.querySelectorAll("#selecao-produto").checked = false

    print(tags_nao_selecionados)
}

function get_produtos_selecionados() {
    let selecionados = []

    let tags_selecionados = document.querySelectorAll("#selecao-produto:checked")

    tags_selecionados.forEach(
        (t)=>{
            selecionados.push(t.value)
        }
    )

    return selecionados

} 

function enviar_produtos_selecionados(){
    let selecionados = []
    let nao_selecionados = []

    produtos.forEach(
        produto => {
            if (produto["checked"]){
                selecionados.push(produto.value)
            } else {
                nao_selecionados.push(produto.value)
            }
        }
    )

    fetch("/compra/produto/consumo", {
        method: "POST",
        body: JSON.stringify({
          selecionados: selecionados,
          nao_selecionados: nao_selecionados
        }),
        headers: {
          "Content-type": "application/json; charset=UTF-8"
        }
      }).then(data=> {
        location.reload()
      })
}