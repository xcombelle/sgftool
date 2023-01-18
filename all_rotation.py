def test(r):
    return r(0,0)==(19,0) and r(19,0 )==(19,19) and r(19,19) == (0,19) and r(0,19)==(0,0)

def r(x,y):
    return (19-y),x 
print(test(r))
