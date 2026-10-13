from collections import OrderedDict

class LRUCache:

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.oDict = OrderedDict()
        

    def get(self, key: int) -> int:
        if key not in self.oDict:
            return -1
        else:
            # Move the key to the end to 
            # show that it was recently used
            self.oDict.move_to_end(key)
            return self.oDict[key]
        

    def put(self, key: int, value: int) -> None:
        if key not in self.oDict:
            # New items are added to the right of OrderedDict, 
            # which is the most recently used side
            self.oDict[key] = value

            while(len(self.oDict) > self.capacity):
                # last=False means pop the first item (least recently used)
                self.oDict.popitem(last=False)
        else:
            self.oDict[key] = value
            self.oDict.move_to_end(key)


def main():
    # LeetCode 146 example
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1
    cache.put(3, 3)                 # evicts key 2
    assert cache.get(2) == -1
    cache.put(4, 4)                 # evicts key 1
    assert cache.get(1) == -1
    assert cache.get(3) == 3
    assert cache.get(4) == 4

    # Missing key on an empty cache
    cache = LRUCache(1)
    assert cache.get(99) == -1

    # Capacity 1: every new key evicts the previous one
    cache.put(1, 10)
    cache.put(2, 20)
    assert cache.get(1) == -1
    assert cache.get(2) == 20

    # Updating an existing key changes the value without evicting
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.put(1, 100)
    assert cache.get(1) == 100
    assert cache.get(2) == 2
    assert len(cache.oDict) == 2

    # Updating an existing key refreshes its recency
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.put(1, 11)                # key 2 is now least recently used
    cache.put(3, 3)                 # evicts key 2
    assert cache.get(2) == -1
    assert cache.get(1) == 11
    assert cache.get(3) == 3

    # get refreshes recency
    cache = LRUCache(3)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.put(3, 3)
    cache.get(1)                    # order is now 2, 3, 1
    cache.put(4, 4)                 # evicts key 2
    assert cache.get(2) == -1
    assert cache.get(1) == 1
    assert cache.get(3) == 3
    assert cache.get(4) == 4

    print("All tests passed")


if __name__ == "__main__":
    main()