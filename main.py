# Controle do tempo de execução do programa. No final do código tem um trecho que termina de calcular o tempo e imprime o resultado.
from time import time
tempo_inicial = time()

from Levenshtein import distance
from argparse import ArgumentParser
from monlib import Monarca # Garanta que monlib.py esteja atualizado

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

# A variável c é o índice da linha. O laço for foi trocado por while para permitir o controle do fluxo de execução.
c = 0
while c < len(script):
    linha = script[c]
    monarca.linha = c
    linha_original = linha.replace('\n', '')

    # Ignora comentários
    if '::info' in linha_original:
        índice = linha_original.find('::info')
        linha_original = linha_original[:índice]

    # Checa se é uma linha vazia. Se sim, apenas pula para a próxima.
    if linha_original.strip() == '':
        c += 1
        continue

    # Conta os espaços no início da linha para ver a identação
    numEspaços = len(linha_original) - len(linha_original.lstrip())
    if numEspaços % 4 != 0:
        monarca.erro('Erro de identação. Consulte a documentação.')

    nivel_identacao = numEspaços // 4
    linha_processada = linha_original.lstrip()
    dlinha = linha_processada.split(' ')

    # Debug senão
    if dlinha[0] == 'senão':
        # Sem if
        if not monarca.pilha_se:
            monarca.erro('Comando "senão" utilizado sem um "se" correspondente.')
        # Sem então
        if dlinha[-1] != 'então:':
            dica = f'senão \033[1;32mentão:\033[0m'
            monarca.erro(f'A palavra "então:" deve ser explicitada no comando "senão então:".', dica)
        # Identação incorreta
        if nivel_identacao != monarca.pilha_se[-1][0] - 1:
            monarca.erro('Comando "senão" com indentação incorreta.')
        
        # Inverte a condição do "se" no topo da pilha para decidir se executa o "senão"
        monarca.pilha_se[-1][1] = not monarca.pilha_se[-1][1]
        c += 1
        continue

    #  Manipulando a pilha de identação
    # Pilha se
    if monarca.pilha_se and nivel_identacao < monarca.pilha_se[-1][0]:
        monarca.pilha_se.pop()

    # Pilha para
    if monarca.pilha_para and nivel_identacao < monarca.pilha_para[-1]['nivel_identacao']:
        loop = monarca.pilha_para[-1]
        loop['iterador'] += 1
        if loop['iterador'] < loop['fim']:
            c = loop['linha_inicio']
            continue
        else:
            monarca.pilha_para.pop()
    # Pula se o se está ativo e a condição é falsa
    if monarca.pilha_se and not monarca.pilha_se[-1][1]:
        c += 1
        continue

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
        dica = ''
        if chute == 'mostrar':
            dica = f'Talvez você quisesse dizer: \033[1;32mmostrar\033[0m na tela: [valor]'
        elif chute == 'variável':
            dica = f'Talvez você quisesse dizer: \033[1;32mvariável\033[0m [nome] recebe [valor]'
        elif chute == 'deletar':
            dica = f'Talvez você quisesse dizer: \033[1;32mdeletar\033[0m variável [nome]'
        elif chute == 'se':
            dica = f'Talvez você quisesse dizer: \033[1;32mse\033[0m [condição] então:'
        elif chute == 'para': #for adicionado
            dica = f'Talvez você quisesse dizer: \033[1;32mpara\033[0m contando até [número]:'

        monarca.erro(f'Comando "{dlinha[0]}" não encontrado. Consulte a documentação.', dica)

    c += 1

tempo_final = time()
print(f'\n\033[1;33mTempo de execução: {tempo_final - tempo_inicial:.4f} segundos.\033[m')
