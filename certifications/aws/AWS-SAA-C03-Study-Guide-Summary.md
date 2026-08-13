# AWS SAA-C03 Study Guide — Summary

> Condensed companion to [AWS-SAA-C03-Study-Guide-Core.md](AWS-SAA-C03-Study-Guide-Core.md) and [AWS-SAA-C03-Study-Guide-Additional.md](AWS-SAA-C03-Study-Guide-Additional.md). Use this as a quick-reference index and a final-review checklist, not a replacement for the full guides.

---

## 1. AWS Services Covered

### Identity, Access & Security

| Service | What It's Used For | Common Use Cases |
|---|---|---|
| IAM | Manage users, groups, roles, and permission policies | Least-privilege access control, cross-account roles, MFA enforcement |
| AWS Organizations | Centrally manage multiple AWS accounts with consolidated billing | Multi-account governance, Service Control Policy (SCP) guardrails |
| AWS Control Tower | Automated setup/governance of a secure multi-account landing zone | Enterprise multi-account environments with guardrails |
| AWS KMS | AWS-managed encryption key creation, rotation, and usage auditing | Encrypting S3/EBS/RDS data (SSE-KMS), envelope encryption |
| AWS CloudHSM | Dedicated, single-tenant hardware security modules you fully control | Compliance needing full key custody, Oracle TDE, Redshift encryption |
| AWS Secrets Manager | Store and auto-rotate secrets like DB credentials | RDS credential rotation, multi-region secret replication |
| SSM Parameter Store | Secure hierarchical storage for config values and secrets | App configuration, KMS-encrypted secrets, expiration policies |
| AWS Certificate Manager (ACM) | Provision and auto-renew TLS/SSL certificates | HTTPS on ALB/CloudFront/API Gateway |
| AWS WAF | Layer 7 firewall filtering HTTP requests | Blocking SQLi/XSS, rate limiting, geo-blocking |
| AWS Shield | DDoS protection (Layer 3/4, and Layer 7 with Advanced) | Protecting EC2/ELB/CloudFront from DDoS attacks |
| AWS Firewall Manager | Centrally manage WAF/Shield/Security Group rules org-wide | Multi-account security policy compliance |
| Amazon GuardDuty | ML-based threat detection across CloudTrail/VPC/DNS logs | Detecting compromised instances, crypto-mining, anomalous API calls |
| Amazon Inspector | Automated vulnerability scanning for EC2/ECR/Lambda | Finding known CVEs in workloads and container images |
| Amazon Macie | ML-based discovery of sensitive data (PII) in S3 | Data privacy audits, compliance scanning |
| AWS IAM Identity Center | Single sign-on across AWS accounts and business apps | Workforce SSO, permission sets, attribute-based access control |
| AWS Directory Service (Managed AD / AD Connector / Simple AD) | Managed Microsoft Active Directory options in AWS | Windows workload auth, hybrid AD trust relationships |

### Compute

| Service | What It's Used For | Common Use Cases |
|---|---|---|
| EC2 | Virtual machines with configurable OS/CPU/RAM/storage | General-purpose hosting, web servers, batch jobs, HPC |
| Auto Scaling Groups (ASG) | Automatically adjusts EC2 instance count to meet demand | Elastic horizontal scaling, self-healing fleets |
| Elastic Load Balancing (ALB/NLB/GWLB/CLB) | Distributes traffic across targets with health checks | Microservices routing (ALB), high-throughput TCP (NLB), 3rd-party appliances (GWLB) |
| AWS Lambda | Runs code without managing servers, billed per invocation | Event-driven microservices, glue logic, scheduled tasks |
| Amazon ECS | AWS-native container orchestration | Running Docker containers on EC2 or Fargate |
| Amazon EKS | Managed Kubernetes control plane | Migrating/running Kubernetes workloads on AWS |
| AWS Fargate | Serverless compute engine for ECS/EKS tasks | Running containers without managing EC2 instances |
| AWS Elastic Beanstalk | PaaS that provisions/manages infra for your app code | Fast deployment of web apps without infra management |
| AWS Batch | Fully managed batch job scheduling and compute provisioning | Large-scale batch/ETL processing jobs |
| AWS Outposts | Extends AWS infrastructure and services to on-prem hardware | Low-latency on-prem processing, data residency |

