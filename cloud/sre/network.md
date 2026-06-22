# SRE Networking: Concepts & Interview Guide

---

## Part 1: Core Networking Concepts for SREs

### 1. The OSI Model

The OSI (Open Systems Interconnection) model is a conceptual framework that describes how data travels across a network in 7 layers. SREs must understand which layer a problem lives at to debug it efficiently.

| Layer | Name | Key Protocols / Examples |
|-------|------|--------------------------|
| 7 | Application | HTTP, HTTPS, DNS, SMTP, gRPC |
| 6 | Presentation | TLS/SSL, encoding, compression |
| 5 | Session | TCP sessions, authentication sessions |
| 4 | Transport | TCP, UDP — ports, reliability, flow control |
| 3 | Network | IP, ICMP, routing |
| 2 | Data Link | Ethernet, MAC addresses, ARP, switches |
| 1 | Physical | Cables, NICs, fiber, signals |

> **SRE tip:** Most production incidents live at Layer 3 (routing), Layer 4 (TCP timeouts, connection limits), or Layer 7 (application-level errors). Being able to say "this is a Layer 4 issue — connections are establishing but dropping" immediately narrows the blast radius.

---

### 2. TCP vs UDP

**TCP (Transmission Control Protocol)**
- Connection-oriented: requires a 3-way handshake (SYN → SYN-ACK → ACK)
- Guarantees ordering and delivery
- Has congestion control and flow control
- Use cases: HTTP/HTTPS, SSH, databases, gRPC

**UDP (User Datagram Protocol)**
- Connectionless: no handshake, fire-and-forget
- Lower latency, no delivery guarantees
- Use cases: DNS, video streaming, VoIP, gaming, QUIC

**TCP 3-Way Handshake:**
```
Client ──SYN──────────────► Server
Client ◄──SYN-ACK────────── Server
Client ──ACK──────────────► Server
[Connection established]
```

**TCP Connection Teardown (4-way):**
```
Client ──FIN──────────────► Server
Client ◄──ACK────────────── Server
Client ◄──FIN────────────── Server
Client ──ACK──────────────► Server
[Connection closed]
```

**TIME_WAIT state:** After closing, a socket stays in TIME_WAIT for 2×MSL (Maximum Segment Lifetime, ~60s) to handle delayed packets. High-traffic servers can exhaust ephemeral ports if connections close too frequently.

---

### 3. IP Addressing & Subnetting

**IPv4 address:** 32-bit, written as 4 octets (e.g., `192.168.1.10`)

**CIDR notation:** `192.168.1.0/24` — the `/24` means the first 24 bits are the network prefix, leaving 8 bits for hosts (2⁸ - 2 = 254 usable hosts).

| CIDR | Subnet Mask | Hosts |
|------|-------------|-------|
| /8 | 255.0.0.0 | ~16.7M |
| /16 | 255.255.0.0 | ~65K |
| /24 | 255.255.255.0 | 254 |
| /28 | 255.255.255.240 | 14 |
| /32 | 255.255.255.255 | 1 (host route) |

**Private address ranges (RFC 1918):**
- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`

**IPv6:** 128-bit, written in hex groups separated by colons. `::1` is the loopback address.

---

### 4. DNS (Domain Name System)

DNS translates human-readable names to IP addresses. It is hierarchical and distributed.

**Resolution chain:**
```
Browser cache → OS cache → Resolver (ISP/8.8.8.8) → Root → TLD → Authoritative NS
```

**Key record types:**

| Record | Purpose |
|--------|---------|
| A | Maps hostname → IPv4 address |
| AAAA | Maps hostname → IPv6 address |
| CNAME | Alias to another hostname |
| MX | Mail exchange server |
| TXT | Arbitrary text (SPF, DKIM, verification) |
| NS | Nameserver for a domain |
| PTR | Reverse lookup (IP → hostname) |
| SRV | Service discovery (host + port) |

**TTL (Time to Live):** Controls how long a record is cached. Low TTL = faster propagation but more DNS queries. High TTL = less load but slow failover.

**Split-horizon DNS:** Serving different DNS answers to internal vs external clients (e.g., returning a private IP internally and a public IP externally for the same hostname).

---

### 5. HTTP / HTTPS

**HTTP methods:** GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS

**Key status codes:**

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 301/302 | Redirect (permanent/temporary) |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests (rate limiting) |
| 500 | Internal Server Error |
| 502 | Bad Gateway |
| 503 | Service Unavailable |
| 504 | Gateway Timeout |

**HTTP/1.1 vs HTTP/2 vs HTTP/3:**

- **HTTP/1.1:** Text-based, one request per connection (with keep-alive), head-of-line blocking
- **HTTP/2:** Binary, multiplexed streams over one TCP connection, header compression (HPACK), server push
- **HTTP/3:** Uses QUIC (UDP-based), eliminates TCP head-of-line blocking, built-in TLS 1.3

**HTTPS / TLS handshake (TLS 1.3 simplified):**
```
Client Hello (supported ciphers, key share)
                    ──────────────────────►
                    ◄──────────────────────
            Server Hello (chosen cipher, cert, key share)
