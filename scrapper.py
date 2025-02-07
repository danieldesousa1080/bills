from bs4 import BeautifulSoup
from requests import get
from pprint import pprint
from datetime import datetime
from database import *

def get_bill_info(url):

    soup = BeautifulSoup(get(url).text, 'html.parser')
    
    ## store info
    store = soup.find_all("table", class_='table table-hover')[3]
    store_name = store.find_all("td")[0].text.strip()
    store_cnpj = store.find_all("td")[1].text.strip()
    store_insc_estadual = store.find_all("td")[2].text.strip()
    store_UF = store.find_all("td")[3].text.strip()
    
    estabelecimento = criar_estabelecimento(store_name,store_cnpj, store_insc_estadual, store_UF)


    ## purchase info
    purchase_itens_qtd = float(soup.find_all('div', class_="col-lg-2")[0].text.strip().replace(",","."))
    purchase_total_price = float(soup.find_all('div', class_="col-lg-2")[1].text)
    purchase_payment_method = soup.find("div", {"id": "formPrincipal:j_idt74:0:j_idt82"}).text
    p_date_str = soup.find_all("table", class_="table-hover")[5].find_all("td")[3].text
    purchase_date = datetime.strptime(p_date_str, "%d/%m/%Y %H:%M:%S")
    purchase_protocol = soup.find_all("table", class_="table-hover")[7].find("td").text

    compra = criar_compra(purchase_protocol, purchase_itens_qtd, purchase_total_price, purchase_payment_method, purchase_date, estabelecimento)



    ## products info
    if compra:
        products = soup.find("table", class_="table table-striped")
        for product in products.find_all("tr"):
            product_name = product.find("h7").text.strip()
            product_code = product.find("td").text.replace(product_name, "").strip().strip("(Código: ").strip(")")
            product_qtt = float(product.find_all("td")[1].text.strip('Qtde total de ítens: '))
            product_unidade = product.find_all("td")[2].text[4:]
            product_valor_total = float(product.find_all("td")[3].text.strip("Valor total R$: R$ ").replace(",", "."))
            
            produto = criar_produto(product_name, product_qtt, product_unidade, product_valor_total, compra, product_code)


