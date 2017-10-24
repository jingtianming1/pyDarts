
import numpy as np
from  sklearn.externals import joblib



#values必须转化成np.array
class DoubleArrayTrie(object):

    __slots__ = ['check','used','base','size','allowSize','error','keys','values','lengths','nextCheckPos','keySize','progress'
                 'vaues','progress']

    def __init__(self):
        self.check = np.zeros(shape=[100],dtype=np.int32)

        self.base = np.zeros(shape=[100],dtype=np.int32)
        self.used = np.zeros(shape=[100],dtype=np.bool)
        self.size = 0
        self.allowSize  = 0
        self.error = 0
        self.keys = []
        self.values = None
        self.lengths = None
        self.nextCheckPos = 0

        self.keySize = 0

        self.progress = 0

    #必须按照字典顺序排列好
    def __build(self,keys,values,lengths=None):

        self.keys = keys

        self.values = values
        self.lengths = lengths
        self.keySize = len(keys)

        self.progress = 0

        self.__resize(32 * 256 * 256)

        self.base[0] = 1

        rootNode = self.Node()
        rootNode.left = 0
        rootNode.right = self.keySize
        rootNode.depth = 0

        childNodes = []
        self.__fetch(rootNode, childNodes)
        self.__insert(childNodes)


    def build(self,dic):

        values = [dic[k] for k in sorted(dic.keys())]
        keys = [k for k in sorted(dic.keys())]
        values  = np.array(values)
        self.__build(keys=keys,values=values)

    def __insert(self, childNodes):


        first = 0
        pos = max(childNodes[0].code+1,self.nextCheckPos)  -1
        begin = 0
        nonzero_num= 0


        while(True):
            pos +=1
            if(self.allowSize<pos):
                self.__resize(pos)
            if self.check[pos] !=0:
                nonzero_num+=1
                continue
            elif first==0:
                first = 1
                self.nextCheckPos = pos


            begin = pos - childNodes[0].code

            if self.allowSize < begin+childNodes[-1].code:
                expand_size = 1.05 * self.keySize / (self.progress + 1)

                self.__resize(expand_size * self.allowSize)

            if self.used[begin] == True:
                continue

            for i in range(0,len(childNodes)):
                result = True
                if self.check[begin+childNodes[i].code] !=0:    #如果不满足这个条件，跳出这层循环，如果满足，外层循环结束
                    break
            else:

                break






         # 从位置 next_check_pos 开始到 pos 间，如果已占用的空间在95%以上，
         # 下次插入节点时，直接从 pos 位置处开始查找
        if (1.0 * nonzero_num / (pos - self.nextCheckPos + 1) >= 0.95):
            self.nextCheckPos = pos


        self.size = self.size if self.size>begin+childNodes[-1].code+1 else begin+childNodes[-1].code+1



        self.used[begin] = True

        for i in range(len(childNodes)):
            self.check[begin+childNodes[i].code] = begin

        for i in range(len(childNodes)):

            newNodes = []

            if self.__fetch(childNodes[i], newNodes)  ==0:

                self.base[childNodes[i].code+begin] = -childNodes[i].left-1
                self.progress +=1

            else:


                h = self.__insert(newNodes)

                self.base[childNodes[i].code+begin] = h

        return  begin


    #  pos表示字符串的第几个，例如我爱佩佩去匹配佩佩，那么pos要输入2
    #
    # nodePos 如果不为0，那么可以从当前节点接着去查找

    def exactMatchSearch(self,key ,pos=0,keylen=0,nodePos=0):
        if (keylen <= 0):
            keylen = len(key)
        if (nodePos <= 0):
            nodePos = 0
        result = -1
        b = self.base[nodePos]
        p = 0
        for i in range(pos,len(key)):
            p = b + ord(key[i]) + 1    #   67   136
            if self.check[p] == b:
                b = self.base[p]    # 68       69

            else:
                return  result

        p = b   #    69
        if(b==self.check[p] and self.base[p]<0):
            result = -self.base[p] -1

        return  result




    def commonPrefixSearchWithValue(self,key,pos = 0,length = 0):

        if length<=0:
            length = len(key)

        indexes = []
        p=0
        b = self.base[0]

        for i in range(pos,length):

            p = b + ord(key[i]) +1

            if self.check[p] ==b:
                b = self.base[p]
            else:
                return self.values[indexes]

            p = b     #68
            if  b==self.check[p] and self.base[p]<0:
                index  = -self.base[p] -1
                indexes.append(index)

        return self.values[indexes]


    #查询目标字符串中所有键
    def serarch(self,key,length = 0):

        if length<=0:
            length = len(key)

        indexes = []

        for pos in range(length):

            p = 0
            b = self.base[0]
            for i in range(pos, length):

                p = b + ord(key[i]) + 1

                if self.check[p] == b:
                    b = self.base[p]
                else:
                    break

                p = b  # 68
                if b == self.check[p] and self.base[p] < 0:
                    index = -self.base[p] - 1
                    indexes.append(index)

        return self.values[indexes]


    #以返回star，end，name，value
    def Search_word(self,key,length = 0):
        if length<=0:
            length = len(key)
        values = []
        for pos in range(length):
            starIndex = -1
            p = 0
            b = self.base[0]
            for i in range(pos, length):

                p = b + ord(key[i]) + 1

                if self.check[p] == b:

                    b = self.base[p]

                    if starIndex==-1:
                        starIndex=i
                else:

                    break

                p = b  # 68
                if b == self.check[p] and self.base[p] < 0:
                    index = -self.base[p] - 1

                    word = self.Word(_star=starIndex, _end=i + 1, _value=self.values[index], _name=self.keys[index])

                    values.append(word)

        return values




    #最大词匹配，例如有AC，A,C，则只添加AC
    def maxLenSearch(self,key,length=0):
        if length<=0:
            length = len(key)
        values = []
        for pos in range(length):
            starIndex = -1
            p = 0
            b = self.base[0]
            for i in range(pos, length):

                p = b + ord(key[i]) + 1

                if self.check[p] == b:

                    b = self.base[p]

                    if starIndex==-1:
                        starIndex=i
                else:
                    break

                p = b  # 68
                if b == self.check[p] and self.base[p] < 0:
                    index = -self.base[p] - 1

                    #例如有A与AC,   AC包含A，那么不添加A
                    if len(values) !=0 and values[-1].star==starIndex:
                        values.pop()

                    # 例如有C与AC,   AC包含C，那么不添加C
                    if len(values) !=0 and values[-1].end==i+1:
                        continue


                    word = self.Word(_star=starIndex, _end=i + 1, _value=self.values[index], _name=self.keys[index])

                    values.append(word)

        return values



    def __fetch(self, parentNode, childNodes):

        prev = 0

        for i in range(parentNode.left,parentNode.right):

            if parentNode.depth>len(self.keys[i]):
                continue
            cur = 0
            tem = self.keys[i]
            if parentNode.depth< len(self.keys[i]):
                cur = ord(tem[parentNode.depth])+1

                if(prev>cur):
                    self.error = -3
                    return 0



            if cur!=prev or len(childNodes)==0:
                temNode = self.Node()

                temNode.depth = parentNode.depth+1
                temNode.left = i
                temNode.code = cur
                if len(childNodes)!=0:
                    childNodes[-1].right = i

                childNodes.append(temNode)
                prev = cur

        if len(childNodes)!=0:
            childNodes[-1].right = parentNode.right

        return len(childNodes)


    def __resize(self, newsize):


        size = self.base.size

        newbase =  np.hstack([self.base, np.zeros(shape=[newsize-size],dtype=np.int32)])

        newcheck = np.hstack([self.check,np.zeros(shape=[newsize-size],dtype=np.int32)])
        newused = np.hstack([self.used, np.zeros(shape=newsize-size,dtype=np.bool)])

        self.used = newused
        self.base = newbase
        self.check = newcheck
        self.allowSize = newsize
        return newsize


    def save(self):

        joblib.dump(self,filename='collo.m')

    def load(self,fileName):
        return joblib.load(fileName)
    class Node():
        __slots__ = ['left','right','depth','code']
        def __init__(self):
            self.left  = 0
            self.right = 0
            self.depth = 0
            self.code = 0


    class Word():
        __slots__ = ['value','star','end','name']
        def __init__(self,_value,_star,_end,_name):


            self.value =_value
            self.star = _star
            self.end = _end
            self.name = _name
        def __str__(self):

            tostring = 'value : %s   name  :%s   star : %d   end : %d'%(str(self.value),self.name,self.star,self.end)

            return tostring

