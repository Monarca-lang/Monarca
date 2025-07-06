#RYAN: quero implementar o 'senão' como uma flag pra isso, vou precisar contar os espaços de identação e utilizar flag

# Controle do tempo de execução do programa. No final do código tem um trecho que termina de calcular o tempo e imprime o resultado.
from time import time
tempo_inicial = time()

from Levenshtein import distance # type: ignore
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
    linha = linha.replace('\n', '') # Impede que a quebra de linha atrapalhe a leitura dos dados

    # Conta os espaços no início da linha para ver a identação [linha com espaço - sem (strippada)]
    numEspaços = len(linha) - len(linha.lstrip(' '))
    if numEspaços % 4 != 0:  # Esse valor 4 é porque 1 TAB equivale a 4 espaços em Python. Se o programador colocar uma identação estranha, vai dar erro.
        monarca.erro('Erro de identação. Consulte a documentação.')
    # Pega nível da identação 
    nivel_identacao = numEspaços // 4   
    # Se identação menor que nível da chave, reseta a flag
    if nivel_identacao < monarca.chaveSE[0]:
        monarca.chaveSE[0] = 0
        monarca.chaveSE[1] = True
    # Se a flag manda pular a linha, pula.
    if nivel_identacao == monarca.chaveSE[0] and not monarca.chaveSE[1]:
        # Se for um else, não pula
        if linha.lstrip().startswith('senão'):
            pass
        else:
            continue


    if '::info' in linha:   # Ignora comentários
        índice = linha.find('::info')
        linha = linha[:índice]
    
    linha = linha.lstrip()

    dlinha = linha.split(' ') # Lista que contém a linha dividida em palavras.    
    if linha.strip() == '': # Checa se é uma linha vazia. Se sim, apenas pula para a próxima.
        continue                                                      
    # Informa o index da linha para o Monarca, a fim de apontar onde ocorreu algum eventual erro.  
    monarca.linha = c 
    
    # Verifica se a palavra inicial é um comando previsto na documentação, afim de evitar tempo de processamento desnecessário.
    if dlinha[0] in monarca.palavras_reservadas:
        # Verifica se o usuário quer iniciar uma variável
        if dlinha[0] == 'variável':
            # Verificações de sintaxe do comando
            if dlinha[1] == 'recebe':
                dica = f'variável \033[1;32m[nome de sua escolha]\033[0m recebe {' '.join(dlinha[2:]) if len(dlinha)>2 else "[valor de sua escolha]"}'
                monarca.erro(f'O nome da variável não pode ser nulo.', dica) 
            elif dlinha[2] != 'recebe':
                dica = f'variável {dlinha[1]} \033[1;32mrecebe\033[0m {' '.join(dlinha[3:]) if len(dlinha)>2 else "[valor de sua escolha]"}'
                monarca.erro(f'A palavra "recebe" deve ser explicitada após o nome da variável.', dica)
            elif len(dlinha) == 3:
                dica = f'variável {dlinha[1]} recebe \033[1;32m[valor de sua escolha]\033[0m'
                monarca.erro(f'Um valor deve ser definido para a variável.', dica)
            else:
                if dlinha[3] == 'entrada:':
                    # Tratamento especial para receber entrada do usuário
                    if len(dlinha) != 4:
                        # Verifica se o usuário quer apresentar um texto ao pedir a entrada:
                        monarca.variavel(operacao='input', nome=dlinha[1], var=' '.join(dlinha[4:]))
                    else:
                        # Se não, vai no seco
                        monarca.variavel(operacao='input', nome=dlinha[1])
                else:
                    # Envia tudo o que vier depois de "recebe" para ser processado.
                    valor = ' '.join(dlinha[3:])
                    valor = monarca.processar_expressao(expressao=valor)
                    monarca.variavel(operacao='add', nome=dlinha[1], var=valor)
                
        # Verifica se o usuário quer deletar uma variável
        elif dlinha[0] == 'deletar':
            if dlinha[1] != 'variável':
                dica = f'deletar \033[1;32mvariável\033[0m {dlinha[2] if len(dlinha) == 3 else "[variável de sua escolha]"}'
            else:
                monarca.variavel('del', dlinha[2])
            
        # Verifica se o usuário quer mostrar uma mensagem na tela
        elif dlinha[0] == 'mostrar':
            if dlinha[1] != 'na':
                dica = f'mostrar \033[1;32mna\033[0m tela: {' '.join(dlinha[3:]) if len(dlinha)>3 else "[valor de sua escolha]"}'
                monarca.erro('A palavra "na" deve ser explicitada no comando "mostrar na tela".', dica)
            elif dlinha[2] != 'tela:':
                dica = f'mostrar na \033[1;32mtela:\033[0m {' '.join(dlinha[3:]) if len(dlinha)>3 else "[valor de sua escolha]"} '
                monarca.erro(f'A palavra "tela:" deve ser explicitada no comando "mostrar na tela".', dica)
            else:
                monarca.escrever(texto=linha[17:])
        elif dlinha[0] == 'se': 
            if dlinha[-1] != 'então:': #termina sem 'então:'
                dica = f'se [condição] \033[1;32mentão:\033[0m' 
                monarca.erro(f'A palavra "então:" deve ser explicitada no comando "se [condição] então:".', dica)
            else:
                valor = ' '.join(dlinha[1:len(dlinha)-1])
                valor = monarca.processar_expressao(expressao=valor)
                cond_true = not(valor == 'falso' or (valor.isnumeric() and int(valor) == 0))
                # Se condiçao  true, executa (muda a flag)
                monarca.chaveSE = [nivel_identacao + 1, cond_true]
                continue
        elif dlinha[0] == 'senão':
            if dlinha[-1] != 'então:':
                dica = f'senão \033[1;32mentão:\033[0m'
                monarca.erro(f'A palavra "então:" deve ser explicitada no comando "senão então:".', dica)
            if nivel_identacao != monarca.chaveSE[0] - 1:
                monarca.erro('Comando "senão" com indentação incorreta.')
            #Se a flag de condição for verdadeira, pula a linha
            monarca.chaveSE[1] = not monarca.chaveSE[1]
            continue


    # Entrega um erro e uma sugestão de correção casoo o comando não esteja previsto na documentação. 
    else:
        distancias = [distance(dlinha[0], palavra) for palavra in monarca.palavras_reservadas]
        chute = monarca.palavras_reservadas[distancias.index(min(distancias))]
        if chute == 'mostrar':
            dica = f'\033[1;32mmostrar\033[0m na tela: [valor de sua escolha]'
        elif chute == 'variável':
            dica = f'\033[1;32mvariável\033[0m [nome de sua escolha] recebe [valor de sua escolha]'
        elif chute == 'deletar':
            dica = f'\033[1;32mdeletar\033[0m variável [variável de sua escolha]'
        elif chute == 'se':
            dica = f'\033[1;32mse\033[0m [condição] então:'
        elif chute == 'entrada':
            dica = f'\033[1;32mentrada\033[0m [nome] [mensagem opcional]'
        monarca.erro(f'Comando "{dlinha[0]}" não encontrado. Consulte a documentação.', dica)   
        
tempo_final = time()
print(f'\n\033[1;33mTempo de execução: {tempo_final-tempo_inicial:.4f} segundos.\033[m')
