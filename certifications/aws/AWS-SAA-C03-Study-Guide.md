# AWS Certified Solutions Architect – Associate (SAA-C03) Study Guide

> Focused on the services that show up most frequently on the exam and the use cases they're tested on. Organized roughly by exam domain weighting: Design Resilient Architectures, Design High-Performing Architectures, Design Secure Applications, Design Cost-Optimized Architectures.

---

## 1. Identity, Access & Governance

### IAM (Identity and Access Management)
- **Core concepts**: Users, Groups, Roles, Policies (JSON), Managed vs Inline policies.
- **Roles vs Users**: Use **roles** for EC2/Lambda/ECS to access other AWS services — never hardcode access keys in code or instances.
- **Cross-account access**: IAM roles with trust policies let one account assume a role in another (used heavily in multi-account setups).
- **Policy evaluation logic**: Explicit Deny > Explicit Allow > Default Deny. SCPs (Organizations) set the max permission boundary; IAM policies operate within that.
- **STS (Security Token Service)**: Temporary credentials via `AssumeRole`, used for federation and cross-account access.
- **Identity Federation**: SAML 2.0 for corporate directories, Cognito for web/mobile apps, IAM Identity Center (SSO) for workforce access across accounts.
- Exam tests: least privilege, when to use a role vs a user, policy troubleshooting (explicit deny wins).

### AWS Organizations & Control Tower
- **Organizations**: Centralized multi-account management, consolidated billing, **Service Control Policies (SCPs)** to restrict what accounts *can* do (guardrails, not grants).
- **Control Tower**: Automates landing zone setup with pre-built guardrails on top of Organizations.
- Use case: Large enterprises separating prod/dev/sandbox accounts with centralized governance.

### AWS KMS (Key Management Service)
- Manages encryption keys (CMKs). Envelope encryption used behind the scenes.
- **SSE-S3** (AWS-managed keys) vs **SSE-KMS** (customer-managed, auditable via CloudTrail, has API call limits/throttling to consider) vs **SSE-C** (customer-provided keys).
- Key rotation, key policies (separate from IAM policies), multi-region keys.
- Use case: Compliance requirements needing audit trails on key usage → SSE-KMS.

### AWS Secrets Manager vs Systems Manager Parameter Store
- **Secrets Manager**: Automatic rotation, integrates with RDS, costs more, built for secrets (DB passwords, API keys).
- **Parameter Store**: Free tier (standard params), good for config data and simple secrets, no built-in rotation (standard tier).
- Exam tests: rotation requirement → Secrets Manager; cost-sensitive/simple config → Parameter Store.

---

## 2. Compute

### EC2 (Elastic Compute Cloud)
- **Purchasing options**:
  - **On-Demand**: pay per second/hour, no commitment — unpredictable workloads.
  - **Reserved Instances**: 1 or 3-year commitment, up to ~72% discount — steady-state predictable workloads.
  - **Savings Plans**: flexible commitment by $/hour spend, applies across instance families.
  - **Spot Instances**: up to 90% discount, can be reclaimed with 2-min warning — fault-tolerant, flexible, batch workloads.
  - **Dedicated Hosts/Instances**: compliance needs requiring physical isolation or license-based (BYOL) software.
- **Placement Groups**: Cluster (low latency, same AZ), Spread (critical instances, separate hardware), Partition (large distributed workloads like Hadoop/Kafka).
- **EC2 Instance Store vs EBS**: instance store = ephemeral, high IOPS, lost on stop; EBS = persistent network-attached block storage.

### Auto Scaling Groups (ASG) + Elastic Load Balancing (ELB)
- **ASG**: scales EC2 count based on CloudWatch metrics/schedules/predictive scaling. Works across multiple AZs for high availability.
- **ALB (Application Load Balancer)**: Layer 7, HTTP/HTTPS, path/host-based routing, ideal for microservices & container-based apps.
- **NLB (Network Load Balancer)**: Layer 4, ultra-low latency, handles millions of requests/sec, static IP support — for TCP/UDP traffic.
- **GWLB (Gateway Load Balancer)**: for deploying third-party virtual appliances (firewalls, IDS/IPS).
- Exam tests: choosing the right LB type for the traffic pattern given.

### Lambda (Serverless Compute)
- Event-driven, no server management, pay per invocation/duration, max execution timeout (15 min).
- Triggers: S3 events, API Gateway, DynamoDB Streams, SQS, EventBridge, CloudWatch schedules.
- **Concurrency**: reserved vs provisioned concurrency (provisioned = pre-warmed, avoids cold starts for latency-sensitive apps).
- Use case: event-driven microservices, glue logic, image processing on S3 upload, cron-like scheduled tasks.

