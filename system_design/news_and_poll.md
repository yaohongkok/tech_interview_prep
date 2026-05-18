# News Site with Polling

Designing a backend for a news site with live polling requires balancing two very different traffic patterns:

* The News Site: Read-heavy, highly cacheable, and generally static content.

* Live Polling: Write-heavy, real-time, with sudden, massive spikes in traffic (especially during breaking news or viral topics).


Here is a scalable, resilient system architecture designed to handle both workloads seamlessly.


## 1. High-Level Architecture Overview

To prevent heavy poll traffic from crashing the news delivery service, we must decouple the core news infrastructure from the polling infrastructure.

```
[ Clients: Web / Mobile ]
           |
           v
   [ CDN (Cloudflare) ] ----(Cache Hit)----> [ Static News / Articles ]
           |
     (Cache Miss / Poll Actions)
           v
  [ API Gateway / Load Balancer ]
     /                        \
    v                          v
[ News Service ]        [ Polling Service ]
    |                          |
[ SQL Replica ]         [ Redis (Pub/Sub) ] <--> [ WebSocket Gateway ]
                               |
                        [ Kafka / SQS ]
                               |
                        [ Worker Pool ]
                               |
                        [ NoSQL / Cache DB ]
```



Designing a backend for a news site with live polling requires balancing two very different traffic patterns:

The News Site: Read-heavy, highly cacheable, and generally static content.

Live Polling: Write-heavy, real-time, with sudden, massive spikes in traffic (especially during breaking news or viral topics).

Here is a scalable, resilient system architecture designed to handle both workloads seamlessly.

1. High-Level Architecture Overview
To prevent heavy poll traffic from crashing the news delivery service, we must decouple the core news infrastructure from the polling infrastructure.

[ Clients: Web / Mobile ]
           |
           v
   [ CDN (Cloudflare) ] ----(Cache Hit)----> [ Static News / Articles ]
           |
     (Cache Miss / Poll Actions)
           v
  [ API Gateway / Load Balancer ]
     /                        \
    v                          v
[ News Service ]        [ Polling Service ]
    |                          |
[ SQL Replica ]         [ Redis (Pub/Sub) ] <--> [ WebSocket Gateway ]
                               |
                        [ Kafka / SQS ]
                               |
                        [ Worker Pool ]
                               |
                        [ NoSQL / Cache DB ]


## 2. Component Design
### A. The News Delivery System (Read-Heavy)

Because news articles don’t change second-by-second, we optimize heavily for reads using a layered caching strategy.

CDN Layer: Edge servers cache HTML fragments and article JSON data. A cache hit ratio of 90%+ is the goal here.

Application Layer: A stateless Microservice (e.g., Go or Node.js) handles content delivery.

Database: A relational database (like PostgreSQL) handles complex queries for content management, paired with Read Replicas to distribute the load.

Cache Invalidation: When an editor updates an article, a webhook triggers a CDN purge and updates the internal cache (Redis).

### B. The Live Polling System (Write-Heavy & Real-Time)
Polling requires capturing thousands of votes per second and broadcasting the updating results back to millions of users in real time.

1. Vote Ingestion (The Write Path)
To prevent database bottlenecks, we avoid writing votes directly to a traditional database.

Rate Limiting & Idempotency: The API Gateway uses a combination of user IDs (for logged-in users) and IP/Device fingerprinting (for guests) to prevent vote-spamming.

Message Queue (Ingestion Buffer): Instead of processing the vote immediately, the Polling Service pushes the vote event into a message queue like Apache Kafka or AWS SQS. This acts as a shock absorber for the system.

Stream Processing/Workers: Worker nodes consume batches of votes from the queue and increment the poll counts using atomic operations (e.g., Redis INCR).

2. Result Broadcasting (The Read/Real-Time Path)
Pulling the database every second for updates doesn't scale. We use a push model.

WebSocket Gateway: Dedicated, lightweight servers manage open WebSocket connections with active users viewing the poll.

Pub/Sub Mechanism: As workers update the vote totals in Redis, they publish the new totals to a Redis Pub/Sub channel.

Fan-out: The WebSocket servers subscribe to this channel and "fan out" the real-time updates to all connected clients simultaneously.

Throttling Updates: To save bandwidth, updates don't need to be sent on every single vote. We can throttle broadcasts to once every 1–2 seconds.

