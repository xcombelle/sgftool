def test(r):
    return r(0,0)==(21,0) and r(21,0 )==(21,21) and r(21,21) == (0,21) and r(0,21)==(0,0)

def r(x,y):
    return (21-y),x 
print(test(r))
