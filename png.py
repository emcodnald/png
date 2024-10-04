import math
import zlib

"""
the paeth function - input: number, number, number | output: number
prediction model used in png image filtering
"""
def paeth(a, b, c):
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    elif pb <= pc:
        return b
    else:
        return c

"""
the matrix function - input: string | output: three dimensional matrix
takes a filename, opens the file, and converts the contents into a matrix representing the pixel data
"""
def matrix(fn):
    sb = open(fn, 'rb').read()
    count = 8
    c = []
    cn = []
    ualp = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    lalp = 'abcdefghijklmnpoqrstuvwxyz'
    while count < len(sb):
        cLen = 0
        for i in range(4):
            cLen+=sb[count+i]*pow(256,3-i)
        sub = ''
        for i in range(4):
            if sb[count+i+4] < 96:
                sub += ualp[sb[count+i+4]-65]
            elif sb[count+i+4] >= 96:
                sub += lalp[sb[count+i+4]-97]
        cn.append(sub)
        count += 8
        sub = []
        for i in range(cLen):
            sub.append(sb[count+i])
        count += cLen+4
        c.append(sub)
    width = 0
    height = 0
    for i in range(4):
        width += c[0][i]*pow(256,3-i)
        height += c[0][i+4]*pow(256,3-i)
    ad = b''
    for j in range(len(c[4])):
        ad += ((c[4][j]).to_bytes(1, byteorder='big'))
    a = zlib.decompress(ad)
    pList = []
    filts = []
    for i in range(len(a)):
        if i%(width*4+1) == 0:
            pList.append([])
            filts.append(a[i])
        elif ((i%(width*4+1))-1)%4 == 0:
            pList[-1].append([])
            pList[-1][-1].append(a[i])
        else:
            pList[-1][-1].append(a[i])
    for i in range(len(pList)):
        for j in range(len(pList[i])):
            for k in range(4):
                if filts[i] == 1:
                    if j > 0:
                        pList[i][j][k] = (pList[i][j][k]+pList[i][j-1][k])%256
                elif filts[i] == 2:
                    if i > 0:
                        pList[i][j][k] = (pList[i][j][k]+pList[i-1][j][k])%256
                elif filts[i] == 3:
                    sub = 0
                    if j > 0:
                        sub = pList[i][j-1][k]
                    sub2 = 0
                    if i > 0:
                        sub2 = pList[i-1][j][k]
                    pList[i][j][k] = (pList[i][j][k]+int((sub+sub2)/2))%256
                elif filts[i] == 4:
                    sub = 0
                    if j > 0:
                        sub = pList[i][j-1][k]
                    sub2 = 0
                    if i > 0:
                        sub2 = pList[i-1][j][k]
                    sub3 = 0
                    if i > 0 and j > 0:
                        sub3 = pList[i-1][j-1][k]
                    pList[i][j][k] = (pList[i][j][k]+paeth(sub,sub2,sub3))%256
    return pList

"""
the image function - input: three dimensional matrix | no output
takes a three dimensional pixel matrix and converts it into a .png image
"""
def image(ma,fn):
    finStream = b''
    for i in range(len(ma)):
        finStream += (0).to_bytes(1,byteorder='big')
        for j in range(len(ma[i])):
            for k in range(4):
                if k == 3:
                    finStream += int(ma[i][j][k]*255).to_bytes(1,byteorder='big')
                else:
                    finStream += int(ma[i][j][k]).to_bytes(1,byteorder='big')
    compStr = zlib.compress(finStream)
    idatStr = b'IDAT'
    for i in range(len(compStr)):
        idatStr += (compStr[i]).to_bytes(1,byteorder='big')
    idatCrc = zlib.crc32(idatStr)
    for i in range(4):
        idatStr += (int(idatCrc/pow(256,3-i))%256).to_bytes(1,byteorder='big')
    ihdrStr = b'IHDR'
    for i in range(4):
        ihdrStr += int(len(ma[0])/pow(256,3-i)%256).to_bytes(1,byteorder="big")
    for i in range(4):
        ihdrStr += int(len(ma)/pow(256,3-i)%256).to_bytes(1,byteorder="big")
    hb = [8, 6, 0, 0, 0]
    for i in range(len(hb)):
        ihdrStr += (hb[i]).to_bytes(1,byteorder='big')
    ihdrCrc = zlib.crc32(ihdrStr)
    for i in range(4):
        ihdrStr += (int(ihdrCrc/pow(256,3-i))%256).to_bytes(1,byteorder='big')
    iendStr = b'IEND'
    iendCrc = zlib.crc32(iendStr)
    for i in range(4):
        iendStr += (int(iendCrc/pow(256,3-i))%256).to_bytes(1,byteorder='big')
    sb = b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'
    ch = [ihdrStr,idatStr,iendStr]
    with open(fn, 'wb') as f:
        for i in range(len(sb)):
            f.write((sb[i]).to_bytes(1,byteorder='big'))
        for i in range(len(ch)):
            for j in range(4):
                f.write((int((len(ch[i])-8)/pow(256,3-j))%256).to_bytes(1,byteorder='big'))
            for j in range(len(ch[i])):
                f.write((ch[i][j]).to_bytes(1,byteorder='big'))

"""
the image function - input: array, array | array
takes a base color c1 and adds a sample color c2 to it, taking into account transparency
"""
def addColors(c1,c2):
    rop = 1-((1-c1[3])*(1-c2[3]))
    if rop > 0:
        final = []
        for i in range(3):
            final.append((c1[i]*c1[3]*(1-c2[3])+c2[i]*c2[3])/rop)
        final.append(rop)
        return final
    else:
        return [0,0,0,0]

