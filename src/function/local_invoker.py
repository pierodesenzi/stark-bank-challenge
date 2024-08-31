from index import handler

# Calling the function
amount_transfered = 100
response = handler(
    {
        "body": f'{{"event": {{"log": {{"invoice": {{"nominalAmount": {amount_transfered}}}}}}}}}'
    }
)

print(response)
