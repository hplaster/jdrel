import pandas as pd

"""
from openpyxl import load_workbook

# Carregar a planilha
workbook = load_workbook('planilha.xlsx')
worksheet = workbook.active  # Selecionando a primeira planilha

# Criar o arquivo TXT
with open('teste.txt', 'w') as f:
    for row in worksheet.iter_rows(values_only=True):
        line = '|'.join(str(cell) for cell in row)  # Unindo as células com tabulação
        f.write(line + '||\n')
"""


#Ler a planilha
df = pd.read_excel('planilha.xlsx')

# Removendo todos os espaços em branco de uma coluna
df['Date'] = df['Date'].str.replace('\s+', '|', regex=True)

#Quebrando a coluna 'Date' onde tiver '|' e pegando apenas o último valor, e criando a coluna 'ano' para armazenar este registro
df['ano'] = df['Date'].str.split('|').apply(lambda x: x[-1])

#Filtrando LINHAS à partir da coluna 'ano'
df = df[df['ano'].apply(lambda x: int(x)) > 2020]

#Filtrando COLUNAS
#df = df[['Date', 'Open', 'Close']]  # Selecionar apenas essas colunas

print(df)

"""
# Salvando como CSV com personalizações
df.to_csv('teste.txt',
          sep='|',  # Delimitador: ponto e vírgula
          #decimal=',',  # Separador decimal para números
          encoding='utf-8',  # Codificação
          index=False,  # Não incluir índice
          header=False)  # Incluir cabeçalho
"""