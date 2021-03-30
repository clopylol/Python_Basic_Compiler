import basic

while True:
    text = input('basic > ')
    #print(text)

    result, error = basic.run(text)
    print(result)
    if error: print(error.as_string())
    else: print(result)