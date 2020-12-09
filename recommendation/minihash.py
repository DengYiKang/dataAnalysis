import numpy as np
import random
arr = np.array([[0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 1, 0, 0]]).T
def miniHash(arr,h = 5):
#     print(arr)
    x = arr.shape[0]
    y = arr.shape[1]
    hashmap = [0]*h
    for i in range(h):              #生成映射函数（使用随机数模拟）
        hashmap[i] = random.sample(list(range(x)),x) 
#     print(hashmap)
    signarr = np.full((h,y),9999)
    for m in range(y):               #生成签名矩阵
        for n in range(h):
            for q in range(x):
                if arr[q][m] != 0 and signarr[n][m] > hashmap[n][q]:
                    signarr[n][m] = hashmap[n][q]
#     print(signarr)
    simarr = np.zeros((y,y))
    for m in range(y):       #统计相似程度
        for n in range(m,y):
            equalCount = 0
            for q in range(h):
                if signarr[q][m] == signarr[q][n]:
                    equalCount = equalCount + 1
            simarr[m][n] = float(equalCount)/float(h)
            simarr[n][m] = simarr[m][n]
    return simarr