### Storage

| Service | What It's Used For | Common Use Cases |
|---|---|---|
| Amazon S3 | Object storage with virtually unlimited scale | Data lakes, backups, static website hosting, archiving |
| Amazon EBS | Persistent block storage for a single EC2 instance | Boot volumes, databases, high-IOPS workloads |
| Amazon EFS | Managed NFS shared across many EC2 instances/AZs | Shared content storage, CMS, home directories |
| Snow Family (Snowball / Snowcone / Snowmobile) | Physical devices for offline bulk data transfer/edge compute | Large one-time migrations, edge sites with poor connectivity |
| Amazon FSx | Managed third-party file systems (Windows/Lustre/ONTAP/OpenZFS) | HPC, Windows shares, NetApp/ZFS lift-and-shift |
| AWS Storage Gateway | Bridges on-prem environments to S3/EBS-backed storage | Hybrid backup, tiered storage, tape-backup replacement |
| AWS Transfer Family | Managed FTP/FTPS/SFTP endpoints into S3/EFS | Legacy file-transfer protocol integrations |
| AWS DataSync | Fast data transfer between on-prem and cloud storage systems | Migrating large datasets, ongoing sync |

### Databases

| Service | What It's Used For | Common Use Cases |
|---|---|---|
| Amazon RDS | Managed relational databases (multiple engines) | OLTP apps needing HA and automated backups |
| Amazon Aurora | AWS-proprietary MySQL/PostgreSQL-compatible database | High-performance, auto-scaling relational workloads |
| Amazon ElastiCache | Managed in-memory Redis/Memcached | Caching, session storage, gaming leaderboards |
| Amazon DynamoDB | Managed NoSQL key-value/document store | High-scale web/mobile apps, gaming |
| Amazon Redshift | Columnar OLAP data warehouse | Business intelligence, large analytical queries |
| Amazon DocumentDB | MongoDB-compatible managed NoSQL database | JSON document storage and querying |
| Amazon Neptune | Managed graph database | Social networks, fraud detection, recommendation engines |
| Amazon Keyspaces | Managed Cassandra-compatible database | IoT device data, time-series data at scale |
| Amazon Timestream | Managed time-series database | IoT/operational metrics, real-time analytics |
| Amazon QLDB | Immutable, cryptographically verifiable ledger database | Ledger/transaction history requiring tamper-evidence |

### Analytics & Machine Learning

| Service | What It's Used For | Common Use Cases |
|---|---|---|
| Amazon Athena | Serverless SQL queries directly on S3 data | Ad hoc analysis of S3 data, log querying |
| Amazon OpenSearch Service | Managed search/analytics engine (search any field) | Full-text search, log analytics dashboards |
| Amazon EMR | Managed Hadoop/Spark clusters for big data processing | Large-scale data processing, ML training |
| Amazon QuickSight | Serverless, ML-powered BI dashboards | Business analytics, embeddable visualizations |
| AWS Glue | Serverless ETL and data catalog service | Preparing/transforming data for analytics |
| AWS Lake Formation | Automates building a secure S3-based data lake | Centralized data lake with fine-grained access control |
| Amazon Managed Service for Apache Flink | Managed stream processing with Apache Flink | Real-time stream analytics on Kinesis/MSK data |
| Amazon MSK | Managed Apache Kafka | Kafka-based streaming pipelines |
| Amazon Rekognition | Image/video analysis (objects, faces, moderation) | Content moderation, facial search |
| Amazon Transcribe | Speech-to-text | Call transcription, closed captioning |
| Amazon Polly | Text-to-speech | Voice-based apps, accessibility |
| Amazon Translate | Language translation | Localizing websites/apps for international users |
| Amazon Lex | Conversational AI / chatbot engine | Building chatbots, call-center bots |
| Amazon Connect | Cloud-based contact center | Customer service call centers |
| Amazon Comprehend | NLP: sentiment, entities, key phrases | Mining customer feedback, topic grouping |
| Amazon Comprehend Medical | NLP for clinical text, PHI detection | Healthcare document analysis |
| Amazon SageMaker AI | Build/train/deploy custom ML models | Custom ML use cases needing full model control |
| Amazon Kendra | ML-powered enterprise document search | Natural-language search across enterprise documents |
| Amazon Personalize | Real-time personalized recommendations | Product recommendations, targeted marketing |
| Amazon Textract | Extract text/forms/tables from scanned documents | Invoice, medical record, and tax form processing |

