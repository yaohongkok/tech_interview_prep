# Leet Code 56. Merge Intervals

# Key tricks:
# - Sort intervals by the left
# - Use a reference interval that can grow by merging
# - If overlap, take the max of the right
#     No need to worry about left as it is sorted.
# - If no overlap, the current interval is the new reference
# - Push the ref interval at the end


class Solution:
    def merge(self, intervals: list[list[int]]) -> list[list[int]]:
        results = []

        sorted_intvs = sorted(intervals, key=lambda x: x[0])

        ref_intv = sorted_intvs.pop(0)

        for cur_intv in sorted_intvs:
            ref_intv_right = ref_intv[1]
            cur_intv_left = cur_intv[0]

            # Merge by picking the largest right boundary
            # Since it is sorted, we don't need to worry about the left
            if cur_intv_left <= ref_intv_right:
                ref_intv[1] = max(ref_intv[1], cur_intv[1])
            else:
                results.append(ref_intv)
                ref_intv = cur_intv

        # Need to append one last time
        results.append(ref_intv)

        return results