### Containers: ECS, EKS, Fargate
- **ECS (Elastic Container Service)**: AWS-native container orchestration.
- **EKS (Elastic Kubernetes Service)**: managed Kubernetes control plane.
- **Fargate**: serverless compute engine for ECS/EKS — no EC2 instances to manage, pay per task.
- Use case: Fargate when you don't want to manage underlying servers; EC2 launch type when you need more control over instance type/cost optimization at scale.

### Elastic Beanstalk
- PaaS: upload code, AWS handles provisioning (EC2, ELB, ASG, RDS). Good for quick deployment without deep infra config.

---

## 3. Storage

### S3 (Simple Storage Service)
- Object storage, virtually unlimited, 99.999999999% (11 nines) durability.
- **Storage Classes**:
  - **Standard**: frequently accessed data.
  - **Intelligent-Tiering**: unknown/changing access patterns — auto-moves objects between tiers.
  - **Standard-IA / One Zone-IA**: infrequent access, IA = cheaper storage, retrieval fee. One Zone = single AZ (cheaper, less durable).
  - **Glacier Instant Retrieval / Flexible Retrieval / Deep Archive**: archival, ms to hours/days retrieval time — long-term backup/compliance.
- **Lifecycle policies**: automate transitions between storage classes and expiration.
- **Versioning**: protects against accidental deletes/overwrites; required for Cross-Region Replication.
- **S3 Encryption**: SSE-S3, SSE-KMS, SSE-C, client-side.
- **Security**: Bucket Policies (resource-based) vs ACLs (legacy) vs IAM policies; **Block Public Access** settings; presigned URLs for temporary access.
- **Performance**: multipart upload for large files, S3 Transfer Acceleration (via CloudFront edge locations) for long-distance uploads.
- **Static website hosting**, **Event Notifications** (trigger Lambda/SQS/SNS on object events).
- Exam tests heavily: storage class selection based on access pattern + cost, lifecycle transitions, encryption choice, securing buckets.

### EBS (Elastic Block Store)
- Persistent block storage attached to a single EC2 instance (in the same AZ).
- Types: **gp3/gp2** (general purpose SSD), **io1/io2** (high-performance/provisioned IOPS, for databases), **st1** (throughput-optimized HDD, big data), **sc1** (cold HDD, infrequent access).
- Snapshots stored in S3 (incremental), can copy across regions for DR.

### EFS (Elastic File System)
- Managed NFS, **multi-AZ**, scales automatically, can be mounted by many EC2 instances concurrently.
- Use case: shared file storage across a fleet of Linux instances (e.g., content management systems).
- vs EBS: EBS = single instance, single AZ; EFS = multiple instances, multiple AZs.

### Storage Gateway
- Bridges on-premises environments to AWS storage.
- **File Gateway** (NFS/SMB → S3), **Volume Gateway** (iSCSI block storage, cached or stored mode), **Tape Gateway** (virtual tape library for backup).
- Use case: hybrid cloud storage, gradual migration, on-prem backup to AWS.

### Snow Family
- **Snowcone/Snowball/Snowmobile**: physical data transfer devices for large datasets where network transfer is too slow/costly.
- Use case: petabyte-scale migration, or edge computing in disconnected environments (Snowball Edge with compute).

---

## 4. Databases

### RDS (Relational Database Service)
- Managed relational DB (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server, and Aurora-compatible engines).
- **Multi-AZ**: synchronous replication to a standby in another AZ for **high availability/failover** (not for read scaling).
- **Read Replicas**: asynchronous replication for **read scaling**, can be cross-region, promotable to standalone.
- Automated backups, snapshots, encryption at rest via KMS.
- Exam tests: Multi-AZ (HA) vs Read Replica (scaling) — a very common distinction question.

### Aurora
- AWS-proprietary, MySQL/PostgreSQL-compatible, higher performance and availability than standard RDS.
- Storage auto-scales up to 128TB, 6 copies of data across 3 AZs.
- **Aurora Serverless**: auto-scaling capacity for unpredictable/intermittent workloads.
- **Global Database**: cross-region replication with low latency for DR/global reads.

