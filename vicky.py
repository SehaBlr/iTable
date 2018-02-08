import time



def func(n):
	l = [2,3]
	for i in range(3,n):
		for j in l:
			if i%j==0:
				break
		else:
			l.append(i)
	print(l)




def prst(iter):
    list=[]
    for i in range(2,iter):
        list.append(i)

    for j in list:
        for i in range(2,iter):
            if j*i<iter:
                try:
                    list.remove(j*i)
                except:
                    pass
            else:
                break
    print(list)




a = time.clock()
prst(100)

b =time.clock()

func(100)
c =time.clock()

print(b-a)
print(c-b)