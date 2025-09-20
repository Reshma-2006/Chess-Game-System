from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chess
from typing import List, Optional

app = FastAPI()

# In-memory state
board = chess.Board()
move_history: List[str] = []

class MoveRequest(BaseModel):
    from_square: str
    to_square: str
    promotion: Optional[str] = None

@app.get("/board")
def get_board():
    return {
        "fen": board.fen(),
        "turn": "white" if board.turn else "black",
        "is_check": board.is_check(),
        "is_checkmate": board.is_checkmate(),
        "move_history": move_history
    }

@app.post("/move")
def make_move(move: MoveRequest):
    try:
        uci_move = move.from_square + move.to_square
        if move.promotion:
            uci_move += move.promotion.lower()
        chess_move = chess.Move.from_uci(uci_move)
        if chess_move not in board.legal_moves:
            raise HTTPException(status_code=400, detail="Illegal move")
        board.push(chess_move)
        move_history.append(board.san(chess_move))
        return {
            "fen": board.fen(),
            "move_history": move_history
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/reset")
def reset_board():
    global board, move_history
    board = chess.Board()
    move_history = []
    return {"message": "Board reset"}
