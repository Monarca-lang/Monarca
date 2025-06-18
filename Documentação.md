# Sintaxe Base

## Tipos Primitivos de Dados

Os tipos primitivos de dados presentes na linguagem Monarca podem ser listados em:

* **Inteiro**: Representa qualquer número no conjunto dos números inteiros. Passível de sofrer operações aritméticas.
* **Real**: Representa qualquer número no conjunto dos números reais. Passível de sofrer operações aritméticas.
* **Texto**: Representa qualquer caractere visual dentro do padrão UTF-8. Não está passível de sofrer operações aritméticas e precisa estar envolvido por aspas duplas ( "" ).
* **Lógico**: Representa operações lógicas ou seus resultados, que podem ser Verdadeiro ou Falso.

## Variáveis
### Inicializar
Para inicializar uma variável, basta seguir a seguinte sintaxe, inserindo (de acordo com a necessidade) o nome da mesma e seu valor:

```
variável [nome da variável] recebe [dado]
```

Perceba que não é necessário declarar seu tipo primitivo, apenas seu nome e seu valor. Em uma aplicação real, esta sintaxe se pareceria com o seguinte exemplo:

```
variável idade recebe 30
variável nome recebe "Monteiro"
variável altura recebe 1,60
variável gosta_de_paçoca? recebe Verdadeiro
```

Nomes de variáveis não podem ter espaços, embora possam conter caracteres especiais.
### Deletar
Para deletar uma variável já criada, basta seguir a sintaxe:
```
deletar variável [nome da variável]
```
Se a variável realmente existir, ela será deletada instantâneamente e seu espaço na memória será liberado, dando ao usuário da linguagem uma autonomia parcial sobre o consumo de memória de seus programas.
### Clonar
Para clonar o valor e o tipo de uma variável já criada para outra variável, basta adicionar:
```
clonar variável [nome da variável a ser clonada] para [nome da variável alvo] 
```
Caso a variável a ser clonada exista na memória, todos os seus dados - com exceção do nome - serão clonados para a variável alvo.

Este comando não checa se a variável alvo existe na memória.
# Funções Básicas

## mostrar na tela:

A função "***mostrar na tela:***"  só possui como parâmetro o conteúdo a ser exibido na tela. Este deve estar a 1 caractere de espaço (" ") de distância após o caractere de dois pontos ( : ) e precisa estar envolvido por aspas duplas ( "" ). Exemplo:

```
mostrar na tela: "Olá Mundo em Monarca!"

::info Saída:
::info Olá Mundo em Monarca!
```

Esta função também pode ser usada referenciando-se uma variável no campo dos dados:

```
variável nome recebe "Maria"
mostrar na tela: nome

::info Saída:
::info Maria
```

Além disto, é possível exibir texto direto e conteúdo de variável ao mesmo tempo:

```
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
* **dividindo**: Operador de divisão.

A utilização destes operadores foi desenhada para a mais intuitiva possível. Por exemplo:

```
variável idade recebe inteiro 20 menos 10 mais 5
mostrar na tela: Minha idade é \idade

::info Saída
::info Minha idade é 15
```

Desta forma, é possível encadear diversas operações uma após a outra, de modo que sejam executadas pela ordem aritmética comum/correta.

# Questionamentos Previstos:


* > ***Como posso comentar meu código?***

    Você deve ter percebido que, ao longo desse documento, as saídas de comandos foram precedidas por "::info". Essa sintaxe, ao ser reconhecida pelo interpretador, faz com que a linha onde ela aparece não seja alvo de checagens de comandos, tendo a mesma funcionalidade que comentários em outras linguagens de programação.
    Exemplo:
  ```
  mostrar na tela: Hoje eu fui no parque
  ::info mostrar na tela: tomei um sorvete
  mostrar na tela: e depois voltei pra casa

  ::info Saída:
  ::info Hoje eu fui no parque
  ::info e depois voltei pra casa  ```


