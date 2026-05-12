// static/js/jogo.js
const socket = io()
let currentRoom = ""
let selectedCards = []
let mySid = null

const realmColors = {
  strath: "#3498db",
  pelia: "#2ecc71",
  nida: "#f1c40f",
  shetan: "#e74c3c",
  alara: "#9b59b6",
  fara: "#e67e22",
  Especial: "#7f8c8d",
}

const realmNames = {
  strath: "Strath",
  pelia: "Pelia",
  nida: "Nida",
  shetan: "Shetan",
  alara: "Alara",
  fara: "Fara",
}

// ---------------------------------------------------------------------------
// Entrada no jogo
// ---------------------------------------------------------------------------

socket.on('rooms_update', (rooms) => {
  const roomsList = document.getElementById("rooms-list")
  if (!roomsList) return
  roomsList.innerHTML = ""
  
  if (rooms.length === 0) {
    roomsList.innerHTML = "<li>Nenhuma sala criada.</li>"
    return
  }

  rooms.forEach(room => {
    roomsList.innerHTML += `
      <li style="margin-bottom: 10px; border: 1px solid #ccc; padding: 10px; border-radius: 5px; display: flex; justify-content: space-between; align-items: center;">
        <span><strong>${room.name}</strong> (${room.players}/6)</span>
        <button onclick="joinExistingGame('${room.name}')">Entrar</button>
      </li>
    `
  })
})

socket.on('join_success', (data) => {
  currentRoom = data.room
  document.getElementById("login-screen").style.display = "none"
  document.getElementById("game-screen").style.display = "block"
})

function createGame() {
  const name = document.getElementById("username").value
  const room = document.getElementById("room").value

  if (name && room) {
    socket.emit("create_game", { name: name, room: room })
  } else {
    alert("Preencha nome e sala.")
  }
}

function joinExistingGame(roomName) {
  const name = document.getElementById("username").value

  if (name) {
    socket.emit("join_game", { name: name, room: roomName })
  } else {
    alert("Preencha seu nome para entrar na sala.")
  }
}

// ---------------------------------------------------------------------------
// Ações básicas
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Poder dos Guerreiros: modal de escolha de reino
// ---------------------------------------------------------------------------

socket.on("choose_realm", (data) => {
  showRealmModal(data.realms)
})

function showRealmModal(realms) {
  // Remove modal anterior se existir
  document.getElementById("realm-modal")?.remove()

  const modal = document.createElement("div")
  modal.id = "realm-modal"
  modal.style.cssText = `
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.6); display: flex; align-items: center;
    justify-content: center; z-index: 1000;
  `

  const box = document.createElement("div")
  box.style.cssText = `
    background: #fff; border-radius: 10px; padding: 24px;
    min-width: 280px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  `
  box.innerHTML = `<h3 style="margin-bottom: 16px;">Guerreiros: escolha o reino alvo</h3>`

  realms.forEach((realm) => {
    const btn = document.createElement("button")
    btn.textContent = realmNames[realm] || realm
    btn.style.cssText = `
      display: block; width: 100%; margin: 6px 0; padding: 10px;
      background: ${realmColors[realm] || "#ccc"}; color: #fff;
      border: none; border-radius: 6px; cursor: pointer; font-size: 1em;
      font-weight: bold; letter-spacing: 0.5px;
    `
    btn.onclick = () => {
      socket.emit("action_choose_realm", { room: currentRoom, realm: realm })
      modal.remove()
    }
    box.appendChild(btn)
  })

  modal.appendChild(box)
  document.body.appendChild(modal)
}

// ---------------------------------------------------------------------------
// Poder dos Elfos: modal de escolha de cartas a manter
// ---------------------------------------------------------------------------

socket.on("choose_keep_cards", (data) => {
  showKeepCardsModal(data.cards, data.n_manter)
})

