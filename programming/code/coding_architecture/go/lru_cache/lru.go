package lru_cache

import "container/list"

type Entry struct {
    key   int
    value int
}

type LRUCache struct {
    // By storing the element, it enables O(1) read & write
    keyEntryMap map[int]*list.Element
    // Doubly linked list
    orderedValList *list.List
    capacity int
}


func Constructor(capacity int) LRUCache {
    return LRUCache{
        capacity: capacity,
        keyEntryMap: make(map[int]*list.Element),
        orderedValList: list.New(),
    }
}


func (this *LRUCache) Get(key int) int {
    currentElement, ok := this.keyEntryMap[key]

    if !ok {
        return -1
    } else {
        this.orderedValList.MoveToFront(currentElement)

        // Need to assert that element is of type *Entry 
        // to access the value
        return currentElement.Value.(*Entry).value
    }
}


func (this *LRUCache) Put(key int, value int)  {
    currentElement, ok := this.keyEntryMap[key]

    if !ok {
        entry := &Entry{key: key, value: value}
        pushedElement := this.orderedValList.PushFront(entry)
        this.keyEntryMap[key] = pushedElement

        for (this.orderedValList.Len() > this.capacity) {
            lastElement := this.orderedValList.Back()
            key := lastElement.Value.(*Entry).key

            delete(this.keyEntryMap, key)
            this.orderedValList.Remove(lastElement)
        }
    } else {
        this.orderedValList.MoveToFront(currentElement)
        currentElement.Value.(*Entry).value = value
        this.keyEntryMap[key] = currentElement
    }
}
