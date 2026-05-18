def solution(arr):
	if(len(arr) < 2):
		return ""
	
	leftTotal = traverseAndAdd(1, arr, 0)
	rightTotal = traverseAndAdd(2, arr, 0)
	
	if(leftTotal > rightTotal):
		return "Left"
	elif(leftTotal < rightTotal):
		return "Right"
	else:
		return ""

def traverseAndAdd(idx, arr, total):
	if(idx >= len(arr)):
		return total
	
	if(arr[idx] >= 0):
		total = total + arr[idx]
	
	leftChildIndex = getLeftChildIndex(idx)
	rightChildIndex = getRightChildIndex(idx)
	
	total = traverseAndAdd(leftChildIndex, arr, total)
	total = traverseAndAdd(rightChildIndex, arr, total)
	
	return total

def getLeftChildIndex(idx):
	return idx*2 + 1
	
def getRightChildIndex(idx):
	return idx*2 + 2
	
if __name__ == "__main__":
	#arr = [1,2,3,4,5,6,7]
	#arr = [1]
	#arr = [1,5,3]
	arr = [1,2,3,4,5,6,-1]
	print(solution(arr))
	
