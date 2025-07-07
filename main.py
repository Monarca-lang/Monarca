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
c = 0
while c < len(script):
    linha = script[c]
    monarca.linha = c
    linha_original = linha.replace('\n', '')

    # Ignora comentários
    if '::info' in linha_original:
        índice = linha_original.find('::info')
        linha_original = linha_original[:índice].rstrip() # Essa linha faz com que comentários a direita dos ifs não quebrem a busca pelo "então:"
    
    # Checa se é uma linha vazia. Se sim, apenas pula para a próxima.
    if linha_original.strip() == '':
        c += 1
        continue

    # Conta os espaços no início da linha para ver a identação
    numEspaços = len(linha_original) - len(linha_original.lstrip())
    if numEspaços % 4 != 0: # Esse valor 4 é porque 1 TAB equivale a 4 espaços em Python.
        monarca.erro('Erro de identação. Consulte a documentação.')
    nivel_identacao = numEspaços // 4
    linha_processada = linha_original.lstrip()
    dlinha = linha_processada.split(' ')

    # olha o senão primeiro
    if dlinha[0] == 'senão':
            if not monarca.pilha_se:
                monarca.erro('Comando "senão" utilizado sem um "se" correspondente.')
            if dlinha[-1] != 'então:':
                dica = f'senão \033[1;32mentão:\033[0m'
                monarca.erro(f'A palavra "então:" deve ser explicitada no comando "senão então:".', dica)
            if nivel_identacao != monarca.pilha_se[-1][0] - 1:
                monarca.erro('Comando "senão" com indentação incorreta.')
            
            monarca.pilha_se[-1][1] = not monarca.pilha_se[-1][1]
            c += 1
            continue

    # Gerencia o fim dos blocos com base na diminuição da indentação.
    # Debug: Melhorando o clean da pilha
    if monarca.pilha_para and nivel_identacao < monarca.pilha_para[-1]['nivel_identacao']:
        loop = monarca.pilha_para[-1]
        
        # Clear na pilha se antes de repetir o laço
        while monarca.pilha_se and monarca.pilha_se[-1][0] > loop['nivel_identacao']:
            monarca.pilha_se.pop()
            
        loop['iterador'] += 1
        if loop['iterador'] < loop['fim']:
            c = loop['linha_inicio']
            continue
        else:
            # Limpa pilha for quandofinaliza o laço
            monarca.pilha_para.pop()
    if monarca.pilha_se and nivel_identacao < monarca.pilha_se[-1][0]:
        monarca.pilha_se.pop()

    # Pula as linhas seguintes se a condição de um bloco 'se' for falsa.
    if monarca.pilha_se and not monarca.pilha_se[-1][1]:
        c += 1
        continue

    # Processa os comandos normais.
    if dlinha[0] in monarca.palavras_reservadas:
        if dlinha[0] == 'variável':
            if len(dlinha) < 4:
                monarca.erro('Sintaxe incorreta para "variável". Use: variável [nome] recebe [valor]')
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
            if len(dlinha) < 3 or ' '.join(dlinha[1:3]) != 'na tela:':
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
                cond_true = not (valor == 'falso' or (valor.replace('.', '').isnumeric() and float(valor) == 0))
                monarca.pilha_se.append([nivel_identacao + 1, cond_true])
        elif dlinha[0] == 'para':
            if len(dlinha) != 4 or ' '.join(dlinha[1:3]) != 'contando até' or not dlinha[3].endswith(':'):
                dica = 'para contando até [número]:'
                monarca.erro('Sintaxe do laço "para" incorreta.', dica)
            try:
                fim = int(dlinha[3][:-1])
            except ValueError:
                monarca.erro('O valor final do laço "para" deve ser um número inteiro.')
            monarca.pilha_para.append({
                'nivel_identacao': nivel_identacao + 1,
                'iterador': 0,
                'fim': fim,
                'linha_inicio': c + 1
            })

    else:
        distancias = {palavra: distance(dlinha[0], palavra) for palavra in monarca.palavras_reservadas}
        chute = min(distancias, key=distancias.get)
        dica = f'Talvez você quisesse dizer: \033[1;32m{chute}\033[0m'
        monarca.erro(f'Comando "{dlinha[0]}" não encontrado. Consulte a documentação.', dica)

    c += 1
tempo_final = time()
print(f'\n\033[1;33mTempo de execução: {tempo_final - tempo_inicial:.4f} segundos.\033[m')
