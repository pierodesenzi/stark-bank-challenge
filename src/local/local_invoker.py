import sys
from pathlib import Path

# Add the root directory to sys.path
root_dir = Path(__file__).resolve().parents[2]
sys.path.append(str(root_dir))

from src.app.index import handler

# Calling the function
amount_transferred = 100
response = handler(
    {
        "body": f'{{"event": {{"log": {{"invoice": {{"amount": {amount_transferred}}}}}}}}}'
    }
)

print(response)
