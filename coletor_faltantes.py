from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
import os
import re

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def coletar_tabelas(table):
    
    rows = []
    headers = [th.text.strip() for th in table.findAll('th')]
    entity = [td.text.strip() for td in table.findAll('td')]
    rows.append(entity)
    df = pd.DataFrame(rows, columns=headers)
    return df

# Configuração do navegador
options = Options()
options.headless = False  # Configurar como True se quiser rodar sem interface gráfica
navegador = webdriver.Chrome(options=options)

all_df = []
base_url = "https://cipm.fcsh.unl.pt"
base_url2 = "https://cipm.fcsh.unl.pt/corpus/"

diretorio = "textos_faltantes"
os.makedirs(diretorio, exist_ok=True)
cont = 0

try:   
    navegador.get("https://cipm.fcsh.unl.pt/corpus/")
    time.sleep(0.1)  # Espera para carregar a página

   
    inputUsuario = navegador.find_element(By.NAME, "username")
    inputUsuario.send_keys("joaovitor")

    inputSenha = navegador.find_element(By.NAME, "password")
    inputSenha.send_keys("1499ab")
    time.sleep(0.1)

    # Localizar o botão de login e clicar nele
    botao_entrar = navegador.find_element(By.XPATH, "//input[@value='Entrar']")
    botao_entrar.click()
    time.sleep(1)
    # Esperar alguns segundos para o servidor processar o login e carregar a página seguinte

    # Capturar e exibir o HTML da página após o login para confirmar sucesso
    soup_principal = BeautifulSoup(navegador.page_source, "html.parser")
    # print(soup)
    for table_principal in soup_principal.findAll('table', attrs={'cellspacing':'20'}):
        for table2_principal in table_principal.findAll('table'):
            for a_sessao in table2_principal.findAll('a', href= True, attrs={'id':['n_1131','n_1213','n_1216','n_1180','n_1215','n_1186','n_1143','n_1144']}):
                link_sessao = base_url + a_sessao['href']
                cont_name = 1
                navegador.get(link_sessao)
                time.sleep(1)

                soup_sessao = BeautifulSoup(navegador.page_source,  "html.parser")
                for a_pag_texto in soup_sessao.find_all("a", href=lambda href:"texto.jsp?" in href):
                    link_pag_texto = base_url2 + a_pag_texto['href']
                   
                    #indo para pagina de texto........................................................................
                    navegador.get(link_pag_texto)
                    time.sleep(1)
                    

                    #marcando checkbox................................................................................
                    if cont % 10 == 0: 
                        print('passou')
                        for name in ["breakfolio", "visiblefolio","hidecomments","highlighting","diacritics"]:
                            checkbox = WebDriverWait(navegador, 10).until(EC.element_to_be_clickable((By.NAME, name)))
                            navegador.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                            if not checkbox.is_selected():
                                 checkbox.click()
                            time.sleep(0.1)
                        cont += 1

                    soup_pag_texto = BeautifulSoup(navegador.page_source, "html.parser")
                    
                    # coletando tabela inicial................................................................................
                    table = soup_pag_texto.find("table", {"class": "cdoc"})
                    df = coletar_tabelas(table)
                    all_df.append(df)
                
                    #gerando nome do arquivo..................................................................................
                    nome_doc = f"{df['Texto'][0]} - {df['Documento'][0]}.txt" 
                    nome_doc = re.sub(r'[\\/:"*?<>|]+', " - ", nome_doc) 

                    if os.path.exists(os.path.join(diretorio, nome_doc)):
                        cont_name += 1
                        df['Documento'][0] = df['Documento'][0]+'_'+str(cont_name)
                        nome_doc = f"{df['Texto'][0]} - {df['Documento'][0]}.txt"
                    caminho = os.path.join(diretorio, nome_doc)            
                    texto = ""

                    #coletando texto.........................................................................................   
                    for div_texto in soup_pag_texto.findAll('div', attrs={'class': 'ctext'}):
                        # Substituir cada <br> por uma quebra de linha (\n)
                        for br in div_texto.find_all('br'):
                            br.replace_with("\n")

                        for nobr in div_texto.find_all('nobr'):
                            nobr.replace_with(nobr.text)

                        for span in div_texto.find_all('span'):
                            span.replace_with(span.text)

                        for table_cref in div_texto.findAll("table", attrs={'class': 'cref'}):
                            info_texto = coletar_tabelas(table_cref)
                            table_cref.decompose()

                        texto += div_texto.text
                        
                    
                    with open(caminho, "w", encoding="utf-8") as arquivo:
                        arquivo.write(texto)
                        print(f"{caminho} salvo com sucesso")   
except Exception as e:
    print(f"Erro durante o login: {e}")

finally:
    # Fechar o navegador
    combined_df = pd.concat(all_df, ignore_index=True).fillna(pd.NA)
    print(combined_df)
    combined_df.to_csv("textos_faltantes.csv", index=False, encoding="utf-8")
    navegador.quit()

