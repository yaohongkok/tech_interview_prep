# Leet Code 33: Search in Rotated Sorted Array

# Key Trick:
# - Find rotated index
#    > When sorted rotated nums[0] > nums[-1]
#    > Many edge conditions to handle to find rotated index
#
# - When list is rotated, slice the list for bisect
# - When nums[-1] to figure out to use left or right side
# - When target could be on the right half, record the offset to be added back to the found index

from bisect import bisect_left

class Solution:
    # If nums is rotated, nums[lo] > nums[hi]
    def find_rotation_idx(self, nums: list[int]) -> int:
        lft = 0
        rgt = len(nums) - 1

        while lft <= rgt:
            # nums is not rotated
            # Should be in loop because splitting
            # can help reach this state faster
            if nums[lft] <= nums[rgt]:
                return lft

            mid = (lft + rgt)//2
            #print(f"{lo}, {mid}, {hi}")
            #print(f"{nums[lo]}, {nums[mid]}, {nums[hi]}")
            #print("===")

            # At the right edge, all we need is nums[mid - 1] > nums[mid]
            if nums[mid - 1] > nums[mid] and mid == rgt:
                return mid
            # The mid num is lower than the left  right neighbor, it is the rotated index
            elif nums[mid-1] > nums[mid] and nums[mid+1] >= nums[mid]:
                return mid
            elif nums[mid] >= nums[lft]:
                lft = mid + 1
            # Rotated index is on the left half
            elif nums[mid] < nums[lft]:
                rgt = mid - 1
            

        raise Error("Unexpected situation.")

    def search(self, nums: list[int], target: int) -> int:
        rot_idx = self.find_rotation_idx(nums)
        #print(f"rot_idx: {rot_idx}")

        if len(nums) == 1:
            return 0 if nums[0] == target else -1

        offset = 0

        if rot_idx != 0:
            if target == nums[-1]:
                return len(nums) - 1
            elif target < nums[-1]:
                nums = nums[rot_idx:]
                offset = rot_idx
            else:
                nums = nums[0:rot_idx]

        insert_idx = bisect_left(nums, target)
        found = insert_idx < len(nums) and nums[insert_idx] == target

        if found:
            return insert_idx + offset
        else:
            return -1