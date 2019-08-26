# Dependencias locais

from colorama import init as colorama_init
from colorama import deinit as colorama_deinit
colorama_init(autoreset=True)
from colorama import Fore, Style
############################

# Dependencias já instaladas por padrão
import time
import sys

class RagnaChecker(object):
    """Objeto fundamental para criação de um verificador de preços para ragnarok."""



    def loadItensArq(self, arquivo):

        try:
            arq = open(arquivo,"r")
        except FileNotFoundError:
            sys.exit("Erro: Não foi possivel encontrar o arquivo \"{}\".".format(arquivo))

        # Array com dados contidos no arquivo
        # [ item_nome, comparadores, cmp_val ],
        arq_dados = []

        for _i ,_ in enumerate(arq):

            #remove espaços e tabs do inicio e do fim da linha
            l = _.strip()
            linha_num = (_i + 1)
            loja_tipo = 0
            #ignora comentarios ou linhas vazias
            if( len(l) <= 0 or l[0] == "#"): continue


            # Verifica se é compra ou venda

            if not (l[:2] == "C>") and not (l[:2] == "c>"):
                #Remove V>
                if (l[:2] == "V>") or (l[:2] == "v>"): l = l[2:].lstrip()

            else:
                #Tipo de loja = 1: Venda
                loja_tipo = 1
                #Remove "C>"
                l = l[2:].lstrip()

            comparadores = self.getComparadores(l)

            #valor após o comparador
            cmp_val = -1
            item_nome = l

            # 0 operadores
            if comparadores == -1:
                item_nome = item_nome.title()

            elif comparadores:
                item_nome, cmp_val = l.split(comparadores)

                item_nome = item_nome.rstrip().title()

                if len(cmp_val) < 1 :
                    print("Erro: Na linha {}: Valor não especificado após o uso do comparador; A linha será ignorada.".format(linha_num))
                    continue
                cmp_val = cmp_val.lstrip()


                for _ in cmp_val:
                    if not _.isdigit():
                        print("Erro: Na linha {}: O valor \'{}\' é invalido; A linha será ignorada.".format(linha_num,cmp_val))
                        continue

                # valor valido
                cmp_val = int(cmp_val)

            else:
                print("Erro: A linha {} na lista de itens será ignorada pois a sintaxe é invalida.".format(linha_num))
                continue



            arq_dados.append([loja_tipo, item_nome, str(), comparadores, cmp_val])

        # item_nome, comparadores, cmp_val; validos
        arq.close()
        return arq_dados

    # Adiciona/Remove item X da lista de itens para verificar
    def AddItens(self, arr_itens ):

        # 0: Tipo de loja
        # 1: Nome do item
        # 2: Url do item

        _arr_itens = list(map(lambda x: x[:2], arr_itens))

        # Remove duplicatas
        _arr_itens = list(set( tuple(sub) for sub in _arr_itens ))

        #associa o valor de um item de acordo com a ultima entrada dele descrita
        for item in arr_itens:
            for _i, _item in enumerate(_arr_itens):
                if (item[0] == _item[0]) and (item[1] == _item[1]):
                    _arr_itens[_i] = item
                    break





        #inserção do item na lista de itens
        for x in _arr_itens:

            self.lista_itens.append([x , [] ])
            self.old_lista_itens.append([])

    def getComparadores(self, l):

        #getComparadores Retorno:
        #   None:   Erro de sintaxe
        #   Str:    Sucesso, retorna operador
        #   -1:     Sucesso, 0 operadores

        # Recebe uma string como argumento e retorna comparadores se valido;

        #verifica se a string contém mais de 2 operadores de calculo
        if len(list(filter(self.__contain_ops ,l ))) > 2: return


        ultimo_idx = len(l) -1

        for i_x, x in enumerate(l):

            #Existe sucessor ?
            x_suc_existe = i_x < ( len(l) - 1 )

            #Existe antecessor ?
            x_ant_existe = i_x != 0

            if (x == ">") or (x == "<"):

                if x_suc_existe and (l[i_x + 1] == "="):
                    # >= ou <=
                    return  x + l[i_x + 1]

                elif x_suc_existe and ( (l[i_x + 1] == "<") or (l[i_x + 1] == ">") ):
                    # >>, <<, ><, <> : Erro
                    return

                elif x_ant_existe and (l[i_x - 1] == "="):
                    # =< ou => : Erro
                    return

                else:

                    # remove operador detectado atual da string (< ou >)
                    z = l[: i_x ] + l[i_x + 1: ]

                    # Verifica se existe algum outro operador comparador na string;
                    # Obs: Se o codigo até chegou até aqui é porque o caractere sucessor ou antessor
                    # não são operadores.
                    # pode ser que a linha contenha apenas um caractere comparador ou seja uma linha invalida.

                    # Operadores não juntos, Linha invalida.
                    if len(list(filter(self.__contain_ops, z ))) > 0: return

                    # 1 operador apenas; retorna-o
                    return x
                    # > ou <

            #Se chegou até o ultimo caractere da string é porque não existem operadores nessa string
            #logo operador será <= por padrão
            if(i_x == ultimo_idx): return -1



    def compararLojas(self, l_velha, l_nova):
        #compara duas listas, primeiro a velha seguido pela nova;


        arr_p_nova = []
        arr_p_velha = []

        #cria lista contendo comparador e valor (ex: [ ['>',100 ],...  ) para cada item;
        arr_cmp_val = list(map(
        lambda x: [
            x[0][3] if x[0][3] is not -1 else "<=" ,
            x[0][4] if x[0][4] is not -1 else self.__MAX_ZENY

         ], l_nova))


        #calcula o melhor preço para cada item da velha lista
        for _i, _ in enumerate(l_velha):

            #mp = melhor preço
            #mpi = melhor preço item
            mpi = []
            mp = -1

            #obtem valores aceitaveis de acordo com o range do comparador
            for __i, __ in enumerate(_):

                #print(__[4], arr_cmp_val[_i][0], str(arr_cmp_val[_i][1])," == ",eval(str(__[4]) + arr_cmp_val[_i][0] + str(arr_cmp_val[_i][1]) ) )

                #MP <comparador> <comparador_valor> ?
                #valor esta no range aceitavel ?
                if eval(str(__[4]) + arr_cmp_val[_i][0] + str(arr_cmp_val[_i][1]) ):

                    if (mp > -1) and not (mp > __[4]):
                        continue
                    mp = __[4]
                    mpi = __

            if mp != -1:
                arr_p_velha.append([mp, mpi])
            else:
                arr_p_velha.append([mp])

        #calcula o melhor preço para cada item da nova lista
        for _i, _ in enumerate(l_nova):

            #mp = melhor preço
            #mpi = melhor preço item
            mpi = []
            mp = -1

            #obtem valores aceitaveis de acordo com o range do comparador
            for __i, __ in enumerate(_[1]):

                #print(__[4], arr_cmp_val[_i][0], str(arr_cmp_val[_i][1])," == ",eval(str(__[4]) + arr_cmp_val[_i][0] + arr_cmp_val[_i][1] ) )


                #MP <comparador> <comparador_valor> ?
                #valor esta no range aceitavel ?
                if eval(str(__[4]) + arr_cmp_val[_i][0] + str(arr_cmp_val[_i][1]) ):

                    if (mp > -1) and not (mp > __[4]):
                        continue
                    mp = __[4]
                    mpi = __

            if mp != -1:
                arr_p_nova.append([mp, mpi])
            else:
                arr_p_nova.append([mp])


        # por fim compara as duas arrays
        for _i, _ in enumerate(arr_p_velha):


            if (_[0] != -1) and (arr_p_nova[_i][0] != -1):
                #verifica se o preço dos itens foi modificado

                #nada mudou ?
                if (_[0] == arr_p_nova[_i][0]):
                    continue

                #obtem informação sobre a loja
                loja_info = self.__getLoja(arr_p_nova[_i][1][2])


                #compra ou venda ?
                if (l_nova[_i][0][0] != 1):
                    c_ou_v = "venda"
                    cor_boa = Fore.GREEN
                else:
                    c_ou_v = "compra"
                    cor_boa = Fore.RED

                #variavel percentual
                vp = round( ((arr_p_nova[_i][0] - _[0]) / _[0]) * 100)



                if (_[0] < arr_p_nova[_i][0]):

                    print(
                    f"{cor_boa}O preço mais barato de {c_ou_v} do item '{Style.BRIGHT}{Fore.MAGENTA}{l_nova[_i][0][1]}{cor_boa}' subiu ! \n"
                    f"Subiu de {Style.DIM}{Fore.WHITE}{_[0]:,}z{Style.NORMAL}{cor_boa}"
                    f" para {Style.BRIGHT}{cor_boa}{arr_p_nova[_i][0]:,}z{cor_boa} ({vp}%);\n"
                    f"- Player:\t\t{Style.BRIGHT}{Fore.CYAN}{loja_info[0]}{cor_boa}\n"
                    f"- Nome da loja:\t\t{Style.NORMAL}{Fore.WHITE}{arr_p_nova[_i][1][0]}{cor_boa}\n"
                    f"- Local:\t\t{Fore.WHITE}{loja_info[1]}{cor_boa}\n"
                    f"- Quantidade:\t\t{Fore.WHITE}{arr_p_nova[_i][1][3]}x{cor_boa}\n"
                    f"- Preço:\t\t{Style.BRIGHT}{cor_boa}{arr_p_nova[_i][0]:,}{cor_boa}z\n")

                elif (_[0] > arr_p_nova[_i][0]):


                    print(
                    f"{cor_boa}O preço mais barato de {c_ou_v} do item '{Style.BRIGHT}{Fore.MAGENTA}{l_nova[_i][0][1]}{cor_boa}' abaixou ! \n"
                    f"Abaixou de {Style.DIM}{Fore.WHITE}{_[0]:,}z{Style.NORMAL}{cor_boa}"
                    f" para {Style.BRIGHT}{cor_boa}{arr_p_nova[_i][0]:,}z{cor_boa} ({vp}%);\n"
                    f"- Player:\t\t{Style.BRIGHT}{Fore.CYAN}{loja_info[0]}{cor_boa}\n"
                    f"- Nome da loja:\t\t{Style.NORMAL}{Fore.WHITE}{arr_p_nova[_i][1][0]}{cor_boa}\n"
                    f"- Local:\t\t{Fore.WHITE}{loja_info[1]}{cor_boa}\n"
                    f"- Quantidade:\t\t{Fore.WHITE}{arr_p_nova[_i][1][3]}x{cor_boa}\n"
                    f"- Preço:\t\t{Style.BRIGHT}{cor_boa}{arr_p_nova[_i][0]:,}{cor_boa}z\n")

            elif (_[0] == -1) and (arr_p_nova[_i][0] != -1):
                #alguem colocou o item para ser vendido

                loja_info = self.__getLoja(arr_p_nova[_i][1][2])

                c_ou_v = "comprando" if l_nova[_i][0][0] == 1 else "vendendo"


                print(f"{Fore.YELLOW}O jogador {Style.BRIGHT}{Fore.CYAN}{loja_info[0]}{Style.NORMAL}{Fore.YELLOW} "
                 f"abriu uma loja {c_ou_v} o item '{Style.BRIGHT}{Fore.MAGENTA}{l_nova[_i][0][1]}{Style.NORMAL}{Fore.YELLOW}'\n"
                 f"- Player:\t\t{Style.BRIGHT}{Fore.CYAN}{loja_info[0]}{Style.NORMAL}{Fore.YELLOW}\n"
                 f"- Nome da loja:\t\t{Fore.WHITE}{arr_p_nova[_i][1][0]}{Fore.YELLOW}\n"
                 f"- Local:\t\t{Fore.WHITE}{loja_info[1]}{Fore.YELLOW}\n"
                 f"- Quantidade:\t\t{Fore.WHITE}{arr_p_nova[_i][1][3]}x{Fore.YELLOW}\n"
                 f"- Preço:\t\t{Style.BRIGHT}{Fore.YELLOW}{arr_p_nova[_i][0]:,}{Fore.YELLOW}z\n")

                continue
            elif (_[0] != -1) and (arr_p_nova[_i][0] == -1):
                #alguem fechou a loja que estava aberta

                c_ou_v = "comprando" if (l_nova[_i][0][0] == 1) else "vendendo"

                print(f"{Fore.RED}Nenhuma loja agora está {c_ou_v}{Style.BRIGHT}{Fore.MAGENTA} {l_nova[_i][0][1]}{Style.NORMAL}{Fore.RED}.")


            else:
                #-1 e -1; o item não esta a venda
                continue



        print(arr_p_velha)
        print(arr_p_nova)
        #print(l_nova)


    def CheckerLoop(self):

        #primeira atualização flag;
        PAF = True

        while(True):
            for seg in range(self.att_tempo,0,-1):
                print("Proxima atualização em ({}{}{}{}) Segundos...".format(Fore.BLUE, Style.BRIGHT, seg, Style.RESET_ALL ))
                time.sleep(1)



            for i, _ in enumerate(self.lista_itens):
                #_ equivale a :  [ [loja1_dados],[lojas] ]

                #Salva dados antigos para comparação
                self.old_lista_itens[i] = _[1]


                # (Re)faz request e atualiza dados
                #Passa tipo de loja(_[0][0]) e url do item(_[0][2]) para obter as lojas

                self.lista_itens[i][1] = self.__getLojas(_[0][0], _[0][2])


            # Após obter nova lista de lojas compara a lista antiga com a nova
            if not PAF:
                self.compararLojas(self.old_lista_itens, self.lista_itens)
            else:
                PAF = False
            #print(self.lista_itens)
            #print("\r\033[2K",end="")




    def __init__(self, func_getLojas, func_getLojaInfo, arg_tempo):
        self.att_tempo = arg_tempo
        self.__getLojas = func_getLojas
        self.__getLoja = func_getLojaInfo
        self.__MAX_ZENY = (2 ** 31) - 1
        #lista de matrizes contendo item_nome, url, lojas[]
        self.lista_itens = []

        #Lista de itens desatualizada, usada como buffer secundario para comparação de valores
        self.old_lista_itens = []

        #verifica se tem mais de 2 operadores de calculo
        self.__contain_ops = lambda x: (x is ">" ) or (x is "<") or (x is "=")
