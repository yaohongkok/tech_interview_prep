# You are given coins of different denominations and a total amount of money amount. 
# Write a function to compute the fewest number of coins that you need to make up that amount. 
# If that amount of money cannot be made up by any combination of the coins, return -1.
#
# Input: coins = [1, 2, 5], amount = 11
# Output: 3 
# Explanation: 11 = 5 + 5 + 1

class Solution(object):
    def coinChange(self, coins, amount):
        """
        :type coins: List[int]
        :type amount: int
        :rtype: int
        """
        coins = sorted(coins)
        minNumCoins = amount//coins[0] + 1
        return self.helper(coins,amount,0, minNumCoins)
        
    def helper(self,coins,amount,numCoins, minNumCoins):
        if(amount==0):
            return numCoins
        
        if(amount<0 or coins==[] or numCoins>=minNumCoins):
            return -1
        
        oldMinNumCoins = minNumCoins
        maxNumCoinsForLargestCoin = amount//coins[len(coins)-1]
        
        for i in xrange(maxNumCoinsForLargestCoin,-1,-1):
            #print (amount,numCoins,minNumCoins)
            newNumCoins = numCoins + i
            remainder = amount - i*coins[len(coins)-1]
            
            if(newNumCoins<=minNumCoins):
				someNumCoins = self.helper(coins[0:len(coins)-1],remainder,newNumCoins,minNumCoins)
            else:
				break
            
            #>=0 because -1 means it is not a possible solution
            if(someNumCoins<minNumCoins and someNumCoins>=0):
                minNumCoins = someNumCoins
            elif(someNumCoins>=minNumCoins):
                break
            
        if(oldMinNumCoins == minNumCoins):
            return -1
        else:
            return minNumCoins
