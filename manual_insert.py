from scrapper import *

codigo = input("digite o codigo da nf: ")
try:
    url = f"https://portalsped.fazenda.mg.gov.br/portalnfce/sistema/qrcode.xhtml?p={codigo}%7C3%7C1"
    get_bill_info(url)
    print("Nota incluida com sucesso!")
except:
    print("Ocorreu um erro!")
exit()
