import React, { useEffect, useState } from "react";
import Chessboard from "react-chessboard";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [fen, setFen] = useState("start");
  const [moveHistory, setMoveHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch board state
  const fetchBoard = async () => {
    setIsLoading(true);
    const res = await fetch(`${API_URL}/board`);
    const data = await res.json();
    setFen(data.fen);
    setMoveHistory(data.move_history);
    setIsLoading(false);
  };

  useEffect(() => {
    fetchBoard();
  }, []);

  // Handle move
  const onDrop = async (sourceSquare, targetSquare, piece) => {
    const promotion = piece && piece[1] === "p" && (targetSquare[1] === "8" || targetSquare[1] === "1") ? "q" : undefined;
    const res = await fetch(`${API_URL}/move`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        from_square: sourceSquare,
        to_square: targetSquare,
        promotion,
      }),
    });
    if (res.ok) {
      const data = await res.json();
      setFen(data.fen);
      setMoveHistory(data.move_history);
      return true;
    } else {
      alert("Illegal move");
      return false;
    }
  };

  // Reset board
  const handleReset = async () => {
    await fetch(`${API_URL}/reset`, { method: "POST" });
    fetchBoard();
  };

  return (
    <div style={{ display: "flex", gap: 32, alignItems: "flex-start", padding: 32 }}>
      <div>
        <Chessboard position={fen} onPieceDrop={onDrop} boardWidth={400} />
        <button onClick={handleReset} style={{ marginTop: 16 }}>Reset</button>
      </div>
      <div>
        <h3>Move History</h3>
        <ol>
          {moveHistory.map((move, idx) => (
            <li key={idx}>{move}</li>
          ))}
        </ol>
      </div>
    </div>
  );
}

export default App;
