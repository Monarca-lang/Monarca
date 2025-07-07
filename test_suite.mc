::info Arquivo de Testes Abrangente para a Linguagem Monarca

mostrar na tela: "--- INÍCIO DA SUÍTE DE TESTES MONARCA ---"
mostrar na tela: ""

::info ===================================================
mostrar na tela: "--- 1. Testes de Variáveis e 'mostrar na tela' ---"
::info ===================================================

variável str_simples recebe "Olá, testador!"
mostrar na tela: "1.1. Variável de string simples: " str_simples

variável num_inteiro recebe 10
variável num_float recebe 25.5
mostrar na tela: "1.2. Variáveis numéricas: " num_inteiro " e " num_float

variável bool_verdadeiro recebe verdadeiro
mostrar na tela: "1.3. Variável booleana: " bool_verdadeiro

variável reatribuida recebe "valor inicial"
variável reatribuida recebe "valor modificado"
mostrar na tela: "1.4. Variável reatribuída: " reatribuida

variável outra_var recebe num_inteiro
mostrar na tela: "1.5. Variável recebendo outra variável (10): " outra_var

variável str_vazia recebe ""
mostrar na tela: "1.6. String vazia: [" str_vazia "]"

variável reatribuida_tipo recebe "texto"
variável reatribuida_tipo recebe 12345
mostrar na tela: "1.7. Reatribuição com tipo diferente (12345): " reatribuida_tipo

mostrar na tela: "1.8. Teste de quebra de linha: Linha 1\nLinha 2"
mostrar na tela: ""

::info ===================================================
mostrar na tela: "--- 2. Testes de Expressões Aritméticas ---"
::info ===================================================

variável soma recebe 5 mais 10.5
mostrar na tela: "2.1. Soma (5 + 10.5): " soma

variável mult_prec recebe 2 mais 3 vezes 4 ::info Deve ser 14, não 20
mostrar na tela: "2.2. Precedência (2 + 3 * 4): " mult_prec

variável div_prec recebe 10 menos 8 dividido por 2 ::info Deve ser 6, não 1
mostrar na tela: "2.3. Precedência (10 - 8 / 2): " div_prec

variável complexa recebe num_inteiro mais num_float vezes 2 ::info 10 + 25.5 * 2 = 61
mostrar na tela: "2.4. Expressão com variáveis (10 + 25.5 * 2): " complexa

variável negativo recebe 5 menos 10
mostrar na tela: "2.5. Resultado negativo (5 - 10): " negativo
mostrar na tela: ""

::info ===================================================
mostrar na tela: "--- 3. Testes de Condicionais (se/senão) e Lógica ---"
::info ===================================================

mostrar na tela: "3.1. Testando 'se' com condição verdadeira:"
se 10 é maior que 5 então:
    mostrar na tela: "  (SUCESSO) Bloco 'se' executado."
senão então:
    mostrar na tela: "  (FALHA) Bloco 'senão' executado."

mostrar na tela: "3.2. Testando 'senão' com condição falsa:"
se "texto" é igual a "outro texto" então:
    mostrar na tela: "  (FALHA) Bloco 'se' executado."
senão então:
    mostrar na tela: "  (SUCESSO) Bloco 'senão' executado."

mostrar na tela: "3.3. Testando 'e'/'ou' (precedência):"
::info A condição (falso ou verdadeiro e verdadeiro) deve ser verdadeira
se 5 é igual a 4 ou 3 é menor que 4 e "A" é igual a "a" então:
    mostrar na tela: "  (SUCESSO) Precedência de 'e' sobre 'ou' funcionou."
senão então:
    mostrar na tela: "  (FALHA) Precedência de 'e' sobre 'ou' falhou."