[Keys derived from key shares]
Client Finished
                    ──────────────────────►
[Encrypted data flows]
```

---

### 6. Load Balancing

Load balancers distribute traffic across multiple backends to ensure availability and scalability.

**Layer 4 (Transport) Load Balancing:**
- Routes based on IP and TCP/UDP port
- Faster, no application-layer inspection
- Examples: AWS NLB, HAProxy (TCP mode)

**Layer 7 (Application) Load Balancing:**
- Routes based on HTTP headers, URL paths, cookies
- Supports content-based routing, SSL termination, retries
- Examples: AWS ALB, nginx, Envoy, HAProxy (HTTP mode)

**Load balancing algorithms:**

| Algorithm | Description |
|-----------|-------------|
| Round Robin | Rotate through backends in order |
| Least Connections | Send to backend with fewest active connections |
| Weighted Round Robin | Assign more traffic to higher-capacity backends |
| IP Hash | Hash client IP to sticky-route to same backend |
| Random | Pick a backend randomly (works well at scale) |
| Least Response Time | Route to fastest-responding backend |

**Health checks:** Load balancers periodically probe backends (HTTP GET /healthz, TCP connect, etc.) and remove unhealthy ones from the pool.

---

### 7. NAT (Network Address Translation)

NAT allows multiple devices on a private network to share a single public IP.

- **SNAT (Source NAT):** Rewrites source IP of outbound packets — used for outbound internet access
- **DNAT (Destination NAT):** Rewrites destination IP of inbound packets — used to forward traffic to internal servers (port forwarding)
- **Masquerade:** Dynamic SNAT using the outbound interface's IP (common in iptables)

---

### 8. Firewalls & Security Groups

**Stateful firewalls** track connection state and automatically allow return traffic for established sessions.

**Stateless firewalls** (ACLs) evaluate each packet independently — you must explicitly allow return traffic.

**AWS Security Groups** are stateful. **Network ACLs** are stateless.

**iptables chain flow:**
```
Incoming packet → PREROUTING → (routing decision) → INPUT (local) or FORWARD (routed)
Outgoing packet → OUTPUT → POSTROUTING
```

---

### 9. Proxies & Reverse Proxies

**Forward proxy:** Sits between clients and the internet. Clients are aware of it. Use cases: egress filtering, caching, anonymity.

**Reverse proxy:** Sits in front of backend servers. Clients are unaware of the actual servers. Use cases: load balancing, SSL termination, caching, rate limiting.

Common reverse proxies: nginx, HAProxy, Envoy, Caddy, Traefik.

**Service mesh** (e.g., Istio, Linkerd): A network of sidecar proxies (typically Envoy) deployed alongside each service to handle mTLS, retries, observability, and traffic management transparently.

---

### 10. CDN (Content Delivery Network)

A CDN caches content at edge nodes geographically close to users, reducing latency and origin load.

**Cache hit:** Request served from edge (fast, cheap).  
**Cache miss:** Edge fetches from origin, then caches.

**Cache-Control headers:** Control what is cached and for how long.
```
Cache-Control: public, max-age=86400       # Cache for 1 day
Cache-Control: private, no-store           # Don't cache at all
Cache-Control: s-maxage=3600               # CDN caches for 1 hour, ignores max-age
```

**Cache invalidation:** Purging stale content from edge nodes (can be slow/expensive to propagate). Common strategy: use content-addressable URLs with hash in filename.

---

### 11. BGP & Routing

**BGP (Border Gateway Protocol):** The routing protocol that runs the internet. Used between autonomous systems (AS) to advertise IP prefixes.

- **eBGP:** Between different ASes (internet routing)
- **iBGP:** Within the same AS

**OSPF / IS-IS:** Interior gateway protocols for routing within a datacenter or enterprise network.

**Anycast:** The same IP prefix is advertised from multiple locations globally. Traffic is routed to the nearest (in BGP terms) origin. Used heavily in DNS (e.g., 8.8.8.8) and CDNs.

---

### 12. Key Networking Tools for SREs

| Tool | Use Case |
|------|---------|
| `ping` | ICMP reachability & latency |
| `traceroute` / `mtr` | Hop-by-hop path tracing |
| `dig` / `nslookup` | DNS resolution debugging |
| `curl` / `wget` | HTTP request testing |
| `netstat` / `ss` | Socket and connection state |
| `tcpdump` | Packet capture and analysis |
| `Wireshark` | GUI packet analysis |
| `iperf3` | Bandwidth testing |
| `nmap` | Port scanning |
| `ip` / `ifconfig` | Interface and route management |
| `iptables` / `nftables` | Firewall rule management |
| `strace` | System call tracing |

---

## Part 2: Popular SRE Networking Interview Questions & Answers

---

### Q1: What happens when you type `https://www.google.com` in a browser?

