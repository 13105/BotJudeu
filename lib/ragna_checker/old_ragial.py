from core import RagnaChecker
import requests
from requests.exceptions import HTTPError
from requests.exceptions import ConnectionError
import urllib.parse
import sys
#Sopa do makako como parser html
from bs4 import BeautifulSoup

from colorama import init as colorama_init
from colorama import deinit as colorama_deinit

colorama_init(autoreset=True)
from colorama import Fore, Style

class RagialChecker(RagnaChecker):
    """Checker para o Ragial"""

    #gera lista de itens com base em um arquivo
    #retorno: [ [Tipo_de_loja, nome_do_item, comparador, valor_do_comparador],...]


    def getItemUrl(self, item_nome):
        #Pesquisa o nome de um item e retorna a url

        try:
            r = requests.get(self.url_pesquisa.format(urllib.parse.quote_plus(item_nome) ) , headers=self.http_headers)
            r.raise_for_status()

        except HTTPError:
            sys.exit("Erro HTTP: Não foi possivel consultar o nome do item \"{}\". Codigo de status HTTP: {}".format(item_nome, r.status_code))
            return str()
        except requests.exceptions.ConnectionError:
            sys.exit("{}Erro: Não foi possivel conectar ao site {}.".format(Fore.RED,self.url_host))


        pagina = BeautifulSoup(r.text, "html.parser")

        nada = pagina.find("td", {"class":"hundo"})
        if nada: return str()

        tds = pagina.find_all("td", {"class":"name"})

        for td in tds:
            #td.a.href

            td_item_nome = td.get_text().strip()
            if td_item_nome == item_nome:
                url = td.contents[1]["href"]
                return url.replace(self.url_item_base, "")


        return str()
        #Retorna nulo se nada

    def getItensIds(self):
        #carrega arquivo com url ja salva para evitar pesquisar sempre

        ids = []
        try:
            arq = open(self.itens_url_ids_arq,"r")
        except FileNotFoundError:
            sys.exit("{}Erro: Não foi possivel encontrar o arquivo \"{}\".".format(Fore.RED,self.itens_urlids_arq))

        for _ in arq:
            l = _.rstrip()
            if len(l) > 0:
                #l[0] = nome_do_item
                #l[1] = url_id
                ids.append(l.split("\x00"))






        arq.close()
        return ids

    def getLojas(self, item):
        try:
            r = requests.get(self.url_getLojas.format(item) , headers=self.http_headers)
            r.raise_for_status()


        except HTTPError as http_erro:
            print("{}Erro HTTP ao tentar atualizar um item: {}".format(Fore.RED, http_erro))
            return []

        pagina = BeautifulSoup(r.text, "html.parser")


        lojas = []
        for tr in pagina.find_all("tr"):
            loja = []
            for i, td in enumerate(tr):
                if i != 0:


                    # depois da primeira linha na coluna todos os outros valores são inteiros
                    # uso da lambda para remover caracteres e converter em inteiros
                    loja.append( int(str().join(list(filter(self.__is_digit, td.get_text().strip() )) )))
                else:

                    #Nenhum item a venda ?
                    if len(td.contents) <= 1: return []

                    #Nome da loja
                    loja.append(td.a.get_text().strip())

                    #Tipo de loja; Venda = True, Compra = False
                    loja.append(td.img["src"][-8:-4] == "vend")

                    # Não há necessidade de filtrar coordenadas
                    loja.append( td.div.get_text().strip())


            lojas.append(loja)



        return lojas

    def validarUrls(self, itens, ids):

        try:
            arq = open(self.itens_url_ids_arq, "a")

        except PermissionError:
            sys.exit("{}Erro: Permissões insuficientes para a criar/modificar arquivos.".format(Fore.RED))

        #lista de erros; exibe msg de arquivo invalido e finaliza programa quando len(err_li) > 0
        err_li = []

        #flag de retorno
        # False -> Erro
        # True -> Sucesso

        ret_flag = True
        #Verifica se a url_id já foi pesquisada para o item X na lista de itens

        for i, item in enumerate(itens):
            err = False

            #id já existe em ids ?
            for id in ids:
                #id[0] == Nome do item
                #id[1] == Url

                #item[1] == Nome do item
                #item[2] == reservado para url; padrão nulo

                if id[0] == item[1]:
                    #Item ja pesquisado, seta url_id em itens para o do arquivo de ids
                    if len(id[1]) > 0:
                        itens[i][2] = id[1]
                        break

                    # Item foi marcado como inexistente; Ativa flag de erro e printa msg

                    #seta flag global para retorno
                    if(ret_flag): ret_flag = False

                    err = True
                    print("{}Erro: Item denominado \"{}\" na linha {} não existe.".format(Fore.RED,item[1], i+1))
                    break

                #Se continuar nulo é porque não existe tal nome na lista

            if err: continue
            #itens = [ [<tipo_de_loja>, 'Nome_do_item', <url>, '>=', 123123], ...]]
            # Pesquisa nome do item, obtem url, adiciona na lista e escreve no arquivo;
            # Se encontrar tal item, seta url na lista de itens para comparar
            # Adiciona uma linha no fim do arquivo de itens para evitar pesquisar novamente
            # A linha contem o valor da url ou None caso não encontre nada
            #=============================================================================
            if not itens[i][2]:

                item_url_id = x.getItemUrl(item[1])

                print("Pesquisando pelo item \"{}{}{}\"... ".format(Fore.YELLOW, item[1],Fore.RESET), end="" )

                #Item encotrado  ?
                if (item_url_id):

                    #Seta url na lista de itens para comparar
                    itens[i][2] = item_url_id
                    #print(item[1],"->", item_url_id)
                    print("{}Encontrado!{}({}{}{}{})".format(Fore.GREEN, Fore.RESET,Style.BRIGHT,Fore.GREEN, item_url_id, Fore.RESET))

                else:
                    print("{}Não encontrado.".format(Fore.RED))
                    #adiciona linha do erro e nome do item na lista erros
                    err_li.append([i+1, item[1]])

                    #seta flag de erro global se nao setada
                    if(ret_flag): ret_flag = False
                arq.write(item[1]+"\x00"+item_url_id+"\n")

        arq.close()
        # Verifica se existe alguma linha que contem um item inexistente
        if len(err_li) > 0:

            for err in err_li:
                print("{}Erro: Item denominado \"{}\" na linha {} não existe.".format(Fore.RED,err[1], err[0]))


        return ret_flag


    def __init__(self, arg_tempo):
        super(RagialChecker, self).__init__(self.getLojas, arg_tempo )
        self.__is_digit = lambda x: x.isdigit()
        #Host base
        self.url_host = "http://ragial.org"
        self.itens_url_ids_arq = "ragial_ids"
        self.url_pesquisa = self.url_host + "/search/iRO-Renewal/{}"
        self.url_getLojas = self.url_host + "/live_reqo/iRO-Renewal/{}"
        self.url_item_base = self.url_host + "/item/iRO-Renewal/"
        self.http_headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0"}

#Prot. Retorna sempre array


x = RagialChecker(1)

x.AddItens([
 ["strawberry","QgI"],
 ["Kick step","hGK"]
])

#print(x.lista_itens)
#x.CheckerLoop()

itens = x.loadItensArq("itens.txt")
ids = x.getItensIds()

if x.validarUrls(itens, ids):
    if len(itens) > 0:
        print("Tudo certo !")
    else:
        print("{}Erro: Não há nenhum item na lista de itens para monitorar.".format(Fore.RED))

    # TODO:

# Url invalida
sys.exit()

#Verifica se id já existe na lista de ids; Key=nome_do_item
#for id in ids:
