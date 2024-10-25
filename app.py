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



print("DataFrame Original")
print(df)
print('--------------------------------------------------------------------------------------------------')


# Criando tabela de comparação para COLORIR registro com devolução mas não inclusos em "df_devolucoes_validas"
# Filtrar apenas as linhas onde há devoluções (baseado no nome da coluna *DS_CC* ou DS_BANCO)
df_devolucoes = df[df['DS_CC'].str.contains("DEVOLUÇ", na=False)]


# Criar um DataFrame vazio para armazenar as linhas de devolução válidas
df_devolucoes_validas = pd.DataFrame()

# Agrupar o DataFrame por CPF_CNPJ e DATMOV para identificar valores totais de entrada e saída
for _, group in df_devolucoes.groupby(['DATMOV', 'CPF_CNPJ']):
    # Dividir o grupo em registros de entrada e saída
    total_entrada = group['ENTRADA'].sum()
    total_saida = group['SAIDA'].sum()
    
    # Verificar se o total de entrada bate com o total de saída
    if total_entrada == total_saida:
        # Adicionar todas as linhas do grupo ao DataFrame de devoluções válidas
        df_devolucoes_validas = pd.concat([df_devolucoes_validas, group])
df_devolucoes_validas.reset_index(drop=True, inplace=True)

print(df_devolucoes_validas[['DATMOV', 'RAZAO_SOCIAL', 'SAIDA', 'ENTRADA', 'CPF_CNPJ']])
print('--------------------------------------------------------------------------------------------------')

# Realizar um merge para identificar registros em df que não estão em df_devolucoes_validas
df_filtrado = df.merge(df_devolucoes_validas, how='left', indicator=True)
# Manter apenas os registros que não estão no df_devolucoes_validas
df_filtrado = df_filtrado[df_filtrado['_merge'] == 'left_only'].drop(columns='_merge')
df_filtrado.reset_index(drop=True, inplace=True)


desconto_devolucao = df[df['DESC_MERC_DEV'].apply(lambda x: float(x) != 0.0)] #Filtrando linhas com VlrDesconto
df_filtrado.loc[df_filtrado['DESC_MERC_DEV'] != 0.0, 'DESC_MERC_DEV'] = 0.0 #Zerando valores filtrados com Desconto
if (create):
    df_devolucoes_validas.to_excel('LANCTO.EXCLUIDOS_EM_DEVOLUÇÃO_08.xlsx', index=False) #Criando tabela com as linhas filtradas
    desconto_devolucao.to_excel('LINHAS_COM_DESC.POR_DEVOLUÇÃO_08.xlsx', index=False) #Criando tabela com as linhas filtradas
    df_filtrado.to_excel('Movimentação_Mercantis_08.xlsx', index=False)



df_pagto = df_filtrado[df_filtrado['SAIDA'].apply(lambda x: float(x) != 0.0 )] # Separando a tabela de PAGTO e RECEBTO
df_recebto = df_filtrado[df_filtrado['ENTRADA'].apply(lambda x: float(x) != 0.0 )] # Separando a tabela de PAGTO e RECEBTO



# print(df_pagto[['DATMOV', 'SAIDA', 'ENTRADA', 'NRO_NFE', 'HISTORICO']])
# print(df_recebto[['DATMOV', 'SAIDA', 'ENTRADA', 'NRO_NFE', 'HISTORICO']])

print("DataFrame Filtrado")
print(df_filtrado)
print('--------------------------------------------------------------------------------------------------')
print("DataFrame Desconto por Devolução")
print(desconto_devolucao)
print('--------------------------------------------------------------------------------------------------')
print("DataFrame Excluidos por Devolução")
print(df_devolucoes)
print('--------------------------------------------------------------------------------------------------')
print("DataFrame Pagamentos")
print(df_pagto)
print('--------------------------------------------------------------------------------------------------')
print("DataFrame Recebimentos")
print(df_recebto)
print('--------------------------------------------------------------------------------------------------')




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