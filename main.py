from flask import Flask, make_response, jsonify
import pandas as pd
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
import re

app = Flask(__name__)

# Lista com Colunas e URL usada no WebScraping
colunas = ['Dia', 'Mês', 'Ano', 'Hora', 'Cidade', 'Ocorrência', 'Descrição', 'Local', 'Qntd_Viaturas',
           'Qntd_Militares']
cbm_url = ['https://cbm.al.gov.br/paginas/ocorrencias/true']


#df = pd.DataFrame(nova_linha, index=[0])

@app.route('/leitura')
def get_read():

    # Criação do DataFrame Pandas que  recebe a base de dados do arquivo CSV.
    dataframe_cbmal = pd.read_csv("dataframe_cbmal.csv", sep=",", encoding='UTF-8', index_col=0)

    # Acessar site do CBMAL e copiar parte específica da página HTML.
    pagina = []
    uClient = uReq(cbm_url[0])
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    pagina = [page.text for page in page_soup.find_all("div", {"class": "panel panel-default"})]

    # Tratamento dos dados Parte 1: Excluir Duplicações e Informações não desejadas.
    k = 0
    while k < len(pagina):
        x = re.split("\n", pagina[k])
        new_list = [item for item in x if item]

        unwanted = [4, 5, 6]
        for ele in sorted(unwanted, reverse=True):
            del new_list[ele]

        i = 0
        while i < len(new_list):
            if "\xa0" in new_list[i]:
                new_list[i] = new_list[i][1:]
            i = i + 1

        y = new_list[0].split("-")
        del new_list[0]
        y.extend(new_list)
        z = y[0].split("/")

        i = 0
        while i < len(z):
            z[i] = int(z[i])
            i = i + 1

        del y[0]
        z.extend(y)
        z[8] = z[8][:1]
        z[9] = z[9][:1]

        z[8] = int(z[8])
        z[9] = int(z[9])

        nova_linha = dict(zip(colunas, z))  # Transformando as listas em um dicionário
        dataframe_cbmal.loc[len(dataframe_cbmal)] = nova_linha

        k = k + 1

    # Tratamento dos dados Parte 2: excluir duplicações e atualizar a base de dados.
    sem_duplicados = dataframe_cbmal.drop_duplicates()
    sem_duplicados = sem_duplicados.reset_index()
    sem_duplicados = sem_duplicados.drop(columns='index')
    sem_duplicados.to_csv("dataframe_cbmal.csv")

    texto = f'Tamnho atual do arquivo CSV: {len(sem_duplicados)}'

    return texto

app.run()