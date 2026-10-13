# LC 560
# Subarray Sum Equals K

from itertools import accumulate

class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:
        sum_eq_k_count = 0

        accum_sum = list(accumulate(nums))
        accum_sum_idx_dict = {}

        for i, total in enumerate(accum_sum):
            accum_sum_idx_dict.setdefault(total, []).append(i)

        for n, cur_total in enumerate(accum_sum):
            if cur_total == k:
                sum_eq_k_count += 1

            target = cur_total - k
            potential_idx = accum_sum_idx_dict.get(target, [])
            valid_idx = [x for x in potential_idx if x < n]

            if len(potential_idx) > 0:
                sum_eq_k_count = sum_eq_k_count + len(valid_idx)

        return sum_eq_k_count