### Networking & Content Delivery

| Service | What It's Used For | Common Use Cases |
|---|---|---|
| Amazon Route 53 | Managed DNS and domain registration | Traffic routing, health-check-based failover |
| Amazon VPC | Isolated virtual network for AWS resources | Custom network topology, subnetting, security |
| Amazon CloudFront | Global content delivery network (CDN) | Low-latency content delivery, DDoS mitigation |
| AWS Global Accelerator | Static anycast IPs routing traffic over the AWS backbone | Non-HTTP global apps, fast regional failover |
| Amazon API Gateway | Managed API front door | Serverless REST/HTTP/WebSocket APIs |
| Amazon Cognito | User authentication for web/mobile apps | App login, temporary AWS credentials for end users |
| AWS Direct Connect | Dedicated private network link to AWS | High-bandwidth, low-latency hybrid connectivity |
| AWS Site-to-Site VPN | Encrypted IPsec connection to a VPC over the internet | Quick/interim hybrid connectivity, DX backup |
| AWS Transit Gateway | Hub-and-spoke transitive routing across VPCs/VPNs/DX | Simplifying networking at scale across many VPCs |
| AWS Network Firewall | Managed network firewall for a VPC | Layer 3–7 traffic filtering and intrusion prevention |

### Application Integration & Messaging

| Service | What It's Used For | Common Use Cases |
|---|---|---|
| Amazon SQS | Managed message queue | Decoupling producers/consumers, buffering load spikes |
| Amazon SNS | Pub/sub notification service | Fan-out messaging, alerting |
| Amazon Kinesis Data Streams | Real-time data streaming and processing | Clickstream/log ingestion, real-time analytics |
| Amazon Data Firehose | Near-real-time streaming delivery to storage/analytics targets | Loading streaming data into S3/Redshift/OpenSearch |
| Amazon EventBridge | Serverless event bus | Event-driven architectures, scheduled jobs |
| AWS Step Functions | Visual workflow orchestration (state machines) | Multi-step business processes, order fulfillment |
| Amazon MQ | Managed RabbitMQ/ActiveMQ message broker | Migrating on-prem apps that use open messaging protocols |
| Amazon SES | Managed email sending/receiving service | Transactional and marketing email |
| Amazon Pinpoint | Two-way marketing communications (email/SMS/push) | Targeted, scheduled marketing campaigns |

### Monitoring, Management & DevOps

| Service | What It's Used For | Common Use Cases |
|---|---|---|
| Amazon CloudWatch | Metrics, logs, dashboards, and alarms | Monitoring performance, triggering Auto Scaling |
| AWS CloudTrail | Logs every API call made in an account | Governance and security auditing |
| AWS Config | Tracks resource configuration and compliance over time | Compliance auditing, configuration drift detection |
| AWS CloudFormation | Infrastructure as Code via declarative templates | Repeatable, version-controlled infrastructure deployment |
| AWS Systems Manager (SSM) | Hybrid operations toolset (Session Manager, Run Command, Patch Manager) | Remote management without SSH, patching server fleets |
| AWS Backup | Centralized managed backup across AWS services | Cross-service backup policies, WORM vault lock |
| AWS Trusted Advisor | Automated best-practice checks across an account | Cost, security, performance, and fault-tolerance reviews |

