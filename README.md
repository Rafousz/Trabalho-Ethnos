# Trabalho-Ethnos

Um jogo de tabuleiro estratégico multiplayer para 2 a 6 jogadores, onde cada jogador assume o papel de líder de uma facção que disputa o controle de territórios ao longo de três eras.
---
 
## Objetivo do Jogo
 
Controlar o maior número de territórios ao final das 3 eras, acumulando pontos através de domínio territorial e uso estratégico das facções.
---
 
## Mecânicas Principais
 
### 1. **Combinação de Cartas**
- Forme grupos de cartas da mesma facção **OU** mesma cor
- Quanto maior o grupo, mais forte a jogada
- A carta do topo define o poder da facção
- A quantidade de cartas influencia na pontuação

### 2. **Controle de Territórios**
- O tabuleiro é dividido em 6 regiões (reinos)
- Cada região pode ser dominada por quem tiver mais tokens
- Cada região tem pontuação diferente
- Para colocar um token numa região é necessário baixar um número de cartas maior que a quantidade de tokens na região

### 3. **Sistema de Eras**
- **Era 1** → Início
- **Era 2** → Meio
- **Era 3** → Final
- Ao final de cada era, gera uma pontuação parcial

### 4. **Habilidades por Facção**
 
| Facção | Habilidade |
|--------|-----------|
| ⚔️ Guerreiros | Dominam territórios independente do líder |
| 🔮 Magos | Compram cartas extra após jogar um bando |
| 💎 Anões | Ganham pontos extras pelo tamanho do bando |
| 🗡️ Orcs | Reduzem cartas necessárias (igual ao número de tokens) |
| 👿 Trolls | Desempatam regiões em caso de igualdade |
| 🌳 Elfos | Mantêm cartas equivalentes ao tamanho do bando |
 
---
 
## Como Executar

### 1️⃣ Abrir PowerShell na pasta do projeto
> Navegue até a pasta do projeto
```powershell
cd A:\Documentos\trabalho_GPMS\Trabalho-Ethnos
```

### 2️⃣ Deletar o venv antigo (se existir)
```powershell
rmdir /s venv
```

### 3️⃣ Criar novo ambiente virtual com Python 3.12
```powershell
python -m venv venv
```

### 4️⃣ Ativar o ambiente virtual
```powershell
venv\Scripts\activate
```
Você deve ver `(venv)` no início da linha no PowerShell.

### 5️⃣ Atualizar pip
```powershell
python -m pip install --upgrade pip
```

### 6️⃣ Instalar as dependências
```powershell
pip install -r requirements.txt
```

**Esperado:** Todas as dependências devem instalar sem erros.

### 7️⃣ Rodar a aplicação
```powershell
python app.py
```

**Esperado:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

---

## 🌐 Acessar o jogo

Abra seu navegador em: **http://localhost:5000**

1. Digite seu nome
2. Digite o nome da sala
3. Clique em "Entrar na Partida"
4. Jogue! 🎮

---
