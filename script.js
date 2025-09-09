const boardElement = document.getElementById("gameBoard");
const mineCounter = document.getElementById("mineCounter");
const resetButton = document.getElementById("reset");
const difficultySelect = document.getElementById("difficulty");

let board = [];
let rows, cols, totalMines;
let minePositions = new Set();
let revealedCount = 0;
let flaggedCount = 0;
let gameOver = false;

// Initialize game parameters
function setDifficulty(level) {
  if (level === "easy") {
    rows = cols = 9;
    totalMines = 10;
  } else if (level === "medium") {
    rows = cols = 16;
    totalMines = 40;
  } else if (level === "hard") {
    rows = cols = 24;
    totalMines = 99;
  }
}

// Create board data structure
function createBoard() {
  board = [];
  for (let r = 0; r < rows; r++) {
    const row = [];
    for (let c = 0; c < cols; c++) {
      row.push({
        isMine: false,
        isRevealed: false,
        isFlagged: false,
        adjacentMines: 0,
        element: null,
      });
    }
    board.push(row);
  }
}

// Place mines randomly
function placeMines() {
  minePositions = new Set();
  while (minePositions.size < totalMines) {
    const pos = Math.floor(Math.random() * rows * cols);
    minePositions.add(pos);
  }
  minePositions.forEach(pos => {
    const r = Math.floor(pos / cols);
    const c = pos % cols;
    board[r][c].isMine = true;
  });
}

// Compute adjacent mine counts per cell
function calculateAdjacent() {
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (board[r][c].isMine) continue;
      let count = 0;
      for (let dr = -1; dr <= 1; dr++) {
        for (let dc = -1; dc <= 1; dc++) {
          let rr = r + dr;
          let cc = c + dc;
          if (
            rr >= 0 &&
            rr < rows &&
            cc >= 0 &&
            cc < cols &&
            board[rr][cc].isMine
          ) {
            count++;
          }
        }
      }
      board[r][c].adjacentMines = count;
    }
  }
}

// Create visual board grid html
function renderBoard() {
  boardElement.innerHTML = "";
  boardElement.style.width = cols * 30 + "px";
  boardElement.style.height = rows * 30 + "px";
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const cell = document.createElement("div");
      cell.classList.add("cell");
      cell.setAttribute("data-row", r);
      cell.setAttribute("data-col", c);
      cell.addEventListener("click", () => handleReveal(r, c));
      cell.addEventListener("contextmenu", e => {
        e.preventDefault();
        handleFlag(r, c);
      });
      board[r][c].element = cell;
      boardElement.appendChild(cell);
    }
  }
  updateMineCounter();
}

// Reveal cell and recursively reveal neighbors if no adjacent mines
function handleReveal(r, c) {
  if (gameOver) return;
  const cell = board[r][c];
  if (cell.isRevealed || cell.isFlagged) return;
  cell.isRevealed = true;
  revealedCount++;
  updateCellVisual(cell);

  if (cell.isMine) {
    cell.element.classList.add("mine");
    endGame(false);
    return;
  }

  if (cell.adjacentMines === 0) {
    // Reveal all adjacent cells recursively
    for (let dr = -1; dr <= 1; dr++) {
      for (let dc = -1; dc <= 1; dc++) {
        let rr = r + dr;
        let cc = c + dc;
        if (
          rr >= 0 &&
          rr < rows &&
          cc >= 0 &&
          cc < cols &&
          !board[rr][cc].isRevealed
        ) {
          handleReveal(rr, cc);
        }
      }
    }
  }
  checkWin();
}

// Flag or unflag a cell
function handleFlag(r, c) {
  if (gameOver) return;
  const cell = board[r][c];
  if (cell.isRevealed) return;
  if (cell.isFlagged) {
    cell.isFlagged = false;
    flaggedCount--;
  } else {
    cell.isFlagged = true;
    flaggedCount++;
  }
  updateCellVisual(cell);
  updateMineCounter();
  checkWin();
}

// Update mine counter display
function updateMineCounter() {
  mineCounter.textContent = `Mines left: ${totalMines - flaggedCount}`;
}

// Update individual cell appearance
function updateCellVisual(cell) {
  const el = cell.element;
  if (cell.isRevealed) {
    el.classList.add("revealed");
    el.classList.remove("flagged");
    if (cell.isMine) {
      el.textContent = "💣";
    } else if (cell.adjacentMines > 0) {
      el.textContent = cell.adjacentMines;
      el.classList.add(`number${cell.adjacentMines}`);
    } else {
      el.textContent = "";
    }
  } else {
    el.classList.remove("revealed");
    if (cell.isFlagged) {
      el.classList.add("flagged");
      el.textContent = "🚩";
    } else {
      el.classList.remove("flagged");
      el.textContent = "";
    }
  }
}

// End the game with win or lose state
function endGame(won) {
  gameOver = true;
  if (won) {
    setTimeout(() => alert("Congratulations, You Win! 🎉"), 100);
  } else {
    setTimeout(() => alert("Game Over! You hit a mine! 💥"), 100);
    revealAllMines();
  }
}

// Reveal all mines at game over
function revealAllMines() {
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const cell = board[r][c];
      if (cell.isMine && !cell.isRevealed) {
        cell.isRevealed = true;
        updateCellVisual(cell);
      }
    }
  }
}

// Check if player has revealed all non-mine squares and flagged correctly
function checkWin() {
  if (gameOver) return;
  if (
    revealedCount === rows * cols - totalMines &&
    flaggedCount === totalMines
  ) {
    endGame(true);
  }
}

// Start or restart game with current settings
function startGame() {
  setDifficulty(difficultySelect.value);
  createBoard();
  placeMines();
  calculateAdjacent();
  revealedCount = 0;
  flaggedCount = 0;
  gameOver = false;
  renderBoard();
  updateMineCounter();
}

resetButton.addEventListener("click", startGame);

// Start first game on page load
startGame();
