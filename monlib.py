class Monarca:
    def __init__(self, linha=0):
        self.linha = linha
        self.pilha_se = []  # Pilha if else
        self.pilha_para = [] # Pilha for
        self.variaveis = {}
        self.palavras_reservadas = (
            'mostrar',
            'variável',
            'deletar',
            'se',
            'senão',
            'para'
        )
        self.operações = (
            'mais',
            'menos',
            'vezes',
            'dividido por',
            'igual',
            'ou',
            'e',
            '(',
            ')'
        )
        self.opcondicionais = {
            'é igual a',
            'é diferente de',
            'é menor que',
            'é maior que'
        }
        self.booleanos = (
            'verdadeiro',
            'falso'
        )

    # Função de erro. Basta passar a mensagem de erro como argumento que ele vai reconhecer a linha do erro sozinho.
    def erro(self, mensagem='', dica=''):
        print('\033[1;33m='*10, 'Monarca', '='*10)
        print(f'\033[1;31m * Erro na linha {self.linha + 1}. \033[0m' + mensagem)
        print(f'\033[1;32m * Sugestão:\033[0m {dica}' if dica else '\r')
        exit()

    def identificar_elementos(self, expressao):
        elementos = []
        trecho = ''
        # A cada loop, um trecho é lido, interpretado e armazenado na lista "elementos".
        # O trecho lido também é apagado da variável "expressao", então o loop abaixo roda enquanto houver informação na variável.
        # A seleção do trecho se baseia na existência de aspas ou não.
        while expressao:
            if expressao[0] == "\"": # Checa se a expressão começa com aspa, ou seja, se há uma string logo no início. Se sim, checa se há outra aspa e caso haja armazena o trecho e o apaga da variável dado.
                c = expressao.find("\"", 1) # Índice da próxima aspa
                if c != -1: # Ou seja, se existe outra aspa para completar o par, já que seria -1 se não encontrasse.
                    elementos.append(expressao[0:c+1]) 
                    expressao = expressao[c+1:] 
                    continue
                else:   # Se não existe par, aponta erro
                    raise Exception  # COLOCAR UM ERRO MAIS ELABORADO AQUI               
            else: # Em caso de não começar com aspa. Ou seja, poderia ser um número, uma variável, um operador etc.
                if "\"" in expressao:                # Esse if...else checa se em dado momento aparecerá uma string. Se não aparecer, o código só lê tudo. Se aparecer, lê até o momento da string.
                    c = expressao.find("\"")
                    trecho = expressao[0:c]                        
                    expressao = expressao[c:]
                else:                    
                    trecho = expressao[0:]
                    expressao = ''
                trecho = trecho.replace('(', ' ( ').replace(')', ' ) ')
                for palavra in trecho.split(): # Leitura do trecho. Checa e substitui as variáveis, checa a validade dos números, etc
                    if palavra in self.variaveis.keys():
                        palavra = self.variaveis[palavra]
                        palavra = palavra.replace(',', '.') if palavra.replace(',', '.').isnumeric() else palavra
                    elif palavra.replace(',','').isnumeric() and palavra.count(',') <= 1: # Se o trecho for apenas números e vírgula e, havendo vírgula, houver apenas uma.                 
                        palavra = palavra.replace(",",".")  # Converte vírgula para ponto para poder ser lido nas operações.
                    # Se não for variável, nem número, nem booleano e nem operação, dá erro.
                    elif not any(palavra in operador.split() for operador in self.opcondicionais) and not any(palavra in operador.split() for operador in self.operações) and not palavra in self.booleanos and not '\n': 
                        dica = f'O termo "\033[1;31m{palavra}\033[0m" não parece estar sendo utilizado da maneira correta. Seria uma variável não declarada?'
                        self.erro(f'Não é possível resolver "{''.join(trecho)}".', dica)
                    elementos.append(palavra)
        return elementos
    
    def calcular(self, elementos):
        i = 0
        try:
            # Resolução de parênteses (recursivamente)
            while '(' in elementos:
                start_index = -1
                # Encontra o último '(', que corresponde ao grupo mais interno
                for i_paren, token in enumerate(elementos):
                    if token == '(':
                        start_index = i_paren
                
                # Encontra o ')' correspondente
                end_index = -1
                for i_paren in range(start_index, len(elementos)):
                    if elementos[i_paren] == ')':
                        end_index = i_paren
                        break
                
                if start_index == -1 or end_index == -1:
                    self.erro("Erro de sintaxe com parênteses não balanceados.")

                sub_expressao = elementos[start_index + 1 : end_index]
                resultado_sub = self.calcular(sub_expressao)
                del elementos[start_index : end_index + 1]
                elementos.insert(start_index, resultado_sub[0])

            while 'vezes' in elementos or 'dividido' in elementos:
                if elementos[i] == 'vezes':
                    num1 = elementos[i - 1]
                    num1 = float(num1) if '.' in num1 else int(num1)
                    num2 = elementos[i + 1]
                    num2 = float(num2) if '.' in num2 else int(num2)                      
                    resultado = num1 * num2
                    elementos[i+1] = str(resultado)                   
                    elementos.pop(i - 1)                    
                    elementos.pop(i - 1)
                
                elif elementos[i] == 'dividido':
                    if elementos[i + 1] != 'por':
                        for c, palavra in enumerate(elementos):
                            elementos[c] = palavra.replace('.', ',') if palavra.replace('.', '').isnumeric() else palavra
                        dica = f'{' '.join(elementos[:i+1])} \033[1;32mpor\033[0m {' '.join(elementos[i+1:])}'
                        self.erro('O termo "por" deve ser explicitado no operador "dividido por".', dica)
                    
                    num1 = elementos[i - 1]
                    num1 = float(num1) if '.' in num1 else int(num1)
                    num2 = elementos[i + 2]
                    num2 = float(num2) if '.' in num2 else int(num2) 
                    resultado = num1 / num2
                    del elementos[i-1:i+3] # Remove 'num1', 'dividido', 'por', 'num2'
                    elementos.insert(i-1, str(resultado))
                    i = 0
                else:
                    i += 1 
            i = 0
            while 'mais' in elementos or 'menos' in elementos:                                      
                if elementos[i] == 'mais' or elementos[i] == 'menos':
                    num1 = elementos[i - 1]
                    num1 = float(num1) if '.' in num1 else int(num1)
                    num2 = elementos[i + 1]
                    num2 = float(num2) if '.' in num2 else int(num2)
                    match elementos[i]:
                        case 'mais':                        
                            resultado = num1 + num2
                        case 'menos':
                            resultado = num1 - num2                 
                    elementos[i+1] = str(resultado)                 
                    elementos.pop(i - 1)                    
                    elementos.pop(i - 1)                                        
                    i = 0
                else:
                    i += 1
            i = 0
            
            # Operações Lógicas
            while any(operador in elementos for operador in ['igual', 'menor', 'maior', 'diferente']):
                if elementos[i] == 'igual':
                    # Verificação de erros de sintaxe
                    if elementos[i - 1] != 'é':
                        for c, palavra in enumerate(elementos):
                            elementos[c] = palavra.replace('.', ',') if palavra.replace('.', '').isnumeric() else palavra
                        dica = f'{elementos[i-1]} \033[1;32mé\033[0m igual a {elementos[i+2] if elementos[i+1] == 'a' and len(elementos)>=elementos.index(elementos[i]) else elementos[i+1]}'
                        self.erro('O termo "é" deve ser explicitado na declaração lógica.', dica)
                    elif elementos[i+1] != 'a':
                        for c, palavra in enumerate(elementos):
                            elementos[c] = palavra.replace('.', ',') if palavra.replace('.', '').isnumeric() else palavra
                        dica = f'{elementos[i-2]} é igual\033[1;32m a\033[0m {elementos[i+1]}'
                        self.erro('O termo "a" deve ser explicitado ao usar o operador "igual a".', dica)    
                          
                    op1 = elementos[i - 2]
                    op2 = elementos[i + 2]
                    try:
                        # Tenta comparar como números
                        resultado = 'verdadeiro' if float(op1) == float(op2) else 'falso'
                    except (ValueError, TypeError):
                        # Se falhar, compara como texto (ignorando aspas e maiúsculas/minúsculas)
                        str1 = str(op1)[1:-1] if isinstance(op1, str) and op1.startswith('"') else str(op1)
                        str2 = str(op2)[1:-1] if isinstance(op2, str) and op2.startswith('"') else str(op2)
                        resultado = 'verdadeiro' if str1.lower() == str2.lower() else 'falso'

                    # Substitui a sub-expressão pelo resultado
                    del elementos[i-2:i+3]
                    elementos.insert(i-2, resultado)
                    i = 0

                elif elementos[i] == 'diferente':
                    # Verificação de erros de sintaxe
                    if elementos[i - 1] != 'é':
                        for c, palavra in enumerate(elementos):
                            elementos[c] = palavra.replace('.', ',') if palavra.replace('.', '').isnumeric() else palavra
                        dica = f'{elementos[i-1]} \033[1;32mé\033[0m diferente de {elementos[i+2] if elementos[i+1] == 'de' and len(elementos)>=elementos.index(elementos[i]) else elementos[i+1]}'
                        self.erro('O termo "é" deve ser explicitado na declaração lógica "diferente de".', dica)
                    elif elementos[i+1] != 'de':
                        for c, palavra in enumerate(elementos):
                            elementos[c] = palavra.replace('.', ',') if palavra.replace('.', '').isnumeric() else palavra
                        dica = f'{elementos[i-2]} é diferente\033[1;32m de\033[0m {elementos[i+1]}'
                        self.erro('O termo "de" deve ser explicitado ao usar o operador "diferente de".', dica)    
                    
                    op1 = elementos[i - 2]
                    op2 = elementos[i + 2]
                    try:
                        # Tenta comparar como números
                        resultado = 'verdadeiro' if float(op1) != float(op2) else 'falso'
                    except (ValueError, TypeError):
                        # Se falhar, compara como texto (ignorando aspas e maiúsculas/minúsculas)
                        str1 = str(op1)[1:-1] if isinstance(op1, str) and op1.startswith('"') else str(op1)
                        str2 = str(op2)[1:-1] if isinstance(op2, str) and op2.startswith('"') else str(op2)
                        resultado = 'verdadeiro' if str1.lower() != str2.lower() else 'falso'

                    # Substitui a sub-expressão pelo resultado
                    del elementos[i-2:i+3]
                    elementos.insert(i-2, resultado)
                    i = 0

                elif elementos[i] == 'maior':
                    # Verificação de erros de sintaxe
                    if elementos[i - 1] != 'é':
                        dica = f'{elementos[i-1]} \033[1;32mé\033[0m maior que {elementos[i+2] if elementos[i+1] == 'que' and len(elementos)>=elementos.index(elementos[i]) else elementos[i+1]}'
                        self.erro('O termo "é" deve ser explicitado na declaração lógica "maior que".', dica)
                    elif elementos[i+1] != 'que':
                        dica = f'{elementos[i-2]} é maior\033[1;32m que\033[0m {elementos[i+1]}'
                        self.erro('O termo "que" deve ser explicitado ao usar o operador "maior que".', dica)    
                    elif not elementos[i-2].replace('.', '').isnumeric() or not elementos[i+2].replace('.', '').isnumeric():
                        dica = f'{elementos[i-2] if elementos[i-2].isnumeric() else '\033[1;32m[número]\033[0m'} é maior que {elementos[i+2] if elementos[i+2].isnumeric() else '\033[1;32m[número]\033[0m'}'
                        self.erro('Dados numéricos devem ser explicitados ao utilizar o operador "maior que".', dica)
                    
                    num1 = float(elementos[i - 2])
                    num2 = float(elementos[i + 2])
                    resultado = 'verdadeiro' if num1 > num2 else 'falso'
                    # Substitui a sub-expressão pelo resultado
                    del elementos[i-2:i+3]
                    elementos.insert(i-2, resultado)
                    i = 0
                
                elif elementos[i] == 'menor':
                    # Verificação de erros de sintaxe
                    if elementos[i - 1] != 'é':
                        dica = f'{elementos[i-1]} \033[1;32mé\033[0m menor que {elementos[i+2] if elementos[i+1] == 'que' and len(elementos)>=elementos.index(elementos[i]) else elementos[i+1]}'
                        self.erro('O termo "é" deve ser explicitado na declaração lógica "menor que".', dica)
                    elif elementos[i+1] != 'que':
                        dica = f'{elementos[i-2]} é menor\033[1;32m que\033[0m {elementos[i+1]}'
                        self.erro('O termo "que" deve ser explicitado ao usar o operador "menor que".', dica)    
                    elif not elementos[i-2].replace('.', '').isnumeric() or not elementos[i+2].replace('.', '').isnumeric():
                        dica = f'{elementos[i-2] if elementos[i-2].isnumeric() else '\033[1;32m[número]\033[0m'} é menor que {elementos[i+2] if elementos[i+2].isnumeric() else '\033[1;32m[número]\033[0m'}'
                        self.erro('Dados numéricos devem ser explicitados ao utilizar o operador "menor que".', dica)
                    
                    num1 = float(elementos[i - 2])
                    num2 = float(elementos[i + 2])
                    resultado = 'verdadeiro' if num1 < num2 else 'falso'
                    # Substitui a sub-expressão pelo resultado
                    del elementos[i-2:i+3]
                    elementos.insert(i-2, resultado)
                    i = 0
                
                else:
                    i += 1
            
            # Operadores lógicos "ou" e "e"
            # Loop de precedência para o 'e' (AND)
            i = 0
            while 'e' in elementos:
                if elementos[i] == 'e':
                    val1 = elementos[i - 1]
                    val2 = elementos[i + 1]
                    # Converter para booleano Monarca
                    bool1 = (val1 == 'verdadeiro' or val1 == 'True' or val1 == '1')
                    bool2 = (val2 == 'verdadeiro' or val2 == 'True' or val2 == '1')
                    resultado = 'verdadeiro' if (bool1 and bool2) else 'falso'
                    elementos[i+1] = resultado
                    elementos.pop(i - 1)
                    elementos.pop(i - 1)
                    i = 0
                else:
                    i += 1
            
            # Loop para o 'ou' (OR)
            i = 0
            while 'ou' in elementos:
                if elementos[i] == 'ou':
                    val1 = elementos[i - 1]
                    val2 = elementos[i + 1]
                    # Converter para booleano Monarca
                    bool1 = (val1 == 'verdadeiro' or val1 == 'True' or val1 == '1')
                    bool2 = (val2 == 'verdadeiro' or val2 == 'True' or val2 == '1')
                    resultado = 'verdadeiro' if (bool1 or bool2) else 'falso'
                    elementos[i+1] = resultado
                    elementos.pop(i - 1)
                    elementos.pop(i - 1)
                    i = 0
                else:
                    i += 1
            return elementos
        except Exception as e:
            self.erro(f'Não é possível resolver "{' '.join(elementos)}".')

    def processar_expressao(self, expressao):
        # A função identificar_elementos divide a expressão em uma lista cujos elementos são separados levando em contas strings, números, operações, variáveis etc.
        # Por exemplo, uma expressão "5 mais 5" eventualmente se tornaria {'5', 'mais', '5'}.
        # Variáveis também são identificadas e substituídas.
        # Ex: A expressão ""Meu nome é " nome", supondo que "nome" seja uma variável de valor "Carlos", ficaria armazenada como {'"Meu nome é "', 'Carlos'}.
        elementos = self.identificar_elementos(expressao=expressao)
        # Identifica os operadores e aplica os cálculos.
        elementos = self.calcular(elementos=elementos)
            
        # Terceira etapa: tipagem e finalização. Nesse ponto, se a expressão não retornar uma lista com um único elemento, será tratada como uma string. 
        # Também será tratada como string se tiver um único elemento envolto em aspas.
        # Só converte ponto para vírgula se for para exibição na tela

        if len(elementos) > 1 or elementos[0][0] == "\"":
            elementos = "\"" + ''.join(elementos).replace("\"",'') + "\""
            return elementos
        else:
            i = elementos[0].find('.')              
            if i != -1 and elementos[0][i + 1] == 0:
                return elementos[0][0:i]
            else:
                return elementos[0]

    # Função análoga ao print
    def escrever(self, texto):
            if texto.strip() != '':
                texto = self.processar_expressao(texto)
                # O Monarca guarda valores de strings com aspas. Para imprimir, removem-se estas aspas.
                if texto.startswith("\"") and texto.endswith("\""):
                    texto = texto[1:-1]
                
                # Substitui \n por uma quebra de linha
                texto = texto.replace('\\n', '\n')
                
                linhas_processadas = []
                # Divide o texto em linhas
                for linha in texto.split('\n'):
                    palavras_processadas = []
                    for palavra in linha.split(' '):
                        palavra_sem_pontuacao = palavra.rstrip('.,!?;:')
                        pontuacao = palavra[len(palavra_sem_pontuacao):]
                        
                        if palavra_sem_pontuacao.replace('.', '').isnumeric():
                            palavras_processadas.append(palavra_sem_pontuacao.replace('.', ',') + pontuacao)
                        else:
                            palavras_processadas.append(palavra)
                    linhas_processadas.append(' '.join(palavras_processadas))
                
                print('\n'.join(linhas_processadas))
            else:
                self.erro("Nenhum valor indicado para impressão na tela.")

    # Função para inicializar ou deletar variáveis
    def variavel(self, operacao='', nome='', var=None):
        if operacao == 'add':
            self.variaveis.update({nome : var})
        elif operacao == 'input':
            if var is None:
                var = input()
            else:
                var = input(f"{var}: ")
            self.variaveis.update({nome : var})
        elif operacao == 'del':
            if nome in self.variaveis.keys():
                self.variaveis.pop(nome)
            else:
                self.erro(f'Variável \033[1m\033[3m"{nome}"\033[0m não existente.')