**Answer:**

This is the classic end-to-end question. Walk through each layer:

1. **URL parsing:** Browser extracts scheme (`https`), host (`www.google.com`), and path (`/`).
2. **DNS resolution:** Browser checks its cache, then OS cache, then queries the configured DNS resolver. The resolver walks the DNS hierarchy (root → `.com` TLD → Google's authoritative NS) and returns the A/AAAA record.
3. **TCP connection:** Browser opens a TCP connection to port 443 on the resolved IP via a 3-way handshake.
4. **TLS handshake:** Client and server negotiate cipher suites, server presents its certificate, and both sides derive session keys (TLS 1.3 does this in 1 round-trip).
5. **HTTP request:** Browser sends `GET / HTTP/2` with headers (Host, Accept, cookies, etc.).
6. **Server processing:** The request hits a load balancer, gets routed to an application server, which generates a response.
7. **HTTP response:** Server returns `200 OK` with HTML, CSS, JS, and appropriate `Cache-Control` headers.
8. **Rendering:** Browser parses HTML, requests sub-resources (images, scripts), and renders the page.
9. **Connection reuse:** HTTP/2 multiplexes subsequent requests over the same connection.

---

### Q2: Explain the difference between TCP and UDP. When would you use each?

**Answer:**

TCP is connection-oriented and guarantees ordered, reliable delivery through acknowledgements, retransmission, and flow control. This reliability comes at the cost of latency (handshake overhead, retransmit delays) and connection state management.

UDP is connectionless and provides no delivery guarantees. It is faster and lighter — packets are sent without confirmation.

**Use TCP when:** data integrity matters and you can tolerate latency — databases, file transfers, APIs, SSH, SMTP.

**Use UDP when:** latency matters more than perfect delivery — DNS lookups (fast query/response), video/audio streaming (a dropped frame is better than freezing), online gaming, VoIP.

**QUIC** (used by HTTP/3) is built on UDP but implements its own reliability and congestion control, giving the best of both worlds with better connection migration support.

---

### Q3: What is a TCP connection in TIME_WAIT state, and why can it be a problem?

**Answer:**

After the 4-way TCP teardown, the client side enters TIME_WAIT for 2×MSL (around 60–120 seconds). This is intentional — it ensures any delayed packets from the old connection are discarded and not confused with a new connection on the same 4-tuple.

**The problem:** On a high-traffic server making many short-lived outbound connections (e.g., a service calling an API), ephemeral ports (typically 32768–60999) can be exhausted because TIME_WAIT sockets hold ports for up to 2 minutes.

**Mitigations:**
- `net.ipv4.tcp_tw_reuse = 1` — allows reusing TIME_WAIT sockets for new outbound connections (safe with TCP timestamps)
- Increase ephemeral port range: `net.ipv4.ip_local_port_range = 1024 65535`
- Use connection pooling to reduce connection churn
- Shift client-side to server-side connections (persistent keep-alive)

---

### Q4: What is DNS TTL and what are the trade-offs of setting it high vs low?

**Answer:**

TTL (Time to Live) tells DNS resolvers how long (in seconds) to cache a record before querying the authoritative nameserver again.

**High TTL (e.g., 86400 = 1 day):**
- Pros: fewer DNS queries, better performance, lower load on nameservers
- Cons: slow propagation — if you change an IP, clients may still hit the old one for up to TTL seconds

**Low TTL (e.g., 60 seconds):**
- Pros: fast failover and propagation during incidents or blue/green deployments
- Cons: more DNS queries, higher load on resolvers, slight increase in latency per request

**SRE best practice:** Pre-lower TTL well before a planned migration (e.g., 48 hours before, drop TTL to 60s). After the migration is stable, raise TTL again.

---

### Q5: What is the difference between a Layer 4 and Layer 7 load balancer? When would you use each?

**Answer:**

**Layer 4 (Transport LB)** operates on IP addresses and TCP/UDP ports. It routes packets without inspecting the application payload. It is extremely fast and CPU-efficient. It cannot make routing decisions based on URL paths or HTTP headers.

**Layer 7 (Application LB)** terminates the connection, inspects HTTP (or gRPC, etc.) content, and can route based on host headers, URL paths, cookies, or any application attribute. It supports SSL termination, HTTP-to-HTTPS redirects, request rewriting, and sophisticated health checks.

**Use L4 when:** raw throughput and minimal latency matter, you have non-HTTP traffic (e.g., raw TCP for a database proxy), or you need to pass through TLS without terminating it.

**Use L7 when:** you need path-based routing (e.g., `/api/*` → service A, `/static/*` → CDN), canary deployments with header-based routing, or centralized SSL termination.

In practice, modern architectures often layer both: an L4 NLB receives external traffic and passes it to an L7 ALB or ingress controller.

---

### Q6: What is a network partition, and how does it affect distributed systems?

**Answer:**

A network partition is when some nodes in a distributed system can no longer communicate with others due to a network failure. The nodes themselves are healthy but connectivity between groups is lost.

This is the "P" in the CAP theorem. According to CAP, in the presence of a network partition, a distributed system must choose between:

- **Consistency (CP):** All nodes see the same data; reject requests to avoid serving stale data. Example: ZooKeeper, etcd.
- **Availability (AP):** Continue serving requests even if some nodes might return stale data. Example: Cassandra, CouchDB.

**For SREs this means:** design your systems to handle partition scenarios. Use timeouts and circuit breakers so partial failures don't cascade. Ensure your observability can distinguish a partition from a full outage (e.g., nodes can reach each other but not the database).

---

### Q7: What is a SYN flood attack and how can you defend against it?

**Answer:**

A SYN flood is a Denial-of-Service (DoS) attack. The attacker sends many TCP SYN packets with spoofed source IPs. The server allocates state for each half-open connection and sends SYN-ACKs that are never acknowledged. The server's connection table (backlog) fills up, preventing legitimate connections.

**Defenses:**

- **SYN Cookies:** The server encodes connection state into the SYN-ACK's sequence number rather than allocating memory. If the ACK arrives, the server reconstructs the state. No memory is consumed for half-open connections. Enabled via `net.ipv4.tcp_syncookies = 1`.
- **Backlog tuning:** Increase `net.ipv4.tcp_max_syn_backlog` to handle burst traffic.
- **Rate limiting:** Use iptables or upstream DDoS scrubbing to drop SYN packets above a threshold per source.
- **Upstream DDoS protection:** Cloudflare, AWS Shield, etc. absorb volumetric attacks before they reach your infrastructure.

---

### Q8: Explain what happens at the network level during a service deployment with zero downtime.

**Answer:**

Zero-downtime deployments rely on several networking mechanisms working together:

1. **Rolling update:** New pods/instances are started before old ones are terminated. The load balancer routes traffic to both old and new until all new ones are healthy.
2. **Health checks:** The load balancer waits for new instances to pass health checks before adding them to the backend pool.
3. **Connection draining / graceful shutdown:** When an old instance is marked for removal, the load balancer stops sending new requests to it but waits for in-flight connections to complete (drain period). The instance stops accepting new connections but finishes existing ones.
4. **DNS TTL:** If DNS is involved (e.g., blue/green with DNS switch), TTL must be low enough so that clients pick up the new endpoint quickly.
5. **Keep-alive / HTTP/2:** Persistent connections mean clients may continue hitting old backends even after they're removed from the pool. Graceful draining handles this.

---

### Q9: What is mTLS and when is it used?

**Answer:**

In standard TLS, only the server presents a certificate (proving its identity to the client). In mTLS (mutual TLS), both the client and server present certificates — each authenticates the other.

**Use cases:**

- **Service mesh communication:** Services in Istio or Linkerd communicate over mTLS automatically, ensuring only authenticated services can talk to each other.
- **Zero-trust networking:** Replaces IP-based trust with identity-based trust. Even if an attacker is inside the network, they cannot communicate with services without a valid certificate.
- **API authentication:** Some APIs use client certificates instead of API keys for stronger authentication.

**Key concepts:** Each service gets a certificate issued by a shared Certificate Authority (CA). The CA itself must be protected — compromise of the CA means compromise of the entire mesh.

---

### Q10: You're seeing elevated 502 errors from your load balancer. How do you debug it?

**Answer:**

A 502 Bad Gateway means the load balancer received an invalid or no response from the backend. Debug it layer by layer:

1. **Check backend health:** Are all backends passing health checks? Are any being removed from the pool? Look at LB metrics for healthy host count.
2. **Check backend logs:** Are backends receiving the requests? Are they returning errors? Are they timing out?
3. **Check connection errors:** Is the LB failing to connect to backends (connection refused, timeout)? This could mean backends are down, overloaded, or their process has crashed.
4. **Check resource exhaustion:** Are backends out of file descriptors, connections, or memory? `ss -s` and `ulimit` can help.
5. **Correlate with deployments or traffic spikes:** Did 502s start after a deploy? Check if new instances are healthy. Did traffic spike beyond backend capacity?
6. **Packet capture:** If necessary, `tcpdump` on a backend to see what the LB is actually sending and how the backend responds.
7. **Check keepalive settings:** Mismatched keepalive timeouts between the LB and backends can cause connections to be used after the backend has closed them, resulting in 502s. Ensure backend keepalive timeout > LB idle timeout.

---

### Q11: What is BGP and why does it matter for SREs?

**Answer:**

BGP (Border Gateway Protocol) is the routing protocol that exchanges reachability information between autonomous systems (ASes) on the internet. Every major network (ISP, cloud provider, CDN) has an AS number and uses BGP to advertise the IP prefixes it owns to its peers.

**Why SREs care:**

- **BGP route leaks/hijacks:** If an AS accidentally or maliciously announces another network's prefixes, traffic can be misdirected. This has caused major outages (e.g., the 2021 Facebook outage was partly BGP misconfiguration).
- **Anycast:** Services like DNS (8.8.8.8) and CDNs use anycast — the same prefix is announced from multiple PoPs globally, and BGP routes clients to the nearest one.
- **Multi-homing:** Large companies peer with multiple ISPs using BGP for redundancy. SREs operating in this context need to understand traffic engineering with BGP attributes (AS path, local preference, MED).
- **Cloud networking:** AWS, GCP, and Azure use BGP for Direct Connect/VPN peering and internally for VPC routing.

---

### Q12: What is the difference between horizontal and vertical scaling, and what networking changes does each require?

**Answer:**

**Vertical scaling (scale up):** Increase the resources (CPU, RAM, network bandwidth) of a single machine. Simpler operationally, no networking changes needed, but has an upper limit and creates a single point of failure.

**Horizontal scaling (scale out):** Add more instances behind a load balancer. Requires:
- A load balancer (L4 or L7) to distribute traffic
- Session affinity or stateless design (if services are stateful, sessions must be externalized to a shared store like Redis)
- Service discovery so the load balancer or service mesh knows about new instances
- Health checking to route away from failed instances
- Potentially wider CIDR blocks in your VPC/network if you're adding many nodes

**SRE preference:** Horizontal scaling is generally preferred for reliability (no SPOF) and cost-effectiveness, but adds operational complexity in networking, service discovery, and data consistency.

---

### Q13: What is a circuit breaker in the context of networking?

**Answer:**

A circuit breaker is a pattern (popularized by Netflix Hystrix) that prevents a client from repeatedly calling a failing service, giving the failing service time to recover.

**States:**

- **Closed:** Normal operation. Requests pass through. Failure count is tracked.
- **Open:** Failure threshold exceeded. Requests are immediately rejected (fail fast) without calling the downstream service. A timer starts.
- **Half-Open:** After the timer expires, a limited number of test requests are allowed through. If they succeed, the circuit closes. If they fail, it opens again.

**Why it matters for SREs:** Without a circuit breaker, a slow or failing downstream service can cause upstream services to exhaust their connection pools and thread pools, cascading the failure. Circuit breakers limit blast radius and improve overall system resilience.

---

*Last updated: June 2026*