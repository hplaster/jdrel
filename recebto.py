import pandas as pd
import json
import re

# Condicional para criar as planilhas
create = False

# Função para carregar o conteúdo de um arquivo JSON
def carregar_json(nome_arquivo):
    with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
        return json.load(arquivo)

# Função para limpar o CNPJ e garantir que tenha 14 dígitos com zeros à esquerda
def limpar_cnpj(cnpj):
    cnpj = int(cnpj)
    cnpj_limpo = re.sub(r'\D', '', str(cnpj))  # Remove qualquer caractere que não seja dígito
    return cnpj_limpo.zfill(14)  # Garante que o CNPJ tenha 14 dígitos, preenchendo com zeros à esquerda se necessário


# Função para aplicar regras de formatação específicas a cada linha do DataFrame
def formatar_linha_recebto(row):
    codigo = "|6000|V||||" #Prefixo
    linhas_txt = [codigo] # Iniciando a lista apenas com o código de sinalização

    ### REGRAS:

    # Certifique-se de que o valor em HISTORICO e RAZAO_SOCIAL não seja None
    historico = str(row['HISTORICO']) if row['HISTORICO'] else ""
    razao_social = str(row['RAZAO_SOCIAL']) if row['RAZAO_SOCIAL'] else ""
    
    # 1º Registro - Vlr - Entrada (Liquido)(D)

    # Carregar JSONs de configuração
    de_paraDS_banco = carregar_json('./recebto_CONTA_CONTÁBIL_A_DÉBITO/de_para_bancos-ds_banco_modificado.json')
    de_paraDS_cc = carregar_json('./recebto_CONTA_CONTÁBIL_A_DÉBITO/de_para_bancos-ds_cc.json')
    conta_debito = ''

    # DE/PARA - DS_BANCO
    for registro in de_paraDS_banco:
        if registro['modo_comparacao'] == 'Contém':
            if registro['conteudo_comparacao'].upper().replace(' ', '') in str(row['DS_BANCO']).upper().replace(' ', ''):
                conta_debito = registro['conta']
                break # Parar ao encontrar o primeiro match
        if registro['modo_comparacao'] == 'Igual':
            if registro['conteudo_comparacao'].upper().replace(' ', '') == str(row['DS_BANCO']).upper().replace(' ', ''):
                conta_debito = registro['conta']
                break # Parar ao encontrar o primeiro match
    # DE/PARA - DS_CC
    for registro in de_paraDS_cc:
        if registro['conteudo_comparacao'].upper() in str(row['DS_CC']).upper():
            conta_debito = registro['conta']
            break # Parar ao encontrar o primeiro match
    
    # Formata o valor com duas casas decimais e substitui '.' por ','
    entrada_formatada = f"{row['ENTRADA']:.2f}".replace('.', ',')

    descricao_historico = f"VR.REC.NF.{f'{re.sub(r'\s{2,}', ' ', str(row['NRO_NFE'])).strip()}' if str(row['NRO_NFE']).upper() != 'NAN' else ''}{f' {re.sub(r'\s{2,}', ' ', str(razao_social)).strip()}' if razao_social.upper() != 'NAN' else ''}{f' {re.sub(r'\s{2,}', ' ', str(historico)).strip()}' if historico.upper() != 'NAN' else ''}"

    primeira_linha = (
        f"|6100|"
        f"{row['DATMOV']}|"
        f"{conta_debito}|"
        f"|"
        f"{entrada_formatada}|"
        f"|"
        f"{descricao_historico}|"
        f"|||"
    )
    linhas_txt.append(primeira_linha)


    # 2º Registro - Vlr - Base (Valor Original)(C)
    de_paraHistorico = carregar_json('./recebto_CONTA_CONTÁBIL_A_CRÉDITO/de_para-historico.json')
    de_paraRazaoSocial = carregar_json('./recebto_CONTA_CONTÁBIL_A_CRÉDITO/de_para-razaosocial.json')

    sinal = ''
    conta_credito = ''

    # Adiciona 'X' na última coluna se o registro for um cliente
    try:
        if int(row['CPF_CNPJ']) > 99999999999 and int(row['NRO_NFE']) >= 1:
            conta_credito = limpar_cnpj(row['CPF_CNPJ'])
            sinal = 'X'
    except (ValueError, TypeError):
        pass  # Ignora erros caso CPF_CNPJ ou NRO_NFE não sejam numéricos
    
    if (conta_credito == ''):
        # DE/PARA - RAZÃO SOCIAL
        for registro in de_paraRazaoSocial:
            if registro['modo_comparacao'] == 'Contém':
                if registro['conteudo_comparacao'].upper() in razao_social.upper():
                    conta_credito = registro['conta']
                    break # Parar ao encontrar o primeiro match
            if registro['modo_comparacao'] == 'Igual':
                if registro['conteudo_comparacao'].upper() == razao_social.upper():
                    conta_credito = registro['conta']
                    break # Parar ao encontrar o primeiro match

    if (conta_credito == ''):
        # DE/PARA - HISTÓRICO
        for registro in de_paraHistorico:
            if registro['modo_comparacao'] == 'Contém':
                if registro['conteudo_comparacao'].upper() in historico.upper():
                    conta_credito = registro['conta']
                    break  # Parar ao encontrar o primeiro match
            if registro['modo_comparacao'] == 'Igual':
                if registro['conteudo_comparacao'].upper() == historico.upper():
                    conta_credito = registro['conta']
                    break  # Parar ao encontrar o primeiro match

    if row['VALOR_BASE'] == 0 or row['VALOR_BASE'] == 0.0:
        valor_base = row['ENTRADA']
        # valor_base = f"{valor_base:.2f}".replace('.', ',')
    else:
        #Valor Base# + #MERC_DEV# + #PERDAS# + #RET_PIS# + #ACERTO# + #RET_COFINS# + #RET_CSLL# + #RET_IR# + #DESC_N#
        valor_base = row['VALOR_BASE'] + row['DESC_MERC_DEV'] + row['DESC_PERDAS'] + row['DESC_RET_PIS'] + row['DESC_ACERTO'] + row['DESC_RET_COFINS'] + row['DESC_RET_CSLL'] + row['DESC_RET_IR'] + row['DESC_N']
        # valor_base = f"{valor_base:.2f}".replace('.', ',')

    segunda_linha = (
        f"|6100|"
        f"{row['DATMOV']}|"
        f"|"
        f"{conta_credito}|"
        f"{f'{valor_base:.2f}'.replace('.', ',')}|"
        f"|"
        f"{descricao_historico}|"
        f"{sinal}|||"
    )
    linhas_txt.append(segunda_linha)


    # 3º Registro - Vlr - Juros (C)
    if row['VALOR_JUROS'] != 0 or row['VALOR_JUROS'] != 0.0: # TRABALHAR ENCIMA DESSA LÓGICA
        conta_credito = 433
        descricao_historico = f"VR.REC.JUROS NF.{f'{re.sub(r'\s{2,}', ' ', str(row['NRO_NFE'])).strip()}' if str(row['NRO_NFE']).upper() != 'NAN' else ''}{f' {re.sub(r'\s{2,}', ' ', str(razao_social)).strip()}' if razao_social.upper() != 'NAN' else ''}{f' {re.sub(r'\s{2,}', ' ', str(historico)).strip()}' if historico.upper() != 'NAN' else ''}"

        if (row['VALOR_JUROS'] + row['VALOR_MULTA']) != 0:
            valor_juros = row['VALOR_JUROS'] + row['VALOR_MULTA']
        
            linhaJuros = (
                f"|6100|"
                f"{row['DATMOV']}|"
                f"|"
                f"{conta_credito}|"
                f"{f'{valor_juros:.2f}'.replace('.', ',')}|"
                f"|"
                f"{descricao_historico}|"
                f"|||"
            )

            linhas_txt.append(linhaJuros)


    # 4º Registro - Desc_N (D)
    if (row['DESC_N'] != 0 and row['DESC_N'] != 0.0) or row['DESC_N'] > 0.1: # TRABALHAR ENCIMA DESSA LÓGICA
        conta_debito = 371
        descricao_historico = f"VR.REC.DESC.NF.{f'{re.sub(r'\s{2,}', ' ', str(row['NRO_NFE'])).strip()}' if str(row['NRO_NFE']).upper() != 'NAN' else ''}{f' {re.sub(r'\s{2,}', ' ', str(razao_social)).strip()}' if razao_social.upper() != 'NAN' else ''}{f' {re.sub(r'\s{2,}', ' ', str(historico)).strip()}' if historico.upper() != 'NAN' else ''}"

        valor_Desc_N = row['DESC_N']
    
        linhaDescN = (
            f"|6100|"
            f"{row['DATMOV']}|"
            f"{conta_debito}|"
            f"|"
            f"{f'{valor_Desc_N:.2f}'.replace('.', ',')}|"
            f"|"
            f"{descricao_historico}|"
            f"|||"
        )

        linhas_txt.append(linhaDescN)


    # 5º Registro - DESC_ACERT (D)
    if row['DESC_ACERTO'] != 0 and row['DESC_ACERTO'] != 0.0: # TRABALHAR ENCIMA DESSA LÓGICA
        conta_debito = 371
        descricao_historico = f"VR.REC.DESC.NF.{f'{re.sub(r'\s{2,}', ' ', str(row['NRO_NFE'])).strip()}' if str(row['NRO_NFE']).upper() != 'NAN' else ''}{f' {re.sub(r'\s{2,}', ' ', str(razao_social)).strip()}' if razao_social.upper() != 'NAN' else ''}{f' {re.sub(r'\s{2,}', ' ', str(historico)).strip()}' if historico.upper() != 'NAN' else ''}"

        valor_Desc_Acerto = row['DESC_ACERTO']
    
        linhaDescAcerto = (
            f"|6100|"
            f"{row['DATMOV']}|"
            f"{conta_debito}|"
            f"|"
            f"{f'{valor_Desc_Acerto:.2f}'.replace('.', ',')}|"
            f"|"
            f"{descricao_historico}|"
            f"|||"
        )

        linhas_txt.append(linhaDescAcerto)


    # 6º Registro - DESC_PERDAS (D)
    if row['DESC_PERDAS'] != 0 and row['DESC_PERDAS'] != 0.0: # TRABALHAR ENCIMA DESSA LÓGICA
        conta_debito = 371
        descricao_historico = f"VR.REC.DESC NF.{f'{re.sub(r'\s{2,}', ' ', str(row['NRO_NFE'])).strip()}' if str(row['NRO_NFE']).upper() != 'NAN' else ''}{f' {re.sub(r'\s{2,}', ' ', str(razao_social)).strip()}' if razao_social.upper() != 'NAN' else ''}{f' {re.sub(r'\s{2,}', ' ', str(historico)).strip()}' if historico.upper() != 'NAN' else ''}"

        valor_Desc_Perdas = row['DESC_PERDAS']
    
        linhaDescPerdas = (
            f"|6100|"
            f"{row['DATMOV']}|"
            f"{conta_debito}|"
            f"|"
            f"{f'{valor_Desc_Perdas:.2f}'.replace('.', ',')}|"
            f"|"
            f"{descricao_historico}|"
            f"|||"
        )

        linhas_txt.append(linhaDescPerdas)


    # 7º Registro - DESC_RET_PIS (D)
    if row['DESC_RET_PIS'] != 0 and row['DESC_RET_PIS'] != 0.0: # TRABALHAR ENCIMA DESSA LÓGICA
        conta_debito = 37
        descricao_historico = f"VR.PROV PIS S/NF.{f'{re.sub(r'\s{2,}', ' ', str(row['NRO_NFE'])).strip()}' if str(row['NRO_NFE']).upper() != 'NAN' else ''}{f' {re.sub(r'\s{2,}', ' ', str(razao_social)).strip()}' if razao_social.upper() != 'NAN' else ''}{f' {re.sub(r'\s{2,}', ' ', str(historico)).strip()}' if historico.upper() != 'NAN' else ''}"

        valor_Desc_RetPis = row['DESC_RET_PIS']

        linhaDescRetPis = (
            f"|6100|"
            f"{row['DATMOV']}|"
            f"{conta_debito}|"
            f"|"
            f"{f'{valor_Desc_RetPis:.2f}'.replace('.', ',')}|"
            f"|"
            f"{descricao_historico}|"
            f"|||"
        )

        linhas_txt.append(linhaDescRetPis)


    # 8º Registro - DESC_RET_COFINS (D)
    if row['DESC_RET_COFINS'] != 0 and row['DESC_RET_COFINS'] != 0.0: # TRABALHAR ENCIMA DESSA LÓGICA
        conta_debito = 36
        descricao_historico = f"VR.PROV COFINS S/NF.{f'{re.sub(r'\s{2,}', ' ', str(row['NRO_NFE'])).strip()}' if str(row['NRO_NFE']).upper() != 'NAN' else ''}{f' {re.sub(r'\s{2,}', ' ', str(razao_social)).strip()}' if razao_social.upper() != 'NAN' else ''}{f' {re.sub(r'\s{2,}', ' ', str(historico)).strip()}' if historico.upper() != 'NAN' else ''}"

        valor_Desc_RetCofins = row['DESC_RET_COFINS']

        linhaDescRetCofins = (
            f"|6100|"
            f"{row['DATMOV']}|"
            f"{conta_debito}|"
            f"|"
            f"{f'{valor_Desc_RetCofins:.2f}'.replace('.', ',')}|"
            f"|"
            f"{descricao_historico}|"
            f"|||"
        )

        linhas_txt.append(linhaDescRetCofins)


    # 9º Registro - DESC_RET_IR (D)
    if row['DESC_RET_IR'] != 0 and row['DESC_RET_IR'] != 0.0: # TRABALHAR ENCIMA DESSA LÓGICA
        conta_debito = 31
        descricao_historico = f"VR.PROV IR S/NF.{f'{re.sub(r'\s{2,}', ' ', str(row['NRO_NFE'])).strip()}' if str(row['NRO_NFE']).upper() != 'NAN' else ''}{f' {re.sub(r'\s{2,}', ' ', str(razao_social)).strip()}' if razao_social.upper() != 'NAN' else ''}{f' {re.sub(r'\s{2,}', ' ', str(historico)).strip()}' if historico.upper() != 'NAN' else ''}"

        valor_Desc_RetIr = row['DESC_RET_IR']

        linhaDescRetIr = (
            f"|6100|"
            f"{row['DATMOV']}|"
            f"{conta_debito}|"
            f"|"
            f"{f'{valor_Desc_RetIr:.2f}'.replace('.', ',')}|"
            f"|"
            f"{descricao_historico}|"
            f"|||"
        )

        linhas_txt.append(linhaDescRetIr)


    # 10º Registro - DESC_RET_CSLL (D)
    if row['DESC_RET_CSLL'] != 0 and row['DESC_RET_CSLL'] != 0.0: # TRABALHAR ENCIMA DESSA LÓGICA
        conta_debito = 43
        descricao_historico = f"VR.PROV CSLL S/NF.{f'{re.sub(r'\s{2,}', ' ', str(row['NRO_NFE'])).strip()}' if str(row['NRO_NFE']).upper() != 'NAN' else ''}{f' {re.sub(r'\s{2,}', ' ', str(razao_social)).strip()}' if razao_social.upper() != 'NAN' else ''}{f' {re.sub(r'\s{2,}', ' ', str(historico)).strip()}' if historico.upper() != 'NAN' else ''}"

        valor_Desc_RetCSLL = row['DESC_RET_CSLL']

        linhaDescRetCSLL = (
            f"|6100|"
            f"{row['DATMOV']}|"
            f"{conta_debito}|"
            f"|"
            f"{f'{valor_Desc_RetCSLL:.2f}'.replace('.', ',')}|"
            f"|"
            f"{descricao_historico}|"
            f"|||"
        )

        linhas_txt.append(linhaDescRetCSLL)


    return "\n".join(linhas_txt)







