def Reverse(head):
	if(head.next==None):
		head.prev = None
		return head
	
	nextNode = head.next
	curNode = head
	curNode.next = None
	curNode.prev = nextNode
	
	head = Reverse(nextNode)
	# NextNode needs to be here to ensure there is no cyclic linked list
	nextNode.next = curNode
	
	return head
  
