# left child, right child, parent

def postOrder(root):
    string = ""
    print(postOrderHelper(root, string).strip())

def postOrderHelper(node, string):
    if(node==None):
        return string

    string = postOrderHelper(node.left, string)
    string = postOrderHelper(node.right, string)
    string = string + str(node.data) + " "

    return string