# This is the different approach of generating all palindrome sets
# and calculating the cost for each set

# You can noticed that the minimum cost for both approaches are the same

import copy

def getPalindromeElements(s):
	palindromePos = [[False]*len(s) for i in xrange(0,len(s))]
	
	for i in xrange(0,len(s)):
		for j in xrange(i,len(s)):
			if(isPalindrome(s[i:j+1])):
				palindromePos[i][j] = True
				
	return palindromePos		

def isPalindrome(s):
	return s[::-1]==s

result = []

def genPalindromeSet(s, index, palindromePos, subset):
	if(index==len(s)):
		result.append(copy.deepcopy(subset))
		return
	
	for i in xrange(index,len(s)):
		if(palindromePos[index][i]==True):
			subset.append(s[index:i+1])
			genPalindromeSet(s, i+1, palindromePos, subset)
			del subset[-1]
			

def findMinForCost(palindromeSet, costFunc):	
	minCost = 999999
	
	for eachSet in palindromeSet:
		cost = 0
		
		for eachStr in eachSet:
			# f is the cost
			# Assuming f throws error if it sees a non-palindrome
			# Although this will never happen using this algorithm
			cost = cost + costFunc[eachStr]

	
		minCost = min(cost,minCost)
	
	return minCost

if (__name__ == "__main__"):
	s = "abbax"
	palindromePos = getPalindromeElements(s)
	genPalindromeSet(s, 0, palindromePos, [])
	cost = {'a':10, 'b':12, 'x': 9, 'bb': 5, 'abba': 2}
	print result
	print findMinForCost(result, cost)
	
	result = []
	s = "abbaxyzcdeedchsdhaassa"
	palindromePos = getPalindromeElements(s)
	genPalindromeSet(s, 0, palindromePos, [])
	cost = {'a':10, 'b':12, 'x': 9, 'bb': 5, 'abba': 2, 'x':52, 'y': 34, \
			'z': 21, 'c':7, 'd':15, 'e':18, 'cdeedc':3, 'deed':2, 'ee':100, \
			'h':5, 's': 9, 'assa':50, 'ss':3, 'aa':6}
	print result
	print findMinForCost(result, cost)
