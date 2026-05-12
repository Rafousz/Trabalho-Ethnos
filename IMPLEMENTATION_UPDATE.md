# Implementação: Mudança de Tela Condicional

## Resumo
Implementado sistema de mudança de tela condicional que aguarda confirmação do backend antes de entrar na tela de jogo.

## Mudanças Realizadas

### Arquivo: `static/js/jogo.js`

#### 1. Função `createRoom()` (linhas 29-38)
**Mudança**: Removidas 2 linhas que mudavam a tela imediatamente

```javascript
// ANTES
function createRoom() {
  const name = document.getElementById("username").value
  currentRoom = document.getElementById("room").value

  if (name && currentRoom) {
    socket.emit("create_room", { name: name, room: currentRoom })
    document.getElementById("login-screen").style.display = "none"  // ← REMOVIDO
    document.getElementById("game-screen").style.display = "block"  // ← REMOVIDO
  } else {
    alert("Preencha nome e sala.")
  }
}

// DEPOIS
function createRoom() {
  const name = document.getElementById("username").value
  currentRoom = document.getElementById("room").value

  if (name && currentRoom) {
    socket.emit("create_room", { name: name, room: currentRoom })
  } else {
    alert("Preencha nome e sala.")
  }
}
```

#### 2. Função `joinExistingRoom()` (linhas 40-50)
**Mudança**: Removidas 2 linhas que mudavam a tela imediatamente

```javascript
// ANTES
function joinExistingRoom(roomName) {
  const name = document.getElementById("username").value
  
  if (!name) {
    alert("Preencha seu nome.")
    return
  }
  
  currentRoom = roomName
  socket.emit("join_room", { name: name, room: roomName })
  document.getElementById("login-screen").style.display = "none"  // ← REMOVIDO
  document.getElementById("game-screen").style.display = "block"  // ← REMOVIDO
}

// DEPOIS
function joinExistingRoom(roomName) {
  const name = document.getElementById("username").value
  
  if (!name) {
    alert("Preencha seu nome.")
    return
  }
  
  currentRoom = roomName
  socket.emit("join_room", { name: name, room: roomName })
}
```

#### 3. Handler `socket.on("game_update")` (linha 287)
**Mudança**: Adicionadas 5 linhas no início do handler

```javascript
// ANTES
socket.on("game_update", (state) => {
  if (state.game_over) {
    // ... resto do código
  }
})

// DEPOIS
socket.on("game_update", (state) => {
  // Muda de tela quando jogo é confirmado (primeira conexão bem-sucedida)
  if (document.getElementById("login-screen").style.display !== "none") {
    document.getElementById("login-screen").style.display = "none"
    document.getElementById("game-screen").style.display = "block"
  }
  
  if (state.game_over) {
    // ... resto do código
  }
})
```

## Fluxo Resultante

### Cenário 1: Criar Sala com Sucesso

```
1. Usuário clica "Criar"
   └─ createRoom() emite create_room
      └─ NÃO muda tela

2. Backend valida e cria sala
   └─ Emite game_update

3. Frontend recebe game_update
   └─ socket.on("game_update") 
      ├─ Muda tela (login → game)
      └─ Renderiza jogo
```

### Cenário 2: Criar Sala com Erro (Duplicada)

```
1. Usuário clica "Criar"
   └─ createRoom() emite create_room
      └─ NÃO muda tela

2. Backend valida e rejeita (sala existe)
   └─ Emite error

3. Frontend recebe error
   └─ socket.on("error")
      ├─ alert("Sala já existe!")
      └─ Permanece em login-screen
```

### Cenário 3: Entrar em Sala com Sucesso

```
1. Usuário clica "Entrar"
   └─ joinExistingRoom() emite join_room
      └─ NÃO muda tela

2. Backend valida e adiciona jogador
   └─ Emite game_update

3. Frontend recebe game_update
   └─ socket.on("game_update")
      ├─ Muda tela (login → game)
      └─ Renderiza jogo
```

### Cenário 4: Entrar em Sala com Erro (Cheia)

```
1. Usuário clica "Entrar"
   └─ joinExistingRoom() emite join_room
      └─ NÃO muda tela

2. Backend valida e rejeita (sala cheia)
   └─ Emite error

3. Frontend recebe error
   └─ socket.on("error")
      ├─ alert("Sala cheia!")
      └─ Permanece em login-screen
```

## Comparação: Antes vs Depois

| Cenário | Antes | Depois |
|---------|-------|--------|
| Criar sala com sucesso | Entra em jogo ✓ | Entra em jogo ✓ |
| Criar sala duplicada | Entra em jogo vazio ✗ | Fica em login + erro ✓ |
| Entrar em sala com sucesso | Entra em jogo ✓ | Entra em jogo ✓ |
| Entrar em sala cheia | Entra em jogo vazio ✗ | Fica em login + erro ✓ |
| Entrar em sala com jogo terminado | Entra em jogo vazio ✗ | Fica em login + erro ✓ |

## Estatísticas de Mudanças

- **Arquivo único modificado**: `static/js/jogo.js`
- **Linhas removidas**: 4
- **Linhas adicionadas**: 5
- **Mudança líquida**: +1 linha (comentário descritivo)
- **Complexidade**: Muito simples - apenas sincronização com backend

## Como Testar

### Teste 1: Criar Sala Duplicada
```
1. Abrir http://localhost:5000
2. Nome: "Jogador1", Sala: "sala_teste" → Clique em "Criar Sala"
   Resultado: Entra na tela de jogo ✓

3. Abrir outra aba (mesmo servidor)
4. Nome: "Jogador2", Sala: "sala_teste" → Clique em "Criar Sala"
   Resultado esperado:
   - alert("Sala já existe!") ✓
   - Permanece em login-screen ✓
   - NÃO entra em jogo vazio ✓
```

### Teste 2: Entrar em Sala Existente
```
1. Primeira aba (de teste 1): Já na tela de jogo
2. Segunda aba: Clique em botão "Entrar" de "sala_teste"
   Resultado esperado:
   - Entra na tela de jogo ✓
   - Sincroniza com primeira aba ✓
```

### Teste 3: Entrar em Sala Cheia
```
1. Criar sala com 6 jogadores (limite máximo)
2. Tentar entrar com 7º jogador
   Resultado esperado:
   - alert("Sala cheia!") ✓
   - Permanece em login-screen ✓
```

## Implicações

### ✅ Vantagens
- Usuário sempre fica no login-screen até confirmação do backend
- Garante sincronização entre frontend e backend
- Nenhum jogo vazio ou quebrado
- Mesma lógica para criar e entrar (coerência)

### 🔄 Comportamento
- `game_update` é sempre enviado pelo backend após sucesso
- `error` é sempre enviado para qualquer falha
- Frontend aguarda um desses dois eventos

### 🎯 Casos de Uso Cobertos
- ✓ Sala já existe (create)
- ✓ Sala cheia (join)
- ✓ Jogo já terminou (join)
- ✓ Nome inválido (ambos)
- ✓ Jogador já na sala (ambos)

## Backend (SEM MUDANÇAS)

O backend (`app.py`) continua igual:
- Handler `create_room` emite `'error'` se sala existe ✓
- Handler `create_room` emite `'game_update'` se sucesso ✓
- Handler `join_room` emite `'error'` se falha ✓
- Handler `join_room` emite `'game_update'` se sucesso ✓

