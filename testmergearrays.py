X = ['a', 'b', 'c', 'd', 'e']
Y = ['a', 'b', 'c', 'd', 'e', 'f', 'x']

newArr = []
count = 0

for i in range(len(Y)):
    for j in range(len(X)):
        if (Y[i] == X[j]):
            count = 0
            break
        else:
            count = count+1

        if count==len(X):
            count = 0
            newArr.append(Y[i])

print newArr
