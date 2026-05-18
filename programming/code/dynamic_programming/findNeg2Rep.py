# you can write to stdout for debugging purposes, e.g.
# print "this is a debug message"

import math
import time

def solution(A):
    # write your code in Python 2.7
    num = convertToNum(A)
    
    oddOrEven = num % 2
    
    rep = [oddOrEven]
    
    return findRepresentation(rep, -num)
    #return findRepresentation2(-num)

def findRepresentation2(B):
	quo = B
	rep = []
	
	while quo:
		quo = quo/(-2)
		rep.append(quo%(-2))
	
	return rep
		

def findRepresentation(rep, B):
    repNum = convertToNum(rep)
    #print rep, repNum, B
    
    if(repNum==B):
        return rep
	
    if(len(rep)>=2*math.log(abs(B),2)):
        return []
      
    guess = findRepresentation(rep + [1], B)
    
    if(guess==[]):
        guess = findRepresentation(rep + [0], B)
    
    return guess

def convertToNum(A):
    num = 0
    
    for i in xrange(0,len(A)):
        num = num + A[i]*(-2)**i
    
    return num

if(__name__ == "__main__"):
	A = [1,0,0,1,1]
	print (convertToNum(A),A)
	A_neg = solution(A)
	print (convertToNum(A_neg),A_neg)
	
