import difflib

# Carregar o conteúdo de cada linha do molde e da conversão
with open('../MovimentacaoMercantis_PAGTO_08.txt', 'r', encoding='latin-1') as f_molde, \
     open('./saida_formatada.txt', 'r', encoding='latin-1') as f_convertido:

    # Ler linhas, removendo espaços e quebras de linha extras
    linhas_molde = [linha.strip() for linha in f_molde]
    linhas_convertido = [linha.strip() for linha in f_convertido]

# Comparar linha por linha
for idx, (linha_molde, linha_convertida) in enumerate(zip(linhas_molde, linhas_convertido), start=1):
    if linha_molde != linha_convertida:
        print(f"Diferença na linha {idx}:")
        for i, s in enumerate(difflib.ndiff(linha_molde, linha_convertida)):
            if s[0] != ' ':
                print(f"Posição {i}: '{s[-1]}' é diferente")
