import json

# Função para carregar o conteúdo de um arquivo JSON
def carregar_json(nome_arquivo):
    with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
        return json.load(arquivo)

# Função para aplicar regras de formatação específicas a cada linha do DataFrame
def formatar_linha(row):
    ### REGRAS:

    ## CONTA CONTÁBIL A DÉBITO (*)
    conta_debito = ''
    # Carregar cada JSON separado
    de_paraHistorico = carregar_json('./CONTA_CONTÁBIL_A_DÉBITO/de_para-historico_modificado.json')
    de_paraRazaoSocial = carregar_json('./CONTA_CONTÁBIL_A_DÉBITO/de_para-razaosocial_modificado.json')

    # DE/PARA - HISTÓRICO
    for registro in de_paraHistorico:
        if (registro['conteudo_comparacao'] in row['HISTORICO']):
            conta_debito = registro['conta']
    # DE/PARA - RAZÃO SOCIAL
    for registro in de_paraRazaoSocial:
        if (registro['conteudo_comparacao'] in row['RAZAO_SOCIAL']):
            conta_debito = registro['conta']
    # IR Taxas e Impostos
    if ( 'IR' in str(row['HISTORICO']).upper() and ( 'Taxas' in str(row['RAZAO_SOCIAL']) or 'Impostos' in str(row['RAZAO_SOCIAL']) ) ):
        conta_debito = '178'
    # Adiciona 'X' na última coluna se o registro for um cliente
    if ( row['CPF_CNPJ'] > 99999999999 and int(row['NRO_NFE']) >= 1):
        conta_debito = row['CPF_CNPJ']
        sinal = 'X'
    else:
        sinal = ''


    ## CONTA CONTÁBIL A CRÉDITO (*)
    conta_credito = ''
    # Carregar cada JSON separado
    de_paraDS_banco = carregar_json('./CONTA_CONTÁBIL_A_CRÉDITO/de_para_bancos-ds_banco_modificado.json')
    de_paraDS_cc = carregar_json('./CONTA_CONTÁBIL_A_CRÉDITO/de_para_bancos-ds_cc.json')

    # DE/PARA - DS_BANCO
    for registro in de_paraDS_banco:
        if (registro['conteudo_comparacao'] in row['DS_BANCO']):
            conta_credito = registro['conta']
    # DE/PARA - DS_CC
    for registro in de_paraDS_cc:
        if (registro['conteudo_comparacao'] in row['DS_CC']):
            conta_credito = registro['conta']



    # Construção da linha do TXT
    linha_txt = (
        f"|6100|"
        f"{row['DATMOV']}|"
        f"{conta_debito}|"
        f"{conta_credito}|"
        f"{row['SAIDA']}|"
        f"VR PG {row['NRO_NFE']} {row['RAZAO_SOCIAL']} {row['HISTORICO']}|" # Descrição Histórico
        f"{sinal}|||"
    )
    return linha_txt
