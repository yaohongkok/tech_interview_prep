# This is the original approach

dp = {}

def findMinCostForPalindromeSet(s, minCost, cost):
	if(isPalindrome(s)):
		return cost[s]
		
	if(s in dp):
		return dp[s]
	
	allCost = []
	
	#print "For " + s + ":"
	for i in xrange(len(s)-1,0,-1):
		part1 = s[i:len(s)]
		part2 = s[0:i]
		
		cost1 = findMinCostForPalindromeSet(part1, minCost, cost)
		dp[part1] = cost1
		cost2 = findMinCostForPalindromeSet(part2, minCost, cost)
		dp[part2] = cost2
		
		#print (part2, cost2, part1, cost1)
		allCost.append(cost1+cost2)
	
	#print "End of " + s + ":"
	minCost = min(allCost)
		
	
	return minCost
		
def isPalindrome(s):
	return s[::-1]==s


if __name__=="__main__":
	minCost = 99999999999
	cost = {'a':10, 'b':12, 'x': 9, 'bb': 5, 'abba': 2}
	print findMinCostForPalindromeSet('abbax', minCost, cost)
	#print dp

	dp = {}
	cost = {'a':10, 'b':12, 'x': 9, 'bb': 5, 'abba': 2, 'x':52, 'y': 34, \
			'z': 21, 'c':7, 'd':15, 'e':18, 'cdeedc':3, 'deed':2, 'ee':100, \
			'h':5, 's': 9, 'assa':50, 'ss':3, 'aa':6}
	print findMinCostForPalindromeSet("abbaxyzcdeedchsdhaassa", minCost, cost)
	#print dp