function showKeepCardsModal(cards, nManter) {
  document.getElementById("elfo-modal")?.remove()

  const modal = document.createElement("div")
  modal.id = "elfo-modal"
  modal.style.cssText = `
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.6); display: flex; align-items: center;
    justify-content: center; z-index: 1000;
  `

  const box = document.createElement("div")
  box.style.cssText = `
    background: #fff; border-radius: 10px; padding: 24px;
    min-width: 320px; max-width: 500px; text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  `
  box.innerHTML = `
    <h3 style="margin-bottom: 8px;">Elfos: escolha até ${nManter} carta(s) para manter</h3>
    <p style="font-size:0.85em; color:#666; margin-bottom:14px;">
      As demais irão para o mercado.
    </p>
  `

  const cardList = document.createElement("ul")
  cardList.style.cssText =
    "list-style: none; padding: 0; margin: 0 0 16px 0; display: flex; flex-wrap: wrap; gap: 8px; justify-content: center;"

  let selectedKeep = []

  cards.forEach((card, index) => {
    const isDragon = !!card.is_dragon
    const label = isDragon ? "Dragão" : card.tribe
    const realm = isDragon ? "Especial" : card.realm
    const borderColor = realmColors[realm] || "#ccc"

    const li = document.createElement("li")
    li.id = `keep-card-${index}`
    li.style.cssText = `
      padding: 8px 12px; border-radius: 6px; cursor: pointer;
      background: ${borderColor}; color: #fff; font-weight: bold;
      border: 3px solid transparent; user-select: none;
    `
    li.textContent = `${label} (${realm})`
    li.onclick = () => {
      const pos = selectedKeep.indexOf(index)
      if (pos > -1) {
        selectedKeep.splice(pos, 1)
        li.style.border = "3px solid transparent"
        li.style.opacity = "1"
      } else {
        if (selectedKeep.length >= nManter) {
          alert(`Você só pode manter ${nManter} carta(s).`)
          return
        }
        selectedKeep.push(index)
        li.style.border = "3px solid #2c3e50"
        li.style.opacity = "0.85"
      }
      confirmBtn.textContent = `Confirmar (${selectedKeep.length}/${nManter})`
    }
    cardList.appendChild(li)
  })

  box.appendChild(cardList)

  const confirmBtn = document.createElement("button")
  confirmBtn.textContent = `Confirmar (0/${nManter})`
  confirmBtn.style.cssText = `
    padding: 10px 24px; background: #27ae60; color: #fff;
    border: none; border-radius: 6px; cursor: pointer; font-size: 1em;
  `
  confirmBtn.onclick = () => {
    socket.emit("action_keep_cards", {
      room: currentRoom,
      indices: selectedKeep,
    })
    modal.remove()
  }

  box.appendChild(confirmBtn)
  modal.appendChild(box)
  document.body.appendChild(modal)
}

// ---------------------------------------------------------------------------
// Atualização do estado público (game_update)
// ---------------------------------------------------------------------------

socket.on("game_update", (state) => {
  if (state.game_over) {
    document.getElementById("turn-indicator").innerHTML =
      `<span style="color: #27ae60; font-size: 1.5em;">🏆 VENCEDOR: ${state.winner} 🏆</span>`
    document
      .querySelectorAll(".actions button")
      .forEach((btn) => (btn.disabled = true))
  } else {
    let currentPlayer = Object.values(state.players).find(p => p.name === state.current_turn);
    let colorSpan = currentPlayer ? `<span style="display:inline-block; width:15px; height:15px; background:${currentPlayer.color}; border-radius:50%; margin-right:8px; vertical-align: middle; border: 1px solid #333;"></span>` : "";

    let turnText = `Turno de: ${colorSpan}${state.current_turn}`

    // Indica poder ativo se há ação pendente
    if (state.pending_action) {
      const tipo = state.pending_action.type
      if (tipo === "guerreiros_choose_realm") {
        turnText += " (escolhendo reino...)"
      } else if (tipo === "elfos_keep_cards") {
        turnText += " (escolhendo cartas...)"
      }
    }

    document.getElementById("turn-indicator").innerHTML = turnText
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

    const color = realmColors[realm] || "#2980b9"
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
    const borderColor = realmColors[realm] || "#ccc"

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

// ---------------------------------------------------------------------------
// Atualização privada da mão (private_update)
// ---------------------------------------------------------------------------

socket.on("private_update", (data) => {
  selectedCards = []
  const handList = document.getElementById("my-hand")
  handList.innerHTML = ""
  data.hand.forEach((card, index) => {
    const isDragon = !!card.is_dragon
    const label = isDragon ? "Dragão" : card.tribe
    const realm = isDragon ? "Especial" : card.realm
    const imgName = isDragon ? "Dragao.png" : `${card.tribe}.png`
    const borderColor = realmColors[realm] || "#ccc"

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
