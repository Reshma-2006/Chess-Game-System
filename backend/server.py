from db_manager import create_game, save_move
from flask import Flask, request, jsonify
from flask_cors import CORS
import chess
import json
import os

app = Flask(__name__)
CORS(app)

STATE_FILE = "game_state.json"

# ------------------- PERSISTENCE LAYER -------------------

def save_state_to_file(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def load_state_from_file():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except:
            return None
    return None


# --------------------------------------------
# GAME STATE MANAGER (Original – unchanged)
# --------------------------------------------

class GameStateManager:
    def __init__(self):
        loaded = load_state_from_file()

        if loaded:
            # Load saved FEN
            self.board = chess.Board(loaded["fen"])
        else:
            # Fresh game
            self.board = chess.Board()
        self.move_count = len(self.board.move_stack)
        self.turn = "white" if self.board.turn == chess.WHITE else "black"    

    def square_to_coords(self, square):
        file = ord(square[0]) - ord('a')
        rank = int(square[1]) - 1
        return file, rank

    def validate_piece_move(self, piece, from_sq, to_sq):
        fx, fy = self.square_to_coords(from_sq)
        tx, ty = self.square_to_coords(to_sq)

        dx = abs(tx - fx)
        dy = abs(ty - fy)

        # ---- ROOK ----
        if piece == chess.ROOK:
            if fx != tx and fy != ty:
                return False, "Rook moves only horizontally or vertically"
            return True, ""

        # ---- BISHOP ----
        if piece == chess.BISHOP:
            if dx != dy:
                return False, "Bishop moves only diagonally"
            return True, ""

        # ---- QUEEN ----
        if piece == chess.QUEEN:
            if not (fx == tx or fy == ty or dx == dy):
                return False, "Queen moves horizontally, vertically, or diagonally"
            return True, ""

        # ---- KNIGHT ----
        if piece == chess.KNIGHT:
            if not ((dx == 1 and dy == 2) or (dx == 2 and dy == 1)):
                return False, "Knight moves in an L-shape"
            return True, ""

        # ---- KING ----
        if piece == chess.KING:
            if dx > 1 or dy > 1:
                return False, "King moves only 1 square in any direction"
            return True, ""

        # ---- PAWN ----
        if piece == chess.PAWN:
            direction = 1 if self.board.turn == chess.WHITE else -1

            # Forward
            if tx == fx and ty == fy + direction:
                return True, ""

            # First double
            if tx == fx and dy == 2 and (
                (fy == 1 and self.board.turn == chess.WHITE) or
                (fy == 6 and self.board.turn == chess.BLACK)
            ):
                return True, ""

            # Capture
            if dx == 1 and ty == fy + direction:
                return True, ""

            return False, "Pawn move invalid"

        return False, "Unsupported piece"
    
    # ------------------- ENDGAME DETECTOR -------------------

    def detect_endgame(self):
        if self.board.is_checkmate():
            winner = "black" if self.board.turn == chess.WHITE else "white"
            return {
                "status": "checkmate",
                "winner": winner,
                "message": f"Checkmate! {winner.capitalize()} wins."
            }

        if self.board.is_stalemate():
            return {
                "status": "stalemate",
                "message": "Stalemate! The game is a draw."
            }

        if self.board.is_insufficient_material():
            return {
                "status": "draw",
                "message": "Draw due to insufficient material."
            }

        if self.board.is_check():
            return {
                "status": "check",
                "message": "Check!"
            }

        return {
            "status": "ongoing",
            "message": "Game is ongoing."
        }


    # ------------------- STATE FUNCTIONS -------------------

    def get_state(self):
        return {
            "fen": self.board.fen(),
            "turn": "white" if self.board.turn else "black",
            "legal_moves": [m.uci() for m in self.board.legal_moves],
            "move_history": [m.uci() for m in self.board.move_stack]
    }


    def make_move(self, from_sq, to_sq):
        try:
            move = chess.Move.from_uci(from_sq + to_sq)
        except:
            return {"valid": False, "error": "Invalid move notation"}

        piece = self.board.piece_at(chess.parse_square(from_sq))
        if piece is None:
            return {"valid": False, "error": "No piece in source square"}

        ok, msg = self.validate_piece_move(piece.piece_type, from_sq, to_sq)
        if not ok:
            return {"valid": False, "error": msg}

        if move not in self.board.legal_moves:
            return {"valid": False, "error": "Illegal move (Check rules)"}

        self.board.push(move)

        # Move number = number of moves made so far
        move_no = len(self.board.move_stack)

        # Player who made the move
        player = "white" if not self.board.turn else "black"

        # Save move to DB
        save_move(
            CURRENT_GAME_ID,
            move_no,
            player,
            from_sq,
            to_sq
        )

        # Update turn state
        self.turn = "white" if self.board.turn == chess.WHITE else "black"

        # Save JSON state
        save_state_to_file(self.get_state())

        return {"valid": True, "state": self.get_state()}
    

    def reset(self):
        self.board.reset()

        # Save reset state
        save_state_to_file(self.get_state())

        return {"status": "reset", "state": self.get_state()}

    def undo(self):
        if self.board.move_stack:
            self.board.pop()
            save_state_to_file(self.get_state())
            return {"status": "undone", "state": self.get_state()}
        return {"error": "No moves to undo"}
    
        # ------------------- AI EVALUATION ENGINE -------------------

    def evaluate_board(self):
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9
        }

        score = 0

        for piece_type, value in piece_values.items():
            score += len(self.board.pieces(piece_type, chess.WHITE)) * value
            score -= len(self.board.pieces(piece_type, chess.BLACK)) * value

        if score > 0:
            message = f"White is better (+{score})"
        elif score < 0:
            message = f"Black is better ({score})"
        else:
            message = "Position is equal (0.0)"

        return {
            "score": score,
            "evaluation": message
        }
    
        # ------------------- AI BEST MOVE SUGGESTION -------------------

    def suggest_best_move(self):
        best_move = None
        best_score = -9999 if self.board.turn == chess.WHITE else 9999

        for move in self.board.legal_moves:
            self.board.push(move)
            evaluation = self.evaluate_board()["score"]
            self.board.pop()

            if self.board.turn == chess.WHITE:
                if evaluation > best_score:
                    best_score = evaluation
                    best_move = move
            else:
                if evaluation < best_score:
                    best_score = evaluation
                    best_move = move

        if best_move:
            return {
                "best_move": best_move.uci(),
                "evaluation": best_score,
                "message": f"Suggested move: {best_move.uci()}"
            }

        return {
            "best_move": None,
            "message": "No legal moves available"
        }




# GLOBAL INSTANCE
game = GameStateManager()
CURRENT_GAME_ID = create_game()


# ---------------------- ROUTES ----------------------------

@app.route('/validate_move', methods=['POST'])
def validate_move():
    data = request.get_json()
    if not data or 'from' not in data or 'to' not in data:
        return jsonify({'valid': False, 'error': 'Invalid request format'}), 400

    result = game.make_move(data['from'], data['to'])
    return jsonify(result)

@app.route('/state', methods=['GET'])
def get_state():
    return jsonify(game.get_state())

@app.route('/reset', methods=['POST'])
def reset_board():
    return jsonify(game.reset())

@app.route('/undo', methods=['POST'])
def undo():
    return jsonify(game.undo())

@app.route('/endgame', methods=['GET'])
def check_endgame():
    return jsonify(game.detect_endgame())

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify({
        "history": [m.uci() for m in game.board.move_stack]
    })

@app.route('/evaluate', methods=['GET'])
def evaluate_position():
    return jsonify(game.evaluate_board())

@app.route('/best_move', methods=['GET'])
def best_move():
    return jsonify(game.suggest_best_move())



if __name__ == '__main__':
    app.run(debug=True)

