# left child, parent, right child


def inOrder(root):
    string = " "
    print(inOrderHelper(root, string).strip())

def inOrderHelper(node, string):
    if(node==None):
        return string

    string = inOrderHelper(node.left, string)
    string = string + str(node.data) + " "
    string = inOrderHelper(node.right, string)

    return string
