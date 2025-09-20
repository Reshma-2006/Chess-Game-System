# Chess Training Backend

## How to run

1. Install dependencies (already handled if you see this file):
   pip install fastapi uvicorn python-chess

2. Start the server:
   uvicorn main:app --reload

## Endpoints

- `GET /board` — Get current board FEN, turn, check/checkmate, move history
- `POST /move` — Make a move (from_square, to_square, promotion optional)
- `POST /reset` — Reset the board

## Example Move Request

POST /move
{
  "from_square": "e2",
  "to_square": "e4"
}

## Note
- State is in-memory and resets on server restart.
