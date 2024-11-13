def compare_files(file1_path, file2_path):
    with open(file1_path, 'r', encoding='latin-1') as file1, open(file2_path, 'r', encoding='latin-1') as file2:
        lines_file1 = file1.readlines()
        lines_file2 = file2.readlines()

    # Convert lists to sets for easy comparison
    set_file1 = set(lines_file1)
    set_file2 = set(lines_file2)

    # Find unique lines
    unique_to_file1 = set_file1 - set_file2
    unique_to_file2 = set_file2 - set_file1

    # Find differences
    differences = unique_to_file1.union(unique_to_file2)

    return unique_to_file1, unique_to_file2, differences

# Paths to your files
file1_path = '../MovimentacaoMercantis_PAGTO_08.txt'
file2_path = './saida_formatada.txt'
# file1_path = 'arquivos_gerados/testeArqjdrel07.txt'
# file2_path = 'arquivos_gerados/testeArqjdrel06.txt'
# file2_path = 'arquivos_gerados/testeArqPC03.txt'

unique_to_file1, unique_to_file2, differences = compare_files(file1_path, file2_path)

# print("Linhas únicas no Arquivo 1:")
# for line in unique_to_file1:
#     print(line.strip())

print("\nLinhas únicas no Arquivo 2:")
for line in unique_to_file2:
    print(line.strip())

# print("\nDiferenças entre os arquivos:")
# for line in differences:
#     print(line.strip())
