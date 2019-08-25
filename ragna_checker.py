

# Dependencias locais
from lib.requests import *
from lib.colorama import init as colorama_init
from lib.colorama import deinit as colorama_deinit
colorama_init(autoreset=True)
from lib.colorama import Fore, Back, Style

from lib.ragna_checker.core import test
############################

# Dependencias já instaladas por padrão
import sys
import argparse
import time
############################
# Ponto de entrada para console
def main():
    test()

if __name__ == "__main__":
    main()
