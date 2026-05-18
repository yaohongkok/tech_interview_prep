# s = "3[a]2[bc]", return "aaabcbc".
# s = "3[a2[c]]", return "accaccacc".
# s = "2[abc]3[cd]ef", return "abcabccdcdcdef".

class Solution(object):
    def unZip(self, s, i):
        ss = ""
        
        while i < len(s):
            if s[i] in "123456789":
                j = i + 1
                while j < len(s) and s[j] in "0123456789":
                    j += 1
                n = int(s[i:j])                
                substr, k = self.unZip(s, j + 1)
                ss += n * substr
                i = k
                continue
            if s[i] == "]":
                return ss, i + 1
            ss += s[i]
            i += 1
            
        return ss, i
    
    def decodeString(self, s):
        """
        :type s: str
        :rtype: str
        """
        return self.unZip(s, 0)[0]
