# parent, left child, right child

def preOrder(root):
    #Write your code here
	outStr = ""
	print(preOrderHelper(root, outStr).strip())

def preOrderHelper(node, outStr):
	if(node == None):
		return outStr

	outStr = outStr + str(node.data) + " "
	outStr = preOrderHelper(node.left, outStr)
	outStr = preOrderHelper(node.right, outStr)

	return outStr