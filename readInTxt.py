import os
appDataPath = os.getenv('LOCALAPPDATA') + '\shockData'
fileName = '2018-03-04T21-21-36.txt'
fullName = appDataPath + '\\' + fileName
f = open(fullName, 'r')

lines=f.readlines()
result=[]
for x in lines:
    result.append(x.split(' ')[0])
    print (x.split(' ')[0])



"""
print appDataPath
#file_path = "/my/directory/filename.txt"
#directory = os.path.dirname(file_path)

if not os.path.exists(appDataPath):
    os.makedirs(appDataPath)

f = open('Test Results 1\\testFileA.txt', 'r')
lines = f.read().split('\n')
newA = []
for line in lines:
    if line.strip():
        newA.append(int(line))

count = 0
for i in range(len(newA) - 1):
    #print i
    #print newA[i]
    if count > 20:
        index = i - 20
        firstVal = newA[i-20]
        break
    if (newA[i+1] < newA[i]):
        count = count+1
    else:
        count = 0

print "Index: " + str(index)
print "Value: " + str(firstVal)"""
