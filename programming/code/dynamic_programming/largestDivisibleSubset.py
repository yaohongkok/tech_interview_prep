"""
Given a set of distinct positive integers, find the largest subset such 
that every pair (Si, Sj) of elements in this subset satisfies: Si % Sj = 0 
or Sj % Si = 0.
"""

class Solution(object):
    
    def largestDivisibleSubset(self, nums):
        """
        :type nums: List[int]
        :rtype: List[int]
        """
        size = len(nums)
        if(size <=1) :
            return nums
        nums.sort()
        print(nums)
        
        # f is the max count of pairs that are divisible
        f = [ 1 for i in range(size)]
        
        # This is where DP happens
        # Assume n > k, thus nums[n] > nums[k]
        # If k can form f[k] pairs with other numbers,
        # Then, when nums[n]%nums[k] == 0, then f[n] = max(f[n], f[j] + 1)
        # The max function serves as a way to prevent smaller count to overwrite the
        # bigger
        for i in range(1,size):
            print("=============")
            print("i: " + str(i))
            print("nums[i]: " + str(nums[i]))
            for j in range(i):
                if(nums[i] % nums[j] == 0):
                    f[i] = max(f[i], f[j]+1)
                    print("j: " + str(j))
                    print("nums[j]: " + str(nums[j]))
                    print("f: " + str(f))
        
        # Next, find index with largest numbers of pairs
        length = max(f)
        index = 0
        for i in range(size):
            if (f[i] == length):
                index = i
                break
                
        # Creation of the subset
        res = []
        temp = nums[index]
        tempf = f[index]
        for j in range(index,-1,-1):
            if temp%nums[j]==0 and tempf == f[j]:
                res.append(nums[j])
                temp = nums[j]
                tempf = tempf - 1
        
        print("<<<<<END>>>>>")
        return res

if __name__ == "__main__":
    nl = [2,3,5,6,7,12]
    print(Solution().largestDivisibleSubset(nl))