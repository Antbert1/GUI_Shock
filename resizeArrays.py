import serial.tools.list_ports


ports = list(serial.tools.list_ports.comports())
for p in ports:
    print str(p).split(' ')[0]
# valListB = [1,2,3]
# valListC = [1,2,3]
#
# if len(valListA) <= len(valListB):
#     valListB = valListA[0:len(valListA)]
#     if len(valListA) <= len(valListC):
#         valListC = valListC[0:len(valListA)]
#     else:
#         diffC = len(valListA) - len(valListC)
#         for i in range(diffC):
#             valListC.append(valListC[len(valListC)-1])
# else:
#     diffB = len(valListA) - len(valListB)
#     for i in range(diffB):
#         valListB.append(valListB[len(valListB)-1])
#     if len(valListA) <= len(valListC):
#         valListC.append(valListC[len(valListC)-1])
#     else:
#         diffC = len(valListA) - len(valListC)
#         for i in range(diffC):
#             valListC.append(valListC[len(valListC)-1])
#
# print valListA
# print valListB
# print valListC
