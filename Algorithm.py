import binascii
from gmssl import sm4
import numpy as np
import hashlib
from time import *

# 完全显示数组/矩阵的内容
np.set_printoptions(threshold=np.inf)


# 为用户生成私钥
class GetEi:
    def __init__(self, n):
        self.n = n
        self.matrix = []
        self.randmatrix = []

    def bin_matrix(self, id):
        int_bin = str(bin(id))[2:]
        len_bin = len(int_bin)
        arr = [0 for _ in range(self.n - len_bin)]
        for i in int_bin:
            arr.append(int(i))
        self.matrix = np.array(arr)

    # 生成随机矩阵
    def rand_matrix(self, id):
        self.randmatrix = np.random.RandomState(id).uniform(0, 100, (self.n, self.n))

    def get_ei(self, id):
        self.bin_matrix(id)
        self.rand_matrix(id)
        middle = np.dot(self.matrix, self.randmatrix)
        contrast = np.sum(middle) // self.n
        final = np.where(middle > contrast, 1, 0)
        return final


class SM4:
    """
    国产加密 sm4加解密
    """

    def __init__(self):
        self.crypt_sm4 = sm4.CryptSM4()  # 实例化

    def str_to_hexStr(self, hex_str):
        """
        字符串转hex
        :param hex_str: 字符串
        :return: hex
        """
        hex_data = hex_str.encode('utf-8')
        str_bin = binascii.unhexlify(hex_data)
        return str_bin.decode('utf-8')

    def encryptSM4(self, encrypt_key, value):
        """
        国密sm4加密
        :param encrypt_key: sm4加密key
        :param value: 待加密的字符串
        :return: sm4加密后的十六进制值
        """
        crypt_sm4 = self.crypt_sm4
        crypt_sm4.set_key(encrypt_key.encode(), sm4.SM4_ENCRYPT)  # 设置密钥
        date_str = str(value)
        encrypt_value = crypt_sm4.crypt_ecb(date_str.encode())  # 开始加密。bytes类型
        return encrypt_value.hex()  # 返回十六进制值

    def decryptSM4(self, decrypt_key, encrypt_value):
        """
        国密sm4解密
        :param decrypt_key:sm4加密key
        :param encrypt_value: 待解密的十六进制值
        :return: 原字符串
        """
        crypt_sm4 = self.crypt_sm4
        crypt_sm4.set_key(decrypt_key.encode(), sm4.SM4_DECRYPT)  # 设置密钥
        decrypt_value = crypt_sm4.crypt_ecb(bytes.fromhex(encrypt_value))  # 开始解密。十六进制类型
        return decrypt_value.decode()


def get_key(sql, group_name):
    key = ''
    realykey = ''
    result = sql.query(f"select e,s,r,H,G from `group` where groupname='{group_name}'")[0]
    for i in range(2, 2000, 2):
        key += result['e'][i] if not result['e'][i].isspace() else ''
    for i in range(0, len(key), 8):
        if int(key[i:i + 8], 2) in range(32, 127):
            realykey += chr(int(key[i:i + 8], 2))
    return realykey, result


def gen_si(n, k, ei):  # n,k,w是安全参数，直接固定n = 1268，k = 951
    H = np.random.randint(0, 2, (n - k, n))
    si = np.dot(H, np.transpose(ei)) % 2
    return si


def gen_r(n, t, e, s):  # 在n个人中，选择t个人的密钥，e.append（ei），s.append（si）【e和s都是列表，里面分别包括了t个密钥】
    hashg = np.random.randint(0, 2, (t, n))
    G = np.dot(np.transpose(s), hashg) % 2
    r = []
    for i in range(t):
        ri = np.dot(G, np.transpose(e[i])) % 2
        r.append(ri)
    r = np.array(r)
    return r, G


