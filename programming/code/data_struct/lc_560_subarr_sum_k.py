# LC 560
# Subarray Sum Equals K

# Key Trick:
# - Use accumulate sum to find the sum of subarray in O(1) time.
# - Create a dictionary to store the accumulate sum and 
#     the indices where that accumulate sum occurs.
# - Two cases which we increment count:
#   1. Current accumulate sum (from 0 to n) is equal to k
#   2. Diff between current accumulate sum and k is present in the dictionary. 
#        Only count the indices which are less than current index, 
#        because we want to find the subarray sum from 0 to n.

# Not the fully optimized solution. But, easy to understand and implement.
# Can build a more optimized solution using a single pass and 
# a dictionary to store the accumulate sum and its count.

from itertools import accumulate

class Solution:
    # Create accumulate sum idx dictionary, 
    # where key is the accumulate sum and 
    # value is the list of indices where that accumulate sum occurs.
    def create_accum_sum_idx_dict(self, accum_sum: list[int]) -> dict[int, list[int]]:
        accum_sum_idx_dict = {}

        for i, total in enumerate(accum_sum):
            accum_sum_idx_dict.setdefault(total, []).append(i)

        return accum_sum_idx_dict

    def subarraySum(self, nums: List[int], k: int) -> int:
        sum_eq_k_count = 0

        accum_sum = list(accumulate(nums))

        accum_sum_idx_dict:dict[int, list[int]] \
            = self.create_accum_sum_idx_dict(accum_sum)

        for n, cur_total in enumerate(accum_sum):
            # Case #1 to increment count:
            # Current accumulate sum (from 0 to n) is equal to k
            if cur_total == k:
                sum_eq_k_count += 1

            # Case #2 to increment count:
            # Diff between current accumulate sum and k is present in the dictionary.
            # Only count the indices which are less than current index
            target = cur_total - k
            potential_idx = accum_sum_idx_dict.get(target, [])
            valid_idx = [i for i in potential_idx if i < n]

            if len(potential_idx) > 0:
                sum_eq_k_count = sum_eq_k_count + len(valid_idx)

        return sum_eq_k_count