### Disaster Recovery & Migration

| Service | What It's Used For | Common Use Cases |
|---|---|---|
| AWS Elastic Disaster Recovery (DRS) | Continuous replication for fast disaster recovery | Ransomware/DR protection for physical/virtual/cloud servers |
| AWS Database Migration Service (DMS) | Migrates databases while the source stays live | Homogeneous and heterogeneous database migrations |
| AWS Schema Conversion Tool (SCT) | Converts database schemas between engines | Cross-engine migrations (e.g., Oracle → Aurora) |
| AWS Application Discovery Service | Gathers on-prem server data for migration planning | Migration Hub inventory and dependency mapping |
| AWS Application Migration Service (MGN) | Lift-and-shift server migration to AWS | Rehosting physical/virtual/cloud servers |
| VM Import/Export | Import/export VM images between on-prem and EC2 | VM-based migration, DR repository strategy |
| VMware Cloud on AWS | Runs the VMware SDDC stack on AWS infrastructure | Extending on-prem VMware environments into AWS |

### Cost Management

| Service | What It's Used For | Common Use Cases |
|---|---|---|
| AWS Cost Explorer | Visualize, analyze, and forecast AWS cost/usage | Cost analysis, Savings Plan recommendations |
| AWS Cost Anomaly Detection | ML-based detection of unusual spend | Automated spend anomaly alerts |
| AWS Budgets | Tracks and alerts on spend against a threshold | Budget governance and alerting |

### Specialized / Hybrid

| Service | What It's Used For | Common Use Cases |
|---|---|---|
| Amazon AppFlow | Transfers data between SaaS apps and AWS | SaaS-to-AWS data integration (Salesforce, Slack, etc.) |
| AWS Amplify | Toolset for full-stack web/mobile app development | Rapid app development with auth/storage/API backend |
| Instance Scheduler on AWS | Automates start/stop of EC2/RDS on a schedule | Cutting non-prod costs outside business hours |
| AWS ParallelCluster | Open-source HPC cluster management/orchestration | Automating HPC cluster provisioning |

---

## 2. Most Important Points (50 Bullets)

**Identity & Security**

1. IAM is global; use roles (not hardcoded keys) for EC2/Lambda to access other AWS services.
2. Policy evaluation: an explicit Deny always wins; otherwise an Allow is needed at every applicable layer (SCP, resource, identity, boundary).
3. Permission boundaries cap the max permissions of an IAM user/role; SCPs govern entire accounts via Organizations.
4. KMS: AWS manages the keys for you; CloudHSM: AWS manages only the hardware, you fully own the keys.
5. Secrets Manager auto-rotates secrets via Lambda and integrates natively with RDS credentials.
6. AWS WAF filters Layer 7 (HTTP) threats on ALB/API Gateway/CloudFront; Shield protects against Layer 3/4 DDoS.
7. GuardDuty uses ML on CloudTrail, VPC Flow Logs, and DNS logs to detect threats with no agents required.
8. IAM Identity Center provides SSO across AWS accounts and SaaS apps via Permission Sets and attribute-based access.
9. Amazon Inspector scans EC2 (via SSM), ECR images, and Lambda functions for known vulnerabilities.

**Compute**

10. EC2 purchasing trades commitment for discount: On-Demand, Reserved/Savings Plans, or Spot (up to 90% off, interruptible).
11. Security Groups are stateful and allow-only; NACLs are stateless and support explicit deny at the subnet level.
12. Auto Scaling Groups keep EC2 instance count within a min/max/desired range, paired with a Load Balancer.
13. Lambda is serverless, billed per request and duration, capped at 15-minute executions, needs VPC config for private resources.
14. AWS Fargate removes all EC2 server management for ECS/EKS containers; you only define task CPU/RAM.
15. ALB routes Layer 7 HTTP traffic by path/host; NLB handles Layer 4 traffic at millions of requests/sec with static IPs.

**Storage**

