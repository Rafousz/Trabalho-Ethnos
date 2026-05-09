# Trabalho Gerência de projetos e Manutenção de Software

**Escopo do produto:**

**Nome:** Reino em ascensão

**Descrição:** Jogo de tabuleiro estratégico para 2 a 6 jogadores, onde cada jogador assume o papel de líder de uma facção (magos, guerreiros, mercadores, etc.) que disputa o controle de territórios ao longo de três eras. O jogo combina estratégia de cartas e domínio de regiões do mapa.

**Objetivo:** Controlar o maior número de territórios ao final das 3 eras, acumulando pontos através de domínio territorial e uso estratégico das facções.

**Mecânicas principais:**

1. **Combinação de cartas**  
   1. Jogadores formam grupos de cartas da mesma facção OU mesma cor  
   2. Quanto maior o grupo,  mais forte a jogada  
   3. A carta do topo defini o poder da e facção  
   4. A quantidade de cartas, influência na pontuação

2. **Controle de territórios**  
   1. O tabuleiro é dividido em regiões  
   2. Cada região pode ser dominada por quem tiver mais tokens  
   3. Cada região tem pontuação diferente  
   4. Para colocar um token numa região é necessário baixar um número de cartas maior do que a quantidade de tokens na região.

3. **Sistema de eras**  
   1. Era 1 → início  
   2. Era 2 → meio  
   3. Era 3 → final  
   4. Ao final de cada era, gera uma pontuação parcial

4. **Habilidades por facção**

| Facção | Habilidade |
| :---- | :---- |
| Magos | Jogar cartas extras |
| Guerreiros | Dominar territórios com menos cartas |
| Mercadores | Ganhar pontos extras |
| Assassinos | Remover token adversário |
| Nobres | Bônus no final da era |

**Componentes**

* Tabuleiro com regiões conectadas  
* Cartas de facções  
* Tokens (marcadores de território)  
* Contadores de pontos

**Regras principais**:

* Sua vez:  
  * O jogador deve escolher uma ação:   
    * Comprar uma carta   
    * Jogar cartas para colocar tokens

* Ao jogar cartas:  
  * Deve jogar cartas da mesma cor OU facção  
  * Coloca tokens em territórios  
  * Ativa habilidade da facção dependendo do líder da sua facção

* Colocar Tokens:  
  * Para colocar tokens em territórios deverá baixar número de cartas maior que o número de tokens no território


* Pontuação:  
  * Ao final de cada era, o jogador que controlar mais territórios em cada região ganha pontos

* Após 3 eras:  
  * Soma total de pontos  
  * Quem tiver mais pontos, vence o jogo

**Escopo do projeto:**   
Trabalho que deve ser feito para construir o produto. Poderia usar EAP para fazer o escopo do projeto.

- Deve existir sistema de pontuação por território  
- Deve haver divisão em 3 eras  
- Cada facção deve possuir habilidades únicas  
- O jogador deve poder comprar ou jogar cartas por turno
