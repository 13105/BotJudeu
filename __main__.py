import sys, colorama, argparse, time, requests
from colorama import init as colorama_init
from colorama import deinit as colorama_deinit

colorama_init(autoreset=True)
from colorama import Fore, Back, Style

from rag_comercio import rag_comercio_checker


testeObj = rag_comercio_checker(19)

print(testeObj.__doc__)
sys.exit()
__version__ = "1.0"
parser = argparse.ArgumentParser(prog="rag_comercio", usage="%(prog)s [options] champ1:champ2", description="Verifica preços de certos itens a cada X segundos.")
parser.add_argument("-t","--tempo",
help="Especifica o tempo de intervalo a cada atualização. Se não especificado o intervalo por padrão será 30 segundos.",
type=int,
 metavar="<segundos>",
default=30)

args, args_desconhecidos = parser.parse_known_args()

async def getLojas(item_nome, server):

    return
# Atualizando infinitamente
# A cada 30 segundos Verifica novamente


if __name__ == "__main__":

    #segundos para esperar a cada a cada atualizaçao
    # +1 para mostrar todos os segundos
    SegAtualizar = args.tempo +1


    try:

        # 1565784000
        # 1565784030 + 30


        TempoMarcado = time.time() + SegAtualizar
        UltimoSegundo = SegAtualizar

        while(1):
            TempoAtual = time.time()
            SegundosRestantes = round(TempoMarcado - TempoAtual)



            if (TempoMarcado >= TempoAtual) and (UltimoSegundo != SegundosRestantes):
                print("\033[2JProxima atualização em ({}{}{}{}) Segundos...".format(Fore.BLUE, Style.BRIGHT, SegundosRestantes, Style.RESET_ALL ),end="")
                UltimoSegundo = SegundosRestantes


            if UltimoSegundo == 0:
                print("\nAtualizando...")
                # (Re)faz request


                #Reseta timer para o argumento especificado
                TempoMarcado = time.time() + SegAtualizar
                UltimoSegundo = SegAtualizar



        colorama_deinit()
    except KeyboardInterrupt:
        colorama_deinit()
        print("\nFinalizando...")
        sys.exit()
