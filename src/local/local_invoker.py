from ..app.index import handler

# Calling the function
amount_transferred = 100
response = handler(
    {
        "body": f'{{"event": {{"log": {{"invoice": {{"amount": {amount_transferred}}}}}}}}}'
    }
)

print(response)
