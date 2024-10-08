import pandas as pd
#from openpyxl import load_workbook
"""
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

"""
df_2021 = df['Date'].str.split('|')[2] == 2021
df['ano'] = df['Date'].str.split('|')
df['ano'] = df['ano'][2]
"""

df['ano'] = df['Date'].str.split('|').apply(lambda x: x[-1])
print(df)

#print(df)
#Formatar os dados
#df = df[['Date', 'Open', 'Close']]  # Selecionar apenas essas colunas

"""
# Salvando como CSV com personalizações
df.to_csv('teste.txt',
          sep='|',  # Delimitador: ponto e vírgula
          #decimal=',',  # Separador decimal para números
          encoding='utf-8',  # Codificação
          index=False,  # Não incluir índice
          header=False)  # Incluir cabeçalho
"""
