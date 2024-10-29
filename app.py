import pandas as pd

# Condicional para criar as planilhas
create = False

# Função para aplicar regras de formatação específicas a cada linha do DataFrame
def formatar_linha(row):
    # REGRAS:
    
    # CONTA CONTÁBIL A DÉBITO (*)


    # # Exemplo de regra: adicionar 'X' na última coluna se 'Flag' for verdadeiro
    # if row['Flag']:
    #     flag_column = 'X'
    # else:
    #     flag_column = ''

    # # Exemplo de regra: ajustar o valor formatado dependendo do valor na coluna 'Conta'
    # if row['Conta'] == 2260:
    #     descricao = "DESPESAS BANCARIAS"
    # elif row['Conta'] == 2253:
    #     descricao = "TARIFA"
    # else:
    #     descricao = row['Descricao']  # Usa o valor original se não atender a uma regra específica

    # # Exemplo de regra: formatar valor com sinal negativo se coluna 'Tipo_Registro' for um valor específico
    # if row['Tipo_Registro'] == 6100:
    #     valor_formatado = f"-{row['Valor']:.2f}"  # Coloca o valor como negativo
    # else:
    #     valor_formatado = f"{row['Valor']:.2f}"

    # # Construção da linha do TXT
    # linha_txt = (
    #     f"|{row['Tipo_Registro']}|"
    #     f"{str(row['CNPJ']).zfill(14)}|"
    #     f"{str(row['Conta']).zfill(4)}|"
    #     f"{row['Data']}|"
    #     f"{valor_formatado}|"
    #     f"{descricao}|"
    #     f"{flag_column}|||"
    # )

    # Exemplo de formatação
    linha_txt = (
        f"|6100|"
        f"{row['DATMOV']}|"
        f"{row['CNPJ']}|"
        f"{row['Data']:02}/{row['Mes']:02}/{row['Ano']}|"  # Exemplo para data
        f"{row['Valor']:.2f}|"
        f"{row['Descricao']}|"
        f"{'X' if row['Flag'] else ''}|||"
    )
    return linha_txt












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


# Realizar um merge para identificar registros em df que não estão em df_devolucoes_validas
df_filtrado = df.merge(df_devolucoes_validas, how='left', indicator=True)
# Manter apenas os registros que não estão no df_devolucoes_validas
df_filtrado = df_filtrado[df_filtrado['_merge'] == 'left_only'].drop(columns='_merge')
df_filtrado.reset_index(drop=True, inplace=True)


desconto_devolucao = df[df['DESC_MERC_DEV'].apply(lambda x: float(x) != 0.0)] #Filtrando linhas com VlrDesconto
df_filtrado.loc[df_filtrado['DESC_MERC_DEV'] != 0.0, 'DESC_MERC_DEV'] = 0.0 #Zerando valores filtrados com Desconto



# Separando a tabela de PAGTO e RECEBTO
df_pagto = df_filtrado[df_filtrado['SAIDA'].apply(lambda x: float(x) != 0.0 )] 
df_recebto = df_filtrado[df_filtrado['ENTRADA'].apply(lambda x: float(x) != 0.0 )]



if (create):
    df_devolucoes_validas.to_excel('LANCTO.EXCLUIDOS_EM_DEVOLUÇÃO_08.xlsx', index=False) #Criando tabela com as linhas filtradas
    desconto_devolucao.to_excel('LINHAS_COM_DESC.POR_DEVOLUÇÃO_08.xlsx', index=False) #Criando tabela com as linhas filtradas
    df_filtrado.to_excel('Movimentação_Mercantis_08.xlsx', index=False)
    df_pagto.to_excel('Movimentação_Mercantis_PAGTO_08.xlsx', index=False)
    df_recebto.to_excel('Movimentação_Mercantis_RECEBTO_08.xlsx', index=False)



'''
# Filtrando valores nulos de pagamento
df_pagto_nulos = df_filtrado[df_filtrado['SAIDA'].isnull()]
# Filtrando valores nulos de recebimento
df_recebto_nulos = df_filtrado[df_filtrado['ENTRADA'].isnull()]
'''


# print(df_pagto[['DATMOV', 'SAIDA', 'ENTRADA', 'NRO_NFE', 'HISTORICO']])
# print(df_recebto[['DATMOV', 'SAIDA', 'ENTRADA', 'NRO_NFE', 'HISTORICO']])

print("DataFrame Filtrado")
print(df_filtrado)
print('--------------------------------------------------------------------------------------------------')
print("DataFrame Desconto por Devolução")
print(desconto_devolucao)
print('--------------------------------------------------------------------------------------------------')
print("DataFrame Devoluções Válidas")
print(df_devolucoes_validas[['DATMOV', 'RAZAO_SOCIAL', 'SAIDA', 'ENTRADA', 'CPF_CNPJ']])
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





# Criar lista de linhas formatadas para o TXT
linhas_txt = [formatar_linha(row) for _, row in df_pagto.iterrows()]

# Adicionar cabeçalhos ou rodapés, se necessário
cabecalho = "|0000|00085822000112|"
codigo = "|6000|V||||"

# Juntar todas as linhas em uma estrutura de TXT
conteudo_txt = "\n".join([cabecalho] + [codigo] + linhas_txt)

# Salvar o conteúdo em um arquivo TXT
with open('saida_formatada.txt', 'w') as arquivo_txt:
    arquivo_txt.write(conteudo_txt)

