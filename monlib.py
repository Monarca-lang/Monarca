class Monarca:
    def __init__(self, linha=0):
        self.linha = linha
        self.variaveis = {}
        self.palavras_reservadas = (
            'mostrar',
            'variável',
            'clonar',
            'deletar',
            'se'
        )
        self.operações = (
            'mais',
            'menos',
            'vezes',
            'dividindo'
        )
        #eu juro que eu vou incorporar isso de maneira mais clean no resto do código depois
        self.opcondicionais = {
            'mais': '+',
            'menos': '-',
            'vezes': '*',
            'dividindo': '/'
        }

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
                    for palavra in trecho.split(): # Leitura do trecho. Checa e substitui as variáveis, checa a validade dos números, etc
                        if palavra in self.variaveis.keys():
                            palavra = self.variaveis[palavra]
                        elif palavra.replace(',','').isnumeric() and palavra.count(",") <= 1: # Se o trecho for apenas números e vírgula e, havendo vírgula, houver apenas uma.                 
                            palavra = palavra.replace(",",".")  # Converte vírgula para ponto para poder ser lido nas operações.
                        elif not palavra in self.operações: # Se não for variável nem número, e também não for nenhuma operação, dá erro.
                            self.erro(f'Não é possível resolver "{''.join(trecho)}".')
                        elementos.append(palavra)
        return elementos
    
    def operacoes(self, elementos):
        i = 0
        try:      
            while 'vezes' in elementos or 'dividindo' in elementos:                                      
                if elementos[i] == 'vezes' or elementos[i] == 'dividindo':
                    num1 = elementos[i - 1]
                    num2 = elementos[i + 1]
                    match elementos[i]:
                        case 'vezes':                        
                            resultado = float(num1) * float(num2)
                        case 'dividindo':
                            resultado = float(num1) / float(num2)
                    elementos[i+1] = str(resultado)                   
                    elementos.pop(i - 1)                    
                    elementos.pop(i - 1)                                        
                else:
                    i += 1 
            i = 0
            while 'mais' in elementos or 'menos' in elementos:                                      
                if elementos[i] == 'mais' or elementos[i] == 'menos':
                    num1 = elementos[i - 1]
                    num2 = elementos[i + 1]
                    match elementos[i]:
                        case 'mais':                        
                            resultado = float(num1) + float(num2)
                        case 'menos':
                            resultado = float(num1) - float(num2)                    
                    elementos[i+1] = str(resultado)                 
                    elementos.pop(i - 1)                    
                    elementos.pop(i - 1)                                        
                else:
                    i += 1
            return elementos
        except Exception:
            self.erro(f'Não é possível resolver "{''.join(elementos)}".')

    def processar_expressao(self, expressao):
        # A função identificar_elementos divide a expressão em uma lista cujos elementos são separados levando em contas strings, números, operações, variáveis etc.
        # Por exemplo, uma expressão "5 mais 5" eventualmente se tornaria {'5', 'mais', '5'}.
        # Variáveis também são identificadas e substituídas.
        # Ex: A expressão ""Meu nome é " nome", supondo que "nome" seja uma variável de valor "Carlos", ficaria armazenada como {'"Meu nome é "', 'Carlos'}.
        elementos = self.identificar_elementos(expressao=expressao)
        # Identifica os operadores e aplica os cálculos.
        elementos = self.operacoes(elementos=elementos)
            
        # Terceira etapa: tipagem e finalização. Nesse ponto, se a expressão não retornar uma lista com um único elemento, será tratada como uma string. 
        # Também será tratada como string se tiver um único elemento envolto em aspas.
        # Converte ponto para vírgula
        for i, palavra in enumerate(elementos):                
            if palavra.replace('.','').isnumeric():
                elementos[i] = elementos[i].replace(".",",")

        if len(elementos) > 1 or elementos[0][0] == "\"":
            elementos = "\"" + ''.join(elementos).replace("\"",'') + "\""
            return elementos
        else:
            i = elementos[0].find(".")              
            if i != -1 and elementos[0][i + 1] == 0:
                return elementos[0][0:i]
            else:
                return elementos[0]           

    # Função usada pelo interpretador para entender automaticamente de que tipo são os dados escritos no código do usuário
    def tipo_de_dado(self, dado=''):
        # Verifica se é um inteiro
        if dado.isnumeric():
            return 'inteiro'
        # Verifica se é um número real.
        # Primeiro, se tiver um "." no dado, separa os dois lados do . em uma lista e verifica se ambos os lados são numéricos e não possuem nenhum caractere além de números.
        # Desta forma, se o dado for "12.5" ele se tornará "[12, 5]" para facilitar a verificação, afim de evitar erros como tentar converter "abc.6" em um número real, o que seria absolutamente incorreto.
        elif '.' in dado and (dado.split('.')[0].isnumeric() and dado.split('.')[1].isnumeric()):
            return 'real'
        # Aqui ficará a verificação que determinará se é uma expressão de lógica booleana: em desenvolvimento
        # Caso o dado não seja de nenhum dos tipos anteriores, o interpretador o assume como texto
        else:
            return 'texto' 

    # Função análoga ao print
    def escrever(self, texto):
        if texto.strip() != '':
            texto = self.processar_expressao(texto)
            texto = texto[1:len(texto)-1] if texto[0] == "\"" else texto # O Monarca guarda valores de strings com aspas. Para imprimir, removem-se estas aspas.
            print(texto)
        else:
            self.erro("Nenhum valor indicado para impressão na tela.")    

    # Função para inicializar ou deletar variáveis
    def variavel(self, operacao='', nome='', var=None):
        if operacao == 'add':
            self.variaveis.update({nome : var})
        elif operacao == 'del':
            if nome in self.variaveis.keys():
                self.variaveis.pop(nome)
            else:
                self.erro(f'Variável \033[1m\033[3m"{nome}"\033[0m não existente.')

    # função para clonar o valor e o tipo de uma variável para a outra
    def clonar_valor(self, var1, var2):
        if var1 in self.variaveis.keys() and var2 in self.variaveis.keys():
            self.variaveis[var2] = self.variaveis[var1]
            self.vartipos[var2] = self.vartipos[var1]

    # funções condicionais, extremamente WIP
    # só retorna se o resultado da condição é verdadeira ou não e só funciona com equações de valores numéricos declarados na hora,
    # mas eventualmente vai ficar fully fledged
    def condicional_se(self, condições):
        # pega as condições "brutas" e trata elas
        condições = [x.strip('",') for x in condições]
        # faz o resto dos b.o
        expressão = []
        indice = 0
        while indice != len(condições):
            elemento = condições[indice]
            if elemento.isnumeric():
                expressão.append(elemento)
            else:
                if elemento in self.opcondicionais:
                    expressão.append(self.opcondicionais[elemento])
                elif elemento == "igual":
                    expressão.append("==")
                    indice += 1
            indice += 1
        return eval(''.join(expressão))  






