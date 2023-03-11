import os
import csv
import glob
import time
import json
import shutil
import pandas as pd
from datetime import date, timedelta, datetime
from pathlib import Path
from cryptography.fernet import Fernet
import html5lib
import lxml
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileReader, PdfFileWriter
import asyncio
from pyppeteer import launch
import openpyxl
from functools import partial
import threading
import socket


# classe de referencia com metodos recorrentes de criação, leitura e exclusão de arquivos
class Referencias:
    def __init__(self,gui:object=None):
        self.db_local = None
        #if gui !=None:
        self.gui = gui
        print(gui)


    @staticmethod
    def verificar_ou_criar_pasta(pasta:str,caminho_externo:str=''):
        #print('#' * 100)
        #print('METODO: def verificar_criar_pasta(pasta:str):')
        #print('#' * 100)
        pasta = str(pasta).lower().strip()
        if len(caminho_externo)>0:
            caminho = caminho_externo + f'\{pasta}'
        else:
            caminho = str(os.path.abspath(os.getcwd()))
            barra = '\ '
            barra = barra.strip()
            lista_pasta1 = str(pasta).split(barra)
            #print(lista_pasta1)
            lista_pasta2 = list(map(lambda fol: str(fol).split('/'),lista_pasta1))
            #print(lista_pasta2)
            lista_pasta=[]
            for lista in lista_pasta2:
                for item in lista:
                    lista_pasta.append(item)
            #print(lista_pasta)
            if not ':' in pasta:
                for fol in lista_pasta:
                    caminho += f'\{fol}'
                    try:
                        os.mkdir(caminho)
                    except Exception as e:
                        #print(e)
                        pass
            else:
                caminho = pasta
        try:
            #os.mkdir(pasta)
            os.mkdir(caminho)
            #print(f'{pasta} criada com sucesso!')
        except Exception as e:
            #print('Pasta já existe ou não foi possivel criar-la!')
            #print(e)
            pass
        #print(caminho)
        return caminho


    # funcao para criar tabela de excel com as informações das credenciais de acesso de forma dinamica
    # passado o nome de referencia para o arquivo credenciais (apelido_credenciais) a ser criado e uma lista com os parametros (lista_parametros)
    @staticmethod
    def criar_credenciais_old(apelido_credenciais:str,lista_parametros:list,formato:str='json',linha_ou_coluna:str='linha',
                          cript:str='s',ask_usuario:str='s',lista_parametros_resp_direct:list=[]) -> None:
        #print('#' * 100)
        #print('METODO: def criar_credenciais(apelido_credenciais:str,lista_parametros:list) -> None:')
        #print('#' * 100)
        gui = Referencias.Interface()
        credenciais = Referencias.ler_credenciais(apelido_credenciais)
        if len(credenciais)<=0:
            #inicializa a lista para as respostas do usuario com o mesmo tamanho da lista de parametros informada e com valores vazios
            apelido_credenciais = str(apelido_credenciais).upper().strip()
            lista_resp_parametros = []
            tamanho = 0
            for j in range(len(lista_parametros)):
                lista_resp_parametros.append('')
            for i, parametro in enumerate(lista_parametros):
                parametro = str(parametro).upper().strip()
                lista_parametros[i] = parametro
                tamanho = 0
                contator_ask = 0
                while tamanho <=0 and contator_ask < 3:
                    contator_ask+=1
                    # pergunta ao usuario as credenciais
                    if ask_usuario == 's':
                        if cript == 's':
                            lista_resp_parametros[i] = Referencias.criptografar_dados(
                                gui.ask_user(parametro, apelido_credenciais))
                        else:
                            lista_resp_parametros[i] = gui.ask_user(parametro, apelido_credenciais)
                    else:
                        if len(lista_resp_parametros)== len(lista_parametros):
                            if cript == 's':
                                lista_resp_parametros[i] = Referencias.criptografar_dados(
                                    lista_parametros_resp_direct[i])
                            else:
                                lista_resp_parametros[i] = lista_parametros_resp_direct[i]
                        else:
                            gui.aviso('tamanho da lista_resp_parametros é diferente do tamanho da lista_parametros')

                    tamanho = len(lista_resp_parametros[i])
                    if tamanho == 0 or lista_resp_parametros[i] == "None":
                        #print('Insira as informações necessarias corretamente!!')
                        pass
                if tamanho == 0 or lista_resp_parametros[i] == "None":
                    break
            if tamanho != 0 and lista_resp_parametros[i] != "None":
                formato = str(formato).upper()
                if 'EXCEL' in formato:
                    #print('Salvando credenciais no formato .xlsx')
                    #cria um dataframe para cada uma das listas e concatena elas no final
                    linha_ou_coluna = str(linha_ou_coluna).upper().strip()
                    if 'COLUNA' in linha_ou_coluna:
                        df_parametros_completo = Referencias.criar_tabela_lista_como_linhas([lista_resp_parametros],lista_parametros,f"Credenciais_{apelido_credenciais}",'parametros')
                    else:
                        df_parametros_completo = Referencias.criar_tabela_lista_como_colunas([lista_parametros,lista_resp_parametros],
                                                                                            ['Credenciais','Credenciais Dados'],
                                                                                            f"Credenciais_{apelido_credenciais}",
                                                                                            'parametros')
                    credenciais = Referencias.ler_credenciais(apelido_credenciais)
                    return credenciais
                elif 'JSON' in formato:
                    #print('Salvando credenciais no formato .json')
                    credenciais={}
                    caminho = Referencias.verificar_ou_criar_pasta('parametros')
                    for l, parametro in enumerate(lista_parametros):
                        credenciais[parametro] = lista_resp_parametros[l]
                    out_file = open(caminho + f"\Credenciais_{apelido_credenciais}.json", "w")

                    json.dump(credenciais, out_file, indent=6)

                    out_file.close()
                    credenciais = Referencias.ler_credenciais(apelido_credenciais)
                    return credenciais
                else:
                    #print('Formato invalido!!! Só é permitido formatos do tipo EXCEL ou JSON')
                    pass
            else:
                #print('Nenhuma tabela foi gerada pois as informações não foram passadas corretamente')
                pass
        return credenciais

    #@staticmethod
    def criar_credenciais(self,apelido_credenciais: str, lista_parametros: list, formato: str = 'json',
                          linha_ou_coluna: str = 'linha',
                          cript: str = 's', ask_usuario: str = 's', lista_parametros_resp_direct: list = [],destroy_gui:bool=True):

        # print('#' * 100)
        # print('METODO: def criar_credenciais(apelido_credenciais:str,lista_parametros:list) -> None:')
        # print('#' * 100)
        #print(gui)
        # if gui == None and self.gui == None:
        #     from ClasseInterfaceCustom import Interface
        #     gui = Interface()
        # else:
        gui = self.gui
        lista_parametros = [str(parametro).upper().strip() for parametro in lista_parametros]
        parametros_copy = lista_parametros.copy()
        credenciais = Referencias.ler_credenciais(apelido_credenciais)
        if len(credenciais) <= 0:
            # inicializa a lista para as respostas do usuario com o mesmo tamanho da lista de parametros informada e com valores vazios
            apelido_credenciais = str(apelido_credenciais).upper().strip()
            lista_resp_parametros = []
            tamanho = 0
            if 'chrome_driver' in apelido_credenciais.lower():
                check_box = False
            else:
                check_box = True
            if ask_usuario == 's':
                if cript == 's':
                    _ = gui.config_credentials_option(parametros_copy,destroy_gui,checkbox=check_box)

                    lista_resp_parametros = gui.resp_params_entry
                    gravar = gui.checkbox_1_remember_me
                    if 'chrome_driver' in apelido_credenciais.lower():
                        gravar = '1'

                    lista_resp_parametros = [Referencias.criptografar_dados(dado) for dado in lista_resp_parametros]
                    print(lista_resp_parametros)
                    print(gravar)
                    if str(gravar) == '1':
                        tamanho = len(lista_resp_parametros)
                    else:
                        tamanho= 0
                        credenciais = {}
                        for l, parametro in enumerate(lista_parametros):
                            credenciais[parametro] = lista_resp_parametros[l]
                else:
                    # lista_resp_parametros[i] = gui.ask_user(parametro, apelido_credenciais)
                    _ = gui.config_credentials_option(parametros_copy,destroy_gui,checkbox=check_box)
                    lista_resp_parametros = gui.resp_params_entry
                    gravar = gui.checkbox_1_remember_me
                    if 'chrome_driver' in apelido_credenciais.lower():
                        gravar = '1'
                    if str(gravar) == '1':
                        tamanho = len(lista_resp_parametros)
                    else:
                        tamanho= 0
                        credenciais={}
                        for l, parametro in enumerate(lista_parametros):
                            credenciais[parametro] = lista_resp_parametros[l]
            else:
                lista_resp_parametros = ['' for param in lista_parametros]
                for i, parametro in enumerate(lista_parametros):
                    parametro = str(parametro).upper().strip()
                    lista_parametros[i] = parametro
                    tamanho = 0
                    contator_ask = 0
                    while tamanho <= 0 and contator_ask < 3:
                        contator_ask += 1
                        if len(lista_resp_parametros) == len(lista_parametros):
                            if cript == 's':
                                lista_resp_parametros[i] = Referencias.criptografar_dados(
                                    lista_parametros_resp_direct[i])
                            else:
                                lista_resp_parametros[i] = lista_parametros_resp_direct[i]
                        else:
                            gui.aviso('tamanho da lista_resp_parametros é diferente do tamanho da lista_parametros')

                        tamanho = len(lista_resp_parametros[i])
                        if tamanho == 0 or lista_resp_parametros[i] == "None":
                            # print('Insira as informações necessarias corretamente!!')
                            pass
                    if tamanho == 0 or lista_resp_parametros[i] == "None":
                        break
            if tamanho != 0 and lista_resp_parametros[0] != "None":
                formato = str(formato).upper()
                if 'EXCEL' in formato:
                    # print('Salvando credenciais no formato .xlsx')
                    # cria um dataframe para cada uma das listas e concatena elas no final
                    linha_ou_coluna = str(linha_ou_coluna).upper().strip()
                    if 'COLUNA' in linha_ou_coluna:
                        df_parametros_completo = Referencias.criar_tabela_lista_como_linhas([lista_resp_parametros],
                                                                                            lista_parametros,
                                                                                            f"Credenciais_{apelido_credenciais}",
                                                                                            'parametros')
                    else:
                        df_parametros_completo = Referencias.criar_tabela_lista_como_colunas(
                            [lista_parametros, lista_resp_parametros],
                            ['Credenciais', 'Credenciais Dados'],
                            f"Credenciais_{apelido_credenciais}",
                            'parametros')
                    credenciais = Referencias.ler_credenciais(apelido_credenciais)
                    return credenciais
                elif 'JSON' in formato:
                    # print('Salvando credenciais no formato .json')
                    credenciais = {}
                    caminho = Referencias.verificar_ou_criar_pasta('parametros')
                    for l, parametro in enumerate(lista_parametros):
                        credenciais[parametro] = lista_resp_parametros[l]
                    out_file = open(caminho + f"\Credenciais_{apelido_credenciais}.json", "w")

                    json.dump(credenciais, out_file, indent=6)

                    out_file.close()
                    credenciais = Referencias.ler_credenciais(apelido_credenciais)
                    return credenciais
                else:
                    # print('Formato invalido!!! Só é permitido formatos do tipo EXCEL ou JSON')
                    pass
            else:
                # print('Nenhuma tabela foi gerada pois as informações não foram passadas corretamente')
                pass
        return credenciais

    #função para ler as credencias solicitada e retornar a tabela
    @staticmethod
    def ler_credenciais(apelido_credenciais:str):
        #print('#' * 100)
        #print('METODO: def ler_credenciais(apelido_credenciais:str) -> pd.DataFrame:')
        #print('#' * 100)
        caminho = Referencias.verificar_ou_criar_pasta('PARAMETROS')
        apelido_credenciais = str(apelido_credenciais).upper().strip()
        try:
            credenciais = Referencias.importar_arquivo('PARAMETROS',f'Credenciais_{apelido_credenciais}','','',0)
            #print(credenciais)
        except Exception as e:
            #print('O arquivo não foi encontrado!!!')
            #print(e)
            credenciais = None
        return credenciais

    # função para retornar o valor das credenciais em linha acessando apenas pelo indice
    @staticmethod
    def retornar_valor_credenciais_linha_by_parametro(credenciais: pd.DataFrame, parametro: str) -> object:
        credenciais.set_index('Credenciais',inplace = True)
        return credenciais['Credenciais Dados'][parametro]

    # função para retornar o valor das credenciais em linha acessando apenas pelo indice
    @staticmethod
    def retornar_valor_credenciais_linha_by_posicao(credenciais: pd.DataFrame, posicao: int)-> object:
        #credenciais.set_index('Credenciais')
        return credenciais['Credenciais Dados'][posicao]

    #função para excluir os arquivos da pasta informada
    @staticmethod
    def delete_Files_Folder_os(folder:str) -> None:
        #print('#' * 100)
        #print('METODO: def delete_Files_Folder(folder:str):')
        #print('#' * 100)
        asteristic = (r'\*.*')
        lista = folder.split('\\')
        caminho = Referencias.verificar_ou_criar_pasta(lista[-1])
        caminho_to_delete = caminho + asteristic
        caminho_to_delete =str(caminho_to_delete)
        print(caminho_to_delete)
        try:
            for f in glob.glob(caminho_to_delete):
                os.remove(f)
        except Exception as e:
            #print(f'Não foi possivel excluir os arquivos da pasta {folder}')
            print(e)
            if "O arquivo já está sendo usado por outro processo" in str(e):
                raise Exception(str(e))
            #pass
        #Referencias.pause()
        return

    # função para excluir os arquivos da pasta informada
    @staticmethod
    def delete_Files_Folder(folder: str) -> None:
        # print('#' * 100)
        # print('METODO: def delete_Files_Folder(folder:str):')
        # print('#' * 100)
        # asteristic = (r'\*.*')
        # lista = folder.split('\\')
        # caminho_to_delete = Referencias.verificar_ou_criar_pasta(lista[-1])
        # caminho_to_delete = caminho + asteristic
        # caminho_to_delete = str(caminho_to_delete)
        print(folder)
        try:
            shutil.rmtree(folder)

            # directory = Path(caminho_to_delete)
            # #directory.rmdir()
            # directory.unlink()
        except Exception as e:
            # print(f'Não foi possivel excluir os arquivos da pasta {folder}')
            print(e)
            if "O arquivo já está sendo usado por outro processo" in str(e):
                raise Exception(str(e))
            #pass
        Referencias.verificar_ou_criar_pasta(folder)
        #Referencias.pause()
        return

    #função para excluir a lista de colunas da tabela passadas como parametros
    @staticmethod
    def excluir_colunas_tabela(df:pd.DataFrame,lista_colunas_excluir:list) -> pd.DataFrame:
        #print('#' * 100)
        #print('METODO: def excluir_colunas_tabela(df:pd.DataFrame,lista_colunas_excluir:list):')
        #print('#' * 100)
        #print(df)
        colunas = list(df.columns)
        for k, coluna_del in enumerate(lista_colunas_excluir):
            for i, coluna in enumerate(colunas):
                if str(coluna_del) in str(coluna):
                    df.drop(coluna, axis=1, inplace=True)
        #print(df)
        return df

    #função para leitura de arquivos em pastas especificas independente do nome
    @staticmethod
    def importar_arquivo(ler_pasta:str,opcional_arquivo:str='',
                         colocar_na_pasta:str='',nome_relatorio:str='',
                         pular_n_linhas:int=0,header_read:int=0,usecols:list=None,index_col:list = None,formato:str='excel',
                         header_write:bool=True,index_write:bool=True,sem_indice:bool=False,caminho_opcional:str='',
                         sheet_name:str=0,delete_unnamed = True,encoding:str='ISO-8859-1', engine:str=None,dtype:str=object,n_tabela_html:int=0):
        #print('#' * 100)
        #print('METODO: def importar_arquivo(ler_pasta:str,opcional_arquivo:str,colocar_na_pasta:str,nome_relatorio:str,pular_n_linhas:int):')
        #print('#' * 100)
        lista = ler_pasta.split('\\')
        caminho = Referencias.verificar_ou_criar_pasta(lista[-1])
        lista_arquivos = os.listdir(caminho)
        meu_arquivo = pd.DataFrame()
        if len(lista_arquivos)>0:
            for k, arquivo in enumerate(lista_arquivos):
                #print(arquivo)
                if len(opcional_arquivo) > 0:
                    if opcional_arquivo in str(arquivo):
                        caminho_arquivo = Path(caminho) / arquivo
                        break
                    else:
                        if k == (len(lista_arquivos)-1):
                            #print(f'Arquivo Opcional {opcional_arquivo} não encontrado na pasta {ler_pasta}')
                            return meu_arquivo
                else:
                    caminho_arquivo = Path(caminho) / arquivo
            #print(caminho_arquivo)
            contador_erro_import = 0
            while contador_erro_import <= 10 and len(meu_arquivo) < 1:
                if '.xls' in str(caminho_arquivo).lower():
                    try:
                        print('tentando abrir em formato html...')
                        lista_caminho = str(caminho_arquivo).split('.')
                        caminho_arquivo = str(lista_caminho[0]) + '.xls'
                        meu_arquivo = pd.read_html(caminho_arquivo,header=header_read,skiprows=pular_n_linhas) # I specify index 0 because pandas read_html returns a list of dataframes and I'm getting the first
                        for table in meu_arquivo:
                            print(table)
                        meu_arquivo = meu_arquivo[n_tabela_html]
                        meu_arquivo = meu_arquivo.astype('str')
                        if delete_unnamed:
                            meu_arquivo = Referencias.excluir_colunas_tabela(meu_arquivo,['Unnamed'])
                        if len(nome_relatorio) > 0 and len(colocar_na_pasta) > 0:
                            caminho_pasta = Referencias.verificar_ou_criar_pasta(colocar_na_pasta)
                            indice = Referencias.qtde_arquivos_na_pasta(colocar_na_pasta)
                            if len(caminho_opcional) > 0:
                                if 'excel' in str(formato).lower():
                                    if sem_indice == False:
                                        meu_arquivo.to_excel(caminho_opcional + f"\{indice}-{nome_relatorio}.xlsx",
                                                             sheet_name=sheet_name, header=header_write,
                                                             index=index_write)
                                    else:
                                        meu_arquivo.to_excel(caminho_opcional + f"\{nome_relatorio}.xlsx",
                                                             sheet_name=sheet_name, header=header_write,
                                                             index=index_write)
                                elif 'csv' in str(formato).lower():
                                    if sem_indice == False:
                                        meu_arquivo.to_csv(caminho_opcional + f"\{indice}-{nome_relatorio}.csv", sep=';',
                                                           index=False)
                                    else:
                                        meu_arquivo.to_csv(caminho_opcional + f"\{nome_relatorio}.csv", sep=';',
                                                           index=False)
                                else:
                                    pass
                            else:
                                if 'excel' in str(formato).lower():
                                    if sem_indice == False:
                                        meu_arquivo.to_excel(caminho_pasta + f"\{indice}-{nome_relatorio}.xlsx",
                                                             sheet_name=sheet_name,header=header_write,index=index_write)
                                    else:
                                        meu_arquivo.to_excel(caminho_pasta + f"\{nome_relatorio}.xlsx",
                                                             sheet_name=sheet_name, header=header_write, index=index_write)
                                elif 'csv' in str(formato).lower():
                                    if sem_indice == False:
                                        meu_arquivo.to_csv(caminho_pasta + f"\{indice}-{nome_relatorio}.csv", sep=';',
                                                           index=False)
                                    else:
                                        meu_arquivo.to_csv(caminho_pasta + f"\{nome_relatorio}.csv", sep=';',
                                                           index=False)
                                else:
                                    pass
                        #print(meu_arquivo)
                        #print('Deu certo...')

                    except Exception as e:
                        #print('Deu erro em ler html...')
                        print(e)
                        try:
                            print('tentando abrir em formato excel...')
                            lista_caminho = str(caminho_arquivo).split('.')
                            caminho_arquivo = str(lista_caminho[0]) + '.xlsx'
                            try:
                                meu_arquivo = pd.read_excel(caminho_arquivo, header = header_read,sheet_name=sheet_name,engine=engine,dtype=dtype)
                            except Exception as e:
                                print(e)
                                try:
                                    other_way = '.'.join(lista_caminho)
                                    meu_arquivo = pd.read_excel(other_way,header = header_read,sheet_name=sheet_name,engine=engine)
                                except Exception as e:
                                    print(e)
                            if delete_unnamed:
                                meu_arquivo = Referencias.excluir_colunas_tabela(meu_arquivo, ['Unnamed'])
                            if len(nome_relatorio)>0 and len(colocar_na_pasta)>0:
                                caminho_pasta = Referencias.verificar_ou_criar_pasta(colocar_na_pasta)
                                indice = Referencias.qtde_arquivos_na_pasta(colocar_na_pasta)
                                if len(caminho_opcional) > 0:
                                    if 'excel' in str(formato).lower():
                                        if sem_indice == False:
                                            meu_arquivo.to_excel(caminho_opcional + f"\{indice}-{nome_relatorio}.xlsx",
                                                                 sheet_name=sheet_name, header=header_write,
                                                                 index=index_write)
                                        else:
                                            meu_arquivo.to_excel(caminho_opcional + f"\{nome_relatorio}.xlsx",
                                                                 sheet_name=sheet_name, header=header_write,
                                                                 index=index_write)
                                    elif 'csv' in str(formato).lower():
                                        if sem_indice == False:
                                            meu_arquivo.to_csv(caminho_opcional + f"\{indice}-{nome_relatorio}.csv",
                                                               sep=';',
                                                               index=False)
                                        else:
                                            meu_arquivo.to_csv(caminho_opcional + f"\{nome_relatorio}.csv", sep=';',
                                                               index=False)
                                    else:
                                        pass
                                else:
                                    if 'excel' in str(formato).lower():
                                        if sem_indice == False:
                                            meu_arquivo.to_excel(caminho_pasta + f"\{indice}-{nome_relatorio}.xlsx",
                                                                 sheet_name=sheet_name,header=header_write,index=index_write)
                                        else:
                                            meu_arquivo.to_excel(caminho_pasta + f"\{nome_relatorio}.xlsx",
                                                                 sheet_name=sheet_name, header=header_write,
                                                                 index=index_write)
                                    elif 'csv' in str(formato).lower():
                                        if sem_indice == False:
                                            meu_arquivo.to_csv(caminho_pasta + f"\{indice}-{nome_relatorio}.csv", sep=';',
                                                               index=False)
                                        else:
                                            meu_arquivo.to_csv(caminho_pasta + f"\{nome_relatorio}.csv", sep=';',
                                                               index=False)
                                    else:
                                        pass
                            #print(meu_arquivo)
                            #print('Deu certo...')
                        except Exception as e:
                            #print('Deu erro em ler excel...')
                            print(e)
                            pass

                elif '.csv' in str(caminho_arquivo).lower() or '.sswweb' in str(caminho_arquivo).lower():
                    #print('tentando abrir em formato csv ou sswweb...')
                    try:
                        lista_caminho = str(caminho_arquivo).split('.')
                        if '.csv' in str(caminho_arquivo).lower():
                            caminho_arquivo = str(lista_caminho[0]) + '.csv'
                        elif '.sswweb' in str(caminho_arquivo).lower():
                            caminho_arquivo = str(lista_caminho[0]) + '.sswweb'
                        meu_arquivo = pd.read_csv(caminho_arquivo, sep=';',encoding=encoding, skiprows=pular_n_linhas,
                                                  dtype=object,header=header_read, error_bad_lines=False,usecols = usecols, index_col=index_col)
                        if delete_unnamed:
                            meu_arquivo = Referencias.excluir_colunas_tabela(meu_arquivo, ['Unnamed'])
                        if len(nome_relatorio) > 0 and len(colocar_na_pasta) > 0:
                            caminho_pasta = Referencias.verificar_ou_criar_pasta(colocar_na_pasta)
                            indice = Referencias.qtde_arquivos_na_pasta(colocar_na_pasta)
                            if len(caminho_opcional) > 0:
                                if 'excel' in str(formato).lower():
                                    if sem_indice == False:
                                        meu_arquivo.to_excel(caminho_opcional + f"\{indice}-{nome_relatorio}.xlsx",
                                                             sheet_name=sheet_name,
                                                             header=header_write, index=index_write)
                                    else:
                                        meu_arquivo.to_excel(caminho_opcional + f"\{nome_relatorio}.xlsx",
                                                             sheet_name=sheet_name,
                                                             header=header_write, index=index_write)
                                elif 'csv' in str(formato).lower():
                                    if sem_indice == False:
                                        meu_arquivo.to_csv(caminho_opcional + f"\{indice}-{nome_relatorio}.csv", sep=';',
                                                           index=False)
                                    else:
                                        meu_arquivo.to_csv(caminho_opcional + f"\{nome_relatorio}.csv", sep=';',
                                                           index=False)
                                else:
                                    pass
                            else:
                                if 'excel' in str(formato).lower():
                                    if sem_indice == False:
                                        meu_arquivo.to_excel(caminho_pasta + f"\{indice}-{nome_relatorio}.xlsx", sheet_name=sheet_name,
                                                             header=header_write,index=index_write)
                                    else:
                                        meu_arquivo.to_excel(caminho_pasta + f"\{nome_relatorio}.xlsx",
                                                             sheet_name=sheet_name,
                                                             header=header_write, index=index_write)
                                elif 'csv' in str(formato).lower():
                                    if sem_indice == False:
                                        meu_arquivo.to_csv(caminho_pasta + f"\{indice}-{nome_relatorio}.csv", sep=';', index=False)
                                    else:
                                        meu_arquivo.to_csv(caminho_pasta + f"\{nome_relatorio}.csv", sep=';',
                                                           index=False)
                                else:
                                    pass
                        #print(meu_arquivo)
                        #print('Deu certo...')
                    except Exception as e:
                        #print('Deu erro em ler csv ou sswweb...')
                        #print(e)
                        pass
                elif '.json' in str(caminho_arquivo).lower():
                    #print('tentando abrir em formato json...')
                    try:
                        lista_caminho = str(caminho_arquivo).split('.')
                        caminho_arquivo = str(lista_caminho[0]) + '.json'
                        with open(caminho_arquivo, "r") as readit:
                            meu_arquivo = json.load(readit)
                        #print(meu_arquivo)
                    except Exception as e:
                        #print('Deu erro em ler json...')
                        #print(e)
                        pass
                #elif '.txt'
                else:
                    #print('Formato de arquivo invalido...')
                    pass

                time.sleep(0.5)
                contador_erro_import+=1
            #fim while
        else:
            #print('A pasta informada está vazia!')
            pass

        return meu_arquivo

    # função para criar tabelas predefinidas com listas de informação como sendo linhas da tabela
    @staticmethod
    def criar_tabela_lista_como_linhas(lista_listas:list,lista_colunas:list,nome_relatorio:str,
                                       colocar_na_pasta:str,sem_indice:bool=False) -> pd.DataFrame:
        #print('#' * 100)
        #print(
            #'METODO: def criar_tabela_lista_como_linhas(lista_listas:list,lista_colunas:list,nome_relatorio:str,colocar_na_pasta:str):')
        #print('#' * 100)
        df = pd.DataFrame(lista_listas)
        if len(lista_colunas) == len(lista_listas[0]):
            df.columns = lista_colunas
        else:
            #print('Lista de colunas não é do mesmo tamanho que a lista de lista ou não foi informada')
            colunas = list(df.columns)
            for i, coluna in enumerate(colunas):
                colunas[i] = f'Coluna-{i + 1}'
            df.columns = colunas
        df.dropna(how='all',inplace=True)
        #print(df)
        if len(str(nome_relatorio))>0 and len(str(colocar_na_pasta))>0:
            caminho_pasta = Referencias.verificar_ou_criar_pasta(colocar_na_pasta)
            indice = Referencias.qtde_arquivos_na_pasta(colocar_na_pasta)
            if sem_indice:
                df.to_excel(caminho_pasta + f"\{nome_relatorio}.xlsx", sheet_name="Sheet1")
            else:
                df.to_excel(caminho_pasta + f"\{indice}-{nome_relatorio}.xlsx", sheet_name="Sheet1")
            #print('Arquivo excel criado com sucesso!')

        return df

    # função para criar tabelas predefinidas com listas de informação como sendo colunas da tabela
    @staticmethod
    def criar_tabela_lista_como_colunas(lista_listas:list,lista_colunas:list,nome_relatorio:str,colocar_na_pasta:str,substituir:bool=True,sem_indice:bool=False) -> pd.DataFrame:
        #print('#' * 100)
        #print('METODO: def criar_tabela_lista_como_colunas(lista_listas:list,lista_colunas:list,nome_relatorio:str,colocar_na_pasta:str):')
        #print('#' * 100)
        if substituir == False:
            Referencias.verificar_ou_criar_pasta(colocar_na_pasta)
            # FILTRO
            df = Referencias.importar_arquivo(colocar_na_pasta, nome_relatorio, '', '', 0)
            if len(df) <= 0:
                df = pd.DataFrame()
                for lista in lista_listas:
                    df_aux = pd.DataFrame(lista)
                    df = pd.concat([df, df_aux], axis=1, ignore_index=True)
                if len(lista_colunas) == len(lista_listas):
                    df.columns = lista_colunas
                else:
                    #print('Lista de colunas não é do mesmo tamanho que a lista de lista ou não foi informada')
                    colunas = list(df.columns)
                    for i, coluna in enumerate(colunas):
                        colunas[i] = f'Coluna-{i + 1}'
                    df.columns = colunas
                #print(df)
                if len(str(nome_relatorio))>0 and len(str(colocar_na_pasta))>0:
                    caminho_pasta = Referencias.verificar_ou_criar_pasta(colocar_na_pasta)
                    if sem_indice:
                        df.to_excel(caminho_pasta + f"\{nome_relatorio}.xlsx", sheet_name="Sheet1")
                    else:
                        indice = Referencias.qtde_arquivos_na_pasta(colocar_na_pasta)
                        df.to_excel(caminho_pasta + f"\{indice}-{nome_relatorio}.xlsx", sheet_name="Sheet1")
        else:
            df = pd.DataFrame()
            for lista in lista_listas:
                df_aux = pd.DataFrame(lista)
                df = pd.concat([df, df_aux], axis=1, ignore_index=True)
            if len(lista_colunas) == len(lista_listas):
                df.columns = lista_colunas
            else:
                # print('Lista de colunas não é do mesmo tamanho que a lista de lista ou não foi informada')
                colunas = list(df.columns)
                for i, coluna in enumerate(colunas):
                    colunas[i] = f'Coluna-{i + 1}'
                df.columns = colunas
            # print(df)
            if len(str(nome_relatorio)) > 0 and len(str(colocar_na_pasta)) > 0:
                caminho_pasta = Referencias.verificar_ou_criar_pasta(colocar_na_pasta)
                indice = Referencias.qtde_arquivos_na_pasta(colocar_na_pasta)
                if sem_indice:
                    df.to_excel(caminho_pasta + f"\{nome_relatorio}.xlsx", sheet_name="Sheet1")
                else:
                    indice = Referencias.qtde_arquivos_na_pasta(colocar_na_pasta)
                    df.to_excel(caminho_pasta + f"\{indice}-{nome_relatorio}.xlsx", sheet_name="Sheet1")

        return df

    # função soma ou subtrair a quantidade de dias informada e retorna o dia atual e a data resultante da operação
    @staticmethod
    def somar_ou_subtrair_dias_da_data_atual(dias: int, operacao:str ='-',formato_data:str='6'):
        #print('#' * 100)
        #print('METODO: def somar_ou_subtrair_dias_da_data_atual(dias: int, operacao: str = "-"):')
        #print('#' * 100)
        try:
            # configurando o periodo do relatorio
            today = date.today()
            if operacao == '-':
                day_operacao = today - timedelta(dias)
            if operacao == '+':
                day_operacao = today + timedelta(dias)

            #print(today)
            #print(day_operacao)

            day_of_the_week = today.isoweekday()
            #print(day_of_the_week)

            tamanho_day_today = len(str(today.day))
            tamanho_month_today = len(str(today.month))
            tamanho_year_today = len(str(today.year)[2:])

            tamanho_day_operacao = len(str(day_operacao.day))
            tamanho_month_operacao = len(str(day_operacao.month))
            tamanho_year_operacao = len(str(day_operacao.year)[2:])

            dia_atual = str(today.day)
            mes_atual = str(today.month)
            ano_atual = str(today.year)[2:]

            dia_operacao = str(day_operacao.day)
            mes_operacao = str(day_operacao.month)
            ano_operacao = str(day_operacao.year)[2:]

            # verificando se o valor das variaveis esta no padrao reconhecido pelo ssw cada variavel com 2 caracteres

            # hoje
            if tamanho_day_today < 2:
                dia_atual = '0' + str(today.day)

            if tamanho_month_today < 2:
                mes_atual = '0' + str(today.month)

            if tamanho_year_today < 2:
                ano_atual = '0' + str(today.year)[2:]

            # dias anteriores
            if tamanho_day_operacao < 2:
                dia_operacao = '0' + str(day_operacao.day)

            if tamanho_month_operacao < 2:
                mes_operacao = '0' + str(day_operacao.month)

            if tamanho_year_operacao < 2:
                ano_operacao = '0' + str(day_operacao.year)[2:]

            # concatenado as variaveis para informar no sistema
            if formato_data == '6':
                data_abrev_hoje = dia_atual + mes_atual + ano_atual
                data_abrev_operacao = dia_operacao + mes_operacao + ano_operacao
            elif formato_data == '8a':
                data_abrev_hoje = dia_atual + mes_atual + str(today.year)
                data_abrev_operacao = dia_operacao + mes_operacao + str(day_operacao.year)
            elif formato_data == '8b':
                data_abrev_hoje = f'{dia_atual}/{mes_atual}/{str(today.year)[2:]}'
                data_abrev_operacao = f'{dia_operacao}/{mes_operacao}/{str(day_operacao.year)[2:]}'
            else:
                data_abrev_hoje = f'{dia_atual}/{mes_atual}/{str(today.year)}'
                data_abrev_operacao = f'{dia_operacao}/{mes_operacao}/{str(day_operacao.year)}'
            return data_abrev_hoje, data_abrev_operacao
        except Exception as e:
            #print(e)
            return None

    #função para criar filtros de tabelas
    @staticmethod
    def criar_filtros(lista_filtro:list,lista_coluna:list,nome_relatorio_filtro:str,substituir:bool=False, sem_indice:bool= True)->pd.DataFrame:
        #print('#' * 100)
        #print('METODO: def criar_filtros(lista_filtro:list,lista_coluna:list,nome_relatorio_filtro:str)->pd.DataFrame:')
        #print('#' * 100)
        Referencias.verificar_ou_criar_pasta('filtros_config')
        # FILTRO
        filtro = Referencias.importar_arquivo('filtros_config', nome_relatorio_filtro, '', '', 0)
        if len(filtro) <= 0:
            filtro = Referencias.criar_tabela_lista_como_colunas([lista_filtro], lista_coluna,nome_relatorio_filtro, 'filtros_config',sem_indice=sem_indice)
        else:
            if substituir:
                filtro = Referencias.criar_tabela_lista_como_colunas([lista_filtro], lista_coluna,
                                                                     nome_relatorio_filtro, 'filtros_config',sem_indice=sem_indice)
        return filtro
    #função para informar a quantidade de arquivos em uma pasta
    @staticmethod
    def qtde_arquivos_na_pasta(pasta:str) -> int:
        #print('#' * 100)
        #print('METODO: def qtde_arquivos_na_pasta(pasta:str) -> int:')
        #print('#' * 100)
        caminho = Referencias.verificar_ou_criar_pasta(pasta)
        lista_arquivos = os.listdir(caminho)
        return len(lista_arquivos)

    @staticmethod
    def excluir_credenciais(apelido_credenciais: str):
        #print('#' * 100)
        #print('METODO: def excluir_credenciais(apelido_credenciais: str):')
        #print('#' * 100)
        caminho = Referencias.verificar_ou_criar_pasta('PARAMETROS')
        apelido_credenciais = str(apelido_credenciais).upper().strip()
        try:
            lista_arquivos = os.listdir(caminho)
            for arquivo in lista_arquivos:
                if f'Credenciais_{apelido_credenciais}' in arquivo:
                    os.remove(str(caminho) + f'\{str(arquivo)}')
                    #print(f'Credenciais_{apelido_credenciais} excluido com sucesso!')
                else:
                    #print(f'Credenciais_{apelido_credenciais} não encontrada!')
                    pass
        except Exception as e:
            #print('O arquivo não foi encontrado!!!')
            #print(e)
            pass

    # função para gerar relatorios
    @staticmethod
    def gerar_relatorio(tabela:pd.DataFrame,nome_relatorio:str,colocar_na_pasta:str,formato:str='excel',sem_indice:bool=True,
                        caminho_opcional:str='',header_write:bool=True,index_write = True,
                        sheet_name:str = 'Sheet1',encoding:str='utf-8') -> None:
        #print('#' * 100)
        #print('METODO: def gerar_relatorio(tabela:pd.DataFrame,nome_relatorio:str,colocar_na_pasta:str) -> None:')
        #print('#' * 100)
        try:
            caminho = Referencias.verificar_ou_criar_pasta(colocar_na_pasta)
            indice = Referencias.qtde_arquivos_na_pasta(colocar_na_pasta)
            if 'excel' in str(formato).lower():
                if len(caminho_opcional)>0:
                    if sem_indice == False:
                        tabela.to_excel(caminho_opcional + f'\{indice}-{nome_relatorio}.xlsx', sheet_name=sheet_name,
                                        header=header_write,index=index_write,encoding= encoding)
                    else:
                        tabela.to_excel(caminho_opcional + f'\{nome_relatorio}.xlsx', sheet_name=sheet_name,
                                        header=header_write,index=index_write,encoding= encoding)
                else:
                    if sem_indice == False:
                        tabela.to_excel(caminho + f'\{indice}-{nome_relatorio}.xlsx', sheet_name=sheet_name,
                                        header=header_write,index=index_write,encoding= encoding)
                    else:
                        tabela.to_excel(caminho + f'\{nome_relatorio}.xlsx', sheet_name=sheet_name,
                                        header=header_write,index=index_write,encoding= encoding)
                #print(f'Relatorio {nome_relatorio}.xlsx gerado com sucesso na pasta {colocar_na_pasta}')
            elif 'csv' in str(formato).lower():
                if len(caminho_opcional) > 0:
                    if sem_indice == False:
                        tabela.to_csv(caminho_opcional + f"\{indice}-{nome_relatorio}.csv", sep=';',index=index_write,
                                      header=header_write,encoding= encoding)
                    else:
                        tabela.to_csv(caminho_opcional + f"\{nome_relatorio}.csv", sep=';', index=index_write,
                                      header=header_write,encoding= encoding)
                else:
                    if sem_indice == False:
                        tabela.to_csv(caminho + f"\{indice}-{nome_relatorio}.csv", sep=';', index=index_write,
                                      header=header_write,encoding= encoding)
                    else:
                        tabela.to_csv(caminho + f"\{nome_relatorio}.csv", sep=';', index=index_write,
                                      header=header_write,encoding= encoding)
                #print(f'Relatorio {nome_relatorio}.csv gerado com sucesso na pasta {colocar_na_pasta}')
            else:
                pass
        except Exception as e:
            #print(e)
            pass

    # função para remover espaços em branco e converter celulas vazias em NaN
    @staticmethod
    def remover_espaces_coluna_for(tabela, coluna):
        #print('#' * 100)
        #print('METODO: def remover_espaces_coluna(tabela, coluna):')
        #print('#' * 100)
        for i, celula in enumerate(tabela[coluna]):
            celula = str(celula)
            tabela.loc[i, coluna] = celula.replace('  ', '').strip()
            if len(celula) <= 0:
                tabela.loc[i, coluna] = str(float(celula))
        return tabela

    # função para remover espaços em branco e converter celulas vazias em NaN
    @staticmethod
    def remover_espaces_coluna(tabela, coluna):
        # print('#' * 100)
        # print('METODO: def remover_espaces_coluna(tabela, coluna):')
        # print('#' * 100)
        tabela[coluna] = tabela[coluna].astype('str')
        tabela[coluna] = list(map(lambda x: x.replace('  ', '').strip(), tabela[coluna].tolist()))
        try:
            tabela[coluna] = list(map(lambda x: x if(len(x)>0 and str(x).lower() != 'nan') else str(float('nan')), tabela[coluna].tolist()))
        except Exception as e:
            print(e)
        return tabela

    #função para criptografar os dados
    @staticmethod
    def criptografar_dados(dados):
        #print('#' * 100)
        #print('METODO: def criptografar_dados(dados):')
        #print('#' * 100)
        key = 'cuZIxVinHla6n6Z5Fl6MomM8120tgDI2A9kyT2-k9cY='
        cipher_suite = Fernet(key)
        cipher_text = cipher_suite.encrypt(bytes(f'{dados}', 'utf-8'))
        #print(cipher_text)
        dado_text = str(cipher_text.decode('utf-8'))
        #print(dado_text)
        return dado_text

    #função para descriptografar os dados
    @staticmethod
    def descriptografar_dados(dado_text):
        #print('#' * 100)
        #print('METODO: def descriptografar_dados(dado_text):')
        #print('#' * 100)
        key = 'cuZIxVinHla6n6Z5Fl6MomM8120tgDI2A9kyT2-k9cY='
        cipher_suite = Fernet(key)
        plain_text = cipher_suite.decrypt(bytes(f'{dado_text}', 'utf-8'))
        plain_text = str(plain_text.decode('utf-8'))
        return plain_text

    #função para criar um arquivo com as preferencias de inicialização e navegação chromedriver
    #@staticmethod
    def criar_inicializacao_and_headless_chromedriver(self,formato:str,nome_chrome_opcional:str='chrome_driver',lista_resp_direct:list=[],substituir:bool=False):
        #print('#' * 100)
        #print('METODO: def criar_inicializacao_and_headless_chromedriver(formato:str):')
        #print('#' * 100)
        config_chrome_driver = self.ler_credenciais(nome_chrome_opcional)
        if len(config_chrome_driver)<=0:
            print(lista_resp_direct)
            if len(lista_resp_direct)>0:
                self.criar_credenciais(nome_chrome_opcional,
                                              ['chromedriver (1)->online (2)->local',
                                               'visualizar (1)->sim (2)->não'], formato, cript='n',lista_parametros_resp_direct=lista_resp_direct,ask_usuario='n')
                config_chrome_driver = self.ler_credenciais(nome_chrome_opcional)
            else:
                self.criar_credenciais(nome_chrome_opcional,['chromedriver (1)->online (2)->local','visualizar (1)->sim (2)->não'],formato,cript='n')
                config_chrome_driver = self.ler_credenciais(nome_chrome_opcional)
        else:
            if substituir:
                self.delete_file('parametros', nome_chrome_opcional)
                print(lista_resp_direct)
                if len(lista_resp_direct) > 0:
                    self.criar_credenciais(nome_chrome_opcional,
                                                  ['chromedriver (1)->online (2)->local',
                                                   'visualizar (1)->sim (2)->não'], formato, cript='n',
                                                  lista_parametros_resp_direct=lista_resp_direct,ask_usuario='n')
                    config_chrome_driver = self.ler_credenciais(nome_chrome_opcional)
                else:
                    self.criar_credenciais(nome_chrome_opcional,
                                                  ['chromedriver (1)->online (2)->local',
                                                   'visualizar (1)->sim (2)->não'], formato, cript='n')
                    config_chrome_driver = self.ler_credenciais(nome_chrome_opcional)
        if 'JSON' in str(formato).upper():
            try:
                inicializacao = int(str(config_chrome_driver[str('chromedriver (1)->online (2)->local'.upper())]))
            except Exception as e:
                print(e)
                inicializacao = int(
                    str(self.descriptografar_dados(config_chrome_driver[str('chromedriver (1)->online (2)->local'.upper())])))
            try:
                headless = int(
                    str(config_chrome_driver[str('visualizar (1)->sim (2)->não'.upper())]))
            except Exception as e:
                print(e)
                headless = int(
                    str(self.descriptografar_dados(config_chrome_driver[str('visualizar (1)->sim (2)->não'.upper())])))
        elif 'EXCEL' in str(formato).upper():
            inicializacao = int(
                str(self.retornar_valor_credenciais_linha_by_posicao(config_chrome_driver,0)))
            headless = int(
                str(self.retornar_valor_credenciais_linha_by_posicao(config_chrome_driver,1)))
        return inicializacao,headless

    #função para verificar se arquivo já foi baixado na pasta
    @staticmethod
    def esperar_downloads(caminho,timeout:int=3600, force_error:bool=True,extensao_opcional:str='.txt'):
        #print('#' * 100)
        #print('METODO: def esperar_downloads(caminho):')
        #print('#' * 100)
        dl_wait = True
        lista_arquivos = os.listdir(caminho)
        contador_while = 0
        caminho_arquivo = None
        while dl_wait and contador_while <= timeout:
            if force_error:
                if contador_while >=(timeout/2) and len(lista_arquivos)<=0:
                    erro
            for arquivo in lista_arquivos:
                caminho_arquivo = Path(caminho) / arquivo
                #print(caminho_arquivo)
                arquivo = str(caminho_arquivo).lower()
                print(arquivo)
                extensao_arquivo = '.' + str(arquivo).split('.')[-1]
                if len(arquivo) > 0:
                    if '.xls' in extensao_arquivo or '.csv' in extensao_arquivo or '.sswweb' in extensao_arquivo or '.json' in extensao_arquivo or '.pdf' in extensao_arquivo or extensao_opcional in extensao_arquivo:
                        dl_wait = False
            time.sleep(1)
            lista_arquivos = os.listdir(caminho)
            contador_while += 1
        return caminho_arquivo

    @staticmethod
    def definir_periodo_mes_anterior(formato_data:str='6'):
        # encontrando o tamanho das strings
        today = date.today()
        # today_date = date.today()

        mes_now = today.month
        year_now = today.year
        if int(mes_now) == 1:
            mes_last = 12
            year_last = year_now - 1
        else:
            mes_last = mes_now - 1
            year_last = year_now


        first_day_mouth_last = datetime(year_last, mes_last, 1).date()
        first_day_month_now = datetime(year_now, mes_now, 1).date()
        last_day_month_last = first_day_month_now - timedelta(1)

        tamanho_first_day_last = len(str(first_day_mouth_last.day))
        tamanho_last_day_last = len(str(last_day_month_last.day))

        tamanho_month_last = len(str(first_day_mouth_last.month))

        tamanho_year = len(str(first_day_mouth_last.year)[2:])

        # definindo as variaveis
        first_dia = str(first_day_mouth_last.day)
        last_dia = str(last_day_month_last.day)
        mes = str(first_day_mouth_last.month)
        # mes_anterior = str(today.month - 1)
        ano_last = str(first_day_mouth_last.year)[2:]
        ano_atual = str(first_day_month_now.year)[2:]

        # verificando se o valor das variaveis esta no padrao reconhecido pelo ssw cada variavel com 2 caracteres

        if tamanho_first_day_last < 2:
            first_dia = '0' + str(first_day_mouth_last.day)

        if tamanho_last_day_last < 2:
            last_dia = '0' + str(last_day_month_last.day)

        if tamanho_month_last < 2:
            mes = '0' + str(first_day_mouth_last.month)

        if tamanho_year < 2:
            ano_last = '0' + str(first_day_mouth_last.year)[2:]
            ano_atual = '0' + str(first_day_month_now.year)[2:]

        # concatenado as variaveis para informar no sistema
        # data_abrev_first = first_dia + mes + ano_atual
        # data_abrev_last = last_dia + mes + ano_atual

        if formato_data == '6':
            data_abrev_first = first_dia + mes + ano_last
            data_abrev_last = last_dia + mes + ano_last
        elif formato_data == '8a':
            data_abrev_first = first_dia + mes + str(first_day_mouth_last.year)
            data_abrev_last = last_dia + mes + str(first_day_mouth_last.year)
        elif formato_data == '8b':
            data_abrev_first = f'{first_dia}/{mes}/{str(first_day_mouth_last.year)[2:]}'
            data_abrev_last = f'{last_dia}/{mes}/{str(first_day_mouth_last.year)[2:]}'
        else:
            data_abrev_first = f'{first_dia}/{mes}/{str(first_day_mouth_last.year)}'
            data_abrev_last = f'{last_dia}/{mes}/{str(first_day_mouth_last.year)}'
        print(data_abrev_first,data_abrev_last)
        return data_abrev_first,data_abrev_last

    @staticmethod
    def agrupar_valores_por_coluna(nome_relatorio, tabela, agrupar_por, lista_colunas_filtro:list=[]):
        #print('#' * 100)
        #print('METODO: def agrupar_valores_por_coluna(nome_relatorio, tabela, agrupar_por, lista_colunas_filtro):')
        #print('#' * 100)
        relatorio_final = tabela.copy()
        copy_relatorio_final = tabela.copy()
        lista_colunas_numericas = []

        for coluna in copy_relatorio_final.columns:
            for n, cel in enumerate(copy_relatorio_final[coluna]):
                cel = str(cel).replace(' ', '')
                cel = str(cel).replace('.', '')
                cel = str(cel).replace(',', '')  # .strip()
                copy_relatorio_final.loc[n, coluna] = cel
            #print(copy_relatorio_final[coluna])
            lista_cel = copy_relatorio_final[coluna].astype('str').str.isnumeric()

            vdd = False
            lista_true = []
            for item in lista_cel:
                if item == True:
                    lista_true.append(item)
                    #vdd = True
            if len(lista_true) > len(lista_cel)/2:
                lista_colunas_numericas.append(coluna)
                continue

        #print(lista_colunas_numericas)

        for coluna in lista_colunas_numericas:
            relatorio_final[coluna] = relatorio_final[coluna].astype('str')
            for n, cel in enumerate(relatorio_final[coluna]):
                cel = str(cel).replace(' ', '')
                cel = str(cel).replace('.', '')
                cel = str(cel).replace(',', '.')
                try:
                    cel = float(cel)
                except Exception as e:
                    #print(e)
                    cel = 0
                    relatorio_final.loc[n, coluna] = float(
                        cel)  # float(re.split(r'[\"]?([0-9\.]*)[\"]?',cel)[1])#float(cel)
            #print(relatorio_final[coluna])
            relatorio_final[coluna] = relatorio_final[coluna].astype('float')
        #print('Relatorio final antes de agrupar')
        #print(relatorio_final)
        print(relatorio_final.info())
        lista_colunas_nao_numericas=[]
        for coluna in lista_colunas_filtro:
            if not coluna in lista_colunas_numericas:
                lista_colunas_nao_numericas.append(coluna)
        print(lista_colunas_nao_numericas)
        if len(lista_colunas_filtro) > 0:
            relatorio_final_agrupado1 = relatorio_final.groupby(agrupar_por, as_index=False).sum()
            #relatorio_final_agrupado2 = relatorio_final.groupby(agrupar_por, as_index=False)[lista_colunas_nao_numericas].agg(lambda x: '/'.join(list(set(x))))
            result = []
            relatorio_final_agrupado2 = relatorio_final.groupby(agrupar_por, as_index=False)[
                lista_colunas_nao_numericas].agg(lambda x: '/'.join(Referencias.reduce_list_duplicated(list(dict.fromkeys(x)))))

            relatorio_final_agrupado = relatorio_final_agrupado2.merge(relatorio_final_agrupado1, how='inner',on=agrupar_por)
        else:
            relatorio_final_agrupado = relatorio_final.groupby(agrupar_por, as_index=False).sum()
        #print(relatorio_final_agrupado)

        Referencias.gerar_relatorio(relatorio_final_agrupado, nome_relatorio, 'relatorios')

        return relatorio_final_agrupado, lista_colunas_numericas

    @staticmethod
    def reduce_list_duplicated(lista:list):
        lista = [i for i in lista if i]
        print(lista)
        return lista
    @staticmethod
    def float_converter_for(tabela, coluna):
        #print('#' * 100)
        #print('METODO: def float_converter(tabela, coluna):')
        #print('#' * 100)
        tabela[coluna] = tabela[coluna].astype('str')
        tabela[coluna] = tabela[coluna].str.replace(' ', '')
        for n, cel in enumerate(tabela[coluna]):
            cel = str(cel).replace('.', '').strip()
            cel = str(cel).replace(',', '.')
            try:
                cel = float(cel)
            except Exception as e:
                #print(e)
                cel = 0
            tabela.loc[n, coluna] = float(cel)
        #print(tabela[coluna])
        tabela[coluna] = tabela[coluna].astype('float')
        return tabela

    @staticmethod
    def float_converter(tabela, coluna):
        # print('#' * 100)
        # print('METODO: def float_converter(tabela, coluna):')
        # print('#' * 100)
        tabela[coluna] = tabela[coluna].astype('str')
        tabela[coluna] = list(map(lambda x: x.replace(' ', '').replace('.', '').replace(',', '.').strip(), tabela[coluna].tolist()))
        tabela[coluna] = list(map(lambda x: 0 if (len(x) <= 0) else str(float(x)), tabela[coluna].tolist()))
        return tabela

    @staticmethod
    def int_float_converter(tabela, coluna):
        # print('#' * 100)
        # print('METODO: def float_converter(tabela, coluna):')
        # print('#' * 100)
        tabela[coluna] = tabela[coluna].astype('str')
        tabela[coluna] = list(
            map(lambda x: x.replace(' ', '').strip(), tabela[coluna].tolist()))
        print(coluna)
        lista_valores_int = list(
            map(lambda x: 'float' if (',' in str(x) or '.' in str(x)) else 'int', tabela[coluna].tolist()))
        #print(lista_valores_int)
        if not 'float' in lista_valores_int:
            tabela[coluna] = list(map(lambda x: 0 if (len(x) <= 0) else str(int(x)), tabela[coluna].tolist()))
        else:
            tabela[coluna] = list(
                map(lambda x: x.replace(' ', '').replace('.', '').replace(',', '.').replace('#', '0').strip(), tabela[coluna].tolist()))
            tabela[coluna] = list(map(lambda x: 0 if (len(x) <= 0) else str(float(x)), tabela[coluna].tolist()))
        return tabela

    @staticmethod
    def int_float_converter_pandas(tabela, coluna):
        # print('#' * 100)
        # print('METODO: def float_converter(tabela, coluna):')
        # print('#' * 100)
        tabela[coluna] = tabela[coluna].astype('str')
        tabela[coluna] = list(
            map(lambda x: x.replace(' ', '').strip(), tabela[coluna].tolist()))
        print(coluna)
        lista_valores_int = list(
            map(lambda x: 'float' if (',' in str(x) or '.' in str(x)) else 'int', tabela[coluna].tolist()))
        # print(lista_valores_int)
        if not 'float' in lista_valores_int:
            #tabela[coluna] = list(map(lambda x: 0 if (len(x) <= 0) else str(int(x)), tabela[coluna].tolist()))
            tabela[coluna] = tabela[coluna].astype('int64')
        else:
            tabela[coluna] = list(
                map(lambda x: x.replace(' ', '').replace('.', '').replace(',', '.').strip(), tabela[coluna].tolist()))
            tabela[coluna] = tabela[coluna].astype('float')
        return tabela

    @staticmethod
    def identificar_colunas_numericas_for(tabela_original):
        tabela = tabela_original.copy()
        lista_colunas_numericas = []
        for coluna in tabela.columns:
            for n, cel in enumerate(tabela[coluna]):
                cel = str(cel).replace(' ', '')
                cel = str(cel).replace('.', '')
                cel = str(cel).replace(',', '')  # .strip()
                tabela.loc[n, coluna] = cel
            #print(tabela[coluna])
            lista_cel = tabela[coluna].astype('str').str.isnumeric()
            vdd = False
            for item in lista_cel:
                if item == True:
                    vdd = True
            if vdd == True:
                lista_colunas_numericas.append(coluna)
                continue

        #print(lista_colunas_numericas)
        return lista_colunas_numericas

    @staticmethod
    def identificar_colunas_numericas(tabela_original):
        tabela = tabela_original.copy()
        lista_colunas_numericas = []
        for coluna in tabela.columns:
            print(coluna)
            tabela[coluna] = tabela[coluna].astype('str')
            tabela[coluna] = list(map(lambda x: x.replace(' ', '').replace('.', '').replace(',', '').replace('#', '0').strip(), tabela[coluna].tolist()))
            lista_cel = tabela[coluna].astype('str').str.isnumeric()
            #print(lista_cel)
            lista_cel = list(
                map(lambda x: str(x), lista_cel))
            if not 'False' in lista_cel:
                print('Numerica!')
                lista_colunas_numericas.append(coluna)
                continue

        print(lista_colunas_numericas)
        return lista_colunas_numericas

    @staticmethod
    def calcular_dia_semana_e_dias_uteis(tabela,coluna_data):
        tabela = Referencias.remover_espaces_coluna(tabela, coluna_data)
        tabela[coluna_data] = pd.to_datetime(tabela[coluna_data], format='%d/%m/%y')
        for i, data in enumerate(tabela[coluna_data]):
            tabela.loc[i, 'Dia_da_semana'] = data.isoweekday()
            #print(data)
            #print(data.isoweekday())
        #Referencias.gerar_relatorio(tabela, 'tabela_dias_da_semana', 'relatorios')
        tabela_data = tabela.drop_duplicates(subset = coluna_data)
        tabela_data = tabela_data.reset_index(drop=True)
        tabela_data = tabela_data[[coluna_data,'Dia_da_semana']]
        #print(tabela_data)
        tabela_data['qdte'] = 1
        tabela_dias_uteis = tabela_data.groupby('Dia_da_semana', as_index=False)[
            ['qdte']].sum()
        #print(tabela_dias_uteis)
        #Referencias.gerar_relatorio(tabela_dias_uteis,'tabela_dias_uteis','relatorios')
        return tabela,tabela_dias_uteis

    #@staticmethod
    def pause(self):
        if self.gui == None:
            from interface import Interface
            self.gui = Interface()
        return self.gui.info('Deseja continuar?')

    @staticmethod
    def ler_csv(ler_pasta:str='downloads',opcional_arquivo:str=''):
        gui = Referencias.Interface()
        lista = ler_pasta.split('\\')
        caminho = Referencias.verificar_ou_criar_pasta(lista[-1])
        lista_arquivos = os.listdir(caminho)
        caminho_arquivo = None
        lista_my_reader = []
        if len(lista_arquivos) > 0:
            for k, arquivo in enumerate(lista_arquivos):
                #print(arquivo)
                if len(opcional_arquivo) > 0:
                    if opcional_arquivo in str(arquivo):
                        caminho_arquivo = Path(caminho) / arquivo
                        break
                    else:
                        if k == (len(lista_arquivos) - 1):
                            #print(f'Arquivo Opcional {opcional_arquivo} não encontrado na pasta {ler_pasta}')
                            gui.aviso(f'Arquivo Opcional {opcional_arquivo} não encontrado na pasta {ler_pasta}')
                            return None
                else:
                    caminho_arquivo = Path(caminho) / arquivo
            #print(caminho_arquivo)
            try:
                with open(caminho_arquivo, 'r') as file:
                    my_reader = csv.reader(file, delimiter=';')
                    lista_my_reader = list(my_reader)
                    for i, row in enumerate(lista_my_reader):
                        #print(row)
                        pass
            except Exception as e:
                #print('Problema em ler arquivo CSV')
                gui.aviso('Problema em ler arquivo CSV')

        else:
            #print('Nenhum arquivo foi encontrado')
            gui.aviso('Nenhum arquivo foi encontrado')
        return lista_my_reader

    @staticmethod
    def pegar_arquivos_na_pasta(pasta: str,especificar_arquivo:str='',caminho_opcional:str=''):
        #print('#' * 100)
        #print('METODO: def pegar_arquivos_na_pasta(pasta:str) -> int:')
        #print('#' * 100)
        lista = pasta.split('\\')
        caminho = Referencias.verificar_ou_criar_pasta(lista[-1])
        if len(caminho_opcional) > 0:
            caminho = caminho_opcional
        lista_arquivos = os.listdir(caminho)
        if len(especificar_arquivo)>0:
            arquivo_busca = str(especificar_arquivo).lower().strip()
            for arquivo in lista_arquivos:
                arquivo_str = str(arquivo).lower().strip()
                if arquivo_busca in arquivo_str:
                    #print(arquivo)
                    caminho_completo = str(caminho) +'/'+ str(arquivo)
                    #print(caminho_completo)
                    return caminho_completo

        return lista_arquivos

    @staticmethod
    def mover_ou_renomear_arquivos_na_pasta(pasta: str,novo_nome:str='',colocar_na_pasta:str='',
                                            sem_indice:bool=False,caminho_opcional:str='',
                                            extensao_opcional:str='',copy:bool=True,especificar_arquivo:str=''):
        #print('#' * 100)
        #print('METODO: def qtde_arquivos_na_pasta(pasta:str) -> int:')
        #print('#' * 100)
        caminho = Referencias.verificar_ou_criar_pasta(pasta)
        lista_arquivos = os.listdir(caminho)
        linha = 0
        extensao = ''
        for i, arquivo in enumerate(lista_arquivos):
            #print(str(arquivo))
            if novo_nome == '':
                novo_nome = str(arquivo).split('.')[0]
            extensao = str(arquivo).split('.')[1]
            #print(extensao)
            if len(extensao_opcional)>0:
                extensao = extensao_opcional
            if len(especificar_arquivo)>0:
                if especificar_arquivo.lower() in str(arquivo).lower():
                    if len(colocar_na_pasta)>0:
                        caminho_outra_pasta = Referencias.verificar_ou_criar_pasta(colocar_na_pasta)
                        if sem_indice:
                            if copy:
                                shutil.copy2(caminho + f'/{str(arquivo)}', caminho_outra_pasta + f'/{novo_nome}.{extensao}')
                            else:
                                Path(caminho + f'/{str(arquivo)}').rename(caminho_outra_pasta + f'/{novo_nome}.{extensao}')
                        else:
                            if copy:
                                shutil.copy2(caminho + f'/{str(arquivo)}', caminho_outra_pasta + f'/{novo_nome}_{i}.{extensao}')
                            else:
                                Path(caminho + f'/{str(arquivo)}').rename(caminho_outra_pasta + f'/{novo_nome}_{i}.{extensao}')
                    elif len(caminho_opcional)>0:
                        if sem_indice:
                            if copy:
                                shutil.copy2(caminho + f'/{str(arquivo)}', caminho_opcional + f'/{novo_nome}.{extensao}')
                            else:
                                Path(caminho + f'/{str(arquivo)}').rename(caminho_opcional + f'/{novo_nome}.{extensao}')
                        else:
                            if copy:
                                shutil.copy2(caminho + f'/{str(arquivo)}', caminho_opcional + f'/{novo_nome}_{i}.{extensao}')
                            else:
                                Path(caminho + f'/{str(arquivo)}').rename(caminho_opcional + f'/{novo_nome}_{i}.{extensao}')
                    else:
                        if sem_indice:
                            if copy:
                                shutil.copy2(caminho + f'/{str(arquivo)}', caminho_opcional + f'/{novo_nome}.{extensao}')
                            else:
                                Path(caminho + f'/{str(arquivo)}').rename(caminho + f'/{novo_nome}.{extensao}')
                        else:
                            if copy:
                                shutil.copy2(caminho + f'/{str(arquivo)}', caminho_opcional + f'/{novo_nome}_{i}.{extensao}')
                            else:
                                Path(caminho + f'/{str(arquivo)}').rename(caminho + f'/{novo_nome}_{i}.{extensao}')
                    linha = i
                else:
                    print('nenhum arquivo com esse nome encontrado!')
            else:
                if len(colocar_na_pasta) > 0:
                    caminho_outra_pasta = Referencias.verificar_ou_criar_pasta(colocar_na_pasta)
                    if sem_indice:
                        if copy:
                            shutil.copy2(caminho + f'/{str(arquivo)}', caminho_outra_pasta + f'/{novo_nome}.{extensao}')
                        else:
                            Path(caminho + f'/{str(arquivo)}').rename(caminho_outra_pasta + f'/{novo_nome}.{extensao}')
                    else:
                        if copy:
                            shutil.copy2(caminho + f'/{str(arquivo)}',
                                         caminho_outra_pasta + f'/{novo_nome}_{i}.{extensao}')
                        else:
                            Path(caminho + f'/{str(arquivo)}').rename(
                                caminho_outra_pasta + f'/{novo_nome}_{i}.{extensao}')
                elif len(caminho_opcional) > 0:
                    if sem_indice:
                        if copy:
                            shutil.copy2(caminho + f'/{str(arquivo)}', caminho_opcional + f'/{novo_nome}.{extensao}')
                        else:
                            Path(caminho + f'/{str(arquivo)}').rename(caminho_opcional + f'/{novo_nome}.{extensao}')
                    else:
                        if copy:
                            shutil.copy2(caminho + f'/{str(arquivo)}',
                                         caminho_opcional + f'/{novo_nome}_{i}.{extensao}')
                        else:
                            Path(caminho + f'/{str(arquivo)}').rename(caminho_opcional + f'/{novo_nome}_{i}.{extensao}')
                else:
                    if sem_indice:
                        if copy:
                            shutil.copy2(caminho + f'/{str(arquivo)}', caminho_opcional + f'/{novo_nome}.{extensao}')
                        else:
                            Path(caminho + f'/{str(arquivo)}').rename(caminho + f'/{novo_nome}.{extensao}')
                    else:
                        if copy:
                            shutil.copy2(caminho + f'/{str(arquivo)}',
                                         caminho_opcional + f'/{novo_nome}_{i}.{extensao}')
                        else:
                            Path(caminho + f'/{str(arquivo)}').rename(caminho + f'/{novo_nome}_{i}.{extensao}')
                linha = i
        return caminho + f'/{novo_nome}_{linha}.{extensao}'

    @staticmethod
    def converter_txt_to_tabela(ler_pasta:str='downloads',nome_final_relatorio:str='relatorio',colocar_na_pasta:str='relatorios',index_write:bool=False):
        tabela = Referencias.importar_arquivo('downloads', '', '', '',)
        print(tabela)
        quebra_colunas = False
        for linha in tabela.index:
            valor = list(tabela.loc[linha].values)
            #print(valor)
            valor = ' ,'.join(valor)
            if '-+-' in valor and quebra_colunas == False:
                index_quebra_colunas = linha
                quebra_colunas = True

        print(f'index_quebra_colunas {index_quebra_colunas}')
        print(f'valor index_quebra_colunas {tabela.loc[index_quebra_colunas].values}')

        linha_separador = tabela.loc[tabela.index[index_quebra_colunas]]
        print(linha_separador)
        separadores = linha_separador.str.split('+').dropna()
        separadores = list(separadores)
        print(separadores)
        lista_tamanhos = []
        for char in separadores[0]:
            cont = 0
            for s in char:
                cont += 1
            lista_tamanhos.append(cont + 1)
        #print(lista_tamanhos)
        #Referencias.verificar_ou_criar_pasta(nome_final_relatorio)
        Referencias.gerar_relatorio(tabela, nome_final_relatorio, colocar_na_pasta, formato='csv',
                                    index_write=index_write)
        #arquivo = Referencias.mover_ou_renomear_arquivos_na_pasta('downloads', nome_final_relatorio,copy=True)
        caminho = Referencias.verificar_ou_criar_pasta('relatorios')
        arquivo = Referencias.pegar_arquivos_na_pasta('relatorios')[0]
        caminho_arquivo = f'{caminho}\{arquivo}'
        tabela = pd.read_fwf(caminho_arquivo, widths=lista_tamanhos)
        #print(tabela)

        return tabela

    @staticmethod
    def dia_da_semana(data:str=''):
        if len(data)>0:
            dta = datetime. strptime(data, '%d/%m/%Y')
            #print(dta)
            day_of_the_week = dta.isoweekday()
            #print(day_of_the_week)
        else:
            today = date.today()
            #print(today)
            day_of_the_week = today.isoweekday()
            #print(day_of_the_week)
        return  day_of_the_week

    @staticmethod
    def definir_mes_fechado(mes:int=0,ano:int=0,formato:int=6):
        if mes == 0 and ano == 0:
            if int(date.today().month) > 1:
                mes = (date.today().month - 1)
                ano = date.today().year
            else:
                mes = 12
                ano = (date.today().year - 1)
        elif ano == 0:
            ano = date.today().year
        elif mes == 0:
            mes = (date.today().month - 1)
        mes = str(mes)
        ano = str(ano)
        if len(mes) < 2:
            mes = '0' + str(mes)
        if len(ano) < 3:
            primeiro_do_mes = datetime.strptime(f'01/{mes}/{ano}', '%d/%m/%y')
            mes_prox = str(int(mes) + 1)
            if mes_prox == '13':
                mes_prox = '01'
                ano = str(int(ano) + 1)
                if len(ano) < 2:
                    ano = '0' + str(ano)
            if len(mes_prox) < 2:
                mes_prox = '0' + str(mes_prox)
            primeiro_do_prox_mes = datetime.strptime(f'01/{mes_prox}/{ano}', '%d/%m/%y')
        elif len(ano) == 4:
            primeiro_do_mes = datetime.strptime(f'01/{mes}/{ano}', '%d/%m/%Y')
            mes_prox = str(int(mes) + 1)
            if mes_prox == '13':
                mes_prox = '01'
                ano = str(int(ano) + 1)
                if len(ano) < 2:
                    ano = '0' + str(ano)
            if len(mes_prox) < 2:
                mes_prox = '0' + str(mes_prox)
            primeiro_do_prox_mes = datetime.strptime(f'01/{mes_prox}/{ano}', '%d/%m/%Y')
        else:
            #print('Ano invalido!')
            return
        ult_do_mes = primeiro_do_prox_mes - timedelta(1)
        #print(f'primeiro_do_mes {primeiro_do_mes}')
        #print(f'ult_do_mes {ult_do_mes}')
        list_primeiro_do_mes = str(primeiro_do_mes).split('-')
        list_ult_do_mes = str(ult_do_mes).split('-')
        if formato == 6:
            primeiro_do_mes = f'{str(list_primeiro_do_mes[2])[:2]}{str(list_primeiro_do_mes[1])}{str(list_primeiro_do_mes[0])[2:]}'
            ult_do_mes = f'{str(list_ult_do_mes[2])[:2]}{str(list_ult_do_mes[1])}{str(list_ult_do_mes[0])[2:]}'
        elif formato == 8:
            primeiro_do_mes = f'{str(list_primeiro_do_mes[2])[:2]}{str(list_primeiro_do_mes[1])}{str(list_primeiro_do_mes[0])}'
            ult_do_mes = f'{str(list_ult_do_mes[2])[:2]}{str(list_ult_do_mes[1])}{str(list_ult_do_mes[0])}'
        elif formato == 10:
            primeiro_do_mes = f'{str(list_primeiro_do_mes[2])[:2]}/{str(list_primeiro_do_mes[1])}/{str(list_primeiro_do_mes[0])}'
            ult_do_mes = f'{str(list_ult_do_mes[2])[:2]}/{str(list_ult_do_mes[1])}/{str(list_ult_do_mes[0])}'
        else:
            #print('Formato Invalido!')
            pass

        #print(f'primeiro_do_mes {primeiro_do_mes}')
        #print(f'ult_do_mes {ult_do_mes}')
        return primeiro_do_mes, ult_do_mes

    @staticmethod
    def delete_file(pasta:str='relatorios',file:str='relatorio',caminho_opcional:str=''):
        try:
            if len(caminho_opcional)>0:
                caminho_completo = Referencias.pegar_arquivos_na_pasta('', file,caminho_opcional=caminho_opcional)
            else:
                caminho_completo = Referencias.pegar_arquivos_na_pasta(pasta, file)
            if os.path.isfile(caminho_completo):
                os.remove(caminho_completo)
                #print("File has been deleted")
            else:
                #print("File does not exist")
                pass
        except Exception as e:
            if "O arquivo já está sendo usado por outro processo" in str(e):
                raise Exception(str(e))
            #print('Arquivo provavelmente não existe!')
            #print(e)


    @staticmethod
    def verificar_valores_numericos(celula):
        try:
            celula =str(celula).replace(' ','').replace(':','').replace('-','').replace('(','').replace(')','')
            celula = str(celula).replace('+', '').replace('_', '').replace('*', '').replace('/', '').replace(';', '')
            try:
                valor = float(celula)
                #print(valor)
                if str(valor) == 'nan':
                    return False
                return True
            except Exception as e:
                #print(e)
                #print('valor não é numerico')
                return False
        except Exception as e:
            #print(e)
            pass

    # função para ler e gravar ultima posição do loop em um arquivo excel
    @staticmethod
    def verificar_e_incrementar_memoria_excel(tamanho_referencia):
        try:
            memoria = Referencias.importar_arquivo('memoria', 'memoria', '', '')
            #print(memoria)
            pos = int(memoria['Coluna-2'][0])
            if pos >= tamanho_referencia:
                Referencias.criar_tabela_lista_como_linhas([['memoria', 0]], [], 'memoria', 'memoria', True)
                pos = 0
            else:
                pos+=1
                Referencias.criar_tabela_lista_como_linhas([['memoria', pos]], [], 'memoria', 'memoria',True)
        except Exception as e:
            #print(e)
            Referencias.criar_tabela_lista_como_linhas([['memoria', 0]], [], 'memoria', 'memoria',True)
            pos = 0
        return pos

    #função para ler e gravar ultima posição do loop em um arquivo json
    @staticmethod
    def verificar_e_incrementar_memoria_json(tamanho_referencia):
        try:
            memoria = Referencias.importar_arquivo('memoria', 'memoria', '', '')
            print(memoria)
            pos = int(str(memoria['posicao']).strip())
            if pos >= tamanho_referencia:
                Referencias.criar_arquivo_json(['posicao'],[0],'memoria','memoria')
                pos = 0
            else:
                pos += 1
                Referencias.criar_arquivo_json(['posicao'],[pos],'memoria','memoria')
        except Exception as e:
            # print(e)
            Referencias.criar_arquivo_json(['posicao'],[0],'memoria','memoria')
            pos = 0
        return pos

    # função para ler e gravar ultima posição do loop em banco de dados local sqlite



    @staticmethod
    def log_erro(pos, erro, tabela: pd.DataFrame = pd.DataFrame()):
        log_erros = Referencias.importar_arquivo('relatorios', 'log_erros', '', '', sem_indice=True)
        #print(log_erros)
        if len(tabela)>0 and len(log_erros) == 0:
            log_erros = tabela.copy()
        log_erros.loc[pos, 'Erro'] = erro
        Referencias.gerar_relatorio(log_erros, 'log_erros', 'relatorios', sem_indice=True)

    @staticmethod
    def backup():
        filtro = Referencias.criar_filtros([0],['filtro_backup'],'filtro_habilitar_backup')
        habilitar=int(str(filtro['filtro_backup'][0]).strip())
        if habilitar == 1:
            caminho = os.path.abspath(os.getcwd())
            lista_arquivos = os.listdir(caminho)
            print(lista_arquivos)
            Referencias.verificar_ou_criar_pasta('backup')
            caminho_backup = os.path.abspath(os.getcwd()) + f'/backup'
            lista_arquivos_backups = os.listdir(caminho_backup)
            print(lista_arquivos_backups)
            caminho_outra_pasta = Referencias.verificar_ou_criar_pasta(f'backup/backup_{len(lista_arquivos_backups)}')
            print(caminho_outra_pasta)
            for i, arquivo in enumerate(lista_arquivos):
                print(caminho + f'/{str(arquivo)}')
                print(caminho_outra_pasta + f'/{str(arquivo)}')
                if not 'BACKUP' in str(arquivo) and not 'venv' in str(arquivo)  and not '.' in str(arquivo) and not 'lib' in str(arquivo).lower():
                    shutil.copytree(caminho + f'/{str(arquivo)}', caminho_outra_pasta + f'/{str(arquivo)}')
                if not 'BACKUP' in str(arquivo) and '.' in str(arquivo) and not '.exe' in str(arquivo) and not 'lib' in str(arquivo).lower():
                    shutil.copy2(caminho + f'/{str(arquivo)}', caminho_outra_pasta + f'/{str(arquivo)}')
        else:
            pass

    @staticmethod
    def nome_mes(numero_mes:int=datetime.today().month):
        if numero_mes == 1:
            return 'JANEIRO'
        elif numero_mes == 2:
            return 'FEVEREIRO'
        elif numero_mes == 3:
            return 'MARÇO'
        elif numero_mes == 4:
            return 'ABRIL'
        elif numero_mes == 5:
            return 'MAIO'
        elif numero_mes == 6:
            return 'JUNHO'
        elif numero_mes == 7:
            return 'JULHO'
        elif numero_mes == 8:
            return 'AGOSTO'
        elif numero_mes == 9:
            return 'SETEMBRO'
        elif numero_mes == 10:
            return 'OUTUBRO'
        elif numero_mes == 11:
            return 'NOVEMBRO'
        elif numero_mes == 12:
            return 'DEZEMBRO'
        else:
            print('Numero de mes invalido!')
            return None

    @staticmethod
    def split_pdf(path, name_of_split,pag:str=''):
        pdf = PdfFileReader(path)
        for page in range(pdf.getNumPages()):
            if pag != '':
                if int(page) <= int(pag):
                    pdf_writer = PdfFileWriter()
                    pdf_writer.addPage(pdf.getPage(page))

                    output = f'{name_of_split}{page}.pdf'
                    with open(output, 'wb') as output_pdf:
                        pdf_writer.write(output_pdf)
                else:
                    break
            else:
                pdf_writer = PdfFileWriter()
                pdf_writer.addPage(pdf.getPage(page))

                output = f'{name_of_split}{page}.pdf'
                with open(output, 'wb') as output_pdf:
                    pdf_writer.write(output_pdf)

    @staticmethod
    def dividir_tabela(pasta_arquivo,qtde):
        caminho = Referencias.verificar_ou_criar_pasta(pasta_arquivo)
        arquivo = Referencias.pegar_arquivos_na_pasta(pasta_arquivo)
        nome_arquivo = str(arquivo[0].split('.')[0])
        tabela = Referencias.importar_arquivo(caminho, '', '', '')
        tamanho = len(tabela)
        partes = int(tamanho / qtde)
        for i in range(qtde):
            cut_ini = i * partes
            cut_fim = (i + 1) * partes-1
            if i == qtde - 1:
                tabela_aux = tabela.loc[cut_ini:]
            else:
                tabela_aux = tabela.loc[cut_ini:cut_fim]
            print(tabela_aux)
            Referencias.gerar_relatorio(tabela_aux, f'{nome_arquivo}_parte_{i+1}', pasta_arquivo,sem_indice=True)

    @staticmethod
    def gerar_logging(pos,tabela,nome_coluna_log:str='STATUS',log:str='',nome_relatorio:str='',pasta:str='relatorios'):
        if pos > 0:
            try:
                tabela_old = Referencias.importar_arquivo(pasta,nome_relatorio,'','')
                print(tabela_old)
                primeiro_elemento_old = str(tabela_old.iloc[0,0])
                primeiro_elemento = str(tabela.iloc[0, 0])
                ultimo_elemento_old = str(tabela_old.iloc[len(tabela_old)-1, 0])
                ultimo_elemento = str(tabela.iloc[len(tabela)-1, 0])
                print(primeiro_elemento,primeiro_elemento_old,ultimo_elemento,ultimo_elemento_old)
                if len(tabela_old)>0 and len(tabela_old) == len(tabela)  and primeiro_elemento==primeiro_elemento_old and ultimo_elemento==ultimo_elemento_old:
                    tabela_old[nome_coluna_log] = tabela_old[nome_coluna_log].astype('str')
                    tabela_filtrada = tabela_old[tabela_old[nome_coluna_log]!='nan']
                    tabela_filtrada.reset_index(drop=True,inplace=True)
                    print('tabela filtrada')
                    print(tabela_filtrada)
                    #Referencias.pause()
                    if len(tabela_filtrada)>0:
                        tabela = tabela_old
            except Exception as e:
                print(e)
        tabela.loc[pos,nome_coluna_log] = log
        Referencias.gerar_relatorio(tabela,nome_relatorio,pasta,sem_indice=True)

    @staticmethod
    async def download_pdf(caminho,nome_pdf,url):
        browser = await launch({'headless': 'true'})
        page = await browser.newPage()
        await page.goto(url, {
            "waitUntil": 'networkidle2',
        })
        await page.screenshot({'path': f'{caminho}/{nome_pdf}'})
        await page.pdf(
            {"path": f'{caminho}/{nome_pdf}',
             "format": 'a4', 'printBackground': 'true'})
        await page.pdf(
            {"path": f'{caminho}/{nome_pdf}',
             "format": 'a4', 'printBackground': 'true'})
        await browser.close()

    @staticmethod
    def verificar_gerar_registro(nome_flag,operacao,*args):
        Referencias.verificar_ou_criar_pasta('flag')
        dta = datetime.today()
        dta = dta.strftime("%d/%m/%Y, %H:%M:%S")
        print(dta)
        ultimo_reg = Referencias.importar_arquivo('flag',f'{nome_flag}')
        if len(ultimo_reg)<=0:
            tabela = Referencias.criar_tabela_lista_como_colunas([[f'{nome_flag}:'],[str(dta)]],['evento','data'],f'{nome_flag}','flag',sem_indice=True)
            print(tabela)
        else:
            last_dta = str(ultimo_reg.loc[0,'data'])
            print(last_dta)
            last_dta = datetime.strptime(last_dta,"%d/%m/%Y, %H:%M:%S")
            dta = datetime.strptime(dta,"%d/%m/%Y, %H:%M:%S")
            print(last_dta)
            print(dta)
            if operacao == '==':
                if 'ano' in args:
                    last_ano = last_dta.year
                    now_ano = dta.year
                    print(last_ano,now_ano)
                    if last_ano == now_ano:
                        return True
                    else:
                        return False
                elif 'mes' in args:
                    last_mes = last_dta.month
                    now_mes = dta.month
                    print(last_mes, now_mes)
                    if last_mes == now_mes:
                        return True
                    else:
                        return False
                elif 'dia' in args:
                    last_dia = last_dta.day
                    now_dia = dta.day
                    print(last_dia, now_dia)
                    if last_dia == now_dia:
                        return True
                    else:
                        return False
                elif 'hora' in args:
                    last_hora = last_dta.hour
                    now_hora = dta.hour
                    print(last_hora, now_hora)
                    if last_hora == now_hora:
                        return True
                    else:
                        return False
                elif 'minuto' in args:
                    last_minuto = last_dta.minute
                    now_minuto = dta.minute
                    print(last_minuto, now_minuto)
                    if last_minuto == now_minuto:
                        return True
                    else:
                        return False
                elif 'segundo' in args:
                    last_segundo = last_dta.second
                    now_segundo = dta.second
                    print(last_segundo, now_segundo)
                    if last_segundo == now_segundo:
                        return True
                    else:
                        return False
                elif 'data_only' in args:
                    last_data = last_dta.date()
                    now_data = dta.date()
                    print(last_data, now_data)
                    if last_data == now_data:
                        return True
                    else:
                        return False
                else:
                    print(last_dta, dta)
                    if last_dta == dta:
                        return True
                    else:
                        return False
            elif operacao == '-':
                if 'ano' in args:
                    last_ano = last_dta.year
                    now_ano = dta.year
                    print(last_ano,now_ano)
                    dif = now_ano-last_ano
                    dif = str(dif).replace(':','').replace('-','')
                    print(int(dif))
                    return int(dif)

                elif 'mes' in args:
                    last_mes = last_dta.month
                    now_mes = dta.month
                    print(last_mes, now_mes)
                    dif = now_mes - last_mes
                    dif = str(dif).replace(':', '').replace('-', '')
                    print(int(dif))
                    return int(dif)

                elif 'dia' in args:
                    last_dia = last_dta.day
                    now_dia = dta.day
                    print(last_dia, now_dia)
                    dif = now_dia - last_dia
                    dif = str(dif).replace(':', '').replace('-', '')
                    print(int(dif))
                    return int(dif)

                elif 'hora' in args:
                    last_hora = last_dta.hour
                    now_hora = dta.hour
                    print(last_hora, now_hora)
                    dif = now_hora - last_hora
                    dif = str(dif).replace(':', '').replace('-', '')
                    print(int(dif))
                    return int(dif)

                elif 'minuto' in args:
                    last_minuto = last_dta.minute
                    now_minuto = dta.minute
                    print(last_minuto, now_minuto)
                    dif = now_minuto - last_minuto
                    dif = str(dif).replace(':', '').replace('-', '')
                    print(int(dif))
                    return int(dif)

                elif 'segundo' in args:
                    last_segundo = last_dta.second
                    now_segundo = dta.second
                    print(last_segundo, now_segundo)
                    dif = now_segundo - last_segundo
                    dif = str(dif).replace(':', '').replace('-', '')
                    print(int(dif))
                    return int(dif)

                elif 'data_only' in args:
                    last_data = last_dta.date()
                    now_data = dta.date()
                    print(last_data, now_data)
                    dif = now_data - last_data
                    dif = str(dif).replace(':', '').replace('-', '')
                    print(int(dif))
                    return int(dif)

                else:
                    print(last_dta, dta)
                    dif = dta - last_dta
                    print(int(dif.seconds))
                    return int(dif.seconds)

    @staticmethod
    def criar_arquivo_json(lista_parametros,lista_resp_parametros,nome_arquivo_json,colocar_na_pasta:str='parametros',substituir:bool=False):
        arquivo = {}
        caminho = Referencias.verificar_ou_criar_pasta(colocar_na_pasta)
        arquivo = Referencias.importar_arquivo(colocar_na_pasta,nome_arquivo_json,'','')
        #print(arquivo)
        #Referencias.pause()
        if len(arquivo) <=0 or substituir == True:
            arquivo = {}
            for l, parametro in enumerate(lista_parametros):
                arquivo[parametro] = lista_resp_parametros[l]
            out_file = open(caminho + f"\{nome_arquivo_json}.json", "w")

            json.dump(arquivo, out_file, indent=6)

            out_file.close()

        return arquivo

    @staticmethod
    def remover_nan_tabela(tabela, coluna):
        #print(tabela[coluna].tolist())
        tabela[coluna] = list(map(lambda x: '' if(x=='nan') else x, tabela[coluna].tolist()))
        tabela[coluna] = list(map(lambda x: '' if (x == 'NaN') else x, tabela[coluna].tolist()))
        #print(tabela[coluna])
        #print(tabela[coluna].tolist())
        return tabela

    @staticmethod
    def remover_null_tabela(tabela, coluna):
        # print(tabela[coluna].tolist())
        tabela[coluna] = list(map(lambda x: '' if (x == 'null') else x, tabela[coluna].tolist()))
        tabela[coluna] = list(map(lambda x: '' if (x == 'NULL') else x, tabela[coluna].tolist()))
        # print(tabela[coluna])
        # print(tabela[coluna].tolist())
        return tabela

    @staticmethod
    def limpar_tabela(tabela):
        tabela = tabela.astype('str')
        for coluna in tabela.columns:
            tabela = Referencias.remover_nan_tabela(tabela, coluna)
            tabela[coluna] = list(map(lambda x: x.replace('  ','').strip(), tabela[coluna].tolist()))
            tabela[coluna] = list(map(lambda x: '' if (x == 'NaT') else x, tabela[coluna].tolist()))
        return tabela

    @staticmethod
    def limpar_tabela_all_blank(tabela):
        tabela = tabela.astype('str')
        for coluna in tabela.columns:
            tabela = Referencias.remover_nan_tabela(tabela, coluna)
            tabela = Referencias.remover_null_tabela(tabela, coluna)
            tabela[coluna] = list(map(lambda x: x.replace('  ', '').strip(), tabela[coluna].tolist()))
            tabela[coluna] = list(map(lambda x: '' if (x == 'NaT') else x, tabela[coluna].tolist()))

        return tabela

    @staticmethod
    def converter_colunas_tabela(tabela, ignorar_tipo:list=[]):
        for coluna in tabela.columns:
            coluna = str(coluna)
            lista_coluna_data = []
            if not 'data' in ignorar_tipo or not 'dia' in ignorar_tipo:
                if 'data' in coluna.lower() or 'dia' in coluna.lower():
                    for valor in tabela[coluna]:
                        if str(valor) != 'nan' and len(str(valor))>0:
                            primeiro = str(valor)
                    if '-' in primeiro:
                        tabela[coluna] = list(map(lambda x: str(x)[:10],tabela[coluna].tolist()))
                    # tabela = ip.cd.remover_espaces_coluna(tabela,coluna)
                    tabela[coluna] = tabela[coluna].astype('str')
                    tabela[coluna] = tabela[coluna].str.replace(' ', '')
                    tabela = Referencias.remover_nan_tabela(tabela, coluna)
                    # ip.cd.pause()

                    try:
                        # date_util_func = (lambda _: dateutil.parser.parse(_))
                        # tabela[coluna] = tabela[coluna].apply(date_util_func)
                        tabela[coluna] = tabela[coluna].apply(
                            (lambda _: datetime.strptime(_, "%d/%m/%y") if (_ != '') else 'NULL'))
                        # tabela[coluna] = tabela[coluna].apply((lambda _: datetime.strftime(_, "%d/%m/%y") if (_ != '') else ''))
                        tabela[coluna] = list(map(lambda x: str(x)[:10] if (x!= 'NULL') else 'NULL', tabela[coluna].tolist()))
                        print(tabela[coluna])
                    except Exception as e:
                        print(e)
                        try:
                            tabela[coluna] = pd.to_datetime(tabela[coluna], format='%d/%m/%y')
                            tabela[coluna] = list(map(lambda x: str(x)[:10], tabela[coluna].tolist()))
                        except Exception as e:
                            print(e)
                            try:
                                tabela[coluna] = tabela[coluna].astype('datetime64[ns]')
                                tabela[coluna] = list(map(lambda x: str(x)[:10] if (len(str(x))>=10) else 'NULL', tabela[coluna].tolist()))
                                # tabela[coluna] = tabela[coluna].apply(
                                #     (lambda _: datetime.strptime(_, "%d/%m/%y") if (_ != '') else 'NULL'))
                                #tabela[coluna] = pd.to_datetime(tabela[coluna], format='%d/%m/%y')
                            except Exception as e:
                                print(e)
                    tabela[coluna] = tabela[coluna].astype('str')
                    tabela[coluna] = list(
                        map(lambda x: x if (len(x) > 0) else 'NULL', tabela[coluna].tolist()))
            if not 'hora' in ignorar_tipo:
                if 'hora' in coluna.lower():
                    try:
                        tabela[coluna] = pd.to_datetime(tabela[coluna], format='%H:%M:%S').dt.time
                    except Exception as e:
                        print(e)
                        tabela[coluna] = tabela[coluna].astype('datetime64[ns]')
                        tabela[coluna] = pd.to_datetime(tabela[coluna], format='%H:%M:%S').dt.time
        # tabela = ip.cd.limpar_tabela(tabela)
        if not 'numerico' in ignorar_tipo:
            lista_colunas_numericas = Referencias.identificar_colunas_numericas(tabela)

            df_col_num = pd.DataFrame()
            df_col_num['col'] = lista_colunas_numericas
            Referencias.gerar_relatorio(df_col_num, 'lista_col_numericas', 'relatorios_debug', 'csv')
            # ip.cd.pause()
            for coluna_n in lista_colunas_numericas:
                tabela = Referencias.int_float_converter(tabela, coluna_n)
        return tabela

    @staticmethod
    def round_to_up(numerador,denominador):
        try:
            div = numerador/denominador
            print(div)
            int_div = int(div)
            print(int_div)
            rest = div - int_div
            print(rest)
            if rest>=0.5:
                div = int_div +1
            else:
                div = int_div

        except Exception as e:
            print(e)
            div = 0

        print(div)
        return div

    @staticmethod
    def converter_excel_to_csv(caminho_to_file, novo_nome_arquivo):
        arquivo = Referencias.pegar_arquivos_na_pasta(caminho_to_file)
        print(arquivo)
        arquivo = arquivo[0]
        caminho_completo = f'{caminho_to_file}/{arquivo}'
        print(caminho_completo)
        # # open given workbook
        # # and store in excel object
        # excel = openpyxl.load_workbook(caminho_completo)
        #
        # # select the active sheet
        # sheet = excel.active
        with open(caminho_completo, 'rb') as file:
            for line in file.readlines():
                print(line)
        # writer object is created
        with open(f"{caminho_to_file}/{novo_nome_arquivo}.csv",'w',encoding = "ISO-8859-1") as file2:
            col = csv.writer(file2,delimiter=';')
            # writing the data in csv file
            for r in file.readlines():
                # row by row write
                # operation is perform
                col.writerow([item for cell in r])

        # read the csv file and
        # convert into dataframe object
        df = pd.DataFrame(pd.read_csv(f"{caminho_to_file}/{novo_nome_arquivo}.csv"))
        return df

    @staticmethod
    def executar_rotina_para_periodo_meses_fechados(ano,function):
        for mes in range(1,13):
            data_ini,data_fim = Referencias.definir_mes_fechado(mes,ano)
            function(data_ini,data_fim)

    @staticmethod
    def try_except(fuction):
        try:
            function()
            return True
        except Exception as e:
            print(e)
            return str(e)

    def menu_config(self,time_out:int=30):
        global out
        out = time_out
        def contador():
            contador_time_out = 0
            while contador_time_out<out:
                contador_time_out+=1
                print(contador_time_out)
                time.sleep(1)
            try:
                self.gui.on_closing()
            except Exception as e:
                print(e)


        #while True:
        self.gui.create_menu_buttons(0, [], [])
        self.gui.select_frame_by_name('config')
        t1 = threading.Thread(target=contador)
        t1.start()
        self.gui.loop()

    def threading_functions(self,functions:list=[]):
        threads=['' for func in functions]
        for i, func in enumerate(functions):
            try:
                threads[i] = threading.Thread(target=func)
                threads[i].start()
                threads[i].join()
            except Exception as e:
                print(e)
                if 'main thread is not in main loop' in str(e):
                    threads[i] = threading.Thread(target=func)
                    threads[i].run()

    def varrer_pastas(self,pasta: str = '', file_name: str = ''):
        try:
            global caminho
            global arquivos
            global sair
            global desired_file
            global caminho_final

            if len(pasta) > 0:
                caminho += f'\\{pasta}'
                print(caminho)
            if len(arquivos) == 0:
                arquivos.append('')
            arquivos[len(arquivos) - 1] = os.listdir(caminho)
            print(len(arquivos), len(arquivos[len(arquivos) - 1]))
            for arquivo in arquivos[len(arquivos) - 1]:
                executaveis = [file for file in arquivos[len(arquivos) - 1] if '.exe' in str(file)]
                if len(executaveis) > 0:
                    print(executaveis)
                    desired_file = [file for file in executaveis if file_name in str(file)][0]
                    if desired_file:
                        print(desired_file)
                        caminho_final = caminho
                        sair = True
                        return desired_file, caminho_final
                else:
                    print(arquivo)
                    arquivos.append('')
                    try:
                        varrer_pastas(arquivo)
                    except Exception as e:
                        pass
                    try:
                        if sair:
                            return desired_file, caminho_final
                    except Exception as e:
                        pass
                    caminho = '\\'.join(os.path.abspath(caminho).split('\\')[:-1])
                    arquivos = arquivos[:-1]
        except Exception as e:
            print(caminho)
            print(len(arquivos), len(arquivos[len(arquivos) - 1]))

    def definir_periodo_acumulado_whole(self, formato,periodo_until:str='yesterday',dias_definir_mes_anterior:list=[1]):
        _, data_ini = self.somar_ou_subtrair_dias_da_data_atual((datetime.today().day - 1), formato_data=formato)
        if periodo_until == 'yesterday':
            _, data_fim = self.somar_ou_subtrair_dias_da_data_atual(1, formato_data=formato)
        else:
            _, data_fim = self.somar_ou_subtrair_dias_da_data_atual(0, formato_data=formato)
        if datetime.today().day in dias_definir_mes_anterior:
            data_ini, data_fim = self.definir_periodo_mes_anterior(formato)
        return data_ini, data_fim




