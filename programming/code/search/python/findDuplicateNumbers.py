# Given an array nums containing n + 1 integers where each integer is 
# between 1 and n (inclusive), prove that at least one duplicate number 
# must exist. Assume that there is only one duplicate number, 
# find the duplicate one.

# Input: [1,3,4,2,2]
# Output: 2

class Solution(object):
    def findDuplicate(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """
        
        lo = 1
        hi = len(nums)-1
        
        while(hi>lo):
            mid = (hi+lo)//2
            
            countOfMid = 0
            
            # count elements than are less than or equal to mid
            for i in xrange(0,len(nums)):
                if(nums[i]<=mid):
                    countOfMid += 1
            
            # Think of it as trying to find a list with max of mid, that
            # satisfy the condition of having a length of at least mid + 1
            if(countOfMid>mid):
                hi = mid
            else:
                lo = mid+1
        
        return hi
            
##################
# Other solutions
###################

class Solution(object):
    def findDuplicate(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """
        return (sum(nums) - sum(set(nums)))/(len(nums)-len(set(nums)))
        


##############################################
# An example to help understand.
# suppose we have 5 integers: 1,3,1,4,2, and we start to jump from index:0

# So the jumping sequence will be liked this: 1(jump to index 1) -> 3 (jump to index 3, so next is 4) -> 4 -> 2 -> 1 (formed a cycle here)
# From this we can see the entry point of the cycle is the duplicated one.

# Another Rho-shape example: 2,3,4,1,1
# The jumping sequence will be liked this:
# 2 -> 4 ->1->3->1(formed a cycle here) : Non-cycle part is : 2->4 and cycle part is: 1->3
# Again the entry point "1" is the duplicated number.

# From now on we can follow the strategy of linked-list problem to solve it.

int findDuplicate3(vector<int>& nums)
{
	if (nums.size() > 1)
	{
		int slow = nums[0];
		int fast = nums[nums[0]];
		
		# Initially, try to get the slow pointer into the loop
		while (slow != fast)
		{
			slow = nums[slow];
			fast = nums[nums[fast]];
		}

		# Once the slow pointer is in the loop, we reuse the fast pointer
		# as a slow one but start from 0. When the new pointer meets the
		# slow one in the loop, it will be the repeated number.
		fast = 0;
		while (fast != slow)
		{
			fast = nums[fast];
			slow = nums[slow];
		}
		return slow;
	}
	return -1;
}