#  # Função de operações aritméticas. Analisa primeiramente os operadores de multiplicação e divisão, depois os de adição e subtração.
#     def aritmetica(self, expressao):
#         total = 0
        
#         # Continua rodando até que todos os operadores de multiplicação e divisão tenham sido substituídos pelos resultados numéricos de suas operações, para que só então as outras operações possam ser executadas.
#         while 'vezes' in expressao or 'dividindo' in expressao:
#             try:
#                 if 'vezes' in expressao:
#                     n1 = expressao[expressao.index('vezes') - 1]
#                     n2 = expressao[expressao.index('vezes') + 1]
#                     resultado = float(n1)*float(n2)
#                     # Substitui a operação pelo resultado.
#                     expressao[expressao.index('vezes')+1] = resultado
#                     expressao.pop(expressao.index('vezes'))
#                     expressao.pop(expressao.index(n1))
#                     total = resultado
#                 elif 'dividindo' in expressao:
#                     n1 = expressao[expressao.index('dividindo') - 1]
#                     n2 = expressao[expressao.index('dividindo') + 1]
#                     resultado = float(n1)/float(n2)
#                     # Substitui a operação pelo resultado
#                     expressao[expressao.index('dividindo')+1] = resultado
#                     expressao.pop(expressao.index('dividindo'))
#                     expressao.pop(expressao.index(n1))
#                     total = resultado
    
#             except Exception:
#                 self.erro(f'Expressão aritmética mal formulada.')

#         try:
#             for c in range(0, len(expressao)):
#                 if expressao[c] == 'mais':
#                     if c == 1:
#                         total = float(expressao[c-1]) + float(expressao[c+1])
#                         c += 1
#                     else:
#                         total += float(expressao[c+1])

#                 elif expressao[c] == 'menos':
#                     if c == 1: 
#                         total = float(expressao[c-1]) - float(expressao[c+1])
#                         c += 1
#                     else:
#                         total -= float(expressao[c+1])
                                        
#             return total

#         except Exception:
#             self.erro(f'Expressão aritmética mal formulada.')