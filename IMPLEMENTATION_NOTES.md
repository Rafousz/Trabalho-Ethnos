# Implementação: Nomes Únicos para Salas

## Resumo
Implementada validação de nomes únicos para salas. Agora não é possível criar duas salas com o mesmo nome.

## Mudanças Realizadas

### 1. Backend (app.py)
**Arquivo**: `app.py` (linhas 52-76)
**Handler**: `@socketio.on('create_room')`

#### Antes:
```python
if room in games:
    # Se sala existe, apenas entra nela (funciona como join_room)
    game = games[room]
    success, updated_hands = game.add_player(request.sid, name)
    ...
else:
    # Cria nova sala
    games[room] = EthnosGame(room)
    ...
```

#### Depois:
```python
if room in games:
    # Se sala existe, retorna erro
    emit('error', {'msg': 'Sala já existe!'})
    return
else:
    # Cria nova sala
    games[room] = EthnosGame(room)
    ...
```

### 2. Comportamento do Sistema

#### Fluxo de Criação de Sala

| Cenário | Antes | Depois |
|---------|-------|--------|
| Jogador1 cria "sala1" | ✓ Cria e entra | ✓ Cria e entra |
| Jogador2 cria "sala1" | ✓ Entra na sala de Jogador1 | ✗ Erro: "Sala já existe!" |
| Jogador2 entra em "sala1" (via lista) | ✓ Entra na sala de Jogador1 | ✓ Entra na sala de Jogador1 |

#### Entrar em Sala (join_room)
- **Sem mudanças**: Continua funcionando normalmente
- Valida se sala existe
- Verifica limite de jogadores
- Rejeita se jogo já terminou

### 3. Tratamento de Erros

#### Frontend
- Handler `socket.on("error")` (linha 409 de jogo.js)
- Exibe mensagem via `alert(data.msg)`
- Usuário permanece na tela de login

#### Backend
- Mensagem: `'Sala já existe!'`
- Event emitido: `'error'`
- Função retorna sem criar sala

### 4. Testes

#### Teste Criado: `test_unique_rooms.py`
Valida os cenários:
1. ✓ Primeira criação de "sala1" - SUCESSO
2. ✓ Segunda tentativa de criar "sala1" - REJEITADA
3. ✓ Criação de "sala2" diferente - SUCESSO

**Resultado**: Todos os testes passaram

```
[OK] Criação 1 de 'sala1': SUCESSO
[OK] Criação 2 de 'sala1': REJEITADA
[OK] Criação de 'sala2': SUCESSO
[OK] TODOS OS TESTES PASSARAM!
```

## Impacto

### ✅ Vantagens
- Identificação única e simplificada de salas
- Sem conflitos de nomes
- Comportamento previsível para usuários
- Menos complexidade no código

### ⚠️ Considerações
- Usuários podem ficar frustrados se nome já existe
  - **Sugestão futura**: Oferecer sugestão de nomes alternativos (ex: "sala1_2")
  - **Sugestão futura**: Mostrar qual jogador criou cada sala

### 🔮 Melhorias Futuras (Fora do escopo)
- Limpeza automática de salas vazias/inativas
- Persistência em database (atualmente tudo é memória)
- Permitir deletar salas vazias
- Validar nome da sala (comprimento, caracteres especiais)

## Arquivos Modificados
- `app.py` - Handler create_room invertido
- `test_unique_rooms.py` - Novo arquivo de teste

## Arquivos Não Afetados
- `jogo.js` - Frontend continua igual
- `index.html` - Interface HTML sem mudanças
- `engine.py` - Lógica do jogo sem mudanças
- `jogador.py` - Classes de jogador sem mudanças

## Como Testar

### Teste Unitário
```bash
python test_unique_rooms.py
```

### Teste Manual (via Interface)
1. Abrir navegador em `http://localhost:5000`
2. **Teste 1 - Criar nova sala**:
   - Nome: "João"
   - Sala: "sala_teste"
   - Resultado: Deve entrar normalmente
3. **Teste 2 - Tentar criar sala duplicada**:
   - Em outra aba/navegador
   - Nome: "Maria"
   - Sala: "sala_teste"
   - Resultado: Deve aparecer `alert("Sala já existe!")`
4. **Teste 3 - Entrar em sala existente**:
   - Na lista de salas, clicar "Entrar" em "sala_teste"
   - Resultado: Deve entrar normalmente

