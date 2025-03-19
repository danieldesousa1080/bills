from scrapper import *

url = input("digite a url: ")
try:
    get_bill_info(url)
except:
    print("Ocorreu um erro!")
exit()
