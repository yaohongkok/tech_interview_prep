// go test .

package rate_limiter

import (
	"context"
	"net/http"
	"net/http/httptest"
	"sync"
	"testing"
	"time"
)

func TestLocalIPRateLimiter(t *testing.T) {
	// Setup constants
	limit := 5
	window := 1 * time.Second

	// Initialize Store and Limiter
	store := NewLocalLimitStore(limit, window)
	go store.counters.Start() // Start the ttlcache cleanup goroutine
	defer store.counters.Stop()

	limiter := NewLocalIPRateLimiter(store)

	// Mock next handler
	nextHandler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	})

	handlerToTest := limiter.ProceedOrReject(nextHandler)

	t.Run("Happy Path: Allow requests under limit", func(t *testing.T) {
		for i := 0; i < limit; i++ {
			req := httptest.NewRequest("GET", "http://localhost", nil)
			req.RemoteAddr = "1.1.1.1"
			rr := httptest.NewRecorder()

			handlerToTest.ServeHTTP(rr, req)

			if status := rr.Code; status != http.StatusOK {
				t.Errorf("request %d: expected status 200, got %v", i+1, status)
			}
		}
	})

	t.Run("Edge Case: Reject request exactly over limit", func(t *testing.T) {
		req := httptest.NewRequest("GET", "http://localhost", nil)
		req.RemoteAddr = "1.1.1.1" // Same IP
		rr := httptest.NewRecorder()

		handlerToTest.ServeHTTP(rr, req)

		if status := rr.Code; status != http.StatusTooManyRequests {
			t.Errorf("expected status 429, got %v", status)
		}
	})

	t.Run("Edge Case: Different IP has its own quota", func(t *testing.T) {
		req := httptest.NewRequest("GET", "http://localhost", nil)
		req.RemoteAddr = "2.2.2.2" // New IP
		rr := httptest.NewRecorder()

		handlerToTest.ServeHTTP(rr, req)

		if status := rr.Code; status != http.StatusOK {
			t.Errorf("expected status 200 for new IP, got %v", status)
		}
	})

	t.Run("Edge Case: Concurrency Safety", func(t *testing.T) {
		// New IP for fresh test
		ip := "3.3.3.3"
		var wg sync.WaitGroup
		concurrentRequests := 10
		results := make(chan int, concurrentRequests)

		for i := 0; i < concurrentRequests; i++ {
			wg.Add(1)
			go func() {
				defer wg.Done()
				req := httptest.NewRequest("GET", "/", nil)
				req.RemoteAddr = ip
				rr := httptest.NewRecorder()
				handlerToTest.ServeHTTP(rr, req)
				results <- rr.Code
			}()
		}

		wg.Wait()
		close(results)

		successCount := 0
		blockedCount := 0
		for res := range results {
			if res == http.StatusOK {
				successCount++
			} else if res == http.StatusTooManyRequests {
				blockedCount++
			}
		}

		if successCount != limit {
			t.Errorf("expected exactly %d successful requests, got %d", limit, successCount)
		}
	})

	t.Run("Edge Case: Reset after window expires", func(t *testing.T) {
		if testing.Short() {
			t.Skip("skipping time-based test in short mode")
		}

		ip := "4.4.4.4"
		// Fill the quota
		for i := 0; i < limit; i++ {
			param := RateLimitParam{RateLimitKey: ip, Context: context.Background()}
			store.Allow(param)
		}

		// Wait for TTL to expire
		time.Sleep(window + 100*time.Millisecond)

		// Should be allowed again
		param := RateLimitParam{RateLimitKey: ip, Context: context.Background()}
		allowed, _ := store.Allow(param)
		if !allowed {
			t.Error("expected request to be allowed after window expiration")
		}
	})
}