16. S3 offers 11-nines durability across all storage classes; availability and retrieval cost vary by class.
17. S3 replication (CRR/SRR) requires versioning on both buckets and only replicates new objects going forward.
18. EBS is single-instance block storage; EFS is a shared NFS file system mountable by many instances across AZs.
19. Snow Family devices move offline data faster than a network transfer when that transfer would take roughly a week or more.
20. FSx offers managed third-party file systems: Windows File Server (SMB), Lustre (HPC), NetApp ONTAP, and OpenZFS.
21. Storage Gateway bridges on-prem to S3/EBS-backed storage via File, Volume, or Tape Gateway modes.

**Databases**

22. RDS Multi-AZ gives synchronous failover for high availability; Read Replicas give asynchronous read scaling (up to 15).
23. Aurora stores six copies across three AZs, fails over in under 30 seconds, and offers Global Database for multi-region reads.
24. ElastiCache Redis supports HA, persistence, and replicas; Memcached only supports sharding, with no persistence.
25. DynamoDB is a NoSQL store scaling to millions of requests/sec; DAX adds microsecond in-memory caching in front of it.
26. Redshift is a columnar OLAP data warehouse; Redshift Spectrum queries S3 data directly without loading it first.
27. Athena runs serverless SQL directly against S3 data; partitioning and columnar formats reduce scan cost.

**Networking**

28. Route 53 is a highly available DNS service with the only 100% availability SLA, supporting many routing policies.
29. VPC Peering is not transitive; Transit Gateway solves transitive routing across many VPCs at scale.
30. Gateway VPC Endpoints (S3/DynamoDB) are free; Interface Endpoints cover other services via a priced ENI.
31. CloudFront caches content globally at edge locations and secures private S3 origins with Origin Access Control.
32. Global Accelerator proxies TCP/UDP traffic over AWS's private backbone using two static Anycast IPs, without caching.
33. API Gateway fronts REST/HTTP/WebSocket APIs; Edge-Optimized routes through CloudFront, Regional and Private serve narrower audiences.
34. Cognito User Pools handle sign-up/sign-in; Identity Pools exchange logins for temporary AWS credentials.

**Messaging & Integration**

35. SQS decouples producers/consumers with at-least-once delivery; FIFO queues add strict ordering at lower throughput.
36. SNS fans out one published message to many subscribers, including SQS, Lambda, email, SMS, and HTTP endpoints.
37. Kinesis Data Streams is real-time and replayable up to 365 days; Data Firehose is near-real-time with no replay.
38. EventBridge is a serverless event bus routing schedule- and pattern-based events to many AWS destinations.
39. Step Functions orchestrates multi-step workflows across Lambda and other AWS services with built-in retries and error handling.

**Monitoring & DevOps**

40. CloudWatch handles metrics, logs, and alarms; CloudTrail audits every API call made in an account.
41. AWS Config tracks resource configuration compliance over time but does not block non-compliant actions.
42. CloudFormation is declarative Infrastructure as Code; StackSets deploy the same template across many accounts/regions.
43. Systems Manager Session Manager gives shell access without SSH, bastion hosts, or an open port 22.
44. AWS Backup centralizes backup policies across many services; Vault Lock enforces WORM retention even against the root user.

**DR, Migration & Cost**

45. DR strategies scale by cost and RTO/RPO: Backup & Restore, Pilot Light, Warm Standby, then Multi-Site Active/Active.
46. AWS DMS migrates databases while the source stays live; the Schema Conversion Tool handles cross-engine schema changes.
47. Cost Explorer analyzes and forecasts spend; Cost Anomaly Detection uses ML to flag unusual spend automatically.
48. Data transfer costs: same-AZ private IP traffic is free; cross-AZ, cross-region, and internet egress cost more.
49. The Well-Architected Framework's six pillars — Operational Excellence, Security, Reliability, Performance, Cost, Sustainability — work as a synergy, not trade-offs.
50. Exam questions are largely about matching scenario trigger words (e.g., "least operational overhead," "millisecond latency") to the right service.
