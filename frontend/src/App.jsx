import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const ChessBoard = () => {
  const initialBoard = [
    ['♜', '♞', '♝', '♛', '♚', '♝', '♞', '♜'],
    ['♟', '♟', '♟', '♟', '♟', '♟', '♟', '♟'],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['', '', '', '', '', '', '', ''],
    ['♙', '♙', '♙', '♙', '♙', '♙', '♙', '♙'],
    ['♖', '♘', '♗', '♕', '♔', '♗', '♘', '♖'],
  ];

  const [board, setBoard] = useState(initialBoard);
  const [draggedPiece, setDraggedPiece] = useState(null);
  const [draggedFrom, setDraggedFrom] = useState({ row: null, col: null });
  const [gameStatus, setGameStatus] = useState("Game is ongoing");
  const [history, setHistory] = useState([]);
  const [evaluation, setEvaluation] = useState("");
  const [bestMove, setBestMove] = useState("");


  const columnToLetter = (col) => String.fromCharCode(97 + col);
  const rowToNumber = (row) => 8 - row;

  const handleDragStart = (piece, row, col) => {
    setDraggedPiece(piece);
    setDraggedFrom({ row, col });
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleDrop = async (row, col) => {
    if (!draggedPiece) return;

    const from = columnToLetter(draggedFrom.col) + rowToNumber(draggedFrom.row);
    const to = columnToLetter(col) + rowToNumber(row);

    try {
      const response = await axios.post('http://127.0.0.1:5000/validate_move', {
        from,
        to,
      });

      if (response.data.valid) {
        const newBoard = board.map((r) => r.slice());
        newBoard[draggedFrom.row][draggedFrom.col] = '';
        newBoard[row][col] = draggedPiece;
        setBoard(newBoard);
        const endgameRes = await axios.get("http://127.0.0.1:5000/endgame");
        setGameStatus(endgameRes.data.message);
        const historyRes = await axios.get("http://127.0.0.1:5000/history");
        setHistory(historyRes.data.history);
        const evalRes = await axios.get("http://127.0.0.1:5000/evaluate");
        setEvaluation(evalRes.data.evaluation);
        const bestMoveRes = await axios.get("http://127.0.0.1:5000/best_move");
        setBestMove(bestMoveRes.data.message);



      } else {
        alert(response.data.error || "Invalid move!");
      }
    } catch (error) {
      alert("Server error: " + (error.response?.data?.error || "Unknown error"));
    }

    setDraggedPiece(null);
  };

  // ---------------- RESET BOARD ----------------
  const resetBoard = async () => {
  try {
    const res = await axios.post("http://127.0.0.1:5000/reset");
    if (res.data.state?.fen) {
      loadFEN(res.data.state.fen);
      setGameStatus("Game is ongoing");

    }
  } catch (error) {
    alert("Failed to reset!");
  }
};


  // ---------------- RESUME BOARD ----------------
const resumeBoard = async () => {
  try {
    const res = await axios.get("http://127.0.0.1:5000/state");

    if (res.data?.fen) {
  loadFEN(res.data.fen);
  alert("Game resumed successfully!");
}
 else {
      alert("Invalid state response from server");
    }
  } catch (error) {
    alert("Failed to resume game!");
  }
};


  // Convert FEN to Unicode board
  const loadFEN = (fen) => {
    const pieceMap = {
      r: "♜", n: "♞", b: "♝", q: "♛", k: "♚", p: "♟",
      R: "♖", N: "♘", B: "♗", Q: "♕", K: "♔", P: "♙",
    };

    const rows = fen.split(" ")[0].split("/");
    const newBoard = rows.map((row) => {
      let arr = [];
      for (let char of row) {
        if (isNaN(char)) arr.push(pieceMap[char] || "");
        else arr.push(...Array(parseInt(char)).fill(""));
      }
      return arr;
    });

    setBoard(newBoard);
  };

  return (
    <div className="chess-container">
      <h1>♟️ Chess Game System</h1>

      <div className="controls">
        <button onClick={resetBoard}>Reset Game</button>
        <button onClick={resumeBoard}>Resume Game</button>
      </div>

      <div className="board">
        {board.map((row, rowIndex) =>
          row.map((piece, colIndex) => {
            const isBlack = (rowIndex + colIndex) % 2 === 1;
            return (
              <div
                key={`${rowIndex}-${colIndex}`}
                className={`square ${isBlack ? 'black' : 'white'}`}
                onDragOver={handleDragOver}
                onDrop={() => handleDrop(rowIndex, colIndex)}
              >
                {piece && (
                  <span
                    className="piece"
                    draggable
                    onDragStart={() => handleDragStart(piece, rowIndex, colIndex)}
                  >
                    {piece}
                  </span>
                )}
              </div>
            );
          })
        )}
      </div>
     <div className="game-status">
         <h3>Game Status</h3>
         <p>{gameStatus}</p>
      </div>
      <div className="history-panel">
  <h3>Move History</h3>
  <ol>
    {history.map((move, index) => (
      <li key={index}>
        {index % 2 === 0 ? "White" : "Black"}: {move}
      </li>
    ))}
  </ol>
</div>
<div className="game-status">
  <h3>AI Evaluation</h3>
  <p>{evaluation}</p>
</div>
<p><strong>AI Suggestion:</strong> {bestMove}</p>

    </div>
    

  );
};

function App() {
  return <ChessBoard />;
}

export default App; 


