# Sintaxe Base

## Variáveis
### Inicializar
Para inicializar uma variável, basta seguir a seguinte sintaxe, inserindo (de acordo com a necessidade) o nome da mesma e seu valor:

```pseudocode
variável [nome da variável] recebe [dado]
```

Perceba que não é necessário declarar seu tipo primitivo, apenas seu nome e seu valor. Em uma aplicação real, esta sintaxe se pareceria com o seguinte exemplo:

```pseudocode
variável idade recebe 30
variável nome recebe "Monteiro"
variável altura recebe 1,60
variável gosta_de_paçoca? recebe Verdadeiro
```

Nomes de variáveis não podem ter espaços, embora possam conter caracteres especiais.
### Deletar
Para deletar uma variável já criada, basta seguir a sintaxe:
```pseudocode
deletar variável [nome da variável]
```
Se a variável realmente existir, ela será deletada instantâneamente e seu espaço na memória será liberado, dando ao usuário da linguagem uma autonomia parcial sobre o consumo de memória de seus programas.

## Tipos Primitivos de Dados

Os tipos primitivos de dados presentes na linguagem Monarca podem ser listados em:

* **Inteiro**: Representa qualquer número no conjunto dos números inteiros. Passível de sofrer operações aritméticas.

* **Real**: Representa qualquer número no conjunto dos números reais. Passível de sofrer operações aritméticas.

* **Texto**: Representa qualquer caractere visual dentro do padrão UTF-8. Não está passível de sofrer operações aritméticas e precisa estar envolvido por aspas duplas ( "" ).

* **Lógico**: Representa operações lógicas ou seus resultados, que podem ser Verdadeiro ou Falso. Uma declaração lógica é composta por três tipos de informações:

  * **Operadores**: Como exemplos de operadores temos:

    * **igual a**: Utilizado para verificar se dois dados ou variáveis são *exatamente* iguais.
    * **diferente de**: Utilizado para verificar se existe *qualquer mínima* diferença entre dois dados ou variáveis.
    * **menor que**: Utilizado para verificar se um dado numérico é menor que outro.
    * **maior que**: Utilizado para verificar se um dado numérico é maior que outro.

  * **Dados**: Os dados utilizados em declarações lógicas podem ser de qualquer um dos tipos listados acima (*inteiro*, *real*, *texto*, ou até mesmo *lógico*).

  * **Sintaxe**: A sintaxe de uma declaração lógica é estruturada da seguinte forma:

    ```pseudocode
    [dado] é [operador] [dado]
    ```

    Por exemplo:

    ```pseudocode
    "a" é igual a "b"         - falso
    5 é menor que 2           - falso
    1,7 é diferente de "casa" - verdadeiro
    ```

    Operações lógicas também podem ser feitas entre operações matemáticas, comparando seus resultados:
    
    ```pseudocode
    5 vezes 2 é igual a 10         - verdadeiro
    8 menos 3 vezes 2 é igual a 10 - falso
    ```
    
    


# Funções Básicas

## mostrar na tela:

A função "***mostrar na tela:***"  só possui como parâmetro o conteúdo a ser exibido na tela. Este deve estar a 1 caractere de espaço (" ") de distância após o caractere de dois pontos ( : ) e precisa estar envolvido por aspas duplas ( "" ). Exemplo:

```pseudocode
mostrar na tela: "Olá Mundo em Monarca!"

::info Saída:
::info Olá Mundo em Monarca!
```

Esta função também pode ser usada referenciando-se uma variável no campo dos dados:

```pseudocode
variável nome recebe "Maria"
mostrar na tela: nome

::info Saída:
::info Maria
```

Além disto, é possível exibir texto direto e conteúdo de variável ao mesmo tempo:

```pseudocode
variável meu_nome recebe "Paulo"
mostrar na tela: "Olá, meu nome é " meu_nome "!"

::info Saída:
::info Olá, meu nome é Paulo!
```

# Operadores Aritméticos

No Monarca existem basicamente 4 operadores aritméticos:

* **mais**: Operador de adição.
* **menos**: Operador de subtração.
* **vezes**: Operador de multiplicação.
* **dividido por**: Operador de divisão.

A utilização destes operadores foi desenhada para a mais intuitiva possível. Por exemplo:

```pseudocode
variável idade recebe 20 menos 10 vezes 5
mostrar na tela: "Minha idade é " idade

::info Saída
::info Minha idade é 15
```

Desta forma, é possível encadear diversas operações uma após a outra, de modo que sejam executadas pela ordem aritmética comum/correta.

# Estruturas Condicionais
## Se 
A estrutura `se` pode ser utilizada para iniciar um bloco de comandos a serem executados caso uma certa declaração lógica (booleana) seja interpretada como verdadeira. 

Exemplo:

```pseudocode
se "a" é igual "b" então:
    mostrar na tela: "a é igual a b"
```
## Se/Senão
A estrutura `se/senão` diferentemente da estrutura `se`, fornece um bloco alternativo caso uma certa declaração lógica (booleana) não seja intpratada como verdadeira.

Exemplo:

```pseudocode
se "a" é igual "b" então:
    mostrar na tela: "a é igual a b"
senão então:
    mostrar na tela: "a é diferente de b"
```
# Estruturas de Repetição
## Enquanto
A estrutura `enquanto` repete um conjunto de comandos até que uma declaração lógica (booleana) assuma um certo valor.

Exemplo:

```pseudocode
enquanto n é menor que 10 então:
    mostrar na tela: n
    variável n recebe n mais 1
```
## Para

# Questionamentos Previstos:
A estrutura `para` repete um conjunto de comandos utilizando um contador e um ponto de parada.

Exemplo:

```pseudocode
para contando até 3:
    mostrar na tela: "Esta é uma mensagem dentro de um laço!"
```

* > ***Como posso comentar meu código?***

    Você deve ter percebido que, ao longo desse documento, as saídas de comandos foram precedidas por "::info". Essa sintaxe, ao ser reconhecida pelo interpretador, faz com que a linha onde ela aparece não seja alvo de checagens de comandos, tendo a mesma funcionalidade que comentários em outras linguagens de programação.
    Exemplo:
  ```pseudocode
  mostrar na tela: "Hoje eu fui no parque"
  ::info mostrar na tela: tomei um sorvete
  mostrar na tela: "e depois voltei pra casa"
  
  ::info Saída:
  ::info Hoje eu fui no parque
  ::info e depois voltei pra casa