### DynamoDB
- Managed **NoSQL** key-value/document store, single-digit millisecond latency at any scale.
- **On-Demand vs Provisioned capacity** modes.
- **DAX (DynamoDB Accelerator)**: in-memory cache for microsecond read latency.
- **Global Tables**: multi-region, multi-active replication.
- **Streams**: capture item-level changes, trigger Lambda for event-driven processing.
- Use case: high-scale web/mobile apps, gaming leaderboards, session state — when schema is simple/flexible and scale is a priority.

### ElastiCache
- Managed in-memory cache: **Redis** (persistence, replication, pub/sub, sorted sets) vs **Memcached** (simple, multi-threaded, no persistence).
- Use case: reducing read load on RDS/DynamoDB, session storage, leaderboard, caching layer in front of a database.

### Redshift
- Managed **data warehouse** for OLAP/analytics workloads (petabyte-scale, columnar storage).
- Use case: business intelligence, large-scale analytical queries — not for transactional (OLTP) workloads.

### Database Migration Service (DMS)
- Migrates databases to AWS with minimal downtime; can do homogeneous or heterogeneous (with Schema Conversion Tool) migrations.

---

## 5. Networking & Content Delivery

### VPC (Virtual Private Cloud)
- **Subnets**: public (route to Internet Gateway) vs private (no direct route out).
- **Route Tables**, **Internet Gateway (IGW)**, **NAT Gateway** (private subnet outbound internet access, managed, AZ-scoped) vs **NAT Instance** (self-managed, legacy).
- **Security Groups** (stateful, instance-level, allow rules only) vs **NACLs** (stateless, subnet-level, allow + deny rules, processed in rule order).
- **VPC Peering**: 1:1 connection between VPCs, non-transitive.
- **Transit Gateway**: hub-and-spoke connectivity for many VPCs/VPNs — solves the non-transitive peering problem at scale.
- **VPC Endpoints**: Gateway endpoints (S3, DynamoDB — free) and Interface endpoints (PrivateLink, most other services) to keep traffic off the public internet.
- **Site-to-Site VPN** vs **Direct Connect**: VPN = quick, encrypted, over internet; Direct Connect = dedicated private physical connection, more consistent bandwidth/lower latency, longer setup.
- Exam tests heavily: designing multi-tier VPC architectures, choosing connectivity option based on requirements (security, speed, cost, setup time).

### Route 53
- Managed DNS service.
- **Routing policies**: Simple, Weighted (A/B testing, gradual rollout), Latency-based (route to lowest-latency region), Failover (active-passive DR), Geolocation, Geoproximity, Multi-value.
- Health checks trigger failover routing.
- Use case: DNS-level traffic management and failover across regions.

### CloudFront
- CDN: caches content at edge locations close to users, reduces latency and origin load.
- Origins: S3, ALB, EC2, on-prem via custom origin.
- **Origin Access Control (OAC)**: restrict S3 bucket access to only CloudFront.
- Signed URLs/Cookies for private content distribution.
- Use case: global content delivery, reducing load on origin servers, DDoS mitigation (works with AWS Shield).

### API Gateway
- Managed API front door (REST/HTTP/WebSocket APIs).
- Integrates with Lambda (serverless APIs), throttling, caching, request validation, authorization (IAM, Cognito, Lambda authorizers).

---

## 6. Application Integration & Messaging

### SQS (Simple Queue Service)
- Managed message queue, decouples producers/consumers.
- **Standard Queue**: at-least-once delivery, best-effort ordering, high throughput.
- **FIFO Queue**: exactly-once processing, strict ordering, lower throughput.
- **Visibility timeout**, **Dead-Letter Queue (DLQ)** for failed message handling.
- Use case: decoupling microservices, buffering requests to smooth out spiky traffic.

### SNS (Simple Notification Service)
- Pub/sub messaging — one message to many subscribers (SQS, Lambda, email, SMS, HTTP endpoints).
- **Fan-out pattern**: SNS → multiple SQS queues, common exam scenario.

### EventBridge
- Event bus for routing events between AWS services, SaaS apps, and custom applications based on rules.
- More advanced filtering/routing than SNS; use case: building event-driven architectures reacting to state changes across many services.

### Step Functions
- Orchestrates multi-step workflows (state machines) across Lambda, ECS, etc. — visual workflow for complex business logic with retries/error handling.

---

## 7. Monitoring, Management & DevOps

### CloudWatch
- Metrics, Alarms, Logs, Dashboards, Events (now largely EventBridge).
- **Custom metrics**, **Composite alarms**, Logs Insights for querying log data.
- Use case: triggering Auto Scaling, alerting on thresholds, centralized logging.

