# Leet Code 32: Longest Valid Parentheses

# Key trick:
# - Count length from boundary to current index
# - Two types of boundaries:
#   1. Last unmatched right parenthesis index (when stack is empty)
#   2. Last unmatched left parenthesis index (tracked by stack)

class Solution:
    def longestValidParentheses(self, s: str) -> int:
        leftPrthIdxStack = []
        lastUnmatchedRightIdx = -1

        maxValidCharCount = 0

        for i in range(len(s)):
            if s[i]==')':
                if len(leftPrthIdxStack) > 0:
                    leftPrthIdxStack.pop()

                    if len(leftPrthIdxStack) > 0:
                        # Boundary 1 = Last unmatched left parenthesis index
                        boundary = leftPrthIdxStack[-1]
                    else:
                        # Boundary 2 = Last unmatched right parenthesis index
                        boundary = lastUnmatchedRightIdx

                    curCharCount = i - boundary
                    maxValidCharCount = max(maxValidCharCount, curCharCount)
                else:
                    # There is an unmatched right parenthesis, 
                    # update the last unmatched right parenthesis index
                    lastUnmatchedRightIdx = i
            elif s[i]=='(':
                leftPrthIdxStack.append(i)


        return maxValidCharCount