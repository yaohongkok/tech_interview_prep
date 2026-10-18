# Leetcode 91: Decoded ways

# Key Tricks:
#  - Bellman
#  - Handle special cases of 
#
# f(i) = 
#   1. f(i+1), when 3 <= s[i] <= 9
#   2. 0, when s[i] = 0
#   3. f(i+1) + f(i+2), when  s[i] == 1
#   4. When s[i] == 2:
#     a) f(i+1) + f(i+2), when 0 <= s[i] <= 6
#     b) f(i+1), when s[i] >= 7
#
# Base case:
#   > f(>=len(s) - 1) = 1

from functools import lru_cache

class Solution:
    @lru_cache(maxsize=None)
    def _f(self, i: int, s:str) -> int:
        if i < len(s) and s[i] == '0':
            return 0

        if i >= len(s) - 1:
            return 1
        else:
            # s[i] will never be last character
            if s[i] >= '3' and s[i] <= '9':
                return self._f(i + 1, s)
            elif s[i] == '1':
                return self._f(i + 1, s) + self._f(i + 2, s)
            elif s[i] == '2':
                # 20 to 26 can splitted
                if s[i+1] >= '0' and s[i+1] <= '6':
                    return self._f(i + 1, s) + self._f(i + 2, s)
                # 27 onwards cannot be splitted
                elif s[i+1] >= '7':
                    return self._f(i + 1, s)

        raise RuntimeError('Unexpected scenario...')

    def numDecodings(self, s: str) -> int:
        return self._f(0, s)
        


