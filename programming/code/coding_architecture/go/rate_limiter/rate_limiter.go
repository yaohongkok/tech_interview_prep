package rate_limiter

	
import (
	"context"
	"net/http"
	"time"
    "sync/atomic"
	"github.com/jellydator/ttlcache/v3"
	"log/slog"
)

type RateLimitParam struct {
	Context    context.Context
	RateLimitKey string
}

type LimiterStore interface {
	Allow(param RateLimitParam) (bool, error)
}

type IRateLimiter interface {
	GetStoreKey(r *http.Request) string
	ProceedOrReject(next http.Handler) http.Handler
}


// LocalLimitStore
var llsLogger = slog.With("component", "LocalLimitStore")
type LocalLimitStore struct {
	// *atomic.Int64 is important 
	// because we want to automatically increment
	counters *ttlcache.Cache[string, *atomic.Int64]
	limit    int64
	window   time.Duration
}

func NewLocalLimitStore(limit int, window time.Duration) *LocalLimitStore {
	
	llsLogger.Info("Initializing LocalLimitStore", "limit", limit, "window", window)
	
	localLimitStore := &LocalLimitStore{
		// Default expiration is the window;
		counters: ttlcache.New(
			ttlcache.WithTTL[string, *atomic.Int64](window),
		),
		limit: int64(limit),
		window: window,
	}
	llsLogger.Info("LocalLimitStore initialized successfully")

	llsLogger.Info("Starting LocalLimitStore cleanup goroutine")
	go localLimitStore.counters.Start() // Start the ttlcache cleanup goroutine
	llsLogger.Info("LocalLimitStore cleanup goroutine started")
	
	return localLimitStore
}


func (s *LocalLimitStore) Allow(param RateLimitParam) (bool, error) {
	var item *ttlcache.Item[string, *atomic.Int64]
	item = s.counters.Get(param.RateLimitKey)
	var atomicCount *atomic.Int64
	var newVal int64
    
    if item == nil {
		atomicCount = new(atomic.Int64)
		atomicCount.Store(1)
		newVal = 1

		s.counters.Set(param.RateLimitKey, atomicCount, s.window)
    } else {
		// .Value() returns *atomic.Int64, 
		// so we can directly call Add(1) on the pointer
		atomicCount = item.Value()
		newVal = atomicCount.Add(1)
	}

	if newVal > int64(s.limit) {
		llsLogger.Warn("Rate limit exceeded", "key", param.RateLimitKey, "count", newVal)
		return false, nil
	}

    return true, nil
}




// LocalIPRateLimiter

var liprlLogger = slog.With("component", "LocalIPRateLimiter")

type LocalIPRateLimiter struct {
	localLimitStore LimiterStore
}

func NewLocalIPRateLimiter(localLimitStore LimiterStore) *LocalIPRateLimiter {
	return &LocalIPRateLimiter{localLimitStore: localLimitStore}
}

func (l *LocalIPRateLimiter) GetStoreKey(r *http.Request) string {
	return r.RemoteAddr
}

func (l *LocalIPRateLimiter) ProceedOrReject(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// For simplicity, we use the client's IP as the rate limit key.
		// In a real application, you might want to use a more sophisticated key.
		key := l.GetStoreKey(r)
		param := RateLimitParam{
			Context: r.Context(),
			RateLimitKey: key,
		}

		allowed, err := l.localLimitStore.Allow(param)
		if err != nil {
			liprlLogger.Error("Error checking rate limit", "error", err)
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			
			return
		}
		if !allowed {
			liprlLogger.Warn("Rate limit exceeded", "key", key)
			http.Error(w, "Too Many Requests", http.StatusTooManyRequests)
			return
		}
		next.ServeHTTP(w, r)
	})
}



