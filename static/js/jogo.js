// static/js/game.js
const socket = io()
let currentRoom = ""

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

// Atualizações do estado geral do jogo
socket.on("game_update", (state) => {
  document.getElementById("turn-indicator").innerText =
    `Turno de: ${state.current_turn}`

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
})

// Atualizações privadas (Sua mão)
socket.on("private_update", (data) => {
  const handList = document.getElementById("my-hand")
  handList.innerHTML = ""
  data.hand.forEach((card) => {
    handList.innerHTML += `<li>${card.tribe}<br><small>${card.realm}</small></li>`
  })
})

socket.on("error", (data) => {
  alert(data.msg)
})
