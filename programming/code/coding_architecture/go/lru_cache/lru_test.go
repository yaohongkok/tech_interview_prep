package lru_cache

import (
    "testing"
)

func TestLRUCache(t *testing.T) {
    // 1. Initialize Cache with capacity 2
    cache := Constructor(2)

    // 2. Test Put and Get
    cache.Put(1, 1)
    cache.Put(2, 2)
    
    if val := cache.Get(1); val != 1 {
        t.Errorf("Expected 1, got %d", val)
    }

    // 3. Test Eviction
    // Putting 3 should evict key 2 (because key 1 was recently accessed)
    cache.Put(3, 3)
    
    if val := cache.Get(2); val != -1 {
        t.Errorf("Expected -1 (evicted), got %d", val)
    }

    // 4. Test Update existing key
    // Putting 4 should evict key 1
    cache.Put(4, 4)
    
    if val := cache.Get(1); val != -1 {
        t.Errorf("Expected -1 (evicted), got %d", val)
    }
    
    if val := cache.Get(3); val != 3 {
        t.Errorf("Expected 3, got %d", val)
    }
    
    if val := cache.Get(4); val != 4 {
        t.Errorf("Expected 4, got %d", val)
    }
}

func TestLRUOverlap(t *testing.T) {
    cache := Constructor(2)
    cache.Put(2, 1)
    cache.Put(1, 1)
    cache.Put(2, 3) // Update existing key 2
    cache.Put(4, 1) // Should evict key 1, NOT key 2

    if val := cache.Get(1); val != -1 {
        t.Errorf("Key 1 should have been evicted, got %d", val)
    }
    if val := cache.Get(2); val != 3 {
        t.Errorf("Key 2 should be 3, got %d", val)
    }
}