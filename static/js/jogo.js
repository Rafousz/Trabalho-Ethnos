// static/js/jogo.js
const socket = io()
let currentRoom = ""
let selectedCards = []

const realmColors = {
  strath: '#3498db',   // Azul
  pelia: '#2ecc71',    // Verde
  nida: '#f1c40f',     // Amarelo
  shetan: '#e74c3c',   // Vermelho
  alara: '#9b59b6',    // Roxo
  fara: '#e67e22',     // Laranja
  Especial: '#7f8c8d'  // Cinza (Dragão)
}

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
    alert("Selecione pelo menos uma carta!")
    return
  }
  socket.emit("action_play_band", { room: currentRoom, indices: selectedCards })
}

function toggleSelect(index) {
  const idx = selectedCards.indexOf(index)
  const el = document.getElementById(`card-${index}`)

  if (idx > -1) {
    selectedCards.splice(idx, 1)
    el.classList.remove("selected")
    el.classList.remove("leader")
  } else {
    selectedCards.push(index)
    el.classList.add("selected")
  }

  document
    .querySelectorAll("#my-hand li")
    .forEach((li) => li.classList.remove("leader"))
  if (selectedCards.length > 0) {
    document.getElementById(`card-${selectedCards[0]}`).classList.add("leader")
  }
}

socket.on("game_update", (state) => {
  // Anúncio de Vencedor
  if (state.game_over) {
    document.getElementById("turn-indicator").innerHTML =
      `<span style="color: #27ae60; font-size: 1.5em;">🏆 VENCEDOR: ${state.winner} 🏆</span>`
    // Desabilitar botões
    document
      .querySelectorAll(".actions button")
      .forEach((btn) => (btn.disabled = true))
  } else {
    document.getElementById("turn-indicator").innerText =
      `Turno de: ${state.current_turn}`
  }

  document.getElementById("era-indicator").innerText =
    `Era: ${state.current_era}/${state.max_eras}`
  document.getElementById("dragon-indicator").innerText =
    `Dragões: ${state.dragons_drawn}/3`

  const playersList = document.getElementById("players-list")
  playersList.innerHTML = ""
  for (const [sid, p] of Object.entries(state.players)) {
    playersList.innerHTML += `
      <li>
        <span style="display:inline-block; width:10px; height:10px; background:${p.color}; border-radius:50%; margin-right:5px;"></span>
        <strong>${p.name}</strong> - Cartas: ${p.hand_size} | Pontos: ${p.score}
      </li>`
  }

  const boardDiv = document.getElementById("realms-board")
  boardDiv.innerHTML = ""
  for (const [realm, sids] of Object.entries(state.board)) {
    const glorias = state.glory_tokens[realm]

    // Constrói a lista de valores de todas as eras
    let glóriasListHTML =
      '<div style="font-size: 0.85em; text-align: left; margin: 5px 0;">'
    glorias.forEach((val, idx) => {
      const eraNum = idx + 1
      const isCurrent = eraNum === state.current_era && !state.game_over
      const style = isCurrent
        ? "font-weight: bold; color: #e67e22; background: #fff3e0; padding: 1px 4px; border-radius: 3px;"
        : "color: #7f8c8d;"
      glóriasListHTML += `<div style="${style}">Era ${eraNum}: ${val} pts</div>`
    })
    glóriasListHTML += "</div>"

    let tokensHTML = ""
    sids.forEach((sid) => {
      const cor = state.players[sid] ? state.players[sid].color : "#000"
      tokensHTML += `<span style="display:inline-block; width:15px; height:15px; border-radius:50%; background-color:${cor}; margin: 2px; border: 1px solid #333;"></span>`
    })

    const color = realmColors[realm] || '#2980b9'

    boardDiv.innerHTML += `
      <div class="realm" style="min-width: 140px; border-color: ${color};">
        <strong>${realm.toUpperCase()}</strong>
        ${glóriasListHTML}
        <div style="margin-top:8px; min-height:30px; border-top: 1px solid #ddd; padding-top: 5px;">${tokensHTML}</div>
      </div>`
  }

  const marketList = document.getElementById("market-list")
  marketList.innerHTML = ""
  state.face_up_cards.forEach((card, index) => {
    const isDragon = !!card.is_dragon
    const label = isDragon ? "Dragão" : card.tribe
    const realm = isDragon ? "Especial" : card.realm
    const clickAttr =
      isDragon || state.game_over ? "" : `onclick="drawMarketCard(${index})"`
    const classAttr = isDragon ? "dragon" : ""
    const imgName = isDragon ? "Dragao.png" : `${card.tribe}.png`
    const borderColor = realmColors[realm] || '#ccc'

    marketList.innerHTML += `
      <li class="${classAttr}" ${clickAttr} style="background-color: ${borderColor}; border-color: ${borderColor}">
        <img src="/static/images/cards/${imgName}" alt="${label}" class="card-img" onerror="this.src='/static/images/cards/Guerreiros.png'">
        <div class="card-info">
          <span class="tribe-name">Tribo: ${label}</span>
          <small class="realm-name">Reino: ${realm}</small>
        </div>
      </li>`
  })
})

socket.on("private_update", (data) => {
  selectedCards = []
  const handList = document.getElementById("my-hand")
  handList.innerHTML = ""
  data.hand.forEach((card, index) => {
    const isDragon = !!card.is_dragon
    const label = isDragon ? "Dragão" : card.tribe
    const realm = isDragon ? "Especial" : card.realm
    const imgName = isDragon ? "Dragao.png" : `${card.tribe}.png`
    const borderColor = realmColors[realm] || '#ccc'

    handList.innerHTML += `
      <li id="card-${index}" onclick="toggleSelect(${index})" style="background-color: ${borderColor}; border-color: ${borderColor}">
        <img src="/static/images/cards/${imgName}" alt="${label}" class="card-img" onerror="this.src='/static/images/cards/Guerreiros.png'">
        <div class="card-info">
          <span class="tribe-name">Tribo: ${label}</span>
          <small class="realm-name">Reino: ${realm}</small>
        </div>
      </li>`
  })
})

socket.on("error", (data) => {
  alert(data.msg)
})
