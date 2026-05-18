# A:          a1 → a2
#                   ↘
#                     c1 → c2 → c3
#                   ↗            
# B:     b1 → b2 → b3

class Solution(object):
    def getIntersectionNode(self, headA, headB):
        """
        :type head1, head1: ListNode
        :rtype: ListNode
        """
        
        lenA = 0
        lenB = 0
        
        oldHeadA = headA
        oldHeadB = headB
        
        while(headA!=None):
            lenA = lenA + 1
            headA = headA.next
        
        while(headB!=None):
            lenB = lenB + 1
            headB = headB.next
        
        headA = oldHeadA
        headB = oldHeadB
        
        diffLen = lenB - lenA
        
        for i in xrange(0,abs(diffLen)):
            if (diffLen>0):
                headB = headB.next
            else:
                headA = headA.next
        
        while(headA!=None):
            if(headA is headB):
                return headA
            
            headA = headA.next
            headB = headB.next
        
        return None
