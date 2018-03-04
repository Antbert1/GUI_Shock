f = open('testFileA.txt', 'r')
lines = f.read().split('\n')
newA = []
for line in lines:
    if line.strip():
        newA.append(int(line))

print len(newA)
