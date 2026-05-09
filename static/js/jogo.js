// static/js/game.js
const socket = io()
let currentRoom = ""
let selectedCards = [] // Guarda os índices das cartas selecionadas na mão

function joinGame() {
  const name = document.getElementById("username").value
  currentRoom = document.getElementById("room").value

  if (name && currentRoom) {
    socket.emit("join_game", { name: name, room: currentRoom })
    document.getElementById("login-screen").style.display = "none"
    document.getElementById("game-screen").style.display = "block"
  } else {
    alert("Preencha nome e sala.")
  }
}

function drawCard() {
  socket.emit("action_draw_card", { room: currentRoom })
}

function drawMarketCard(index) {
  socket.emit("action_draw_market", { room: currentRoom, index: index })
}

function playBand() {
  if (selectedCards.length === 0) {
    alert("Selecione pelo menos uma carta para formar um bando!")
    return
  }
  socket.emit("action_play_band", { room: currentRoom, indices: selectedCards })
}

function toggleSelect(index) {
  const idx = selectedCards.indexOf(index)
  const el = document.getElementById(`card-${index}`)
  
  if (idx > -1) {
    // Deselecionar
    selectedCards.splice(idx, 1)
    el.classList.remove("selected")
    el.classList.remove("leader")
  } else {
    // Selecionar
    selectedCards.push(index)
    el.classList.add("selected")
  }
  
  // Atualizar visual do líder (primeira carta selecionada)
  document.querySelectorAll("#my-hand li").forEach((li) => li.classList.remove("leader"))
  if (selectedCards.length > 0) {
    document.getElementById(`card-${selectedCards[0]}`).classList.add("leader")
  }
}

// Atualizações do estado geral do jogo
socket.on("game_update", (state) => {
  document.getElementById("turn-indicator").innerText =
    `Turno de: ${state.current_turn}`

  const eraIndicator = document.getElementById("era-indicator")
  if (eraIndicator) {
    const maxEras = state.max_eras || 3
    eraIndicator.innerText = `Era: ${state.current_era}/${maxEras}`
  }

  const dragonIndicator = document.getElementById("dragon-indicator")
  if (dragonIndicator) {
    dragonIndicator.innerText = `Dragoes: ${state.dragons_drawn}/3`
  }

  // Atualiza a lista de jogadores
  const playersList = document.getElementById("players-list")
  playersList.innerHTML = ""
  for (const [sid, p] of Object.entries(state.players)) {
    playersList.innerHTML += `<li><strong>${p.name}</strong> - Cartas: ${p.hand_size} | Pontos: ${p.score}</li>`
  }

  // Atualiza os Reinos
  const boardDiv = document.getElementById("realms-board")
  boardDiv.innerHTML = ""
  for (const [realm, tokens] of Object.entries(state.board)) {
    boardDiv.innerHTML += `
            <div class="realm">
                <strong>${realm.toUpperCase()}</strong><br>
                Marcadores: ${tokens.length}
            </div>`
  }

  // Atualiza o Mercado
  const marketList = document.getElementById("market-list")
  if (marketList) {
    marketList.innerHTML = ""
    state.face_up_cards.forEach((card, index) => {
      const isDragon = !!card.is_dragon
      const label = isDragon ? "Dragao" : card.tribe
      const realm = isDragon ? "Especial" : card.realm
      const clickAttr = isDragon ? "" : `onclick="drawMarketCard(${index})"`
      const classAttr = isDragon ? "dragon" : ""
      marketList.innerHTML += `<li class="${classAttr}" ${clickAttr}>${label}<br><small>${realm}</small></li>`
    })
  }
})

// Atualizações privadas (Sua mão)
socket.on("private_update", (data) => {
  selectedCards = [] // Limpa seleção ao atualizar a mão
  const handList = document.getElementById("my-hand")
  handList.innerHTML = ""
  data.hand.forEach((card, index) => {
    handList.innerHTML += `<li id="card-${index}" onclick="toggleSelect(${index})">${card.tribe}<br><small>${card.realm}</small></li>`
  })
})

socket.on("error", (data) => {
  alert(data.msg)
})