### CloudTrail
- Logs **API calls/account activity** for auditing — "who did what, when."
- Difference from CloudWatch: CloudTrail = API/governance audit trail; CloudWatch = performance/operational metrics and logs.

### AWS Config
- Tracks resource **configuration changes** over time, evaluates compliance against rules.
- Use case: compliance auditing, detecting configuration drift.

### CloudFormation
- **Infrastructure as Code (IaC)**: declarative templates (JSON/YAML) to provision resources repeatably.
- Stacks, Change Sets (preview changes before applying), StackSets (deploy across multiple accounts/regions).
- Use case: repeatable, version-controlled infrastructure deployment.

### AWS Backup
- Centralized backup management across EBS, RDS, DynamoDB, EFS, etc., with policy-based scheduling and retention.

### Trusted Advisor
- Automated recommendations across cost optimization, performance, security, fault tolerance, service limits.

### AWS Well-Architected Framework — 6 Pillars (conceptual, tested throughout)
1. Operational Excellence
2. Security
3. Reliability
4. Performance Efficiency
5. Cost Optimization
6. Sustainability

---

## 8. Disaster Recovery Strategies (common scenario-based topic)

Ordered by increasing cost and decreasing RTO/RPO:
1. **Backup & Restore**: cheapest, highest RTO/RPO — data backed up, infra provisioned only during a disaster.
2. **Pilot Light**: core infrastructure running minimally (e.g., DB replicating), rest scaled up on disaster.
3. **Warm Standby**: scaled-down but fully functional copy of production always running; scaled up on failover.
4. **Multi-Site Active/Active**: full production capacity running in multiple regions simultaneously — lowest RTO/RPO, highest cost.

---

## 9. Cost Optimization Concepts

- **Right-sizing** instances based on utilization (Compute Optimizer, Trusted Advisor).
- **S3 storage class transitions** and **lifecycle policies**.
- **Reserved Instances/Savings Plans** for predictable workloads; **Spot** for flexible/fault-tolerant ones.
- **Cost Explorer** and **AWS Budgets** for tracking and alerting on spend.
- **Data transfer costs**: same-AZ traffic is cheapest; cross-region and internet egress cost more — architecture decisions should minimize unnecessary cross-AZ/region transfer.

---

## 10. Quick Decision Cheat-Sheet

| Need | Use |
|---|---|
| Object storage, static assets, data lake | S3 |
| Block storage for a single EC2 instance | EBS |
| Shared file storage across many Linux instances | EFS |
| Relational DB, need HA | RDS Multi-AZ |
| Relational DB, need read scaling | RDS Read Replica |
| High-performance, auto-scaling relational DB | Aurora |
| NoSQL, massive scale, low latency | DynamoDB |
| In-memory caching layer | ElastiCache |
| Data warehouse / analytics (OLAP) | Redshift |
| Decouple services / buffer messages | SQS |
| Broadcast to multiple subscribers | SNS |
| Event-driven routing between many sources | EventBridge |
| Serverless compute, event-triggered | Lambda |
| Container orchestration, no server management | ECS/EKS + Fargate |
| Global content delivery / caching | CloudFront |
| DNS routing & failover | Route 53 |
| Private connectivity to AWS services (no internet) | VPC Endpoints |
| Dedicated private connection to AWS | Direct Connect |
| Quick encrypted connection to AWS | Site-to-Site VPN |
| Centralized multi-account governance | Organizations + SCPs |
| Auditing API activity | CloudTrail |
| Monitoring metrics & alarms | CloudWatch |
| Infrastructure as Code | CloudFormation |
| Large-scale offline data transfer | Snow Family |
| Encryption key management with audit trail | KMS (SSE-KMS) |
| Auto-rotating secrets (DB credentials) | Secrets Manager |

---

## 11. Suggested Study Approach

1. Go through each domain above and make sure you can articulate the **use case trigger words** in exam questions (e.g., "multiple AZs," "unpredictable traffic," "least operational overhead," "lowest cost," "millisecond latency") — the SAA-C03 exam is largely about matching scenario language to the right service.
2. Do hands-on labs for: VPC design (public/private subnets, NAT, IGW), S3 lifecycle policies, RDS Multi-AZ vs Read Replica setup, and an Auto Scaling Group behind an ALB.
3. Take official AWS practice questions and full-length practice exams; review every wrong answer to understand *why* the "obviously right" distractor was wrong.
4. Review whitepapers: **AWS Well-Architected Framework** and **Disaster Recovery on AWS** — both are conceptually tested throughout, not just in a dedicated section.
