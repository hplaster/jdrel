import pandas as pd

# Condicional para criar as planilhas
create = False

# Ler a planilha
df = pd.read_excel('../MovimentaçãoMercantis_ORIGINAL.xlsx')


# Converter a coluna de data para o tipo datetime
df['DATMOV'] = pd.to_datetime(df['DATMOV'])
# Formatando a data para o formato brasileiro (DD/MM/AAAA)
df['DATMOV'] = df['DATMOV'].dt.strftime('%d/%m/%Y')


df['CNPJ_ES'] = df['CNPJ_ES'].astype(str)
df['CPF_CNPJ'] = df['CPF_CNPJ'].apply(lambda x: str(x) if pd.notnull(x) else x)
# df = df.applymap(lambda x: str(x) if pd.notnull(x) else x) # Método para aplicar função no DataFrame inteiro (apllymap)


# Removendo colunas pelo nome
df.drop(columns=['VALOR_PRINCIPAL', 'VALOR_REC_PAGO'], inplace=True)
'''
# Removendo colunas DINAMICAMENTE pelo nome
dropColumns = ['VALOR_PRINCIPAL', 'VALOR_REC_PAGO']
for column in df.columns:
    if column in dropColumns:
        df.drop(columns=[column], inplace=True)
'''

print("DataFrame Completo")
print(df)
print('--------------------------------------------------------------------------------------------------')


desconto_devolucao = df[df['DESC_MERC_DEV'].apply(lambda x: float(x) != 0.0)] #Filtrando linhas
df_filtrado = df[df['DESC_MERC_DEV'].apply(lambda x: float(x) == 0.0)] #Excluindo linhas filtradas
if (create):
    desconto_devolucao.to_excel('LINHAS_COM_DESC.POR_DEVOLUÇÃO_08.xlsx', index=False) #Criando tabela com as linhas filtradas

#DS_CC ou DS_BANCO
excluido_devolucao = df[df['DS_CC'].apply(lambda x: 'DEVOLUÇ' in x)] #Filtrando linhas
df_filtrado = df[df['DS_CC'].apply(lambda x: not('DEVOLUÇ' in x))] #Excluindo linhas filtradas
if (create):
    excluido_devolucao.to_excel('LANCTO.EXCLUIDOS_EM_DEVOLUÇÃO_08.xlsx', index=False) #Criando tabela com as linhas filtradas


df_pagto = df[df['SAIDA'].apply(lambda x: float(x) != 0.0 )] # Separando a tabela de PAGTO e RECEBTO
df_recebto = df[df['ENTRADA'].apply(lambda x: float(x) != 0.0 )] # Separando a tabela de PAGTO e RECEBTO


# print(df_pagto[['DATMOV', 'SAIDA', 'ENTRADA', 'NRO_NFE', 'HISTORICO']])
# print(df_recebto[['DATMOV', 'SAIDA', 'ENTRADA', 'NRO_NFE', 'HISTORICO']])
print("DataFrame Filtrado")
print(df_filtrado)
print('--------------------------------------------------------------------------------------------------')
print("DataFrame Desconto por Devolução")
print(desconto_devolucao)
print('--------------------------------------------------------------------------------------------------')
print("DataFrame Excluidos por Devolução")
print(excluido_devolucao)
print('--------------------------------------------------------------------------------------------------')
print("DataFrame Pagamentos")
print(df_pagto)
print('--------------------------------------------------------------------------------------------------')
print("DataFrame Recebimentos")
print(df_recebto)
print('--------------------------------------------------------------------------------------------------')


#df.to_excel('Movimentação_Mercantis_08.xlsx', index=False)


# Removendo todos os espaços em branco de uma coluna
#df['Date'] = df['Date'].str.replace('\s+', '|', regex=True)

#Quebrando a coluna 'Date' onde tiver '|' e pegando apenas o último valor, e criando a coluna 'ano' para armazenar este registro
#df['ano'] = df['Date'].str.split('|').apply(lambda x: x[-1])

"""
# Salvando como CSV com personalizações
df.to_csv('teste.txt',
          sep='|',  # Delimitador: ponto e vírgula
          decimal=',',  # Separador decimal para números
          encoding='utf-8',  # Codificação
          index=False,  # Não incluir índice
          header=False)  # Incluir cabeçalho
"""