def threshold_GStern_com_resp(n, H, G, e, b, t):  # 签名模块,直接调用，下面有调用实例
    SEED = 10
    np.random.seed(SEED)
    COM1 = []
    COM2 = []
    COM3 = []
    y = []  # 存储t个yi，t*n,yi可以通过y[i]访问
    derta = []  # 存储t个dertai，t*n，dertai可以通过derta[i]访问
    dertay = []  # 存储t个dertayi，t*n，dertayi可以通过dertay[i]访问
    dertae = []  # 存储t个dertaei，t*n，dertaei可以通过dertae[i]访问
    dertaye = []  # 存储t个dertayei，t*n，dertayei可以通过dertaye[i]访问
    ye = []
    for i in range(t):
        ei = e[i]
        yi = np.random.randint(0, 2, n)  # 1*n
        y.append(yi)
        # print(yi)
        ye.append((ei + yi) % 2)
        dertai = np.arange(n)
        np.random.shuffle(dertai)
        derta.append(dertai)
        # print(dertai)
        dertayi = ['' for i in range(n)]
        for index, value in enumerate(dertai):
            dertayi[index] = yi[value]
        dertay.append(dertayi)
        dertaei = ['' for i in range(n)]
        for index, value in enumerate(dertai):
            dertaei[index] = ei[value]
        dertae.append(dertaei)
        dertayei = ['' for i in range(n)]
        for index, value in enumerate(dertai):
            dertayei[index] = ((yi + ei) % 2)[value]
        dertaye.append(dertayei)
        c1 = hashlib.md5(str(np.hstack((dertai, np.transpose(np.dot(H, np.transpose(yi)) % 2),
                                        np.transpose((np.dot(G, np.transpose(yi)) % 2))))).encode())
        c1 = c1.hexdigest()
        # print(c1)
        c2 = hashlib.md5()
        c2.update(str(dertayi).encode())
        c2 = c2.hexdigest()
        c3 = hashlib.md5()
        c3.update(str(dertayei).encode())
        c3 = c3.hexdigest()
        COM1.append(c1)
        COM2.append(c2)
        COM3.append(c3)
        com1 = hashlib.md5()
        com1.update(str(COM1).encode())
        com1 = com1.hexdigest()
        com2 = hashlib.md5()
        com2.update(str(COM2).encode())
        com2 = com2.hexdigest()
        com3 = hashlib.md5()
        com3.update(str(COM3).encode())
        com3 = com3.hexdigest()
    # print(COM2)
    # print(com1)
    # print(com2)
    # print(com3)
    if b == 0:
        return com1, com2, derta, y
    if b == 1:
        return com1, com3, derta, ye
    if b == 2:
        return com2, com3, dertay, dertae


def threshold_GStern_verify(n, H, G, s, r, b, t, com1, com2, resp1, resp2):  # 验证模块，直接调用，下面有调用实例
    if b == 0:
        # com1 = com1
        # com2 = com2
        # resp1 = derta
        # resp2 = y
        c10 = []  # 存储t个c10i，c10i可以通过c10[i]访问
        for i in range(t):
            c10i = hashlib.md5()
            c10i.update(str(np.hstack((resp1[i], np.transpose(np.dot(H, np.transpose(resp2[i])) % 2),
                                       np.transpose(np.dot(G, np.transpose(resp2[i])) % 2)))).encode())
            c10i = c10i.hexdigest()
            c10.append(c10i)
        # print(c10)
        com10 = hashlib.md5()
        com10.update(str(c10).encode())
        com10 = com10.hexdigest()
        # print(com10)
        c20 = []  # 存储t个c20i，c20i可以通过c20[i]访问
        dertay = []  # 存储t个dertayi，t*n，dertayi可以通过dertay[i]访问
        for i in range(t):
            dertayi = ['' for i in range(n)]
            for index, value in enumerate(resp1[i]):
                dertayi[index] = resp2[i][value]
            dertay.append(dertayi)
            c20i = hashlib.md5()
            c20i.update(str(dertayi).encode())
            c20i = c20i.hexdigest()
            c20.append(c20i)
        # print(c20)
        com20 = hashlib.md5()
        com20.update(str(c20).encode())
        com20 = com20.hexdigest()
        # print(com20)
        if (com1 == com10 and com2 == com20):
            print("VALID!")
            return 1
        else:
            print("INVALID!")
            return 0
    if b == 1:
        # com1 = com1
        # com2 = com3
        # resp1 = derta
        # resp2 = ye
        c11 = []  # 存储t个c11i，c11i可以通过c11[i]访问
        for i in range(t):
            c11i = hashlib.md5()
            c11i.update(str(np.hstack((resp1[i], np.transpose((np.dot(H, resp2[i]) + s[i]) % 2),
                                       np.transpose((np.dot(G, resp2[i]) + r[i]) % 2)))).encode())
            c11i = c11i.hexdigest()
            c11.append(c11i)
        # print(c11)
        com11 = hashlib.md5()
        com11.update(str(c11).encode())
        com11 = com11.hexdigest()
        # print(com11)
        c31 = []  # 存储t个c31i，c31i可以通过c31[i]访问
        dertaye = []  # 存储t个dertayei，t*n，dertayei可以通过dertaye[i]访问
        for i in range(t):
            dertayei = ['' for i in range(n)]
            for index, value in enumerate(resp1[i]):
                dertayei[index] = resp2[i][value]
            dertaye.append(dertayei)
            c31i = hashlib.md5()
            c31i.update(str(dertayei).encode())
            c31i = c31i.hexdigest()
            c31.append(c31i)
        # print(c31)
        com31 = hashlib.md5()
        com31.update(str(c31).encode())
        com31 = com31.hexdigest()
        # print(com31)
        if (com1 == com11 and com2 == com31):
            print("VALID!")
            return 1
        else:
            print("INVALID!")
            return 0
    if b == 2:
        # com1 = com2,
        # com2 = com3
        # resp1 = dertay
        # resp2 = dertae
        # print(resp1)
        c22 = []
        for i in range(t):
            c22i = hashlib.md5()
            c22i.update(str(resp1[i]).encode())
            c22i = c22i.hexdigest()
            c22.append(c22i)
        com22 = hashlib.md5()
        com22.update(str(c22).encode())
        com22 = com22.hexdigest()
        print(com22)
        print(com1)
        c32 = []
        dertayande = []
        dertayande1 = []
        for i in range(t):
            for m, n in zip(resp1[i], resp2[i]):
                dertayande1[i] = (m + n) % 2
                dertayande.append(dertayande1[i])
            print(dertayande[i])
            c32i = hashlib.md5()
            c32i.update(str(dertayande[i]).encode())
            c32i = c32i.hexdigest()
            c32.append(c32i)
        com32 = hashlib.md5()
        com32.update(str(c32).encode())
        com32 = com32.hexdigest()
        print(com32)
        print(com2)
        if (com1 == com22 and com2 == com32):
            print("VALID!")
            return 1
        else:
            print("INVALID!")
            return 0