## 3. Data Modeling
News Schema (Relational - PostgreSQL)
SQL
CREATE TABLE articles (
    id UUID PRIMARY KEY,
    title VARCHAR(255),
    content TEXT,
    status VARCHAR(50), -- draft, published
    published_at TIMESTAMP
);
Polling Schema (Key-Value / Document)
For lightning-fast counters, we store the active poll state in Redis.

Poll Options Counter (Hashes):

Key: poll:{poll_id}:results

Fields: option_A: 4520, option_B: 1250

Deduplication Log (Set):

To ensure a user only votes once: Key: poll:{poll_id}:voters

Members: [user_id_1, user_id_2]

Note: For long-term storage and analytics, the final poll states are flushed from Redis to a persistent NoSQL database (like MongoDB or DynamoDB) once the poll closes.

## 4. Handling Scale & Edge Cases
The "Thundering Herd" Problem: If a breaking news push notification goes out, millions of users click it at once. Cache warm-ups (pre-loading the article into CDN before sending the notification) prevent the origin servers from collapsing.

WebSocket Degradation: If WebSocket connections drop due to extreme load, the frontend should gracefully fallback to Long Polling or standard HTTP GET requests with exponential backoff.

Data Consistency: We favor eventual consistency for the poll results. The exact number of votes doesn't need to be perfectly accurate down to the millisecond on the user's screen, as long as the backend eventually processes and counts every valid vote accurately.




## 5. Important Design Choices & Why

### A. Decoupling News from Polling (Isolation of Concerns)
The Choice: Splitting the architecture into a News Service and a Polling Service.

The Rationale: If a highly controversial poll goes viral, millions of people might smash the "Vote" button simultaneously. If this happens on a unified monolithic backend, the database connections will saturate, causing the entire site—including the ability to read regular news articles—to crash. By decoupling them, a failure in the polling system has zero impact on the core news delivery.

### B. Using a Message Queue for Ingestion (Asynchronous Processing)
The Choice: Putting Kafka or AWS SQS between the API gateway and the database.

The Rationale: In a live poll, you face massive write spikes. If every vote required an immediate INSERT or UPDATE query to a traditional database, the database would quickly run out of connection pools and lock up.

The message queue acts as a buffer (shock absorber). The API gateway quickly accepts the vote, drops it into the queue, and returns a 202 Accepted to the user in milliseconds.

The worker nodes can then drain the queue and update the database at a steady, manageable pace (load leveling), protecting the downstream data stores.


### C. Choosing Redis Over a Relational DB for Active Polls
The Choice: Using Redis (In-Memory Key-Value) to track live vote counts instead of PostgreSQL/MySQL.

The Rationale: Relational databases are built for ACID compliance and complex queries, but they struggle with high-frequency updates to the exact same row (e.g., updating the count of "Option A" over and over). This causes row-locking contention, slowing the system to a crawl.

Redis operates entirely in memory and supports atomic operations like INCR (increment). It can easily handle hundreds of thousands of increments per second on a single instance without locking issues.

### D. Pub/Sub and WebSocket Fan-Out Over Client Polling
The Choice: Using WebSockets backed by Redis Pub/Sub to push updates, rather than having the frontend poll the server every few seconds.

The Rationale: Imagine 100,000 users are looking at a live poll. If their browsers send an HTTP request every 2 seconds to check for updates (client polling), that results in 50,000 requests per second hitting your servers. Most of those requests will return the exact same data, wasting massive amounts of CPU and bandwidth.

With WebSockets, the server holds a single open connection to each user. The server only sends data when the data actually changes.

By using Redis Pub/Sub, when a worker updates a vote count, it publishes it once to Redis, and Redis instantly broadcasts it to all the WebSocket servers, which then "fan out" the update to the connected users.

### E. Favoring Eventual Consistency Over Strong Consistency
The Choice: Allowing a delay of 1–2 seconds before a vote is reflected on the user's UI.

The Rationale: In a live poll with massive scale, Strong Consistency (guaranteeing that every single user sees the absolute exact, perfect vote count down to the millisecond) is mathematically and physically impossible without bringing the system to a halt.

By choosing Eventual Consistency, we throttle the WebSocket updates to broadcast once every second. If a user sees 4,500 votes instead of the actual 4,512 votes for a brief moment, it does not ruin their user experience. The system catches up a second later, allowing us to save massive amounts of network bandwidth and server processing power.
