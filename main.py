# Ryan: implementando o 'senão' como uma flag pra isso, vou precisar contar os espaços de identação

# Controle do tempo de execução do programa. No final do código tem um trecho que termina de calcular o tempo e imprime o resultado.
from time import time
tempo_inicial = time()

from Levenshtein import distance
from argparse import ArgumentParser
from monlib import Monarca

# Define o argumento "-s" ou "--script" para usuários de linha de comando apontarem onde está o script que desejam executar.
argumentos = ArgumentParser(usage='monarca.py -s script.mc')
argumentos.add_argument('-s', '--script', required=True)
argumentos = argumentos.parse_args()

# Cria uma instância da classe geral Monarca(), onde estão todas as funções e dados iniciais.
monarca = Monarca()

# Verifica se o arquivo indicado pelo usuário existe e, se sim, tenta abrí-lo e guardá-lo na variável script. Se não, dá um erro na tela.
try:
    script = open(argumentos.script, encoding='utf-8').readlines()
except Exception:
    monarca.erro(f'Arquivo {argumentos.script} não encontrado.')

# A variável c é o índice da linha, e a variável linha contém o texto da linha em si. A cada laço é interpretada uma linha do script.
for c, linha in enumerate(script):
    linha_original = linha.replace('\n', '') # Impede que a quebra de linha atrapalhe a leitura dos dados
    
    # Ignora comentários
    if '::info' in linha_original:
        índice = linha_original.find('::info')
        linha_original = linha_original[:índice].rstrip() # Essa linha faz com que comentários a direita dos ifs não quebrem a busca pelo "então:"
    
    # Checa se é uma linha vazia. Se sim, apenas pula para a próxima.
    if linha_original.strip() == '':
        continue

    # Conta os espaços no início da linha para ver a identação
    numEspaços = len(linha_original) - len(linha_original.lstrip())
    if numEspaços % 4 != 0:  # Esse valor 4 é porque 1 TAB equivale a 4 espaços em Python.
        monarca.erro('Erro de identação. Consulte a documentação.')
    
    nivel_identacao = numEspaços // 4
    # Informa o index da linha para o Monarca, a fim de apontar onde ocorreu algum eventual erro.
    monarca.linha = c 
    
    linha_processada = linha_original.lstrip()
    dlinha = linha_processada.split(' ') # Lista que contém a linha dividida em palavras.

    # Aplicando else
    if dlinha[0] == 'senão':
        if dlinha[-1] != 'então:':
            dica = f'senão \033[1;32mentão:\033[0m'
            monarca.erro(f'A palavra "então:" deve ser explicitada no comando "senão então:".', dica)
        if nivel_identacao != monarca.chaveSE[0] - 1:
            monarca.erro('Comando "senão" com indentação incorreta.')
        
        # Inverte o "se" anterior para decidir se executa o "senão"
        monarca.chaveSE[1] = not monarca.chaveSE[1]
        continue

    # Se a indentação diminuiu o bloco anterior terminou.
    if nivel_identacao < monarca.chaveSE[0]:
        monarca.chaveSE = [0, True]

    # Se a flag de um "se" anterior for falsa, pula as linhas dentro do bloco
    if nivel_identacao == monarca.chaveSE[0] and not monarca.chaveSE[1]:
        continue
    
    # Verifica se a palavra inicial é um comando previsto na documentação
    if dlinha[0] in monarca.palavras_reservadas:
        if dlinha[0] == 'variável':
            if len(dlinha) < 2 or dlinha[1] == 'recebe':
                dica = f'variável \033[1;32m[nome]\033[0m recebe [valor]'
                monarca.erro(f'O nome da variável não pode ser nulo.', dica) 
            elif len(dlinha) < 3 or dlinha[2] != 'recebe':
                dica = f'variável {dlinha[1]} \033[1;32mrecebe\033[0m [valor]'
                monarca.erro(f'A palavra "recebe" deve ser explicitada após o nome da variável.', dica)
            elif len(dlinha) == 3:
                dica = f'variável {dlinha[1]} recebe \033[1;32m[valor]\033[0m'
                monarca.erro(f'Um valor deve ser definido para a variável.', dica)
            else:
                if dlinha[3] == 'entrada:':
                    if len(dlinha) > 4:
                        monarca.variavel(operacao='input', nome=dlinha[1], var=' '.join(dlinha[4:]))
                    else:
                        monarca.variavel(operacao='input', nome=dlinha[1])
                else:
                    valor = ' '.join(dlinha[3:])
                    valor = monarca.processar_expressao(expressao=valor)
                    monarca.variavel(operacao='add', nome=dlinha[1], var=valor)
                
        elif dlinha[0] == 'deletar':
            if len(dlinha) < 3 or dlinha[1] != 'variável':
                dica = f'deletar \033[1;32mvariável\033[0m [nome]'
                monarca.erro('Sintaxe incorreta. Use "deletar variável [nome]".', dica)
            else:
                monarca.variavel('del', dlinha[2])
            
        elif dlinha[0] == 'mostrar':
            if len(dlinha) < 3 or dlinha[1] != 'na' or dlinha[2] != 'tela:':
                dica = f'mostrar \033[1;32mna tela:\033[0m [valor]'
                monarca.erro('Sintaxe incorreta. Use "mostrar na tela: [valor]".', dica)
            else:
                monarca.escrever(texto=linha_processada[17:])

        elif dlinha[0] == 'se': 
            if dlinha[-1] != 'então:':
                dica = f'se [condição] \033[1;32mentão:\033[0m' 
                monarca.erro(f'A palavra "então:" deve ser explicitada no comando "se".', dica)
            else:
                valor = ' '.join(dlinha[1:-1])
                valor = monarca.processar_expressao(expressao=valor)
                cond_true = not(valor == 'falso' or (valor.isnumeric() and int(valor) == 0))
                monarca.chaveSE = [nivel_identacao + 1, cond_true]
                continue
    
    # Entrega um erro e uma sugestão de correção caso o comando não esteja previsto na documentação.
    else:
        distancias = [distance(dlinha[0], palavra) for palavra in monarca.palavras_reservadas]
        chute = monarca.palavras_reservadas[distancias.index(min(distancias))]
        dica = ''
        if chute == 'mostrar':
            dica = f'\033[1;32mmostrar\033[0m na tela: [valor]'
        elif chute == 'variável':
            dica = f'\033[1;32mvariável\033[0m [nome] recebe [valor]'
        elif chute == 'deletar':
            dica = f'\033[1;32mdeletar\033[0m variável [nome]'
        elif chute == 'se':
            dica = f'\033[1;32mse\033[0m [condição] então:'
        elif chute == 'senão':
            dica = f'\033[1;32msenão\033[0m então:'

        monarca.erro(f'Comando "{dlinha[0]}" não encontrado. Consulte a documentação.', dica)   
        
tempo_final = time()
print(f'\n\033[1;33mTempo de execução: {tempo_final-tempo_inicial:.4f} segundos.\033[m')
