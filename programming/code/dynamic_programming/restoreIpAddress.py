class Solution(object):
    def restoreIpAddresses(self, s):
        """
        :type s: str
        :rtype: List[str]
        """
        r = self.helper(s,1)
        
        if(r==None):
            return []
        
        return r
    
    def helper(self, s, level):
        if(level>4):
            return None
        
        if( (level==4 and len(s)<=0) or \
            (level==3 and len(s)<=1) or \
            (level==2 and len(s)<=2) or \
            (level==1 and len(s)<=3)):
            return None
        
        if(level==4 and (len(s)>=1 and len(s)<=3)):
            part = int(s)
            
            if(part>255):
                return None
            
            if(len(str(part))!=len(s)):
                return None
            
            return [s]
            
        
        res = []
        for i in xrange(3,0,-1):
            part = int(s[0:i])
            
            if(part>255):
                continue
            
            if(len(str(part))!=len(s[0:i])):
                continue
            
            temp = self.helper(s[i:],level+1)
            
            if temp == None:
                continue
            
            for j in xrange(0,len(temp)):
                res.append(s[0:i] + "." + temp[j])
        
        if res == []:
            return None
        
        return res
