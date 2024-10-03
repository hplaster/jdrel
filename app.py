import pandas as pd

#Ler a planilha
df = pd.read_excel('planilha.xlsx')

# Removendo todos os espaços em branco de uma coluna
df['Date'] = df['Date'].str.replace('\s+', '|', regex=True)

#Formatar os dados
#df = df[['Date', 'Open', 'Close']]  # Selecionar apenas essas colunas

print(df)

#Salvar como TXT com "|" como separador
#df.to_csv('dados.txt', sep='|', index=False, )