def link_sign(signature1, signature2):
    list1 = signature1.tolist()
    list2 = signature2.tolist()
    intersection = [val for val in list1 if val in list2]
    index = []
    for i in intersection:
        index.append(str(list1.index(i) + 1))
    if (intersection):
        print("Linked!")
        # print("多次投票的人有：")
        # for j in index:
            # print(f'r{j}')
        return len(index),index
    else:
        print("Non-Linked!")
        return (0,["0","1"])


def threshold_Gkey(n, k, w, t):  # 测试用，产生e和s
    H = np.random.randint(0, 2, (n - k, n))
    e = []  # 私钥e，生成门限值t个，每个ei是一个1*n的列表，e是t个ei组成的二维数组，可以通过e[i]访问每个ei
    for i in range(t):
        ei = [1 for _ in range(w)] + [0 for _ in range(n - w)]  # 1*n
        np.random.shuffle(ei)
        # print(ei)
        e.append(ei)  # 存储的每个列是一个ei，可以理解e是一个n*t的矩阵
    # print(e)
    # print(e[1])
    s = []  # 公钥s，生成门限值t个，每个si是一个1*(n-k)的array数组，s存储为二维array数组类型，可以通过s[i]访问每个s[i]
    for i in range(t):
        si = np.dot(H, np.transpose(e[i])) % 2
        s.append(si)
        # print(si)
    s = np.array(s)  # 存储的是每个si的转置的形式，即每行是一个si，可以理解为s是一个t*(n-k)的矩阵
    # print(s)
    return e, s  # 公钥为s，私钥为e，size均为t，列表存储


n = 1268
w = 25
k = 951
t = 300  # 门限值

if __name__ == '__main__':
    # e1, s1 = threshold_Gkey(n, k, w, t)  # 不用管这个函数了，我是测试用
    # H1 = np.random.randint(0, 2, (n - k, n))
    # r1, G1 = gen_r(n, t, e1, s1)
    # com1_1, com2_1, resp1_1, resp2_1 = threshold_GStern_com_resp(n, H1, G1, e1, 0, t)  # 签名模块，承诺&响应
    # # ver1 = threshold_GStern_verify(n, H1, G1, s1, r1, 0, t, com1_1, com2_1, resp1_1,
    # #                                resp2_1)  # 验证模块，返回值是1说明签名为真，返回值是0说明签名为假
    #
    # e2, s2 = threshold_Gkey(n, k, w, t)
    # H2 = np.random.randint(0, 2, (n - k, n))
    # r2, G2 = gen_r(n, t, e2, s2)
    # # com1_2, com2_2, resp1_2, resp2_2 = threshold_GStern_com_resp(n, H2, G2, e2, 0, t)  # 签名模块，承诺&响应
    # # ver2 = threshold_GStern_verify(n, H2, G2, s2, r2, 0, t, com1_2, com2_2, resp1_2,
    #                                # resp2_2)  # 验证模块，返回值是1说明签名为真，返回值是0说明签名为假
    #
    # link = link_sign(r1, r1)  # 如果两个组要被链接，同时输出交集，如果两个组不被链接，输出0【传参的内容是，分别是两个小组的r】
    s=["1","2"]
    print("-".join(s))