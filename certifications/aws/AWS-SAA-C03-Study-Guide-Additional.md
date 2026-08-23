# AWS Certified Solutions Architect – Associate (SAA-C03) Study Guide — Additional Topics

> This is the **additional/less popular** companion guide — services that appear less frequently on the SAA-C03 exam, or that are typically covered by only a handful of questions (often just "match the use case to the service"). Cover the core guide first: [AWS-SAA-C03-Study-Guide-Core.md](AWS-SAA-C03-Study-Guide-Core.md).

---

## Table of Contents

1. [Advanced Identity & Governance Topics](#1-advanced-identity--governance-topics)
   - [IAM Conditions & Permission Boundaries (advanced policy features)](#iam-conditions--permission-boundaries-advanced-policy-features)
   - [Microsoft Active Directory (AD) & AWS Directory Services](#microsoft-active-directory-ad--aws-directory-services)
2. [Security](#2-security)
   - [AWS CloudHSM](#aws-cloudhsm)
   - [AWS Firewall Manager](#aws-firewall-manager)
   - [Amazon Inspector](#amazon-inspector)
   - [AWS Macie](#aws-macie)
3. [Additional Storage Services](#3-additional-storage-services)
   - [Amazon FSx](#amazon-fsx)
   - [AWS Storage Gateway](#aws-storage-gateway)
   - [AWS Transfer Family](#aws-transfer-family)
   - [AWS DataSync](#aws-datasync)
4. [Data & Analytics](#4-data--analytics)
   - [Amazon Athena](#amazon-athena)
   - [Amazon OpenSearch Service](#amazon-opensearch-service)
   - [Amazon EMR (Elastic MapReduce)](#amazon-emr-elastic-mapreduce)
   - [Amazon QuickSight](#amazon-quicksight)
   - [AWS Glue](#aws-glue)
   - [AWS Lake Formation](#aws-lake-formation)
   - [Amazon Managed Service for Apache Flink & Amazon MSK](#amazon-managed-service-for-apache-flink--amazon-msk)
   - [Big Data Ingestion Pipeline (recurring exam pattern)](#big-data-ingestion-pipeline-recurring-exam-pattern)
   - [Amazon DocumentDB](#amazon-documentdb)
   - [Amazon Neptune](#amazon-neptune)
   - [Amazon Keyspaces (for Apache Cassandra)](#amazon-keyspaces-for-apache-cassandra)
   - [Amazon Timestream](#amazon-timestream)
5. [Machine Learning](#5-machine-learning)
6. [Additional Messaging Services](#6-additional-messaging-services)
   - [Amazon MQ](#amazon-mq)
   - [Lambda + SQS/SNS retry mechanics](#lambda--sqssns-retry-mechanics)
   - [Amazon Simple Email Service (SES)](#amazon-simple-email-service-ses)
   - [Amazon Pinpoint](#amazon-pinpoint)
7. [Specialized / Hybrid Services (light exam coverage)](#7-specialized--hybrid-services-light-exam-coverage)

---

## 1. Advanced Identity & Governance Topics

### IAM Conditions & Permission Boundaries (advanced policy features)
- **IAM Conditions**: a `Condition` block scopes when a statement applies — `aws:SourceIp`/`NotIpAddress` (restrict the client IP an API call comes *from*), `aws:RequestedRegion` (restrict which region an API call targets), a resource-tag condition key like `ec2:ResourceTag/Project` combined with `aws:PrincipalTag/Department` (restrict access based on matching tags between the resource and the calling principal), and `aws:MultiFactorAuthPresent` (e.g. `Deny` on `ec2:StopInstances`/`TerminateInstances` when `BoolIfExists: aws:MultiFactorAuthPresent = false` — forces MFA for destructive actions).
- **IAM for S3, resource granularity**: `s3:ListBucket` is a bucket-level permission (`Resource: arn:aws:s3:::test`); `s3:GetObject`/`PutObject`/`DeleteObject` are object-level permissions (`Resource: arn:aws:s3:::test/*`) — a **very common exam gotcha (bucket ARN without `/*` vs with `/*`)**.
- **`aws:PrincipalOrgID`**: usable in any resource-based policy (e.g. an S3 bucket policy) to restrict access to only principals that are members of a specific AWS Organization — blocks access even from a user with otherwise-matching credentials if they're outside the org.
- **IAM Roles vs Resource-Based Policies for cross-account access**: 
  - assuming a role means giving up your original permissions and taking on the role's permissions; 
  - using a resource-based policy (e.g. an S3 bucket policy, supported by S3 buckets, SNS topics, SQS queues, and others) lets the calling principal keep their own permissions *and* gain the resource's granted access — useful when, say, a user in Account A needs to scan a DynamoDB table in Account A and also dump results into an S3 bucket in Account B without switching identity. EventBridge rules follow the same split: invoking a Lambda/SNS/SQS/S3/API Gateway target needs a resource-based policy on the target; 
  - invoking EC2 Auto Scaling/SSM Run Command/an ECS task needs an IAM role instead.
  - **Top 15 popular target services, categorized** (for cross-account access design questions):

    | Service | Resource-based policy? | Notes |
    |---|---|---|
    | S3 | ✅ Yes | Bucket policy — the classic example |
    | SNS | ✅ Yes | Topic policy |
    | SQS | ✅ Yes | Queue policy |
    | Lambda | ✅ Yes | Function policy (`AddPermission`) — how S3/API Gateway/EventBridge are allowed to invoke it |
    | KMS | ✅ Yes | Key policy is *mandatory* on every CMK; the basis for cross-account key sharing |
    | API Gateway | ✅ Yes | Resource policy — restrict by source VPC/VPC endpoint, IP, or account |
    | ECR | ✅ Yes | Repository policy — cross-account image pull |
    | DynamoDB | ⚠️ Yes (added Nov 2023) | Resource-based policies now exist for tables/streams; older material still treats it as IAM-only |
    | CloudWatch Logs | ✅ Yes | Resource policy for cross-account log delivery/subscription filters (plain CloudWatch metrics/alarms have no resource policy) |
    | EC2 | ❌ No | IAM role (instance profile) only |
    | RDS | ❌ No | IAM identity-based policy + DB-native auth + security groups |
    | VPC | ❌ No | No resource-policy concept; controlled via IAM + SGs/NACLs |
    | CloudFront | ❌ No | IAM only; origin access uses OAC, not a resource policy |
    | Route 53 | ❌ No | IAM only |
    | ECS | ❌ No | IAM role (task role/execution role) only |
- **IAM Permission Boundaries**: supported for Users and Roles only (not Groups) — an advanced feature where a managed policy sets the *maximum* permissions an IAM entity can ever have, regardless of what its identity-based policies grant (Permission Boundary ∩ Identity-based Policy = effective permissions; a boundary that doesn't mention a service means no access to it, even with a full-access identity policy). Use cases: let non-admins create/manage IAM users within a bounded scope, or let developers self-assign policies without being able to escalate to admin; useful for restricting one specific user (vs Organizations SCPs, which govern a whole account).
- **IAM Policy Evaluation Logic (full order)**:
  - SCP: Service Control Policies from AWS Organizations
  ```
  REQUEST ARRIVES
    │
    ▼
  [1] Explicit DENY anywhere (identity/resource/SCP/boundary/session policy)?
    ├─ YES ──────────────────────────────► FINAL: DENY
    └─ NO
      │
      ▼
  [2] Account in an Organization with an applicable SCP?
    ├─ NO ───────────────────────────────► (skip to [3])
    └─ YES
      │
      ▼
      Does the SCP allow it?
        ├─ NO  ─────────────────────────► IMPLICIT DENY
        └─ YES ─────────────────────────► continue to [3]
    │
    ▼
  [3] Does the target resource have a resource-based policy?
    ├─ NO ───────────────────────────────► (skip to [4])
    └─ YES
      │
      ▼
      Does it grant an Allow?
        ├─ YES ─────────────────────────► FINAL: ALLOW  (skips [4]-[6])
        └─ NO  ─────────────────────────► continue to [4]
    │
    ▼
  [4] Does the principal have an identity-based policy with an Allow?
    ├─ NO ───────────────────────────────► IMPLICIT DENY
    └─ YES
      │
      ▼
  [5] Does the principal have a Permissions Boundary?
    ├─ NO ───────────────────────────────► (skip to [6])
    └─ YES
      │
      ▼
      Does the boundary allow it?
        ├─ NO  ─────────────────────────► IMPLICIT DENY
        └─ YES ─────────────────────────► continue to [6]
    │
    ▼
  [6] Session principal (role/federated session) with a session policy?
    ├─ NO ───────────────────────────────► FINAL: ALLOW
    └─ YES
      │
      ▼
      Does the session policy allow it?
        ├─ NO  ─────────────────────────► IMPLICIT DENY
        └─ YES ─────────────────────────► FINAL: ALLOW
  ```
  - Summary of eval attributes:
    1. Explicit Deny
    2. Organization SCP
    3. Target's resource-based policies
    4. Principal's IAM policy
    5. IAM Permission Boundaries
    6. Session policy

> Note: **AWS Systems Manager (SSM)**, including Parameter Store, is covered in the core guide's Monitoring, Management & DevOps section.

### Microsoft Active Directory (AD) & AWS Directory Services
- **Active Directory**: found on any Windows Server with AD Domain Services — a database of objects (user accounts, computers, printers, file shares, security groups) enabling centralized security management, account creation, and permission assignment; a **Domain Controller** serves the directory to clients; objects are organized into **trees**, and a group of trees is a **forest**.
- **AWS Managed Microsoft AD**: create and manage your own real Microsoft AD directory inside AWS, manage users locally, supports MFA; can establish a two-way **trust** relationship with an on-prem AD.
- **AD Connector**: a directory gateway (proxy) that redirects authentication requests to an existing on-prem AD — users continue to be managed entirely on-prem; also supports MFA.
  - **Key difference**: both let AWS resources (Managed AD & AD Connector) authenticate against on-prem identities, but AWS Managed Microsoft AD actually stands up a *second, real directory inside AWS* (linked to on-prem via a two-way trust, so users/objects can exist and be managed on either side), whereas AD Connector holds **no directory data in AWS at all** — it's just a redirect layer, so every user must still exist on-prem.
- **Simple AD**: an AD-compatible (not real Microsoft AD) managed directory native to AWS — cannot be joined/trusted with an on-prem AD.

---

## 2. Security

### AWS CloudHSM (Cloud Hardware Security Module)
- CloudHSM means AWS provisions dedicated encryption **hardware** (HSM = Hardware Security Module) and you manage your own encryption keys entirely — AWS never has access. 
- Devices are tamper-resistant, FIPS 140-2 **Level 3** compliant (vs KMS's Level 3 on the underlying HSM but multi-tenant); supports both symmetric and asymmetric encryption plus SSL/TLS and Oracle TDE cryptographic acceleration; accessed via the CloudHSM Client Software over an SSL connection; no free tier. 
  - Redshift natively supports CloudHSM for database encryption/key management; a good option when you specifically need SSE-C-style full key custody.
- **High Availability**: CloudHSM clusters spread HSMs across multiple AZs, all kept in sync — great for availability and durability, but you provision and pay for it yourself (vs KMS's built-in AWS-managed HA).
- **Integration with AWS services**: configure a KMS **Custom Key Store** backed by CloudHSM so services that only know how to talk to KMS (EBS, S3, RDS, ...) transparently use HSM-backed keys, while CloudTrail still logs key-usage events.
- **CloudHSM vs KMS** (exam-relevant deltas):

  | Dimension | KMS | CloudHSM |
  |---|---|---|
  | Tenancy | Multi-tenant | Single-tenant |
  | Master keys | AWS-owned / AWS-managed / customer-managed | Always customer-managed |
  | Region/network scope | Only accessible within the region they were created (barring multi-region keys) | Deployed in a VPC; clusters can be shared across VPCs via peering |
  | Access/auth | IAM | Users/permissions you create and manage yourself inside the HSM |

### AWS Firewall Manager
- **Centrally manages** security rules across *every account in an AWS Organization* via a Security Policy, which is a common rule set covering:
  1. WAF rules (ALB, API Gateway, CloudFront), 
  2. Shield Advanced protections (ALB, CLB, NLB, Elastic IP, CloudFront), 
  3. Security Groups (EC2, ALB, ENI resources in a VPC), 
  4. AWS Network Firewall (VPC level), and 
  5. Route 53 Resolver DNS Firewall. 
- Policies are created at the region level and automatically apply to new resources as they're created — good for compliance across a growing multi-account org.
- **WAF vs Firewall Manager vs Shield**: 
  - define your rules in WAF; for granular protection of one resource, WAF alone is the right call; 
  - use Firewall Manager on top of WAF when you need those rules applied consistently across many accounts, want faster configuration, or want new resources auto-protected; 
  - Shield Advanced layers on dedicated DDoS response-team support and advanced reporting — worth it if you're a frequent DDoS target.
- **DDoS resiliency best practices**: 
  1. Edge Location Mitigation — put CloudFront and/or Global Accelerator in front of the app (absorbs SYN floods/UDP reflection at the edge) and use Route 53 for DNS resolution at the edge (also DDoS-protected). 
  2. Infrastructure Layer Defense — Elastic Load Balancing + an Auto Scaling Group absorb traffic surges/flash crowds. 
  3. Application Layer Defense — WAF filters malicious requests on top of CloudFront/ALB, rate-based WAF rules auto-block bad-actor IPs, managed WAF rule groups block by IP reputation or anonymous proxies, CloudFront blocks by geography, and Shield Advanced auto-deploys WAF rules for Layer 7 mitigation. 
  4. Attack Surface Reduction — hide backend resources (EC2, Lambda) behind CloudFront/API Gateway/ELB, use Security Groups + NACLs to filter by IP at the subnet/ENI level, and protect Elastic IPs with Shield Advanced.

### Amazon Inspector
- **Automated security assessments**, but only for three resource types: 
  1. *EC2 instances*: via the SSM Agent — checks for unintended network reachability and known OS/package vulnerabilities against a CVE database, 
  2. *container images pushed to Amazon ECR*: assessed as they're pushed, and 
  3. *Lambda functions*: identifies vulnerabilities in function code and package dependencies as they're deployed. 
- Continuously (re-)scans only when needed (e.g. a new CVE is published), rather than on a fixed schedule; 
- every finding gets a risk score for prioritization; 
- results integrate with AWS Security Hub and can be sent to EventBridge.

### AWS Macie
- Fully managed data-security/data-privacy service that uses ML and pattern matching to *discover and protect sensitive data* (notably PII — personally identifiable information) stored in *S3 buckets*; 
- analyzes buckets, notifies findings via EventBridge for downstream integration/automation.

---

## 3. Additional Storage Services

### Amazon FSx
- Family of fully managed, 3rd-party high-performance file systems on AWS.
- Exists to lift-and-shift workloads needing a specific file system's protocol/features (SMB, Lustre, ONTAP, ZFS), unlike generic S3/EFS. i.e. Windows apps.
- **FSx for Windows File Server**: managed Windows share (SMB, Windows NTFS), Microsoft AD integration, ACLs, user quotas, supports Microsoft DFS Namespaces (group multiple file systems), can be mounted on Linux EC2 too; SSD (latency-sensitive: DBs, media processing) or HDD (broad workloads: home dirs, CMS) storage; scales to 10s of GB/s and 100s of PB; reachable from on-prem via VPN/Direct Connect; Multi-AZ option; daily backups to S3.
- **FSx for Lustre**: "Lustre" = Linux + cluster — a parallel distributed file system for large-scale/HPC computing (ML, HPC, video processing, financial modeling, EDA); scales to 100s of GB/s, millions of IOPS, sub-ms latency; SSD (low-latency, small/random I/O) or HDD (throughput-intensive, large/sequential I/O); can mount an S3 bucket as a Lustre file system and write compute output back to S3; usable from on-prem via VPN/Direct Connect. Deployment options: **Scratch** (temporary, not replicated — lost if the file server fails, high burst throughput, short-term/cost-optimized processing) vs **Persistent** (long-term, replicated within the same AZ, failed files replaced within minutes, for sensitive/long-term data).
- **FSx for NetApp ONTAP**: managed NetApp ONTAP file system, compatible with NFS/SMB/iSCSI; used to lift-and-shift workloads already running on ONTAP/NAS; works with Linux, Windows, macOS, VMware Cloud on AWS, WorkSpaces, AppStream 2.0, EC2/ECS/EKS; storage auto-shrinks/grows; snapshots, replication, compression, dedup, and instantaneous point-in-time cloning (handy for spinning up test copies).
- **FSx for OpenZFS**: managed OpenZFS file system, compatible with NFS (v3/v4/v4.1/v4.2); used to lift-and-shift workloads already running on ZFS; works with Linux, Windows, macOS, VMware Cloud on AWS, WorkSpaces, AppStream 2.0, EC2/ECS/EKS; storage auto-shrinks/grows; snapshots, replication, compression, dedup, and instantaneous point-in-time cloning; reaches up to 1,000,000 IOPS at <0.5ms latency.
- **When to use which**: 
  - Windows File Server for SMB/Windows-native apps needing AD integration; 
  - Lustre for HPC/ML workloads needing massive throughput and tight S3 integration; 
  - NetApp ONTAP for migrating existing NetApp/NAS workloads or needing multi-protocol (NFS/SMB/iSCSI) access;
  - OpenZFS for migrating existing ZFS workloads or needing the highest IOPS at the lowest latency among the four.
- **Native storage option summary**: Block = EBS, EC2 Instance Store. File = EFS, FSx. Object = S3, S3 Glacier.

### AWS Storage Gateway
- Bridges on-premises environments to AWS storage (since S3 is a proprietary API, not NFS-compatible, on its own)
- deployed as a VM (VMware/Hyper-V/KVM) on-prem, encrypts data in transit over the internet or Direct Connect. 
- Use cases: disaster recovery, backup & restore, tiered storage, low-latency on-prem cache of cloud data.
- **S3 File Gateway**: exposes S3 buckets over NFS/SMB, caches most-recently-used data locally, supports S3 Standard/Standard-IA/One Zone-IA/Intelligent-Tiering directly (transition to Glacier via a lifecycle policy since Glacier/Deep Archive aren't directly supported), per-gateway IAM role for bucket access, SMB integrates with Active Directory for auth.
- **Volume Gateway**: block storage over Internet Small Computer Systems Interface (iSCSI). Final artifacts are EBS snapshots (which can restore on-prem volumes) and they go thru S3. 
  - **Cached volumes**: entire dataset in S3, only recently used data cached locally (low latency for hot data). 
  - **Stored volumes**: entire dataset kept on-prem, scheduled/async backups to S3 as EBS snapshots.
- **Tape Gateway**: Virtual Tape Library (VTL) backed by S3 and Glacier for companies with existing physical-tape backup processes/software — same workflow, iSCSI interface, "eject" a tape to archive it into S3/Glacier. Usually, final artifacts are in Glacier (going through S3).
- Storage gateways provides hosting options. ***VMWare ESXi, Microsoft Hyper-V, Linux KVMs*** are options that users can host on-premise. Users can also choose EC2, which is on the cloud.

### AWS Transfer Family
- Fully managed **FTP/FTPS/SFTP endpoints** for file transfer into and out of **S3 or EFS**. 
- AWS Transfer for FTP (VPC-only), FTPS, and SFTP; 
- managed, scalable, highly available (Multi-AZ); 
- billed per provisioned endpoint-hour + data transferred; 
- can front the endpoints with Route 53; 
- stores/manages user credentials itself or integrates with Microsoft AD, LDAP, Okta, Cognito, or a custom identity provider, then uses an IAM role to reach S3/EFS. 
- Use cases: sharing files, public datasets, CRM/ERP integrations needing legacy file-transfer protocols.



---

## 4. Data & Analytics

### Amazon Athena
- Serverless query service to analyze data directly in S3 using standard SQL (built on Presto) — no infrastructure to provision. Supports CSV, JSON, ORC, Avro, Parquet. Pricing: $5.00 per TB of data scanned. Commonly paired with QuickSight for reporting/dashboards. Also used to query VPC Flow Logs, ELB logs, and CloudTrail trails. Exam trigger: "analyze data in S3 with serverless SQL" → Athena.
- **Performance/cost tips**: use **columnar formats** (Parquet or ORC, converted via Glue) to scan less data; **compress** data (bzip2, gzip, lz4, snappy, zlip, zstd) for smaller scans; **partition** S3 datasets by virtual columns in the key path (e.g. `s3://bucket/table/year=1991/month=1/day=1/`) so queries skip irrelevant prefixes; use **larger files** (>128MB) to cut per-file overhead.
- **Federated Query**: run SQL across relational, non-relational, object, and custom/on-prem data sources (ElastiCache, DocumentDB, DynamoDB, RDS, Aurora, SQL Server, MySQL, HBase-on-EMR) via Lambda-based Data Source Connectors, storing results back in S3 — lets Athena act as a single SQL layer over heterogeneous sources.

### Amazon OpenSearch Service
- Successor to Amazon ElasticSearch. DynamoDB only supports lookups by primary key or index; OpenSearch lets you search **any field**, including partial matches — commonly used as a search complement layered in front of another database. Two modes: managed cluster or serverless. No native SQL (available via a plugin). Ingests from Kinesis Data Firehose, AWS IoT, and CloudWatch Logs; secured via Cognito & IAM, KMS encryption, TLS; ships with OpenSearch Dashboards for visualization.
- **Patterns**: DynamoDB Table → DynamoDB Stream → Lambda → OpenSearch (app queries DynamoDB directly for retrieval, OpenSearch for search). CloudWatch Logs → Subscription Filter → Lambda (real-time) or → Kinesis Data Firehose (near-real-time) → OpenSearch. Kinesis Data Streams → Lambda (real-time) or → Kinesis Data Firehose, optionally with a Lambda transform (near-real-time) → OpenSearch.

### Amazon EMR (Elastic MapReduce)
- Creates managed **Hadoop clusters** (big data) spanning up to hundreds of EC2 instances to analyze/process vast datasets; bundles Apache Spark, HBase, Presto, Flink, etc.; EMR handles all provisioning/configuration, supports auto-scaling and Spot Instances. Use cases: data processing, machine learning, web indexing, big data.
- **Node types**: Master Node (manages/coordinates the cluster, monitors health — long-running), Core Node (runs tasks and stores data — long-running), Task Node (optional, runs tasks only, typically Spot since it holds no data). **Purchasing options**: On-Demand (reliable, won't be terminated), Reserved (min 1 year, cost savings, EMR uses automatically if available), Spot (cheapest, can be terminated, least reliable). Clusters can be long-running or transient (temporary, torn down after the job).

### Amazon QuickSight
- Serverless, ML-powered BI service for interactive dashboards — fast, auto-scalable, embeddable, per-session pricing. Use cases: business analytics, visualizations, ad-hoc analysis, business insights. Integrates with RDS, Aurora, Athena, Redshift, S3, OpenSearch, Timestream, SaaS sources (Salesforce, Jira), on-prem JDBC databases (e.g. Teradata), and file imports (XLSX, CSV, JSON, TSV, ELF/CLF log formats). Imported data is held in-memory via the **SPICE** engine for fast repeated queries. Enterprise edition adds **Column-Level Security (CLS)**.
- **Users, Groups, Dashboards**: Users (all editions) and Groups (Enterprise) exist only within QuickSight, not IAM. A **dashboard** is a read-only, shareable snapshot of an analysis that preserves its filtering/parameters/controls/sort configuration; a dashboard must be published before it can be shared; anyone who can see a dashboard can also see its underlying data.

### AWS Glue
- Serverless, managed **ETL (Extract, Transform, Load)** service to prepare/transform data for analytics — e.g. extract from S3 + RDS, transform, load into a Redshift warehouse. A common pattern: an S3 PUT triggers a Lambda (or EventBridge) which fires a Glue ETL job to convert an input CSV into Parquet in an output bucket, ready for Athena to query cheaply.
- **Glue Data Catalog**: a catalog of dataset metadata (databases/tables), populated by **Glue Crawlers** scanning S3, RDS, DynamoDB, or JDBC sources; the catalog is used for data discovery by Athena, Redshift Spectrum, and EMR, and read/written by Glue Jobs.
- **Other Glue features**: Job Bookmarks (prevent re-processing already-seen data), Glue DataBrew (clean/normalize data via pre-built, no-code transformations), Glue Studio (GUI for building/running/monitoring ETL jobs), Glue Streaming ETL (built on Apache Spark Structured Streaming, compatible with Kinesis Data Streams, Kafka, and MSK).

### AWS Lake Formation
- Fully managed service to stand up a **data lake** (S3-backed central store for analytics) in days — automates the complex manual steps of collecting, cleansing (including ML-based de-duplication), moving, and cataloging data from structured and unstructured sources; built on top of Glue. Out-of-the-box source blueprints for S3, RDS, and relational/NoSQL databases. 
- Provides **fine-grained access control** (row- and column-level) centrally, then feeds tools like Athena, Redshift, EMR, and Apache Spark. (*!!Popular exam question!!*)

### Amazon Managed Service for Apache Flink & Amazon MSK
- **Amazon MSK (Managed Streaming for Apache Kafka)**: an alternative to Kinesis — fully managed Kafka, creates/manages both broker and Zookeeper nodes, deployed in your VPC across up to 3 AZs for HA, auto-recovers from common Kafka failures, data stored on EBS volumes for as long as you want. **MSK Serverless** removes capacity management entirely (auto-provisions/scales compute & storage). Kafka model: producers write to a **topic** on a **broker**, which replicates across brokers; consumers poll from the topic.
  - **Kinesis Data Streams vs MSK**: Kinesis — 1MB message size limit, streams organized into shards (splittable/mergeable), TLS in-flight + KMS at-rest encryption. MSK — 1MB default message size (configurable higher, e.g. 10MB), topics organized into partitions (can only be added to, not shrunk), PLAINTEXT or TLS in-flight + KMS at-rest encryption. MSK consumers include Managed Service for Apache Flink, Glue Streaming ETL, Lambda, and apps on EC2/ECS/EKS.
- **Amazon Managed Service for Apache Flink** (formerly Kinesis Data Analytics for Apache Flink): runs any Apache Flink (Java/Scala/SQL stream-processing framework) application on a managed cluster — provisioned compute, parallel computation, automatic scaling, application backups via checkpoints/snapshots. Reads from Kinesis Data Streams or Amazon MSK — **not** from Kinesis Data Firehose.
  - Apache Flink: a framework for stateful processing of unbounded (streaming) and bounded (batch) data, supporting event-time processing, exactly-once state consistency, and windowed aggregations at low latency.


### Big Data Ingestion Pipeline (recurring exam pattern)
- A fully serverless real-time ingestion pipeline: IoT devices → **IoT Core** → **Kinesis Data Streams** (real-time collection) → **Kinesis Data Firehose** (near-real-time delivery, ~every 1 minute, optionally invoking a **Lambda** transform) → an **Ingestion S3 bucket**. From there, an S3 event can notify **SQS** (optionally, instead of triggering Lambda directly), which a **Lambda** consumes, triggering **Athena** to query/transform the data with SQL and write results to a **Reporting S3 bucket** — which **QuickSight** and/or **Redshift Serverless** then read for dashboards and warehousing.

> Note: **AWS DMS (Database Migration Service)** is covered in the core guide's Disaster Recovery Strategies & Migrations section.

### Amazon DocumentDB
- The **MongoDB-compatible** counterpart to Aurora (Aurora mirrors PostgreSQL/MySQL, DocumentDB mirrors MongoDB — a NoSQL database for storing, querying, and indexing JSON data). Same deployment concepts as Aurora: fully managed, highly available across 3 AZs, storage auto-scales in 10GB increments, and auto-scales to workloads of millions of requests/second.

### Amazon Neptune
- Fully managed **graph database** — optimized for datasets with complex many-to-many relationships (e.g. a social network: users have friends, posts have comments, comments get likes, users share/like posts). Highly available across 3 AZs with up to 15 read replicas; stores up to billions of relations and queries the graph with millisecond latency. 
- Use cases: knowledge graphs (e.g. Wikipedia), fraud detection, recommendation engines, social networking.
- **Neptune Streams**: a real-time, strictly ordered, no-duplicates sequence of every change to the graph, changes available immediately after write, exposed via an HTTP REST API — used to trigger notifications on changes, keep another data store (S3, OpenSearch, ElastiCache) in sync, or replicate across regions.

### Amazon Keyspaces (for Apache Cassandra)
- Managed, *serverless*, highly available database service compatible with **Apache Cassandra** (an open-source NoSQL distributed database), queried with the Cassandra Query Language (CQL). Auto-scales tables up/down with traffic; tables replicated 3x across multiple AZs; single-digit millisecond latency at any scale, thousands of requests/second. Capacity: on-demand or provisioned with auto-scaling. Encryption, backups, and point-in-time recovery up to 35 days. 
- Use cases: IoT device info, time-series data.

### Amazon Timestream
- Fully managed, serverless **time series database** — auto-scales capacity up/down, stores/analyzes trillions of events/day, claimed 1000x faster and 1/10th the cost of relational databases for this workload. Scheduled queries, multi-measure records, SQL compatibility. 
- **Data storage tiering**: recent data kept in memory, historical data moved to cost-optimized storage. 
- Built-in time-series analytics functions to spot patterns in near real-time. Encrypted in transit and at rest. 
- Use cases: IoT apps, operational applications, real-time analytics — commonly fed by Kinesis Data Streams/Firehose, MSK, or IoT Core, and queried from QuickSight, SageMaker, Grafana, or any JDBC connection.

---

## 5. Machine Learning

- Most AWS ML services are pre-trained/managed — no need to build, train, or deploy your own models for the common cases below; exam questions on this domain are mostly "match the use case to the service."
- **Amazon Rekognition**: finds objects, people, text, and scenes in images/video using ML; facial analysis (gender, age range, emotions) and facial search (verification, celebrity recognition, "familiar faces" database), object/scene labeling, pathing (e.g. sports analysis). **Content Moderation**: flags inappropriate/unwanted/offensive content against a configurable minimum confidence threshold, with optional human review routed to **Amazon Augmented AI (A2I)** — used in social media, broadcast, advertising, e-commerce to build safer experiences and help meet content regulations.
- **Amazon Transcribe**: automatic speech recognition (ASR) deep-learning model converting speech to text; can auto-redact PII and auto-detect the spoken language for multilingual audio. Use cases: transcribing customer service calls, closed captioning/subtitling, generating searchable metadata for media archives.
- **Amazon Polly**: text-to-speech via deep learning. **Lexicons** customize pronunciation of specific words/acronyms (e.g. "AWS" → "Amazon Web Services"), applied via the `SynthesizeSpeech` API. **SSML (Speech Synthesis Markup Language)** marks up text for finer control — emphasis, phonetic pronunciation, breathing/whispering sounds, the Newscaster speaking style.
- **Amazon Translate**: natural, accurate language translation for localizing websites/apps for international users and translating large text volumes efficiently.
- **Amazon Lex**: the same ASR + Natural Language Understanding technology that powers Alexa — recognizes intent from spoken/typed text to build chatbots and call-center bots. **Amazon Connect**: cloud-based virtual contact center — receive calls, build contact flows, integrate with CRMs or other AWS services, no upfront cost and ~80% cheaper than traditional contact center solutions. Typical flow: caller → Connect → streams audio to Lex (recognizes intent) → invokes Lambda → updates a CRM.
- **Amazon Comprehend**: fully managed, serverless **NLP** — detects language, extracts key phrases/entities (places, people, brands, events), sentiment analysis, tokenization/parts-of-speech, and auto-organizes a text collection by topic. Use cases: mining customer email interactions for what drives positive/negative sentiment, auto-grouping articles by topic. **Amazon Comprehend Medical** applies the same NLP to unstructured clinical text (physician notes, discharge summaries, test/case results) and specifically detects Protected Health Information (PHI) via `DetectPHI`; documents typically come from S3, Kinesis Data Firehose (real-time), or Transcribe (audio → text first).
- **Amazon SageMaker AI**: fully managed service for developers/data scientists to build, train, tune, and deploy their own ML models end-to-end (label data → build model → train & tune → apply the model to new data for predictions) — for custom ML use cases that don't fit one of the specialized services above; normally these steps require significant undifferentiated heavy lifting (server provisioning etc.) that SageMaker manages for you.
- **Amazon Kendra**: fully managed, ML-powered **document search** service — natural-language querying (not just keyword search) across S3, RDS, Google Drive, MS SharePoint/OneDrive, Salesforce, ServiceNow, and 3rd-party/custom connectors; learns from user interactions/feedback to promote preferred results (incremental learning), and search relevance can be manually fine-tuned (importance, freshness, custom fields).
- **Amazon Personalize**: fully managed ML service for real-time personalized recommendations (product recommendations/re-ranking, customized direct marketing) — same technology Amazon.com uses internally; ingests historical data from S3 and real-time events via the Personalize API, serves a customized personalization API to websites/apps/SMS/email; implementable in days without building/training/deploying your own models.
- **Amazon Textract**: extracts text, handwriting, and structured data (forms and tables) from any scanned document (PDFs, images) via AI/ML. Use cases: financial services (invoices, financial reports), healthcare (medical records, insurance claims), public sector (tax forms, ID documents, passports).
- **Quick-match cheat sheet**: 
  - face detection/labeling/celebrity recognition → Rekognition. 
  - Audio → text (subtitles) → Transcribe. 
  - Text → audio → Polly. 
  - Translation → Translate. 
  - Chatbots → Lex. 
  - Cloud contact center → Connect. 
  - NLP/sentiment/entities → Comprehend. 
  - Custom ML model, full control → SageMaker. 
  - ML-powered document/enterprise search → Kendra. 
  - Real-time recommendations → Personalize. 
  - Extract text/forms/tables from scanned docs → Textract.

---

## 6. Additional Messaging Services

### Amazon MQ
- SQS/SNS are AWS-proprietary protocols; traditional on-prem apps often use open protocols (MQTT, AMQP, STOMP, OpenWire, WSS). Rather than re-engineer such an app to use SQS/SNS during a migration, **Amazon MQ** is a managed message broker for **RabbitMQ** and **ActiveMQ** 
  -it has both queue (~SQS) and topic (~SNS) features in one service, but doesn't scale as elastically as SQS/SNS since it runs on provisioned broker instances/servers. 
- Supports Multi-AZ with active/standby failover (shared EFS storage behind the brokers in multi AZ for queue failover).

### Lambda + SQS/SNS retry mechanics
- **SQS (standard) → Lambda**: Lambda polls the queue and tries the function; on failure it retries, and after the queue's max-receive threshold is hit the message routes to a **DLQ** attached to the *source queue*.
- **SQS FIFO → Lambda**: same polling model, but retries **block** the group (a failed message halts processing of that Message Group ID until it succeeds or is removed) to preserve ordering — a DLQ on the source queue still catches messages that exhaust retries.
- **SNS → Lambda**: SNS invokes Lambda **asynchronously**; on failure Lambda's own async-invocation retry policy kicks in, and after retries are exhausted the event routes to a DLQ configured **on the Lambda function** (not the SNS topic).
- **Fan-out delivery to multiple SQS queues** without SNS: an SDK can `PUT` the same item into several queues directly (Option 1, simple but the producer must know every queue and calls scale linearly), or `PUT` once into an SNS topic that fans out via subscriptions (Option 2 — the standard Fan-Out pattern, producer stays decoupled from the number/identity of consumers).

### Amazon Simple Email Service (SES)
- Fully managed service to send/receive email securely, globally, at scale — supports inbound and outbound email, a reputation dashboard, performance insights, anti-spam feedback, and delivery/bounce/open statistics. Supports DKIM and SPF for deliverability/anti-spoofing. Flexible IP deployment (shared, dedicated, or customer-owned IPs). Send via the Console, API, or SMTP. Use cases: transactional, marketing, and bulk email.

### Amazon Pinpoint
- Scalable, **2-way** (outbound and inbound) **marketing communications** service — email, SMS, push, voice, and in-app messaging, with reply support, scaling to billions of messages/day. 
  - vs SNS/SES (where you manage each message's audience, content, and delivery schedule yourself)
  - Pinpoint adds message templates, delivery schedules, and highly targeted audience segments — i.e. full campaign management. Streams delivery events (e.g. `TEXT_SUCCESS`, `TEXT_DELIVERED`) to SNS, Kinesis Data Firehose, or CloudWatch Logs. 
  - Use case: running marketing/bulk/transactional SMS campaigns.

---

## 7. Specialized / Hybrid Services (light exam coverage)

- **AWS Outposts**: AWS-managed *physical server racks* installed in your *own data center*, extending the same AWS infrastructure/services/APIs/tools on-premises as in the cloud — for low-latency access to on-prem systems, local data processing, data-residency requirements, and easier eventual migration to the cloud; you're responsible for the rack's physical security.
  - Have access to EC2, EBS, S3, EKS, ECS, RDS, EMR, etc.
- **AWS Batch**: fully managed **batch** processing (jobs with a start and an end, not continuous) at any scale — dynamically provisions the right amount of EC2/Spot compute, jobs are packaged as Docker images and run on ECS/EKS/Fargate; vs Lambda — Lambda has a time limit, limited runtimes, and limited temp disk (serverless); Batch has no time limit, supports any Docker-packaged runtime, and relies on EBS/instance store for disk (backed by EC2, can be AWS-managed).
- **Amazon AppFlow**: fully managed integration service to securely transfer data between SaaS applications (Salesforce, SAP, Zendesk, Slack, ServiceNow, ...) and AWS (S3, Redshift) or other destinations (Snowflake, Salesforce) — on a schedule, on events, or on demand; supports data transformation (filtering, validation); encrypted over the public internet or privately via AWS PrivateLink.
- **AWS Amplify**: a toolset (frontend libraries + CLI + Console) to develop and deploy scalable full-stack web/mobile apps quickly — auth, storage, REST/GraphQL APIs, CI/CD, pub/sub, analytics, and AI/ML predictions on the backend (built on Cognito, S3, API Gateway, AppSync, Lambda, DynamoDB, SageMaker); connects to GitHub/CodeCommit/Bitbucket/GitLab or direct upload; hosted/deployed via Amplify Console + CloudFront.
- **Instance Scheduler on AWS**: a CloudFormation-deployed solution (not a managed service) that automatically starts/stops EC2, ASG, and RDS resources on a schedule (e.g. stop non-prod instances outside business hours) to cut costs by up to 70%; schedules live in a DynamoDB table; uses resource tags + Lambda to act; supports cross-account and cross-region resources.
- **High Performance Computing (HPC)**: the cloud lets you spin up large numbers of resources instantly, scale to speed up results, and pay only for what's used — for genomics, computational chemistry, financial risk modeling, weather prediction, ML/deep learning, and autonomous driving. Supporting building blocks: **Enhanced Networking** (SR-IOV) via the Elastic Network Adapter (ENA, up to 100 Gbps) or the legacy Intel 82599 VF (up to 10 Gbps) for higher bandwidth/PPS/lower latency; **Elastic Fabric Adapter (EFA)** — an improved ENA for HPC, Linux-only, built for tightly coupled inter-node communication via the Message Passing Interface (MPI) standard, bypassing the OS kernel for low-latency reliable transport; Cluster Placement Groups for low-latency 10Gbps+ networking; storage via EBS io2 Block Express (up to 256,000 IOPS), Instance Store (millions of IOPS), or FSx for Lustre (HPC-optimized distributed file system backed by S3); **AWS Batch** and **AWS ParallelCluster** (open-source, text-file-configured HPC cluster management, automates VPC/subnet/cluster/instance-type provisioning, can enable EFA) for automation/orchestration.