# Ler a planilha
df = pd.read_excel('../MovimentaçãoMercantis_ORIGINAL.xlsx')


# Converter a coluna de data para o tipo datetime
df['DATMOV'] = pd.to_datetime(df['DATMOV'])
# Formatando a data para o formato brasileiro (DD/MM/AAAA)
df['DATMOV'] = df['DATMOV'].dt.strftime('%d/%m/%Y')


df['CNPJ_ES'] = df['CNPJ_ES'].astype(str)
#df['CPF_CNPJ'] = df['CPF_CNPJ'].apply(lambda x: str(x) if pd.notnull(x) else x)
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
print(df.columns)
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
    df_devolucoes_validas.to_excel('./arquivos_gerados/LANCTO.EXCLUIDOS_EM_DEVOLUÇÃO_08.xlsx', index=False) #Criando tabela com as linhas filtradas
    desconto_devolucao.to_excel('./arquivos_gerados/LINHAS_COM_DESC.POR_DEVOLUÇÃO_08.xlsx', index=False) #Criando tabela com as linhas filtradas
    df_filtrado.to_excel('./arquivos_gerados/Movimentação_Mercantis_08.xlsx', index=False)
    df_pagto.to_excel('./arquivos_gerados/Movimentação_Mercantis_PAGTO_08_oRetorno.xlsx', index=False)
    df_recebto.to_excel('./arquivos_gerados/Movimentação_Mercantis_RECEBTO_08.xlsx', index=False)









# Criar lista de linhas formatadas para o TXT
linhas_txt = [formatar_linha_recebto(row) for _, row in df_recebto.iterrows()]

# Adicionar cabeçalho de identificação
cabecalho = "|0000|00085822000112|"

# Juntar todas as linhas em uma estrutura de TXT
conteudo_txt = "\n".join([cabecalho] + linhas_txt)

# Salvar o conteúdo em um arquivo TXT
with open('saida_formatada_RECEBTO.txt', 'w', encoding='utf-8') as arquivo_txt:
    arquivo_txt.write(conteudo_txt)
