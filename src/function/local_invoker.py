from index import handler

# Calling the function
amount_transfered = 100
response = handler({"body": '{"event": {"log": {"invoice": {"nominalAmount": 100}}}}'})

print(response)
