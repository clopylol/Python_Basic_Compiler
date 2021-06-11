import basic

while True:
    text = input('test > ')
    #print(text)

    # FileName ve text parametre
    result, error = basic.run('<stdin>', text)
    print(result)
    if error: print(error.as_string())
    elif result: print(result)