# AWS SAA-C03 Study Guide — Summary

> Condensed companion to [AWS-SAA-C03-Study-Guide-Core.md](AWS-SAA-C03-Study-Guide-Core.md) and [AWS-SAA-C03-Study-Guide-Additional.md](AWS-SAA-C03-Study-Guide-Additional.md). Use this as a quick-reference index and a final-review checklist, not a replacement for the full guides.

---

## 1. AWS Services Covered

### Storage

| Service | What It's Used For | Common Use Cases |
|---|---|---|
| **Amazon S3** [#1 pop] | Object storage with virtually unlimited scale | Data lakes, backups, static website hosting, archiving |
| Amazon EBS [#18 pop] | Persistent block storage for a single EC2 instance | Boot volumes, databases, high-IOPS workloads |
| Amazon EFS [#19 pop] | Managed NFS shared across many EC2 instances/AZs | Shared content storage, CMS, home directories |
| Snow Family (Snowball / Snowcone / Snowmobile) | Physical devices for offline bulk data transfer/edge compute | Large one-time migrations, edge sites with poor connectivity |
| Amazon FSx [#16 pop] | Managed third-party file systems (Windows/Lustre/ONTAP/OpenZFS) | HPC, Windows shares, NetApp/ZFS lift-and-shift |
| AWS Storage Gateway | Ongoing repl. on-prem environments to S3/EBS-backed storage | Hybrid backup, tiered storage, tape-backup replacement |
| AWS Transfer Family | Managed FTP/FTPS/SFTP endpoints into S3/EFS | Legacy file-transfer protocol integrations |
| AWS DataSync | 1-time/scheduled data transfer between on-prem and cloud storage systems | Migrating large datasets, ongoing sync |



### Compute

| Service | What It's Used For | Common Use Cases |
|---|---|---|
| **EC2** [#2 pop] | Virtual machines with configurable OS/CPU/RAM/storage | General-purpose hosting, web servers, batch jobs, HPC |
| **Auto Scaling** Groups (ASG) [#4 pop] | Automatically adjusts EC2 instance count to meet demand | Elastic horizontal scaling, self-healing fleets |
| Elastic Load Balancing (ALB/NLB/GWLB/CLB) [#14 pop] | Distributes traffic across targets with health checks | HTTPS routing (ALB), high-throughput TCP/UDP (NLB), 3rd-party sec. appliances (GWLB) |
| AWS **Lambda** [#3 pop] | Runs code without managing servers, billed per invocation | Event-driven microservices, glue logic, scheduled tasks |
| Amazon *ECS* [#13 pop] | AWS-native container orchestration | Running Docker containers on EC2 or Fargate |
| Amazon EKS | Managed Kubernetes control plane | Migrating/running Kubernetes workloads on AWS |
| AWS Fargate [#17 pop] | Serverless compute engine for ECS/EKS tasks | Running containers without managing EC2 instances |
| AWS Elastic Beanstalk | PaaS that provisions/manages infra for your app code | Fast deployment of web apps without infra management |
| AWS Batch | Fully managed batch job scheduling and compute provisioning | Large-scale batch/ETL processing jobs |
| AWS Outposts | AWS *on-prem* infrastructure and services | Low-latency on-prem processing, data residency |


### Networking & Content Delivery

| Service | What It's Used For | Common Use Cases |
|---|---|---|
| Amazon Route 53 [#24 pop] | Managed DNS and domain registration | Traffic routing, health-check-based failover |
| *Amazon VPC* [#6 pop] | Isolated virtual network for AWS resources | Custom network topology, subnetting, security |
| *Amazon CloudFront* [#7 pop] | Global content delivery network (CDN) | Low-latency content delivery, DDoS mitigation |
| AWS Global Accelerator | Static Anycast IPs routing traffic over the AWS backbone (for EC2 stuff) | *Non-HTTP*, *multi-region routing*, fast regional *failover* |
| Amazon API Gateway [#15 pop] | Managed API front door | Serverless REST/HTTP/WebSocket APIs |
| Amazon Cognito | User authentication for web/mobile apps | App login, temporary AWS credentials for end users |
| AWS Direct Connect | Dedicated private network link to AWS | High-bandwidth, low-latency hybrid connectivity |
| AWS Site-to-Site VPN | Encrypted IPsec connection to a VPC over the internet | Quick/interim hybrid (on-prem VPN) connectivity, DX backup |
| AWS Transit Gateway | Hub-and-spoke transitive routing across VPCs/VPNs/DX | Simplifying networking at scale across many VPCs |
| AWS Network Firewall | Managed network firewall for a VPC | Layer 3–7 traffic filtering and intrusion prevention |


### Databases

| Service | What It's Used For | Common Use Cases |
|---|---|---|
| **Amazon RDS** [#5 pop] | Managed relational databases (multiple engines) | OLTP apps needing HA and automated backups |
| *Amazon Aurora* [#10 pop] | AWS-proprietary MySQL/PostgreSQL-compatible database | High-performance, auto-scaling relational workloads |
| Amazon ElastiCache | Managed in-memory Redis/Memcached | Caching, session storage, gaming leaderboards |
| *Amazon DynamoDB* [#9 pop] | Managed NoSQL key-value/document store | High-scale web/mobile apps, gaming |
| Amazon Redshift | Columnar OLAP data warehouse | Business intelligence, large analytical queries |
| Amazon DocumentDB | MongoDB-compatible managed NoSQL database | JSON document storage and querying |
| Amazon Neptune | Managed graph database | Social networks, fraud detection, recommendation engines |
| Amazon Keyspaces | Managed Cassandra-compatible database | IoT device data, time-series data at scale |
| Amazon Timestream | Managed time-series database | IoT/operational metrics, real-time analytics |
| Amazon QLDB | Immutable, cryptographically verifiable ledger database | Ledger/transaction history requiring tamper-evidence |


### Application Integration & Messaging

| Service | What It's Used For | Common Use Cases |
|---|---|---|
| *Amazon SQS* [#8 pop] | Managed message queue | Decoupling producers/consumers, buffering load spikes |
| Amazon SNS  [#20 pop] | Pub/sub notification service | Fan-out messaging, alerting |
| Amazon Kinesis Data Streams | Real-time data streaming and processing | Clickstream/log ingestion, real-time analytics |
| MS Apache Flink/Amazon Kinesis Data Analytics | Processes real-time streaming data using SQL or Apache Flink | Real-time analytics, live dashboards, time series analytics |
| Amazon Data Firehose | Near-real-time streaming delivery to storage/analytics targets | Loading streaming data into S3/Redshift/OpenSearch |
| Amazon EventBridge [#21 pop] | Events router to many targets | Event-driven architectures, scheduled jobs |
| AWS Step Functions | Visual workflow orchestration (state machines) | Multi-step business processes, order fulfillment |
| Amazon MQ | Managed RabbitMQ/ActiveMQ message broker | Migrating on-prem apps that use open messaging protocols |
| Amazon SES | Managed email sending/receiving service | Transactional and marketing email |
| Amazon Pinpoint | Two-way marketing communications (email/SMS/push) | Targeted, scheduled marketing campaigns |


### Caching

| Service | What It's Used For | Common Use Cases |
|---|---|---|
| Amazon ElastiCache | Managed in-memory Redis/Memcached | Caching, session storage, gaming leaderboards |
| Amazon DynamoDB Accelerator (DAX) | Microsecond in-memory cache for DynamoDB | Read-heavy/bursty DynamoDB workloads needing microsecond latency |
| API Gateway Response Caching | Caches API responses at the API Gateway stage level | Reducing backend load/latency for repeated API calls |


### Identity, Access & Security

| Service | What It's Used For | Common Use Cases |
|---|---|---|
| *IAM* [#11 pop] | Manage users, groups, roles, and permission policies | Least-privilege access control, cross-account roles, MFA enforcement |
| AWS Organizations | Centrally manage multiple AWS accounts with consolidated billing | Multi-account governance, Service Control Policy (SCP) guardrails |
| AWS Control Tower | Automated setup/governance of a secure multi-account landing zone | Enterprise multi-account environments with guardrails |
| AWS KMS [#12 pop] | AWS-managed encryption key creation, rotation, and usage auditing | Encrypting S3/EBS/RDS data (SSE-KMS), envelope encryption |
| AWS CloudHSM | Dedicated, single-tenant hardware security modules you fully control | Compliance needing full key custody, Oracle TDE, Redshift encryption |
| AWS Secrets Manager | Store and auto-rotate secrets like DB credentials | RDS credential rotation, multi-region secret replication |
| SSM Parameter Store | Secure hierarchical storage for config values and secrets | App configuration, KMS-encrypted secrets, expiration policies |
| AWS Certificate Manager (ACM) | Provision and auto-renew TLS/SSL certificates | HTTPS on ALB/CloudFront/API Gateway |
| AWS WAF [#25 pop] | Layer 7 firewall filtering HTTP requests | Blocking SQLi/XSS, rate limiting, geo-blocking |
| AWS Shield | DDoS protection (Layer 3/4, and Layer 7 with Advanced) | Protecting EC2/ELB/CloudFront from DDoS attacks |
| AWS Firewall Manager | *Centrally manage* WAF/Shield/Security Group rules org-wide | Multi-account security policy compliance |
| Amazon GuardDuty | ML-based threat detection across CloudTrail/VPC/DNS logs | Detecting compromised instances, crypto-mining, anomalous API calls |
| Amazon Inspector | Automated *vulnerability scanning* for EC2/ECR/Lambda | Finding known CVEs in workloads and container images |
| Amazon Macie | ML-based discovery of sensitive data (*PII*) in S3 | Data privacy audits, compliance scanning |
| AWS IAM Identity Center | *SSO* across AWS accounts and business apps | Workforce SSO, permission sets, attribute-based access control |
| AWS Directory Service (Managed AD / AD Connector / Simple AD) | Managed Microsoft Active Directory options in AWS | Windows workload auth, hybrid AD trust relationships |


### Analytics & Machine Learning

| Service | What It's Used For | Common Use Cases |
|---|---|---|
| Amazon Athena [#22 pop] | Serverless SQL queries directly on S3 data | Ad hoc analysis of S3 data, log querying |
| Amazon OpenSearch Service | Managed search/analytics engine (search any field) | Full-text search, log analytics dashboards |
| Amazon EMR | Managed *Hadoop/Spark* clusters for big data processing | Large-scale data processing, ML training |
| Amazon QuickSight | Serverless, ML-powered BI dashboards | Business analytics, embeddable visualizations |
| AWS Glue | Serverless *batch* ETL and data catalog service | Preparing/transforming in batch data for analytics |
| AWS Lake Formation | Automates building a secure S3-based data lake | Centralized data lake with fine-grained access control |
| Amazon Managed Service for Apache Flink | Managed stream processing with Apache Flink | Real-time stream analytics on Kinesis/MSK data |
| Amazon MSK | Managed Apache Kafka | Kafka-based streaming pipelines |
| Amazon Rekognition | Image/video analysis (objects, faces, moderation) | Content moderation, facial search |
| Amazon Transcribe | Speech-to-text | Call transcription, closed captioning |
| Amazon Polly | *Text-to-speech* | Voice-based apps, accessibility |
| Amazon Translate | Language translation | Localizing websites/apps for international users |
| Amazon Lex | Conversational AI / *chatbot* engine | Building chatbots, call-center bots |
| Amazon Connect | Cloud-based contact center | Customer service *call centers* |
| Amazon Comprehend | *NLP*: sentiment, entities, key phrases | Mining customer feedback, topic grouping |
| Amazon Comprehend Medical | NLP for clinical text, PHI detection | Healthcare document analysis |
| Amazon SageMaker AI | Build/train/deploy custom ML models | Custom ML use cases needing full model control |
| Amazon Kendra | ML-powered enterprise document search | Natural-language search across enterprise documents |
| Amazon Personalize | Real-time personalized recommendations | Product recommendations, targeted marketing |
| Amazon Textract | *Extract* text/forms/tables from *scanned* documents | Invoice, medical record, and tax form processing |


### Monitoring, Management & DevOps

| Service | What It's Used For | Common Use Cases |
|---|---|---|
| Amazon CloudWatch [#23 pop] | Metrics, logs, dashboards, and alarms | Monitoring performance, triggering Auto Scaling |
| AWS CloudTrail | Logs every API call made in an account | Governance and security auditing |
| AWS Config | Tracks resource configuration and compliance over time | Compliance auditing, configuration drift detection |
| AWS CloudFormation | Infrastructure as Code via declarative templates | Repeatable, version-controlled infrastructure deployment |
| AWS Systems Manager (SSM) | *Hybrid operations* toolset (Session Manager, Run Command, Patch Manager) | Remote management without SSH, patching server fleets |
| AWS Backup | Centralized managed backup across AWS services | Cross-service backup policies, WORM vault lock |
| AWS Trusted Advisor | Automated *best-practice checks* across an account | Cost, security, performance, and fault-tolerance reviews |
| AWS X-Ray | Distributed *tracing* for analyzing/debugging apps | Tracing requests across microservices, latency bottleneck analysis |


### Disaster Recovery & Migration

| Service | What It's Used For | Common Use Cases |
|---|---|---|
| AWS Elastic Disaster Recovery (DRS) | Continuous replication for fast disaster recovery | Ransomware/DR protection for physical/virtual/cloud servers |
| AWS Application Migration Service (MGN) | Lift-and-shift migration - cont repl & fast cutover | Rehosting physical/virtual/cloud servers |
| AWS Application Discovery Service | Gathers on-prem server data for migration planning | Migration Hub inventory and dependency mapping |
| AWS Database Migration Service (DMS) | Migrates databases while the source stays live | Homogeneous and heterogeneous database migrations |
| AWS Schema Conversion Tool (SCT) | Converts database schemas between engines | Cross-engine migrations (e.g., Oracle → Aurora) |
| AWS Workload Discovery on AWS | Visualizes on-prem/AWS workloads and their dependencies | Architecture diagramming and dependency mapping for migration planning |
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

## 2. Subservices or Terms for Popular Services

1. **S3**
  - S3 Storage Classes (*Standard/IA/One Zone-IA/Glacier/Deep Archive/Intelligent-Tiering*)
  - S3 *Lifecycle* Policies 
  - S3 *Versioning* 
  - S3 Object *Lock* 
  - S3 Replication (CRR/SRR)
  - S3 Transfer Acceleration { Speeds up uploads via CloudFront edge }
  - S3 Access Points { endpoints for shared buckets } 
  - S3 Multi-Region Access Points { global endpoint routing to closest bucket replica } 
  - S3 Object Lambda - modify S3 GET responses on the fly 
  - S3 Batch Operations
  - S3 Select / Glacier Select - Retrieves a subset of object data using SQL-like queries 
  - S3 Event Notifications {Targets: SQS, SNS, Lambda & EventBridge (for many targets)}
  - S3 Storage Lens - Organization-wide visibility into S3 usage and activity metrics 
  - S3 Access Analyzer - Analyzes and prevents unintended public bucket exposure

2. **EC2**
  - General type (`t/m`), Compute type (`c`), Memory type (`r/x`) & Storage type (`i/d`)
  - Purchase options: On-Demand, Reserved, Covertible Reserved (can change type), Savings (commit to $/hours), Spot, Spot Fleet, Dedicated Host (dedicated physical server, BYOL), Dedicated Instances (dedicated inst, no control over HW type)
  - Capacity Reservation
  - Placement: Cluster (perf), Spread (HA) & Partition
  - Security Group (stateful firewall)
  - Elastic IP
  - Elastic Network Interface (ENI)
  - Hibernate: fast startup
  - Instance Store

3. **Lambda**
  - Reserved concurrency (limit conccurent exec)
  - Provisioned Concurrency (avoid cold start) & Lambda SnapStart (fast startup)
  - Cloudfront Function (lightweight JS Lambda) & Lambda @Edge (fuller Lambda exec @edge)

4. **ASG**
  - Launch Template vs Launch Config
  - Scaling Policies: (1) Simple/Step, (2) Target Tracking, (3) Scheduled, (4) Predictive
  - Scaling Cooldown

5. **RDS**
  - point in time recovery (PITR), cross region read replica (read scaling), Multi-AZ (standby failover)
  - RDS custom: for Oracle & SQL Server
  - Storage Auto Scaling
  - RDS Proxy

6. **VPC** 
  - Basics
    - Layer 3 {Network, IP Address}, Layer 4 {Protocol, TCP/UDP}, Layer 7 {App, HTTPS}
    - Classless Inter-Domain Routing or CIDR {No overlap}
    - Subnets {public or private, inbound traffic}
    - Route Table
    - Internet Gateway or IGW
    - Bastion Host
    - Network Address Translation or NAT {provide outbound internet access for private subnet, usually in public subnet}
      - NAT Gateway {AWS managed, per AZ}
      - NAT Instance {self-managed}
      - Regional NAT Gateway {attach to whole VPC, not per AZ}
  - Security
    - NACL (Network Access Control List) {stateless firewall, inbound & outbound traffic needs to be specified, operate @ subnet}
      - Ephemeral port {client port for receiving response}
    - VPC Flow Log {capture IP traffic @ VPC, subnet or ENI}
    - VPC Traffic Mirror {monitoring traffic}
    - AWS Network Firewall
  - Connecting VPC
    - VPC Peering {Not transitive}
    - VPC Endpoint or AWS Private Link {expose AWS services or own apps through VPC}
      - Gateway Endpoint {S3 or DynamoDB only}
      - Interface Endpoint {most services and hosted-apps, thru ENI}
    - Site-to-Site VPN {on-prem to VPC, non-transitive, connects 1 CGW to 1 VGW, VGW need Route Propagation enabled}
    - AWS VPN CloudHub {hub-and-spoke, transitive, many CGWs to 1 VGW}
    - Direct Connect (DX) {Dedicated DX: Fast speed,  Hosted: Slower}
    - Transit Gateway {hub-and-spoke, transitive, connects VPN, VPC & DX together}
      - Equal Cost Multipath Routing {combine multiple Site-to-Site VPN for faster bandwidth}

7. Cloudfront
  - Origins {S3, private subnet VPC comp, custom HTTP}
  - Geo-Restrictions {allow/block}
  - Cache Invalidation
  - Signed URL/Cookies {private content}

8. SQS
  - Message visibility timeout {default 30s}
  - Long Polling {reduce API call count}
  - Dead Letter Queue {failed messages}
  - Standard Queue {best effort order, unlimited msg/s, dup msg}
  - FIFO Queue {FIFO order, 3000 msg/s, dedup msg, name ends with `.fifo`}

9. DynamoDB
  - Standard IA tables {60% lower storage cost, read/write cost up 25%}
  - Provisioned Capacity {provision read/write, cheaper, auto-scalable with Cloudwatch & more}
  - On-Demand capacity {more \$\$\$, natively auto-scalable}
  - DynamoDB Accelerator/DAX {in-memory cache in front of Dynamo}
  - DynamoDB streams {old, targets: Lambda or DynamoDB Streams Kinesis Adapter library (i.e. your app)}
  - Kinesis Data Streams for DynamoDB {newer, targets: Lambda, Kinesis Data Analytics, Firehose, Glue Streaming ETL}
  - Global Tables {active-active, requires streams}
  - TTL {auto delete}
  - Backup: PITR vs On-demand
  - Export to S3 {need PITR, doesn't use read cap, JSON/ION format}
  - Import from S3 {always new table, doesn't use write cap, CSV/JSON/ION format}

10. Aurora
  - Cluster endpoints: Writer, Reader {load balanced across repl} & Customs {subset of inst, Reader not used anymore}
  - Aurora Serverless {unpredictable workload, no cap planning}
  - Global DB {better than cross-region repl, RTO < 1m}
  - Aurora Machine Learning {SQL integrated with Sagemaker & Comprehend}
  - Babelfish for Aurora Pgres {understand MS SQL Server's T-SQL}
  - Backup: PITR, DB Cloing {copy-on-write, fast & cheap}

11. IAM
  - JSON `Statement` field: `Sid`, `Effect`, `Principal`, `Action`, `Resource` & `Condition`
  - IAM Roles vs Users
  - Cross Account Access
  - Policy eval flow {Explicit Deny > Explicit Allow > Default Deny}
  - Security Token Service (STS) {Federation & Cross account access}
  - Identity Federation
  - MFA
  - IAM Credential Report {user & their credential status, account-level}
  - IAM Access Advisor {right-size user permissions, report per user}

12. KMS
  - AWS Owned Keys {S3, SQS, DynamoDB} vs AWS Managed Keys {RDS, EBS} vs Custom Managed Keys {created vs imported}
  - Automatic Key Rotation {Imported customer key cannot use this}
  - Multi Region Keys {multi-region identical keys, not single global key}
  - Key Policy {Custom policy for cross account}


13. ECS
  - EC2 launch type {Requires ECS agent installed, uses EC2 inst prof IAM role}
  - Fargate launch type {define & scale tasks}
  - ECS Task Role {access AWS resources}
  - ECS Auto Scaling Policies: (1) Simple, (2) Step, (3) Target Tracking, (4) Scheduled
  - Event Driven Task {uses EventBridge}

14. ELB
  - Health Check {uses 200 status code}
  - X-Forwarded-For {client real IP}
  - ALB {Layer 7, multi-app routing}
  - NLB {Layer 4, ultra-low latency}
  - GWLB {Layer 3, 3rd party appliances}
  - Sticky sessions
  - SSL/TLS via SNI {multi certs on 1 LB}
  - Connection Draining/Deregistration Delay

15. API Gateway
  - Integrations: Lambda, HTTP, AWS Services
  - Edge-optimized endpoint
  - Regional endpoint
  - Private endpoint {ENI on VPC}

16. FSx
  - Windows File Server {SMB, AD}
  - Lustre {HPC, S3 integration}
  - NetApp ONTAP {NetApp/NAS, NFS/SMB/iSCSI access}
  - OpenZFS {ZFS, highest IOPS}

18. EBS
  - gp3 {provisionable IOPS, 16k IOPS, almost always better than gp2}
  - io1/io2 block express {critical DB workloads, up to 250k IOPS, attach to multi-EC2}
  - st1 {500 IOPS} vs sc1 {250 IOPS, lowest cost, infrequently access data}
  - Fast Snapshot Restore {remove first use latency}
  - Snapshot Archieve {fastest 24h restore, 75% lower cost}
  - Recycle Bin {prevent accidental snapshot deletion}
  - EBS encryption {at rest, in-flight, snapshot, volume}
  - Inst Deletion: Root {default to 'delete'}, attached {default to 'preserved'}

20. SNS
  - Subscribers/Dest: (1) SQS, (2) Lambda, (3) Firehose, (4) Email/SMS/Mobile, (5) HTTPS
  - Sources: (1) Cloudwatch Alarms, (2) Auto Scale, (3) S3 Events, (4) DMS, (5) RDS, (6) Dynamo, (7) Lambda
  - Topic Publish vs Direct Publish (publish to platform endpoint)
  - SNS Access Policies {cross account, AWS service to pub}
  - Fan-out
  - FIFO Topic {order & dedup}
  - Message Filtering {subscribe limits topics}

21. Amazon EventBridge
  - Schedule vs Event Trigger
  - Source: EC2, S3, TrustedAdvisor, CloudTrail, Schedule
  - Dest {> SNS}: (1) Compute, (2) Messaging & Steams, (3) Orchestration, (4) Maintenance
  - Event bus type {mainly for event subscriptions or sources, cross acc via policies}
    - (1) Default {AWS services}, (2) Partner {SaaS} & (3) Custom {Own App}
  - Schema Registry {infer version & generate code}


22. Athena
  - ORC, Parquet {Columnar, perf}
  - Federated query {query across many type sources with Lambda-based Connectors}

23. Cloudwatch
  - Metrics Stream {stream metrics near-real-time}
  - Log Groups vs Log Streams
  - Alarms
  - Network Synthetic Monitor {monitor network path between (1) AWS with on-prem or (2) DX/Site-to-Site }
  - Container Insights {metrics + logs}
  - Lambda Insights {metrics}
  - Contributor Insights {top N contributors}
  - Application Insights {automated problems discovery}

24. Route53
  - Public Hosted Zone
  - Private Hosted Zone {route traffic between VPCs}
  - A Record {IP4} vs AAAA Record {IP6}
  - CNAME Record {hostname. Target hostname must have A or AAAA}
  - Alias Record {AWS resource}
  - Routing Policies: (1) Simple, (2) Weighted, (3) Latency, (4) Failover, (5) Geolocation, (6) Geoproximity, (7) IP, (8) Mult-value
  - Health Check {failover}
  - Calculated Health Check {using AND/OR}
  - Route53 Hybrid Resolver {resolving DNS between VPC + VPN}
    - Inbound endpoint {enable on-prem to query Route53}
    - Outbound endpoint {enable VPC to query on-prem resolver}

25. WAF
  - Target: (1) ALB, (2) API Gateway, (3) Cloudfront, ...
  - WebACL {IP, HTTP metadata, Geo, Rate, ...}
  - Rule Group {bundle of rule, attachable to WebACL}

---

## 3. Important Points 


### Storage — S3, EBS, EFS, FSx

1. S3 offers **eleven-9's durability** across all storage classes; availability, retrieval time/cost, and minimum storage duration vary by class.
2. S3 **Lifecycle** rules *automate transitions* between storage classes and expirations; **Intelligent-Tiering** auto-moves objects between access tiers with no retrieval fees.
3. S3 Cross-Region/Same-Region **Replication** requires *versioning* on *both buckets* and only *replicates new objects* going forward (not retroactively).
4. S3 **Transfer Acceleration** speeds long-distance uploads via CloudFront edge locations; **Multipart Upload** parallelizes and resumes large object uploads.
6. EBS is persistent block storage attached to a single EC2 instance in the same AZ; types: **gp3**/gp2 (general SSD), io1/**io2** (high/provisioned IOPS, databases), st1 (throughput HDD), sc1 (cold HDD).
7. EBS snapshots are incremental and stored in S3, can be copied across regions/accounts for DR, and **Fast Snapshot Restore** removes first-use latency.
8. EFS is a managed, multi-AZ NFS file system *mountable concurrently* by many EC2/Linux instances (vs. EBS: single-instance, single-AZ).
9. EFS offers **Standard** and **Infrequent Access** storage classes with Lifecycle Management, plus Bursting, Provisioned, and Elastic throughput modes.
10. FSx provides managed third-party file systems: Windows File Server (SMB, AD-integrated), Lustre (HPC), NetApp ONTAP, and OpenZFS.
11. FSx for *Lustre* links directly to an *S3* bucket for *high-throughput, low-latency processing* of S3 data (e.g., ML training, big data workloads).

### Compute — EC2, Lambda, EC2 Auto Scaling, ECS, Fargate, ALB

13. Security Groups are *stateful*, instance-level, allow-only; **NACLs** are *stateless*, subnet-level, and support explicit deny rules evaluated in rule-number order.
14. EC2 **instance store** is ephemeral (*lost* on stop/terminate); EBS-backed instances *persist data* and support stop/start; AMIs snapshot the root EBS volume for reuse.
16. Lambda is *serverless*, billed per invocation/duration in ms, capped at a **15-minute timeout**, and only needs VPC config (via an ENI) to reach private resources like RDS.
17. Lambda concurrency: **reserved concurrency** caps/guarantees *capacity* per function; **provisioned concurrency** *pre-warms* execution environments to eliminate cold starts.
18. Lambda *scales automatically* per-request with no capacity planning; destinations and **DLQs** capture async invocation failures for retry/inspection.
20. EC2 **Auto Scaling Groups** keep instance count within a min/max/desired range using *launch templates* and *scaling policies* (**target tracking, step, scheduled**).
21. ASG *health checks* (EC2 or ELB) trigger replacement of unhealthy instances; *lifecycle hooks* pause instances in Pending/Terminating states for custom actions.
23. **ECS** orchestrates Docker containers as **Tasks** (task definition = image, **CPU/RAM**, roles) run on a Cluster; *EC2 launch type* means you manage/register instances via the ECS Agent, while *Fargate* launch type is fully serverless.
24. ECS integrates with *ALB* for **path-based routing** to containers via dynamic port mapping, and supports **Service Auto Scaling** based on *CloudWatch metrics* (e.g., CPU/memory).
25. **Fargate** removes all EC2 server management for ECS/EKS tasks — you only define per-task CPU/RAM, billed per **vCPU/memory-second** used (no idle server cost).
26. Fargate scales by *increasing task count*, not instance count. Ideal for *spiky/unpredictable workloads* needing least operational overhead.
27. **ALB** operates at *Layer 7*, routing HTTP/HTTPS by *path, host, header, or query string* to different target groups (EC2, ECS, Lambda, or IP targets).
28. ALB supports native *TLS termination* with ACM certificates, WebSocket/HTTP2, and sticky sessions via application-controlled cookies.


### Databases — RDS, DynamoDB, Aurora

29. **RDS Multi-AZ** gives *synchronous* standby failover for HA (not read scaling) within region; **Read Replicas** (up to 15, can *cross-region*) give *asynchronous* *read scaling*.
30. RDS supports **automated backups**, manual snapshots, and **point-in-time restore**; **storage auto scaling** grows volumes automatically as usage nears the threshold.
32. **DynamoDB** is a fully managed *NoSQL* key-value/document store scaling to millions of requests/sec at *single-digit ms latency*; **on-demand** mode *auto-scales*, **provisioned** mode is cheaper for *steady, predictable* traffic.
33. **DAX** adds a microsecond *in-memory cache* in front of DynamoDB; **DynamoDB Streams + Lambda** enable *event-driven* reactions to *table changes*; **Global Tables** give *multi-region active-active* replication.
34. **Aurora** stores *6 copies* of data across *3 AZs*, self-heals, and fails over in under *30 seconds*; **Aurora Global Database** replicates to secondary regions in *<1s*.
35. **Aurora Serverless v2** *scales* database capacity *automatically* for variable/intermittent workloads without managing instances.

### Networking — VPC, CloudFront, API Gateway

36. A **VPC** spans *1 region* across *multiple AZs*; each **subnet** lives in exactly *1 AZ* and is *public/private* based on whether its **route table** has an **IGW** route.
39. **CloudFront** caches content at *edge* locations globally, cutting latency and origin load; **Origin Access Control** (OAC) *restricts S3* origins to CloudFront-only access.
41. **API Gateway** fronts *REST, HTTP, and WebSocket* APIs; **Edge-Optimized** routes through CloudFront, **Regional** serves a single region, **Private** is reachable only within a VPC via an interface endpoint.
42. API Gateway supports throttling/usage plans/API keys, response caching, and Lambda authorizers or Cognito for authentication.

### Messaging & Integration — SQS, SNS

43. **SQS** decouples producers/consumers with *at-least-once delivery* and a default *4-day* (max 14-day) retention;
45. **SNS** *fans out* one published message to many subscribers at once — SQS, Lambda, email, SMS, HTTP/S endpoints — commonly paired with *SQS for durable fan-out* (the SNS+SQS fan-out pattern).
46. SNS *message filtering* (via subscription filter policies) lets each *subscriber* receive only the *subset* of published messages relevant to it.

### Identity & Security — IAM, KMS

47. **IAM** is global (not region-scoped); always prefer *roles* over hardcoded access keys for EC2/Lambda/ECS to call other AWS *services*.
48. IAM **policy evaluation**: an *explicit Deny always wins*; otherwise an Allow must exist at every applicable layer (**SCP**, *resource policy*, identity policy, permissions boundary).
49. **KMS** key types: AWS-owned (free, no visibility), AWS-managed (free, per-service), customer-managed (full control — rotation, key policies, priced); SSE-KMS gives a CloudTrail audit trail that SSE-S3 doesn't.
50. *Envelope encryption*: KMS generates a data key used to encrypt data locally; only the *small* encrypted data key is ever *sent to KMS*, keeping *large-object encryption fast and cheap*.
