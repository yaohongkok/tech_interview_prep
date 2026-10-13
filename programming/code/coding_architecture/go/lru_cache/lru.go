package lru_cache

/*
LeetCode 146. LRU Cache

Key Tricks:
1. Need a map (or dict) plus list
2. In Get, need to move element to front of list when found
3. When Putting new element:
    a. Create entry
    b. Push to front of list
    c. Store list element in map
    4. If list length exceeds capacity, remove last element from list and map
4. When Putting existing element:
    a. Move element to front of list
    b. Update value in entry
*/

import "container/list"

type Entry struct {
	key   int
	value int
}

type LRUCache struct {
	// By storing the element, it enables O(1) read & write
	keyEntryListElmtMap map[int]*list.Element
	// Doubly linked list
	orderedValList *list.List
	capacity       int
}

func Constructor(capacity int) LRUCache {
	return LRUCache{
		capacity:            capacity,
		keyEntryListElmtMap: make(map[int]*list.Element),
		orderedValList:      list.New(),
	}
}

func (this *LRUCache) Get(key int) int {
	curListElement, ok := this.keyEntryListElmtMap[key]

	if !ok {
		return -1
	} else {
		this.orderedValList.MoveToFront(curListElement)

		// Need to assert that element is of type *Entry
		// to access the value
		return curListElement.Value.(*Entry).value
	}
}

func (this *LRUCache) Put(key int, value int) {
	curListElement, ok := this.keyEntryListElmtMap[key]

	if !ok {
		entry := &Entry{key: key, value: value}
		pushedListElement := this.orderedValList.PushFront(entry)
		this.keyEntryListElmtMap[key] = pushedListElement

		for this.orderedValList.Len() > this.capacity {
			lastElement := this.orderedValList.Back()
			key := lastElement.Value.(*Entry).key

			delete(this.keyEntryListElmtMap, key)
			this.orderedValList.Remove(lastElement)
		}
	} else {
		this.orderedValList.MoveToFront(curListElement)
		curListElement.Value.(*Entry).value = value
		this.keyEntryListElmtMap[key] = curListElement
	}
}
