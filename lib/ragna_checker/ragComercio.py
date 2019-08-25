from core import RagnaChecker
import requests
from requests.exceptions import HTTPError


class RagComercioChecker(RagnaChecker):
    """Checker para o RagComercio"""


    def getLojas(self, item_nome, url):

        r = requests.get(url)
        #return [
        #    ["Nome Loja", 300, 1],
        #    ["Nome Loja2", 100, 1]
        #]


    def __init__(self, arg_tempo):
        super(RagComercioChecker, self).__init__(self.getLojas, arg_tempo )

#Prot. Retorna sempre array

x = RagComercioChecker(1)
#x.attAddItens(["Banana","Uva"])
#print(x.lista_itens)
#x.CheckerLoop()

x.getLojas("Morango", "")