mostrar na tela: "3.4. Testando condicionais aninhadas:"
variável permissao recebe "sim"
variável idade_teste recebe 18
se permissao é igual a "SIM" então: ::info Teste de case-insensitivity
    mostrar na tela: "  (SUCESSO) Permissão de nível 1 concedida."
    se idade_teste é maior que 17 então:
        mostrar na tela: "  (SUCESSO) Permissão de nível 2 concedida."
    senão então:
        mostrar na tela: "  (FALHA) Bloco 'senão' aninhado executado indevidamente."

mostrar na tela: "3.5. Comparando tipos diferentes (número e string):"
se 10 é igual a "10" então:
    mostrar na tela: "  (SUCESSO) Comparação '10 é igual a \"10\"' funcionou."
senão então:
    mostrar na tela: "  (FALHA) Comparação '10 é igual a \"10\"' falhou."

mostrar na tela: "3.6. Usando número como booleano:"
se 1 então:
    mostrar na tela: "  (SUCESSO) 'se 1' é verdadeiro."
se 0 então:
    mostrar na tela: "  (FALHA) 'se 0' é verdadeiro."
senão então:
    mostrar na tela: "  (SUCESSO) 'se 0' é falso."
mostrar na tela: ""

::info ===================================================
mostrar na tela: "--- 4. Testes de Parênteses ---"
::info ===================================================

variável paren_aritmetico recebe (2 mais 3) vezes 4 ::info Deve ser 20
mostrar na tela: "4.1. Parênteses aritméticos ((2 + 3) * 4): " paren_aritmetico

variável paren_complexo recebe ( (5 mais 5) dividido por 2 ) mais 3
mostrar na tela: "4.2. Parênteses aninhados ((5+5)/2 + 3): " paren_complexo

mostrar na tela: "4.3. Testando parênteses lógicos:"
::info A condição ((falso ou verdadeiro) e falso) deve ser falsa
se (5 é igual a 4 ou 3 é menor que 4) e "a" é igual a "b" então:
    mostrar na tela: "  (FALHA) Parênteses lógicos falharam."
senão então:
    mostrar na tela: "  (SUCESSO) Parênteses lógicos funcionaram."
mostrar na tela: ""

::info ===================================================
mostrar na tela: "--- 5. Testes de Entrada e Deleção ---"
::info ===================================================

variável para_deletar recebe "este valor será apagado"
mostrar na tela: "5.1. Valor antes de deletar: " para_deletar
deletar variável para_deletar
mostrar na tela: "  (SUCESSO) Variável 'para_deletar' foi deletada."

mostrar na tela: "5.2. Teste de entrada (digite seu nome):"
variável nome_usuario recebe entrada:
mostrar na tela: "  (SUCESSO) Olá, " nome_usuario "! O teste de entrada funcionou."
mostrar na tela: ""

::info ===================================================
mostrar na tela: "--- 6. Testes de Erros (Descomente para testar) ---"
::info mostrar na tela: "Os testes abaixo devem gerar erros. Execute um por vez."
::info ===================================================

::info Teste 6.1: Usar variável não declarada
::info mostrar na tela: variavel_inexistente

::info Teste 6.2: Divisão por zero
::info variável div_zero recebe 10 dividido por 0

::info Teste 6.3: Sintaxe incompleta
::info variável x recebe

::info Teste 6.4: 'senão' sem 'se'
::info se falso então:
::info     mostrar na tela: "não vai aparecer"
::info senão então:
::info     se verdadeiro então:
::info         mostrar na tela: "ok"
::info senão então: ::info Este 'senão' está desalinhado e sem um 'se' correspondente
::info     mostrar na tela: "erro aqui"

::info Teste 6.5: Deletar variável inexistente
::info deletar variável var_que_nao_existe

::info Teste 6.6: Parênteses desbalanceados
::info variável erro_paren recebe (5 mais 3

::info Teste 6.7: Erro de indentação
::info se verdadeiro então:
::info   mostrar na tela: "indentação errada"

mostrar na tela: "--- FIM DA SUÍTE DE TESTES MONARCA ---"