# AWS Certified Solutions Architect – Associate (SAA-C03) Study Guide — Core Topics

> Focused on the services that show up most frequently on the exam and the use cases they're tested on. Organized roughly by exam domain weighting: Design Resilient Architectures, Design High-Performing Architectures, Design Secure Applications, Design Cost-Optimized Architectures.
>
> This is the **core** guide — the services most heavily tested on SAA-C03. For lower-frequency/niche services (advanced IAM features, additional storage/analytics/ML services, specialized hybrid services), see [AWS-SAA-C03-Study-Guide-Additional.md](AWS-SAA-C03-Study-Guide-Additional.md).

---

## Table of Contents

1. [Storage](#1-storage)
   - [S3 (Simple Storage Service) - #1 pop](#s3-simple-storage-service)
   - [Amazon FSx - #16 pop](#amazon-fsx)
   - [EBS (Elastic Block Store) - #18 pop](#ebs-elastic-block-store)
   - [EFS (Elastic File System) - #19 pop](#efs-elastic-file-system)
   - [Snow Family](#snow-family)
   - [AWS Storage Gateway](#aws-storage-gateway)
   - [AWS DataSync](#aws-datasync)
2. [Compute](#2-compute)
   - [EC2 (Elastic Compute Cloud) - #2 pop](#ec2-elastic-compute-cloud)
   - [Scalability & High Availability (concepts)](#scalability--high-availability-concepts)
   - [Auto Scaling Groups (ASG) - #4 pop + Elastic Load Balancing (ELB) - #14 pop](#auto-scaling-groups-asg--elastic-load-balancing-elb)
   - [Lambda (Serverless Compute) - #3 pop](#lambda-serverless-compute)
   - [Docker fundamentals](#docker-fundamentals)
   - [ECS (Elastic Container Service) - #13 pop](#ecs-elastic-container-service)
   - [Fargate - #17 pop](#fargate)
   - [EKS (Elastic Kubernetes Service)](#eks-elastic-kubernetes-service)
   - [Elastic Beanstalk](#elastic-beanstalk)
3. [Databases](#3-databases)
   - [RDS (Relational Database Service) - #5 pop](#rds-relational-database-service)
   - [Aurora - #10 pop](#aurora)
   - [ElastiCache](#elasticache)
   - [DynamoDB - #9 pop](#dynamodb)
   - [Big Data Concepts (Primer)](#big-data-concepts-primer)
   - [Amazon Athena - #22 pop](#amazon-athena)
   - [Redshift](#redshift)
   - [Choosing the Right Database (decision framework)](#choosing-the-right-database-decision-framework)
4. [Networking & Content Delivery](#4-networking--content-delivery)
   - [Route 53 - #24 pop](#route-53)
   - [VPC (Virtual Private Cloud) - #6 pop](#vpc-virtual-private-cloud)
   - [CloudFront - #7 pop](#cloudfront)
   - [AWS Global Accelerator](#aws-global-accelerator)
   - [API Gateway - #15 pop](#api-gateway)
5. [Application Integration & Messaging](#5-application-integration--messaging)
   - [Application communication patterns](#application-communication-patterns)
   - [SQS (Simple Queue Service) - #8 pop](#sqs-simple-queue-service)
   - [SNS (Simple Notification Service) - #20 pop](#sns-simple-notification-service)
   - [Amazon Kinesis Data Streams](#amazon-kinesis-data-streams)
   - [Amazon Data Firehose (formerly Kinesis Data Firehose)](#amazon-data-firehose-formerly-kinesis-data-firehose)
   - [Amazon EventBridge (formerly CloudWatch Events) - #21 popular](#amazon-eventbridge-formerly-cloudwatch-events)
   - [Step Functions](#step-functions)
6. [Identity, Access & Governance](#6-identity-access--governance)
   - [IAM (Identity and Access Management) - #11 pop](#iam-identity-and-access-management)
   - [AWS Organizations & Control Tower](#aws-organizations--control-tower)
   - [AWS IAM Identity Center (successor to AWS Single Sign-On)](#aws-iam-identity-center-successor-to-aws-single-sign-on)
   - [Amazon Cognito](#amazon-cognito)
7. [Security](#7-security)
   - [Why Encryption? (the three flavors, seen throughout AWS)](#why-encryption-the-three-flavors-seen-throughout-aws)
   - [AWS KMS (Key Management Service) - #12 pop](#aws-kms-key-management-service)
   - [AWS Secrets Manager (as a secrets-rotation service)](#aws-secrets-manager-as-a-secrets-rotation-service)
   - [AWS Certificate Manager (ACM)](#aws-certificate-manager-acm)
   - [AWS WAF (Web Application Firewall) - #25 pop](#aws-waf-web-application-firewall)
   - [AWS Shield](#aws-shield)
   - [Amazon GuardDuty](#amazon-guardduty)
8. [Monitoring, Management & DevOps](#8-monitoring-management--devops)
   - [CloudWatch - #23 pop](#cloudwatch)
   - [AWS CloudTrail](#aws-cloudtrail)
   - [AWS Config](#aws-config)
   - [CloudFormation](#cloudformation)
   - [AWS Systems Manager (SSM)](#aws-systems-manager-ssm)
   - [AWS Backup](#aws-backup)
9. [Solutions Architecture Patterns (recurring exam scenarios)](#9-solutions-architecture-patterns-recurring-exam-scenarios)
   - [Serverless Architecture Patterns (recurring exam scenarios)](#serverless-architecture-patterns-recurring-exam-scenarios)
10. [Cost Optimization Concepts](#10-cost-optimization-concepts)
11. [AWS Well-Architected Framework (conceptual, tested throughout)](#11-aws-well-architected-framework-conceptual-tested-throughout)
    - [Trusted Advisor](#trusted-advisor)

---

## 1. Storage

### S3 (Simple Storage Service)
**[#1 pop]**

Exam tests heavily: storage class selection based on access pattern + cost, lifecycle transitions, encryption choice, securing buckets.

#### S3 Fundamentals
- Object storage, advertised as infinitely scaling, 99.999999999% (11 nines) durability across multiple AZs for all storage classes — durability is about not losing objects; **availability** measures how readily the service responds and varies by class (S3 Standard = 99.99%, ≈53 min/year downtime).
- Strong consistency - read-after-write-consistent.
- **Buckets**: created at the region level but namespaced globally — bucket names must be globally unique across all accounts/regions, lowercase, no underscores, must start with a lowercase letter/number, must not start with `xn--` or end with `-s3alias`. **Objects** are identified by a **key** = the full path (`prefix` + object name) — S3 has no real concept of "directories," just keys containing `/`. Object value max size 5TB; **multipart upload required above 5GB** (recommended above 100MB); objects can carry system/user metadata, up to 10 tags, and a version ID if versioning is enabled.
- **Static website hosting**: S3 can serve a bucket as a website at `http://bucket-name.s3-website-region.amazonaws.com`; a 403 Forbidden means the bucket policy doesn't allow public reads.
- **Common use cases**: backup & restore, disaster recovery, archiving (with lifecycle rules to Glacier), static website hosting, data lakes for big data/analytics, application/media hosting (images, video), software delivery, and hybrid cloud storage via Storage Gateway.

#### S3 Versioning & Replication
- **Versioning**: bucket-level; same-key overwrites create version 1, 2, 3…; objects that existed before versioning was enabled show version "null"; protects against accidental deletes/overwrites (delete just adds a delete marker) and enables easy rollback; suspending versioning does not delete prior versions.
- **Replication (CRR & SRR)**: 
  - ***Versioning*** must be enabled for replication.
  - Cross-Region Replication (CRR) and Same-Region Replication (SRR) both require versioning enabled on source and destination; buckets can be cross-account; copying is asynchronous, needs an IAM role with S3 permissions. 
    - CRR use cases: compliance, lower-latency access, cross-account replication. 
    - SRR use cases: log aggregation, live replication between prod and test accounts. 
  - Only **new** objects replicate after enabling — use **S3 Batch Replication** for existing/failed objects. 
  - Delete markers can optionally replicate; deletes with a specific version ID never replicate (prevents malicious deletes). 
  - **No chaining**: bucket1→bucket2→bucket3 does not propagate bucket1's objects to bucket3.
- **MFA Delete**: requires versioning enabled and only the bucket owner (root account) can enable/disable it; required to permanently delete an object version or suspend versioning; not required to enable versioning or list deleted versions.
- **Glacier Vault Lock**: WORM (Write Once Read Many) models for compliance/data retention. Vault Lock policies, once locked, can never be changed or deleted. 
- **S3 Object Lock**: Object Lock (needs versioning) supports:
  - **Compliance mode** (no one, including root, can overwrite/delete or loosen retention) and 
  - **Governance mode** (most users blocked, specific users can still override), 
  - a configurable **Retention Period** (extendable) and 
  - independent **Legal Hold** (indefinite protection, freely toggled via `s3:PutObjectLegalHold`).
  - To lock existing objects, use S3 Batch Ops - `PutObjectRetention`.

#### S3 Storage Classes & Lifecycle
- Storage classes are applicable to each S3 objects.
- **Storage Classes** — durability is 99.999999999% (11 nines) for all classes; differences are availability, AZ spread, retrieval time/cost, and minimum storage commitments:

| Storage Class | Availability | AZs | Retrieval Time | Min Storage Duration | Other Min/ Fees |
|---|---|---|---|---|---|
| **Standard** | 99.99% | ≥3 | Milliseconds | None | None |
| **Standard-IA** (Infrequent Access) | 99.9% | ≥3 | Milliseconds | 30 days | Min 128KB billable size, per-GB retrieval fee |
| **One Zone-IA** | 99.5% | 1 | Milliseconds | 30 days | Min 128KB billable size, per-GB retrieval fee; data lost if the AZ is destroyed |
| **Glacier Instant Retrieval** | 99.9% | ≥3 | Milliseconds | 90 days | Per-GB retrieval fee |
| **Glacier Flexible Retrieval** (formerly "Glacier") | 99.99% | ≥3 | Expedited 1–5 min, Standard 3–5h, Bulk 5–12h (free) | 90 days | Per-GB retrieval fee (except Bulk) |
| **Glacier Deep Archive** | 99.99% | ≥3 | Standard 12h, Bulk 48h | 180 days | Cheapest storage class |
| **S3 Express One Zone** | 99.95% | 1 | Single-digit ms | None | Directory bucket; up to 10x faster/50% cheaper than Standard for high-throughput workloads |
| **Intelligent-Tiering** | 99.9% | ≥3 | Milliseconds (Frequent/Infrequent/Instant tiers) | None | Small monthly monitoring/auto-tiering fee, no retrieval charges |

| Storage Class | Use Case |
|---|---|
| **Standard** | Frequently accessed data — big data, mobile/gaming apps, content distribution |
| **Standard-IA** (Infrequent Access) | DR & backups |
| **One Zone-IA** | Secondary backup copies or easily recreatable data |
| **Glacier Instant Retrieval** | Archive data accessed ~once/quarter |
| **Glacier Flexible Retrieval** (formerly "Glacier") | Archives where retrieval isn't urgent |
| **Glacier Deep Archive** | Long-term retention/compliance archives |
| **S3 Express One Zone** | AI/ML training, financial modeling, HPC — best paired with co-located compute and SageMaker/Athena/EMR/Glue |
| **Intelligent-Tiering** | Unknown/changing access patterns — auto-moves objects between Frequent/Infrequent(30d)/Archive Instant(90d)/Archive(90d+, optional)/Deep Archive(180d+, optional) tiers |

- **Moving between classes & Lifecycle Rules**: manual or automated via Lifecycle configuration (scoped to a prefix and/or object tags). 
  - **Transition actions** move objects to a cheaper class after N days (e.g. Standard → Standard-IA at 60 days → Glacier at 6 months). 
  - **Expiration actions** delete objects after N days — access logs after 365 days, old versions once versioning is enabled, or incomplete multipart uploads. 
  - **S3 Analytics – Storage Class Analysis** recommends Standard↔Standard-IA transitions (not One Zone-IA or Glacier), report updates daily, 24–48h to see data. 

#### S3 Security & Access Control
- **Security** for S3:
  - 3 ways to control:
    1. *IAM policies*
    2. *Bucket policies*: JSON with Resource/Effect/Action/Principal, allow cross-account/public access
    3. *Object/Bucket ACLs*: finer-grained, legacy, can be disabled 
  - Example: (An IAM principal can access an object if the IAM permissions ***OR*** the resource policy allow it) ***AND*** there's no explicit Deny. 
  - **Block Public Access** settings (four toggles) exist to prevent accidental data leaks and can be set account-wide.
  - Can create bucket policy using Amazon Policy Generator tool.
- **CORS (!!popular in exam!!)**: a cross-origin request from a browser against an S3 bucket needs the bucket's CORS configuration to return the right `Access-Control-Allow-Origin`/`-Methods` headers, or the browser blocks it
  - common exam scenario is a static site in one bucket calling assets in another.
- **S3 Access Logs**: logs every request (any account, authorized or denied) to a *separate* logging bucket in the **same region**
  - never point the logging bucket at itself (creates an infinite logging loop that grows the bucket exponentially).
- **Pre-Signed URLs**: 
  - the holder inherits the permissions (GET/PUT) of whoever generated the URL
  - generated via: 
    1. Console: 1 min–12h expiry, 
    2. CLI: `--expires-in` seconds, default 3600, max 604800 ≈168h, or 
    3. SDK 
  - use cases: letting only logged-in users *download premium content*, *dynamically* generated *download links*, *temporary upload* access to a precise key.
- **S3 Access Points**: named endpoints (each with its own DNS name and access-point policy) simplifying security management for large/shared buckets — e.g. a Finance access point granting R/W to `/finance/*`, a Sales access point to `/sales/*`, an Analytics access point read-only on the whole bucket, all layered under one simple bucket policy. A **VPC Origin** access point restricts access to only within a specific VPC (requires a Gateway/Interface VPC Endpoint whose policy also allows the target bucket/access point).

#### S3 Encryption
- **S3 Encryption**: 
  - Types:
      1. **SSE-S3**: AWS-owned/managed keys, AES-256. Enabled by default for all new buckets/objects, header `x-amz-server-side-encryption: AES256`; 
      2. **SSE-KMS**: KMS-managed keys, adds user control + CloudTrail audit of key usage, header `aws:kms` — but uploads/downloads call the KMS `GenerateDataKey`/`Decrypt` APIs.
        - Count against regional *KMS request quotas*, so very high-throughput workloads can be throttled, request a quota increase if needed; 
      3. **SSE-C**: customer-fully-managed keys outside AWS. S3 never stores the key. Key must be passed in headers on every HTTPS request — HTTPS mandatory; 
      4. **Client-Side Encryption** (client encrypts before upload / decrypts after download using a library like the Amazon S3 Encryption Client, customer manages the whole key lifecycle). 
  - Default encryption (SSE-S3) applies automatically, but a bucket policy can force stronger encryption by denying `PutObject` calls missing the right encryption header/condition — bucket policies are evaluated before default encryption.
- **Encryption in transit**: 
  - S3 exposes both an *HTTP* (unencrypted) and *HTTPS* (TLS) endpoint; 
  - HTTPS is recommended (mandatory for SSE-C); 
  - *force HTTPS-only access* with a bucket policy statement that `Deny`s all actions when condition `aws:SecureTransport == false` (i.e. blocks any request that is NOT over HTTPS).

#### S3 Performance & Operations
- **Performance**: 
  - baseline ~100–200ms latency, at least 3,500 PUT/COPY/POST/DELETE or 5,500 GET/HEAD requests/second *per prefix* (no limit on number of prefixes — spread keys across prefixes to multiply throughput). 
    - Prefix: Basically the lowest level folder. E.g. 4 folders will allow for 5.5k*4 requests/second.
  - *Upload speed up* techniques:
    - **Multi-Part Upload** parallelizes upload of one large file (recommended >100MB, required >5GB). 
    - **S3 Transfer Acceleration** routes uploads through the nearest CloudFront edge location over the fast private AWS backbone to the bucket's region — compatible with multipart upload. 
  - *Download speed up*: Use Range HTTP request:
    - **Byte-Range Fetches** parallelize/speed up GETs by requesting specific byte ranges, or 
    - **File Header** (map of file byte range like ZIP) to fetch just part of an object , 
    - Range HTTP request improves resilience to failures.
- **S3 Requester Pays**: the requester (not the bucket owner) pays for the request + data transfer, useful for sharing large datasets across accounts; the requester must be an authenticated AWS principal (no anonymous access).
- **Event Notifications**: 
  - delivered typically within seconds
  - use case: generating thumbnails on upload.
  - `S3:ObjectCreated`, `ObjectRemoved`, `ObjectRestore`, `Replication`, etc., with object-name filtering (e.g. `*.jpg`); 
  - fan out to *SNS, SQS, or Lambda* (each needs a resource policy allowing `s3.amazonaws.com` to invoke it, scoped via `aws:SourceArn` to the bucket)
  - **Amazon EventBridge** as a destination adds advanced JSON-rule filtering (metadata, object size, name), more destination types (18+ services, e.g. Step Functions, Kinesis) and archive/replay/reliable-delivery capabilities.
- **S3 Batch Operations**: 
  - run one action across a large list of existing objects in one job, with retries/progress tracking/completion notifications/reports
  - Example operations: 
    1. encrypt, un-encrypted objects, 
    2. copy between buckets, 
    3. modify metadata/ACLs/tags, 
    4. *restore* from Glacier, 
    5. invoke a Lambda per object 
  - commonly driven by an *S3 Inventory object list* filtered through *Athena*.
- **S3 Object Lambda**: chains a Lambda function in front of GET via an S3 Object Lambda Access Point (built on a supporting S3 Access Point) to *transform objects on the fly* without duplicating data. 
  - Use cases: *redacting PII* for non-prod/analytics, *format conversion* (XML→JSON), on-the-fly *resizing/watermarking* based on the caller.

### Amazon FSx

**[#16 pop]**

- Family of fully managed, 3rd-party high-performance *network* file systems on AWS.
- Exists to *lift-and-shift workloads* needing a specific file system's protocol/features (SMB, Lustre, ONTAP, ZFS), unlike generic S3/EFS. i.e. Windows apps.
- Comparison:
  | | **Windows File Server** | **Lustre** | **NetApp ONTAP** | **OpenZFS** |
  |---|---|---|---|---|
  | *Protocol* | SMB, Windows NTFS | Lustre (parallel distributed FS) | NFS/SMB/iSCSI | NFS (v3/v4/v4.1/v4.2) |
  | *Lift-and-shift target* | Windows-native apps | HPC/ML workloads | existing NetApp/NAS workloads | existing ZFS workloads |
  | *Client OS support* | Windows; can mount on Linux EC2 too | Linux (EC2, on-prem) | Linux, Windows, macOS, VMware Cloud on AWS, WorkSpaces, AppStream 2.0, EC2/ECS/EKS | Linux, Windows, macOS, VMware Cloud on AWS, WorkSpaces, AppStream 2.0, EC2/ECS/EKS |
  | *Storage media* | SSD (latency-sensitive: DBs, media processing) or HDD (broad workloads: home dirs, CMS) | SSD (low-latency, small/random I/O) or HDD (throughput-intensive, large/sequential I/O) | auto-shrinks/grows | auto-shrinks/grows |
  | *Performance* | 10s of GB/s, 100s of PB | 100s of GB/s, millions of IOPS, sub-ms latency | — | up to 1,000,000 IOPS at <0.5ms latency (highest IOPS/lowest latency of the four) |
  | *Key integrations/features* | Microsoft AD integration, ACLs, user quotas, Microsoft DFS Namespaces (group multiple file systems) | mount an S3 bucket as a Lustre FS, write compute output back to S3 | snapshots, replication, compression, dedup, instantaneous point-in-time cloning (handy for test copies) | snapshots, replication, compression, dedup, instantaneous point-in-time cloning |
  | *Deployment/replication* | Multi-AZ option; daily backups to S3 | **Scratch** (temporary, not replicated, lost if file server fails, high burst throughput, short-term/cost-optimized) vs **Persistent** (long-term, replicated within same AZ, failed files replaced within minutes, for sensitive/long-term data) | — | — |
  | *On-prem access* | VPN/Direct Connect | VPN/Direct Connect | — | — |

- **When to use which**: 
  - *Windows File Server* for SMB/Windows-native apps needing *AD integration*; 
  - *Lustre* for *HPC/ML* workloads needing massive throughput and tight *S3 integration*; 
  - *NetApp ONTAP* for migrating existing *NetApp/NAS* workloads or needing *multi-protocol* (NFS/SMB/iSCSI) access;
  - *OpenZFS* for migrating existing *ZFS* workloads or needing the *highest IOPS* at the lowest latency among the four.
- **Native storage option summary**: Block = EBS, EC2 Instance Store. File = EFS, FSx. Object = S3, S3 Glacier.


### EBS (Elastic Block Store)

**[#18 pop]**

- Persistent block storage attached to a single EC2 instance (in the same AZ).
- **gp2/gp3** (general-purpose SSD, 1 GiB–*16 TiB*): cost-effective, boot volumes/dev-test/virtual desktops. 
  - *gp3* decouples IOPS (baseline 3,000, up to *16,000*) and throughput (baseline 125 MiB/s, up to *1,000 MiB/s*) from disk size;
    - Pricing (2026): $0.08/GB + $0.005/IOPS 
  - gp2 links IOPS to size (3 IOPS/GiB, bursts to 3,000, caps at *16,000 IOPS*).
    - Pricing (2026): $0.10GB
  - For small disk size, `gp3` is almost most certainly **cheaper** than `gp2` (even at 100 IOPS). `gp3` is likely better too.
- **io1/io2 Block Express** (provisioned IOPS SSD, 4 GiB–16/*64 TiB*): sustained IOPS/sub-ms latency, *critical DB workloads* needing >16,000 IOPS; 
  - io2 Block Express reaches up to *256,000 IOPS* and 
  - supports **EBS Multi-Attach** — same volume attached read/write to up to *16 instances* in the *same AZ* (needs a cluster-aware file system, not XFS/EXT4).
- **st1** (throughput-optimized HDD, 125 GiB–16 TiB, not bootable): *big data, data warehouses, log processing*; max 500 MiB/s, 500 IOPS.
- **sc1** (cold HDD, 125 GiB–16 TiB, not bootable): *infrequently accessed data*, *lowest cost*; max 250 MiB/s, 250 IOPS.
- **Quick comparison**:

  | Dimension | gp3 | gp2 | io1/io2 (Block Express) | st1 | sc1 |
  |---|---|---|---|---|---|
  | Media | SSD | SSD | SSD | HDD | HDD |
  | Size range | 1 GiB–16 TiB | 1 GiB–16 TiB | 4 GiB–64 TiB | 125 GiB–16 TiB | 125 GiB–16 TiB |
  | Max IOPS | 16,000 | 16,000 (3 IOPS/GiB baseline) | up to 256,000 | 500 | 250 |
  | Max throughput | 1,000 MiB/s | — | — | 500 MiB/s | 250 MiB/s |
  | Bootable | Yes | Yes | Yes | No | No |
  | Best for | Cost-effective general purpose, boot volumes | Legacy general purpose (gp3 usually cheaper/better) | Critical DBs needing >16,000 IOPS, Multi-Attach, sub-ms latency | Big data, data warehouses, log processing | Infrequently accessed data, lowest cost |
- **EBS snapshots**: point-in-time backup of a volume (detaching first is recommended, not required); can copy across AZ or Region. 
  - *Fast Snapshot Restore (FSR)* force-initializes a snapshot to remove first-use latency ($$$).
  - *EBS Snapshot Archive* moves a snapshot to a ~75% cheaper tier (24–72h to restore).
  - *Recycle Bin* retains deleted snapshots for a configurable period (1 day–1 year) to recover from accidental deletion. 
- **EBS encryption**: *encrypts data at rest, in-flight between instance and volume*, and *all snapshots/volumes derived* from it — transparent, minimal latency impact, keys from KMS (AES-256). 
  - To encrypt an existing unencrypted volume: (i) snapshot it, (ii) copy the snapshot with encryption enabled, (iii) create a new volume from new snapshot, and (iv) re-attach.
- **Delete on Termination**: controls whether an EBS volume is deleted when its EC2 instance terminates. *Root* volumes *default* to enabled (*deleted*); other *attached* volumes default to disabled (*preserved*) — toggle via console/CLI.
- Snapshots stored in S3 (incremental), can *copy across regions* for DR.

### EFS (Elastic File System)

**[#19 pop]**

- Managed NFS, **multi-AZ**, *scales automatically*, can be mounted by *many EC2* instances concurrently.
- Use case: *shared file* storage across a fleet of Linux instances (e.g., content management systems).
- vs EBS: EBS = single instance, single AZ; EFS = multiple instances, multiple AZs.

### Snow Family
- Secure, portable offline devices for edge data collection/processing and migrating data into/out of AWS. Rule of thumb: if a transfer would take over ~1 week on your network, ship a Snowball instead.
- **Snowball Edge**: Storage Optimized (104 vCPUs, 416GB RAM, 210TB SSD) or Compute Optimized (104 vCPUs, 416GB RAM, 28TB SSD). Order it, load it, ship it back — AWS imports into S3 (not directly into Glacier; use a lifecycle policy to transition after).
- **Edge Computing with Snowball Edge**: run EC2/Lambda directly on the device to process data on-site (trucks, ships, mines) — preprocessing, ML, media transcoding.
- **Snowcone / Snowmobile**: Snowcone = smaller edge device for tight spaces. Snowmobile = truck-scale, for exabyte migrations too big for Snowball Edge.

### AWS Storage Gateway
- Bridges on-prem environments to AWS storage (S3 isn't NFS-compatible on its own). Deployed as a VM (VMware/Hyper-V/KVM) on-prem or as an EC2 instance; encrypts data in transit.
- Use cases: disaster recovery, backup & restore, tiered storage, low-latency on-prem cache of cloud data.
- **S3 File Gateway**: exposes S3 over NFS/SMB, caches recently-used data locally. Supports S3 Standard/Standard-IA/One Zone-IA/Intelligent-Tiering directly (Glacier needs a lifecycle policy). Per-gateway IAM role for bucket access; SMB integrates with AD for auth.
- **Volume Gateway**: block storage over iSCSI, backed by EBS snapshots via S3. **Cached volumes** keep the full dataset in S3, caching only hot data locally. **Stored volumes** keep the full dataset on-prem, with scheduled backups to S3.
- **Tape Gateway**: a Virtual Tape Library (VTL) backed by S3/Glacier for existing tape-backup workflows — iSCSI interface, "eject" a tape to archive it.
- Hosting options: on-prem via VMware ESXi, Microsoft Hyper-V, or Linux KVM, or on the cloud via EC2.


### AWS DataSync
- **!!Popular on Exam!!**
- Moves large amounts of data to/from on-prem or another cloud (NFS, SMB, HDFS, S3 API — needs a DataSync Agent) or directly between AWS storage services (S3, EFS, FSx — no agent needed).
  - **Preserves file permissions and metadata (NFS POSIX, SMB)** — the only service that does this.
  - Tasks can run on a schedule (hourly/daily/weekly); one agent uses up to 10 Gbps, with an optional bandwidth cap.
  - Rough time estimate: Days ≈ (Data Size / Effective Internet Speed) / 10^5, where 10^5 ≈ (3600s × 24hr / 8b) converts speed from b/s to B/s.
  - Can sync to any S3 storage class, including Glacier.
  - **vs. Storage Gateway/Snowball/DMS**: DataSync does one-time/scheduled bulk file sync. Storage Gateway gives ongoing transparent access to AWS storage from on-prem apps. Snowball is offline/physical transfer for when network transfer is too slow. DMS is specifically for databases (CDC replication), not files.

### Additional Topics

> **Also in this domain (lower exam frequency)**: FSx (Windows/Lustre/NetApp ONTAP/OpenZFS), Storage Gateway, Transfer Family — see the companion Additional Topics guide.


---

## 2. Compute

### EC2 (Elastic Compute Cloud)

**[#2 pop]**

- **Sizing & config options**: 
  - OS (Linux/Windows/Mac), 
  - CPU, RAM, 
  - storage (network-attached: EBS/EFS, or hardware: Instance Store), 
  - network card speed & public IP, firewall rules (security group), and 
  - a bootstrap script (**EC2 User Data**) run once, as root, on first launch — used to install updates/software, download files, or any first-boot automation.
- **Instance type naming**: e.g. `m5.2xlarge` = `[instance class][generation].[size]`. Families: 
  1. **General Purpose** (t/m-series — balanced compute/memory/network, web servers, code repos), 
  2. **Compute Optimized** (c-series — batch processing, media transcoding, HPC, gaming, ML inference), 
  3. **Memory Optimized** (r/x-series — in-memory DBs, BI, real-time big-data processing), 
  4. **Storage Optimized** (i/d-series — high sequential read/write IOPS, OLTP, NoSQL, data warehousing, distributed file systems).
- **Security Groups**: stateful firewall at the instance level; **allow rules only** (no explicit deny), can reference by IP or by another security group; can attach to multiple instances; locked to a region/VPC combination; live "outside" the instance (blocked traffic never reaches it). All inbound traffic blocked by default, all outbound allowed by default. A connection **timeout** usually means a security group issue; **connection refused** means the app isn't running or errored.
- **EC2 Instance Connect**: browser-based SSH using a temporary AWS-uploaded key (no local key file needed) — works out-of-the-box only with Amazon Linux 2, and port 22 must still be open.
- **Purchasing options**:
  - **On-Demand**: pay per second/hour, no commitment — unpredictable, short-term, uninterrupted workloads.
  - **Reserved Instances**: *1 or 3-year* commitment, up to *~72%* discount, *scoped to instance attributes (type/region/tenancy/OS)* — steady-state predictable workloads (e.g. databases). **Convertible RIs** *allow changing instance family/OS/scope/tenancy* for a smaller (*~66%*) discount. Can be bought/sold on the RI Marketplace.
  - **Savings Plans**: commit to *$/hour of usage* for *1 or 3 years* (up to *~72%* discount); locked to an instance family + region but flexible across instance size, OS, and tenancy.
  - **Spot Instances**: *up to 90%* discount, can be reclaimed with a *2-minute warning* if your *max price < current spot price* — the most cost-efficient option, good for batch jobs/data analysis/anything fault-tolerant, **not** for critical jobs or databases. 
    - **Spot Fleets** request a set of Spot (+ optional On-Demand) instances across multiple launch pools using a strategy: `lowestPrice`, `diversified`, `capacityOptimized`, or `priceCapacityOptimized` (recommended default).
  - **Dedicated Hosts**: Most expensive option. An entire physical server dedicated to you, billed per host. For *BYOL*, *socket-or-core-based licensing* or *strict compliance*. 
  - **Dedicated Instances**: run on *hardware dedicated* to your account (may share hardware with your own other instances), billed per instance — no control over instance placement.
  - **Capacity Reservations**: reserve On-Demand capacity in a specific AZ. In case of insufficient on-demand capacity. No time commitment (create/cancel anytime), billed at On-Demand rate with **no discount**. 
    - Good for *short-term uninterrupted workloads* that must *run in a specific AZ*. 
- **Placement Groups**: 
  1. Cluster: low-latency 10 Gbps cluster in a single AZ. *Big data/HPC*, but an AZ failure takes down all instances, 
  2. Spread: each EC2 on separate HW, max 7 per AZ per group, can span AZs (min: 3 AZs, max: 6 AZs). Max *isolation* for *critical* instances, 
  3. Partition: up to 7 partitions per AZ. EC2's don't share racks across partitions. Scales to 100s of instances. Use cases: *Hadoop (EMR)/Cassandra (Keyspace)/Kafka (MSK)/HBase*.
- **Elastic IPs**: a public IPv4 address you own until you release it, remappable to another instance to mask a failure; **limited to 5** per account (soft limit). Generally *best avoided* — often reflects a poor architectural decision; prefer a random *public IP + DNS name*, or a *load balancer*.
- **ENI (Elastic Network Interface)**: a *virtual network card in a VPC* — can carry a primary + secondary private IPv4s, one Elastic IP per private IPv4, one public IPv4, one or more security groups, and a MAC address. Bound to a specific AZ. Can be created independently and moved between instances in that AZ for *failover*.
- *EC2 Hibernate*: *preserves* the *in-memory state* to a file on the root EBS volume (which must be encrypted) so the next start *skips OS boot and app warm-up*. Supported on specific instance families, RAM must be < 150 GB, not supported on bare metal, and an instance can't stay hibernated more than 60 days.
- **EC2 Instance Store vs EBS**: instance store = ephemeral hardware-attached disk, better IOPS (starting from *200k IOPS to 3M IOPS*), data lost on stop/terminate, backups/replication are your responsibility; EBS = persistent network-attached block storage ("network USB stick"), bound to an AZ, billed for all provisioned capacity, can be detached and re-attached to another instance quickly.
- **EBS volume types** (only gp2/gp3 and io1/io2 Block Express can be boot volumes):
  - See subsection [EBS (Elastic Block Store) - #18 pop](#ebs-elastic-block-store)
- **EFS** is another powerful network drive that can attached to multiple EC2 instances across multiple AZ.
  - See subsection [EFS (Elastic File System) - #19 pop](#efs-elastic-file-system)

### Scalability & High Availability (concepts)
- **Vertical scaling**: increase an instance's size (e.g. t2.nano → u-12tb1.metal). Used for non-distributed systems like a single DB (RDS, ElastiCache); hits a hardware ceiling.
- **Horizontal scaling (elasticity)**: add/remove instances — implies a distributed system, typically an ASG + Load Balancer.
- **High Availability**: run the app across ≥2 AZs to survive a data-center loss. Can be passive (RDS Multi-AZ failover) or active (horizontal scaling across AZs).

### Auto Scaling Groups (ASG)

**[#4 pop]**

- **ASG**: scales EC2 count based on CloudWatch *metrics/schedules/predictive scaling*; 
- ensures a min/max/desired instance count; 
- auto-registers new instances to a load balancer and *replaces terminated/unhealthy ones*. 
- Price: **free**.
- **Launch Template** (older "Launch Configurations" are deprecated) includes:
  1. EC2 related: AMI, instance type, EC2 User Data, EBS volumes, 
  2. Security & Access related: security groups, SSH key pair, IAM role, 
  3. Networking: network/subnets, and load balancer info, 
  4. ASG specific: min/max/initial capacity.
- **Scaling policies**: 
  - **Dynamic**: *Target Tracking* (simple, e.g. "keep average ASG CPU ~40%") or *Simple/Step Scaling* (a CloudWatch alarm crossing a threshold adds/removes a set number of instances); 
  - **Scheduled**: anticipate known usage patterns (e.g. raise min capacity at 5pm Fridays); 
  - **Predictive**: continuously *forecasts load* from historical data and *schedules* scaling *ahead of time*. Good metrics to scale on: 
    1. CPUUtilization, 
    2. RequestCountPerTarget, 
    3. Average Network In/Out, or 
    4. any custom CloudWatch metric.
- **Scaling cooldowns**: after a scaling activity, ASG pauses further launches/terminations for a cooldown period to let metrics stabilize
  - Default cooldown: 300s
  - use a ready-to-use AMI to reduce configuration time and shrink the effective cooldown.

### Elastic Load Balancing (ELB)

**[#14 pop]**

- **Why use a load balancer**: single DNS entry point, spreads load across downstream instances, seamlessly handles instance failures via health checks, SSL termination, session stickiness, and separates public from private traffic. An **Elastic Load Balancer** is AWS-managed (HA, upgrades, patching handled for you) — cheaper to run your own, but far more operational effort.
- **Health checks**: LB polls a port + route (e.g. `/health`) on each instance; anything other than a 200 response marks the instance unhealthy and removes it from rotation.
- **ALB** (Application Load Balancer, v2 — 2016): 
  - *Layer 7 (HTTP/HTTPS/WebSocket/HTTP2)*, routes to **target groups** (EC2, ECS tasks, Lambda functions, or private IPs) based on URL path, hostname, query string, or headers
  - one ALB can replace many Classic LBs for *multi-app routing*. A great fit for microservices/containers. 
  - The LB terminates the client connection and passes the *real client IP* via the `X-Forwarded-For` header (also `X-Forwarded-Port`/`-Proto`).
- **NLB (Network Load Balancer, v2 — 2017)**: 
  - *Layer 4 (TCP/UDP/TLS)*, handles *millions of requests/sec at ultra-low latency*; 
  - Target groups: EC2 instances, private IPs, or even another ALB.
  - one static IP per AZ, and supports assigning an Elastic IP (useful for IP whitelisting).
- **GWLB (Gateway Load Balancer, 2020)**: 
  - *Layer 3 (IP packets)*, for deploying/scaling *3rd-party virtual appliances (firewalls, IDS/IPS, deep packet inspection)* 
  - combines a transparent network gateway (single entry/exit point) with a load balancer; 
  - uses the GENEVE protocol on port 6081.
- *Classic Load Balancer (v1, legacy — 2009)*: Layer 4 & 7 (TCP/HTTP/HTTPS); supports only **one SSL certificate** — need multiple CLBs for multiple hostnames/certs. No Server Name Indication (SNI) support, i.e. cannot support multiple website on same IP.
- **Sticky sessions (session affinity)**: 
  - keep a client *routed to the same instance*, supported on *CLB/ALB/NLB* via a *cookie*:
    - either *app-generated* (custom name) or an *AWS-generated* app cookie (`AWSALBAPP`) 
    - *duration-based* cookie (`AWSALB` for ALB, `AWSELB` for CLB). 
  - Can create load imbalance across instances.
- **Cross-zone load balancing**: *evenly distributes* requests across all registered instances in *all* AZs, not just the instance's own AZ. 
  - ALB: *enabled* by default, *free*. 
  - NLB/GWLB: *disabled* by default, *charged for inter-AZ* data if enabled. 
  - CLB: disabled by default, free if enabled.
- **SSL/TLS on load balancers**: the LB holds an X.509 certificate (managed via ACM or self-uploaded). **SNI (Server Name Indication)** lets *1 listener serve multiple certs/domains* by having the client indicate the target hostname during the TLS handshake. Supported on *ALB & NLB (and CloudFront)*, not on CLB (which needs one LB per certificate).
- **Connection draining**: called *Connection Draining* on CLB, *Deregistration Delay* on ALB/NLB — time (1–3600s, *default 300s*) the LB waits for in-flight requests to finish on a de-registering/unhealthy instance before cutting it off; set low for short-lived requests, or 0 to disable.
- Exam tests: 
  1. choosing the right LB type/routing for the traffic pattern given, and 
  2. Multi-AZ (HA) vs Auto Scaling (elasticity) vs vertical scaling distinctions.

### Lambda (Serverless Compute)

**[#3 pop]**

- "Serverless" doesn't mean no servers — it means you never manage/provision/see them; pioneered by Lambda, now applied broadly: DynamoDB, Cognito, API Gateway, S3, SNS/SQS, Kinesis Data Firehose, Aurora Serverless, Step Functions, Fargate.

#### Basic Info
- *Virtual functions*, not virtual servers: no OS/patching to manage, limited by time (*short executions*) not RAM/CPU alone, runs on-demand, *scales automatically* — contrast with EC2 (continuously running, scaling needs manual intervention).
- Lambda's **Triggers**: S3 events, API Gateway, DynamoDB Streams, Kinesis, SQS, SNS, EventBridge/CloudWatch Events (schedules), CloudWatch Logs, Cognito, CloudFront.
- Use case: 
  1. event-driven microservices, 
  2. glue logic, 
  3. image processing on S3 upload, 
  4. cron-like scheduled tasks (EventBridge schedule → Lambda).
- **Languages**: *Node.js, Python, Java, C# (.NET Core)/PowerShell, Ruby*, plus a community Custom Runtime API (e.g. Rust, Go). **Container images** are also supported but must *implement the Lambda Runtime API* — for arbitrary Docker images, ECS/Fargate is the better fit.
- **Pricing**: 2 parts:
  1. pay per request: *first 1M free*, then **$0.20/million**
  2. pay per duration in 1ms increments 
    - *400,000 GB-seconds/month free*. e.g. **400,000s @ 1GB RAM** or **3,200,000s at 128MB**, 
    - then **$1.00 per 600,000 GB-second**.
- **Limits (per region)**: 
  - memory 128MB - **10GB** (1MB increments — more RAM also scales CPU and network proportionally), 
  - max execution time 900s or **15 min**, 
  - env vars *4KB*, 
  - `/tmp` disk 512MB - **10GB**, 
  - default concurrency limit for *all functions per region* is **1,000** (raisable via support ticket), 
  - deployment package *50MB zipped / 250MB unzipped*.
- **Concurrency & throttling**: 
  - **Reserved concurrency** caps/guarantees a function's concurrent executions; 
  - exceeding the concurrency limit triggers a Throttle. 
    - **Synchronous** callers (e.g. API Gateway, ALB, or `invoke` with `RequestResponse`) get a `429 ThrottleError` back immediately, 
    - **Asynchronous** callers (e.g. S3 event notifications, SNS, EventBridge) are retried automatically (exponential backoff from 1s up to 5 min, for up to 6 hours) then routed to a DLQ if still failing. 
  - Without reserved concurrency, one noisy function can starve concurrency from other function/caller in the account's region.

#### Lambda Start Up
- a cold start = a fresh instance runs your init code (loading the runtime, dependencies) before the handler, adding latency to that first request; 
- **Provisioned Concurrency** pre-initializes a set number of execution environments in advance so to avoid cold starts. 
  - Can be managed by *Application Auto Scaling* -  scheduled or target-utilization based.
  - Extra cost of $0.015/GB-hour or  $1.08 per month per GB.
- **Lambda SnapStart**: *Java, Python, .NET* gets up to *10x faster starts at no extra cost* by invoking from a cached, pre-initialized snapshot of memory/disk state taken when you publish a version.

#### Lambda & the Edge
- **Edge functions**: code attached to a CloudFront distribution, running close to users. 
  - E.F. use cases:
    1. Website *Security and Privacy*
    2. Dynamic Web App @ Edge
    3. SEO
    3. *Inteligent routing* across origins & data centers
    3. Bot mitigation @ Edge
    3. Real-time image transformation
    3. A/B testing
    3. User auth
    3. User tracking & analytics
  - Two types:

    | | **CloudFront Functions** | **Lambda@Edge** |
    |---|---|---|
    | Runtime | Lightweight JavaScript | Node.js/Python |
    | Startup | Sub-ms | — |
    | Throughput | Millions of req/s | Thousands of req/s |
    | Triggers | Only **Viewer Request/Response** | **Viewer + Origin Request/Response** |
    | Exec time | <1ms | 5–10s |
    | Max memory | 2MB | Up to 10GB |
    | Package size | 10KB | 1–50MB |
    | Network/filesystem access | No | Yes |
    | Authoring | — | Author in us-east-1; CloudFront replicates globally |
    | Use cases | 1. *Cache key normalization* (transform headers, cookies, query string & URL)<br>2. Header manipulation<br>3. URL rewrites/redirects<br>4. Request auth | 1. >1ms exec time<br>2. Need more CPU/RAM<br>3. 3rd party libraries<br>4. Network access dependency<br>5. File system access<br>6. Calling other AWS services via SDK<br>7. Dynamic content at the edge |

#### Lambda, Networking & DB
- **Networking**: 
  - by default, a Lambda function runs *outside your VPC* (in an AWS-owned VPC) and cannot reach resources inside your VPC (private RDS, ElastiCache, internal ELB). 
  - To reach them, *deploy* the function into your *VPC* (specify VPC ID, subnets, security groups). Lambda creates an *ENI in your subnet* to route traffic, and the *target resource's security group* must allow the Lambda function's security group.
- **Lambda with RDS Proxy**: 
  - many Lambda invocations opening direct DB connections under load can exhaust the database's connection limit; RDS Proxy:
    - *pools/shares connections*, 
    - cuts *failover time ~66%* (require multi-AZ), and 
    - enforces IAM auth + Secrets Manager credentials 
  - the *Lambda* function must itself run *inside the VPC*, since *RDS Proxy is never publicly* accessible.
- **Invoking Lambda from RDS/Aurora**: RDS for PostgreSQL and Aurora MySQL can invoke a Lambda function directly from within the database to react to data events (e.g. on INSERT, send a welcome email via SES) 
  - DB instance requires outbound connectivity (public route, NAT Gateway, or VPC Endpoint) plus both a Lambda resource-based policy and an IAM policy granting the DB instance invoke permission. 
  - different from **RDS Event Notifications**, which only *report* on the DB instance's own *lifecycle* (created/stopped/started, snapshot, parameter/security group, RDS Proxy, custom engine version changes — near-real-time within 5 min) via *SNS or EventBridge*, with no visibility into the data itself.


### Docker fundamentals
- Docker packages apps into **containers** that run identically on any machine/OS — no compatibility issues, less maintenance, works with any language.
- Unlike a VM (guest OS + hypervisor per app), containers share the host OS/kernel via the Docker daemon, so more fit on one server.
- Use cases: microservices, lift-and-shift from on-prem.
- A `Dockerfile` **builds** an **image**, which **runs** as a container. Images are pushed/pulled to a **repository**: **Docker Hub** (public) or **Amazon ECR** (private, plus a public Gallery).
  - ECR is backed by S3, integrates with ECS, uses IAM for access, and supports vulnerability scanning, tags, and lifecycle policies.

### ECS (Elastic Container Service)

**[#13 pop]**

- AWS-native container orchestration — launching a container = running an **ECS Task** (defined by a task definition: image, CPU/RAM, roles, ports, etc.) on an **ECS Cluster**.
- **EC2 Launch Type**: you provision/maintain the underlying EC2 instances, each running the **ECS Agent** to *register* with the *cluster*; AWS starts/stops containers on them for you — gives more control over instance type/cost at scale.
- **Fargate Launch Type**: no EC2 instances to manage at all — fully *serverless*; you just define *tasks* (*CPU/RAM* needed) and AWS runs them; scale by increasing task count, not instance count.
- **IAM roles**: 
  - an **EC2 Instance Profile** (EC2 launch type only) is used by the ECS Agent itself — makes ECS API calls, sends container logs to CloudWatch Logs, pulls images from ECR, references secrets in Secrets Manager/SSM Parameter Store. 
  - An **ECS Task Role** (defined per task definition) lets each task assume a distinct, least-privilege role — e.g. Task A gets S3 access, Task B gets DynamoDB access, from the same cluster.
- To launch ECS services, you need a *task definition* (image name, CPU allocation, memory allocation and more) first.
- **Load balancer integration**: 
  1. *ALB* is supported and *fits most use cases*; 
  2. *NLB* is recommended only for high throughput/*performance* needs or *pairing with PrivateLink*; 
  3. Classic LB is supported but not recommended (no advanced features, no Fargate support).
- **Data volumes (EFS)**: mount an *EFS* file system onto *ECS tasks* — works with both EC2 and Fargate launch types, tasks in any AZ share the same data (Fargate + EFS = fully serverless shared storage). Note: *S3 cannot* be mounted as a file system.
- **ECS Service Auto Scaling** (task count, via AWS Application Auto Scaling) 
  - is *separate* from EC2 Auto Scaling (instance count, EC2 launch type only, via ASG scaling or an *ECS Cluster Capacity Provider* which pairs with an ASG to add EC2 capacity automatically when tasks need more room). 
  - ECS **scaling policies**: 
    1. *Target Tracking*: hit a target CloudWatch metric value, e.g. ECS Service average CPU/RAM, or ALB Request Count Per Target, 
    2. *Step* Scaling: react to a CloudWatch Alarm breach, 
    3. *Scheduled* Scaling: predictable date/time changes. 
  - *Fargate* auto scaling is *simpler* to set up since there's no underlying instance layer.
- **Event-driven tasks**: *EventBridge* can *launch* a new ECS task in response to:
  1. an *event* (e.g. an S3 upload — with an ECS Task Role scoped to read S3/write DynamoDB) or 
  2. on a *schedule* (e.g. hourly batch processing); 
  3. it can also capture `ECS Task State Change` events (e.g. `lastStatus: STOPPED`) and route them to *SNS* to alert an administrator when a *task/container exits unexpectedly*. 
  4. An *SQS* queue can also sit in front of an ECS service so *tasks poll* it directly, scaling with ECS Service Auto Scaling like any other consumer.

### Fargate

**[#17 pop]**

- **!!Popular on exam!!**
- *Serverless* compute engine for *ECS/EKS* — no EC2 instances to manage, pay per task.
- Fargate is part of ECS or EKS.
- Standard Fargate is slightly *more expensive* than the cheaper EC2 instances for web requests.
- Setting Fargate to *0 task* for *web requests* will result in bad user exp. Takes *1 min to spin up* new container to serve requests.
- Use case: 
  1. Fargate when you don't want to *manage underlying servers*; EC2 launch type when you need more control over instance type/cost optimization at scale.
  2. *Bursty* compute

### EKS (Elastic Kubernetes Service)
- Managed control plane for **Kubernetes**, the open-source system for deploying/scaling/managing containerized apps — an alternative to ECS with a Kubernetes-native API. Kubernetes is cloud-agnostic, so EKS suits a company already running it elsewhere. Deploy one cluster per region for multi-region; use CloudWatch Container Insights for logs/metrics.
- **Node types**: Managed Node Groups (EKS manages EC2 nodes in an ASG, On-Demand or Spot), Self-Managed Nodes (you create/register nodes yourself), or Fargate (no nodes to manage).
- **Data volumes**: needs a `StorageClass` manifest with a CSI-compliant driver; supports EBS, EFS (works with Fargate), FSx for Lustre, and FSx for NetApp ONTAP.

### Elastic Beanstalk
- A developer-centric PaaS: handles capacity provisioning, load balancing, scaling, health monitoring, and instance config so you only manage application code — full control over the config remains available. Beanstalk itself is free; you pay only for the underlying resources.
- **Components**: **Application** (a collection of environments/versions/configs), **Application Version** (one code iteration), **Environment** (the AWS resources running one version — Web Server or Worker Tier). Workflow: create application → upload version → launch environment → deploy new versions.
- **Supported platforms**: Go, Java SE/Tomcat, .NET (Core/Windows), Node.js, PHP, Python, Ruby, Packer Builder, Docker.
- **Web Server Tier** = ALB + ASG of EC2 web instances. **Worker Tier** = ASG that pulls/processes messages from an SQS queue, scaling on queue depth.
- **Deployment modes**: Single Instance (one EC2 + Elastic IP, no Multi-AZ RDS) for dev. High Availability (ALB + ASG across AZs, RDS Multi-AZ) for production.


---

## 3. Databases

### RDS (Relational Database Service)

**[#5 pop]**

#### RDS Basics
- Managed relational DB engines: Postgres, MySQL, MariaDB, Oracle, Microsoft SQL Server, IBM DB2, and Aurora.
- Advantages over self-managed DB-on-EC2:      
  - continuous backups with **point-in-time restore**, 
  - monitoring dashboards, 
  - **read replicas** (CR), 
  - **Multi-AZ**, 
  - maintenance windows (auto patch-and-failover), 
  - **vertical/horizontal scaling**, 
  - EBS-backed storage — trade-off: *no SSH access* to the underlying instance (except RDS Custom).
- **RDS Custom**: for *Oracle* and *SQL Server* only — gives admin access to the underlying OS and database (via SSH/SSM) to configure settings, install patches, or enable native features; deactivate Automation Mode first (snapshot recommended before customizing). Trade-off vs standard RDS: RDS manages everything, RDS Custom gives you full admin access.
- **Security**: at-rest encryption via KMS must be set at launch time (an unencrypted master can't have encrypted replicas — snapshot & restore as encrypted to fix); in-flight encryption is TLS-ready by default using AWS TLS root certs; IAM Authentication lets you connect using IAM roles instead of username/password; Security Groups control network access; no SSH except on RDS Custom; Audit Logs can be sent to CloudWatch Logs.

#### RDS Scaling & HA
- **Storage Auto Scaling**: dynamically grows storage when RDS detects you're running low up to a **Maximum Storage Threshold** you set.
  - All 3 conditions for scaling: (i) free storage spaces < 10% of allocated, (ii) low-storage state lasted ≥ 5 min, and (iii) 6 hours since the last modification
  - Good for unpredictable workloads, supports all RDS engines.
- **Multi-AZ**: synchronous replication to a *standby* in another AZ for **high availability/failover** 
  - *Mainly for auto-failover*. One DNS name auto-fails over on AZ loss, network loss, instance or storage failure, no manual intervention needed.
  - *Not for read scaling.* This is the job of Read Replicas.
  - Converting Single-AZ → Multi-AZ is a *zero-downtime* operation. Snapshot + restore in new AZ + sync.
- **Read Replicas**: 
  - up to 15 replicas, 
  - can be within-AZ/cross-AZ/**cross-region**, 
  - **asynchronous replication** (eventually consistent) for **read scaling** only (SELECT, not INSERT/UPDATE/DELETE); 
  - each needs its own connection string in the app; 
  - promotable to a standalone DB. 
  - *Same*-region replication is *free* vs *cross*-region replication incurs data transfer *cost*. In cross region, VPC cannot help eliminate cost because: VPC is region-bound -> Cross region require 2 VPCs -> Cross region cost  still exist.
- **RDS Proxy**: fully managed connection pooler sitting in front of RDS/Aurora. 
  - Make many DB connections *into less connections*. Scale to read more data. 
  - Reduces DB CPU/RAM stress from many open connections/timeouts (common with Lambda), 
  - serverless/auto-scaling/Multi-AZ, 
  - *cuts failover* time by up to *66%*, 
  - enforces IAM auth and stores credentials in Secrets Manager
  - is never publicly accessible (must be reached from within a VPC).
- **Backups**: 
  - Automated backups perform:
    1. take a daily full backup during the backup window 
    2. transaction logs every 5 minutes, giving point-in-time restore anywhere from the oldest backup to 5 minutes ago; 
  - Automated backup retention 1 - 35 days (0 disables). Console defaults to 7 and CLI defaults to 1 day. 
  - Manual DB snapshots are user-triggered with retention for as long as you want. 
  - Restoring a backup/snapshot always **creates a new database**. 
  - A stopped RDS instance still incurs storage charges — for long stops, snapshot & delete instead.
 
- Exam tests: *Multi-AZ (HA) vs Read Replica (scaling)* — a very common distinction question.

### Aurora

**[#10 pop]**

- AWS-proprietary (not open-sourced), Postgres- and MySQL-compatible (drivers work as-is), claims *~5x MySQL* and *~3x Postgres performance* vs standard *RDS*; *costs ~20% more* than RDS but is more efficient.
- Storage auto-scales in 10GB increments up to 256TB; 6 copies of data across 3 AZs (4/6 needed for writes, 3/6 for reads), self-healing peer-to-peer replication, storage striped across hundreds of volumes.
- One Aurora instance takes writes (master); automated master failover in < 30 seconds; up to 15 Aurora Read Replicas serve reads with sub-10ms replica lag (faster than MySQL replication) — HA is native, no separate Multi-AZ setup needed.
- **Cluster endpoints**: 
  - Writer Endpoint (always points to master) 
  - Reader Endpoint (connection-load-balances across all read replicas, which also auto-scale by CPU usage). 
  - **Custom Endpoints** define a named subset of instances (e.g. larger instance types for analytical queries). Once defined, the *Reader* Endpoint is generally *no longer used* directly.
- **Aurora Serverless**: automated instantiation and scaling based on actual usage via a managed proxy fleet — good for *infrequent/intermittent/unpredictable* workloads, no capacity planning, pay per second.
- **Global Database**: 
  - recommended *over* plain *cross-region* read replicas
  - *1 primary* region (read/write) 
  - plus up to *10* secondary *read*-only *regions* with < 1 second typical replication lag and  
    - up to *16 read* replicas per *secondary* region; 
  - promoting a secondary region for *DR* has an *RTO < 1 minute*.
- **Aurora Machine Learning**: *call SageMaker* (any ML model) or *Comprehend* (sentiment analysis) directly *via SQL* from within Aurora 
  - use cases: fraud detection, ad targeting, sentiment analysis, product recommendations.
- **Babelfish for Aurora PostgreSQL**: lets Aurora PostgreSQL *understand MS SQL Server's T-SQL*, so SQL Server–based apps can run against Aurora PostgreSQL with little/no code change after migrating (via SCT + DMS).
- **Backups**: 
  - **point-in-time recovery**: *automated 1–35 days* (cannot be disabled); 
  - *manual snapshots*:  retained as long as you want. 
  - **Backtrack** restores data to any point in time without using backups. 
  - **Database Cloning** creates a new cluster from an existing one using fast, cost-effective *copy-on-write* (*shares* the original data *volume until writes diverge*). Good for spinning up a staging DB from production without impacting it.
- **Security** mirrors RDS: 
  1. KMS at-rest encryption (set at launch), 
  2. TLS in-flight, IAM Authentication, 
  3. Security Groups, 
  4. no SSH, 
  5. CloudWatch audit logs.

### ElastiCache
- Managed Redis or Memcached — in-memory DBs for very high performance/low latency, helping apps stay stateless. AWS handles OS maintenance, setup, monitoring, failure recovery, and backups, but (unlike RDS) still requires application code changes.
- **Redis vs Memcached**: Redis supports Multi-AZ auto-failover, read replicas, AOF durability, backup & restore, and Sets/Sorted Sets. Memcached supports multi-node sharding and is multi-threaded, but has no replication/HA/persistence — only backup & restore (serverless).
- **Security**: IAM only governs API-level access (creating/deleting clusters), not data access. **Redis AUTH** adds a password on top of security groups plus SSL in-flight encryption. Memcached uses SASL auth.
- **Patterns**: Lazy Loading (cache reads, can go stale), Write-Through (update cache on every DB write — avoids staleness but wastes cache space), Session Store (TTL-based temp data). Cache invalidation is the classic hard problem.
- Use cases: reducing RDS/DynamoDB read load, shared session storage, gaming leaderboards (Redis Sorted Sets for ranking).

### DynamoDB 

**[#9 pop]**

**!!Popular Exam Question!!**

- Managed **NoSQL** key-value/document store, fully managed with replication across multiple AZs, transaction support, scales to millions of requests/s and trillions of rows/100s of TB, single-digit millisecond latency at any scale, IAM-integrated security, no maintenance/patching/downtime. **Standard** and **Standard-Infrequent Access (IA)** table classes.
- **Basics**: made of **Tables**, each with a **Primary Key** fixed at creation (either a simple Partition Key, or a composite Partition Key + Sort Key); unlimited items (rows) per table; each item has flexible **attributes** (can be added over time, can be null) up to 400KB/item. Data types: Scalar (String, Number, Binary, Boolean, Null), Document (List, Map), Set (String Set, Number Set, Binary Set) — schema evolves rapidly since only the key is fixed.
- Great for **rapidly evolving schemas**.
- **Standard-Infrequent Access (IA)** reduces cost by 60% but increase read/write cost by 25%. Performance is same as Standard.
  - Use case: logs, archive, analytics or data that is not accessed frequently
- **Capacity modes**: 
  1. **Provisioned** (default) — you specify Read Capacity Units (RCU) and Write Capacity Units (WCU) up front, need to plan capacity, can add auto-scaling on top.
    - Can make *auto-scaling* provisioned with Cloudwatch + Application Auto Scaling services. But, not as fast as On-Demand. 
  2. **On-Demand** — reads/writes auto-scale with the workload, no capacity planning, pay-per-use (more expensive), best for unpredictable workloads/steep sudden spikes.
- **DAX (DynamoDB Accelerator)**: fully managed, highly available, seamless in-memory cache sitting in front of DynamoDB — microsecond latency for cached data, no application logic changes needed (same DynamoDB API), 5-minute default TTL; caches individual objects and Query/Scan results. Different from ElastiCache in front of DynamoDB, which is typically used to cache computed/aggregated results rather than raw DynamoDB API calls.
- **Streams**: an ordered stream of item-level create/update/delete events on a table. **DynamoDB Streams** (24h retention, limited consumers, processed via Lambda triggers or the DynamoDB Streams Kinesis Adapter) vs the newer **Kinesis Data Streams for DynamoDB** (up to 1 year retention, many more consumers, processed via Lambda, Kinesis Data Analytics, Kinesis Data Firehose, AWS Glue Streaming ETL). Use cases: react to changes in real time (e.g. welcome email), real-time usage analytics, populate derivative tables, cross-region replication, invoke Lambda on changes.
- **Global Tables**: active-active, two-way replication across regions for low-latency multi-region access; applications can read AND write in any participating region; requires DynamoDB Streams enabled as a prerequisite.
- **TTL (Time To Live)**: automatically deletes items past an expiration epoch timestamp attribute (scan-and-expire, then scan-and-delete) — reduces stored data/cost, helps meet regulatory retention limits, useful for session data.
  - Use cases: reduce storage, regulatory obligations, web sessions
- **Backups for DR**: continuous backups via **Point-In-Time Recovery (PITR)**, optionally enabled, up to the last 35 days, restore to any point within that window; **On-demand backups** are full, long-term backups kept until explicitly deleted, with no performance/latency impact, manageable via AWS Backup (including cross-region copy). Both restore paths create a **new** table.
- **S3 integration**: Two types of integration:
  1. **Export to S3** requires PITR enabled, works for any point in the last 35 days, doesn't consume table read capacity; exports in DynamoDB JSON or ION format.
    - Use cases: data analysis (e.g. Athena on top), audit snapshots, or ETL before re-importing
  2. **Import from S3** loads CSV, DynamoDB JSON, or ION, doesn't consume write capacity, always creates a new table, and logs import errors to CloudWatch Logs.
- Use case: high-scale web/mobile apps, gaming leaderboards, session state — when schema is simple/flexible and scale is a priority.

### Big Data Concepts (Primer)
*You won't be quizzed on these definitions directly, but Redshift/Athena/EMR/Glue questions assume you know the vocabulary.*
- **OLTP vs OLAP**: OLTP (RDS/Aurora/DynamoDB) = many small, fast reads/writes running the live app. OLAP (Redshift/Athena/EMR) = fewer, heavier queries aggregating large historical data. You don't run OLAP against your OLTP DB directly — it would slow/lock the app — so data is copied out via ETL instead.
- **Data Lake**: cheap, massive storage (S3) holding data as-is — structured, semi-structured, or unstructured — with no schema at write time ("schema-on-read"). Cheaper/more flexible than a warehouse but slower for repeated BI queries. **Lake Formation** helps build one on S3; **Athena/EMR/Redshift Spectrum** query it.
- **Data Warehouse**: a separate DB purpose-built for OLAP, holding cleaned/structured data (usually a star schema) loaded in ahead of time. Optimized for fast SQL aggregation, not flexibility. **Redshift** is AWS's warehouse.
- **Data Lakehouse**: layers warehouse-like structure/performance (schema, indexing, ACID) on top of data-lake storage, avoiding two copies of data. In AWS: S3 + Glue Data Catalog + **Redshift Spectrum**.
- **Batch vs Streaming**: Batch runs on accumulated data at intervals (nightly Glue job, EMR) — simpler, higher latency. Streaming processes data continuously as it arrives (Kinesis Data Streams, Managed Flink, MSK) for near-real-time results. **Kinesis Data Firehose** sits in between: near-real-time (~60s buffer) delivery into S3/Redshift, no infra to manage.


### Amazon Athena

**[#22 pop]**

- Serverless query service to *analyze data directly in S3* using standard SQL (built on Presto). 
  - Supports *CSV, JSON, ORC, Avro, Parquet*. 
  - Pricing: *$5.00 per TB* of data scanned. 
  - Commonly paired with *QuickSight* for reporting/dashboards. 
  - Also used to query *VPC Flow Logs, ELB logs*, and *CloudTrail trails*. 
- Exam trigger: "analyze data in S3 with serverless SQL" → Athena.
- **Performance/cost tips**: 
  - use **columnar formats** (Parquet or ORC, converted via Glue) to scan less data; 
  - **compress** data (bzip2, gzip, lz4, snappy, zlip, zstd) for smaller scans; 
  - **partition** S3 datasets by virtual columns in the key path (e.g. `s3://bucket/table/year=1991/month=1/day=1/`) so queries skip irrelevant prefixes; 
  - use **larger files** (>128MB) to cut per-file overhead.
- **Federated Query**: run SQL across *relational, non-relational, object, and custom/on-prem data sources* (ElastiCache, DocumentDB, DynamoDB, RDS, Aurora, SQL Server, MySQL, HBase-on-EMR) via *Lambda-based Data Source Connectors*, *storing* results back in *S3*. This lets Athena act as a *single SQL layer* over heterogeneous sources.

### Redshift
- PostgreSQL-based but **OLAP**, not OLTP — a data warehouse claiming ~10x better performance than other warehouses via columnar storage and a parallel query engine, scaling to petabytes. SQL interface, integrates with BI tools (QuickSight, Tableau); faster than Athena for joins/aggregations due to indexes, but needs a running cluster.
- **Cluster architecture**: a **Leader Node** plans queries and aggregates results; **Compute Nodes** execute and return results to the leader. **Provisioned** mode (choose instance types, can reserve for savings) or **Serverless** (no cluster management). Some configs support **Multi-AZ** for HA.
- **Snapshots & DR**: incremental, point-in-time backups stored in S3; restoring creates a **new cluster**. Automated snapshots run every 8 hours or every 5GB changed, retained 1–35 days; manual snapshots retained until deleted. Both can auto-copy to another region for DR.
- **Loading data**: bulk inserts beat row-by-row writes. Options: Kinesis Data Firehose, the `COPY` command from S3 (public internet or private via Enhanced VPC Routing), or an EC2 JDBC driver (batch writes recommended).
- **Redshift Spectrum**: queries data in S3 without loading it — still needs a running cluster to originate the query, which fans out to separate Spectrum nodes to scan S3.
- Use case: BI and large-scale analytics, not transactional workloads.

### Choosing the Right Database (decision framework)
- Ask: read/write/balanced workload? Throughput and how it fluctuates? Data size, growth, object size, access pattern? Durability and source of truth? Latency and concurrency needs? Joins needed? Structured vs flexible schema? Reporting/search needs? Worth the licensing switch to a cloud-native DB like Aurora?
- **By category**: RDBMS/OLTP with joins → RDS or Aurora. NoSQL, no joins → DynamoDB (JSON-like), ElastiCache (key/value), Neptune (graph), DocumentDB (MongoDB-compatible), Keyspaces (Cassandra-compatible). Object store → S3 (large objects) / Glacier (archive). Analytics/BI → Redshift, Athena, EMR. Free-text search → OpenSearch. Ledger (immutable history) → QLDB. Time series → Timestream.
- Neptune, DocumentDB, Keyspaces, and Timestream are covered in the companion Additional Topics guide.

---

## 4. Networking & Content Delivery

### Route 53

**[#24 pop]**

- A highly available, scalable, fully managed **authoritative** DNS (you can update the records) that is also a *domain registrar*; the only AWS service with a **100% availability SLA**. Named for port 53, the traditional DNS port.
- *DNS terminology*: Domain Registrar (Route 53, GoDaddy, ...) vs DNS Service — not the same thing, though registrars usually bundle basic DNS; you can register with one provider and manage DNS records with another (e.g. buy via GoDaddy, point its NS records at Route 53). Zone File contains DNS records; Name Server resolves queries (authoritative or non-authoritative); Top Level Domain (.com, .org) and Second Level Domain (amazon.com) make up a Fully Qualified Domain Name.
- Use case: DNS-level traffic management and failover across regions.
- **Hosted Zones** ($0.50/month each): a container of records for how to route traffic for a domain + subdomains. 
  1. **Public Hosted Zone** routes internet traffic (public domain names); 
  2. **Private Hosted Zone** routes traffic within one or more VPCs (internal domain names like `app.company.internal`).
- **Records**: each has a domain/subdomain name, record type, value, routing policy, and TTL (time DNS resolvers cache the answer — high TTL = less Route 53 traffic/cost but more outdated data on change; low TTL = opposite; TTL is mandatory except for Alias records). Must-know types: 
  - **A**: hostname → IPv4
  - **AAAA**: hostname → IPv6
  - **CNAME**: hostname → another hostname. Target must itself have an A/AAAA record, and CNAME can't be used for the zone apex/root domain 
  - **NS** (name servers for the hosted zone).
- *Alias records vs CNAME*: *Alias* maps a *hostname* to an *AWS resource* (ALB/NLB, CloudFront, API Gateway, Elastic Beanstalk, S3 website, VPC interface endpoint, Global Accelerator, or another Route 53 record in the same zone), auto-tracks the resource's underlying IP changes, works for **both root and non-root domains**, is free, has *native health checking*, and you can't set its TTL — always of type A/AAAA. You cannot create an Alias for a raw EC2 DNS name. CNAME is non-root only.
- **Routing policies**: 
  - **Simple** — one record, optionally *multiple values* with the client picking one at *random* (only one AWS resource if Alias-enabled; no health checks). 
  - **Weighted** — traffic split by relative weight (traffic % = weight ÷ sum of weights, needn't total 100; weight 0 stops traffic to that record; if all are 0, traffic is split evenly)
    - Use case: A/B testing, canary rollouts. 
  - **Latency-based** — routes to the region with *lowest measured latency* between the user and AWS Regions (not necessarily the geographically nearest), supports health-check failover. 
  - **Failover (Active-Passive)** — routes to a primary, *health check mandatory*, fails over to a secondary/DR resource when unhealthy. 
  - **Geolocation** — routes by the user's *location* (continent/country/US state, most-specific match wins); should define a "Default" record for unmatched locations; 
    - use cases: localization, content restriction. 
  - **Geoproximity** (requires Route 53 Traffic Flow) — routes by *geographic distance* between users and resources (AWS region or lat/long for non-AWS resources), with a **bias** value (1 to 99 to expand a region's reach, -1 to -99 to shrink it) to shift traffic volume. 
  - **IP-based routing** — maps *CIDR* blocks of *client IPs* to specific endpoints/locations.
    - Use case: for optimizing *performance* or steering a particular *ISP's* users. 
  - **Multi-Value** — returns up to *8 healthy record values* per query, can be health-checked, but is **not a substitute for a real load balancer**.
- **Health Checks (HC)**: 
  - HTTP checks only work for **public** resources (can't reach private/on-prem endpoints directly). 
  - Use Cases: monitoring, *failover*, Cloudwatch integration, *smart routing* control
  - About *15 global checker* locations poll 
  - Default interval *30s*. Can drop to *10s* for higher cost; 
  - default healthy/unhealthy threshold is 3 consecutive checks; 
    - *passes* only on *2xx/3xx* responses, and can additionally require specific text in the first 5KB. 
  - Types of HC: 
    1. monitor an **endpoint** directly, 
    2. **Calculated Health Checks** combine up to *256 child checks* with *OR/AND/NOT* and a *pass threshold* — useful for maintaining a site without failing all checks at once, 
    3. monitor a **CloudWatch Alarm** — the workaround for **private resources** (create a CloudWatch metric + alarm on the private resource, then health-check the alarm itself
  - *Firewalls/routers* must *allow inbound* traffic from Route 53's *published checker IP ranges*.
- **Hybrid DNS / Resolver**: 
  - the Route 53 *Resolver* automatically answers queries for *local EC2 domain* names, *Private Hosted Zone* records, and *public name servers*. 
  - For *hybrid* resolution between a *VPC* and *other networks* (peered VPCs or on-prem via Direct Connect/VPN): 
    - an **Inbound Endpoint** lets your *on-prem DNS resolvers* query *AWS-side records* (EC2 names, Private Hosted Zones). 
    - an **Outbound Endpoint** forwards *VPC-originated* queries out to your *on-prem DNS* resolvers.
    - both Inbound & Outbound endpoint sit inside the Central Hub VPC & they are typically private subnet.


### VPC (Virtual Private Cloud)

**[#6 pop]**

#### Basics for Networking
- *Networking layers*: 
  - **Layer 3 (Network)** = IP addresses and routing — gets a packet to the right *machine*, no notion of ports; 
  - **Layer 4 (Transport)** = TCP/UDP and port numbers — gets a packet to the right *process* on that machine; 
  - **Layer 7 (Application)** = HTTP/HTTPS and above, where a request carries meaning like URL paths, headers, and hostnames. 
  - This is the shorthand the exam uses to distinguish tools by what they can see and act on: an NLB/Network Firewall/Shield Standard (L3/4) only ever sees IP:port, while an ALB/API Gateway/AWS WAF (L7) can route or filter on URL path, hostname, or request content that a Layer 4 tool never touches.
- **CIDR**: Classless Inter-Domain Routing, the method for allocating/writing IP ranges.
  - Format: `base IP/subnet mask`, e.g. `192.168.0.0/26` = 64 addresses, i.e `192.168.0.0` to `192.168.0.63`; `/32` = 1 IP, `/0` = all IPs.
  - More examples: `192.168.0.0/24` would have range of `192.168.0.0` to `192.168.0.255` (256 IPs). `192.168.0.0/16` would have range of `192.168.0.0` to `192.168.255.255` (65,536 IPs).
  - Used in security group rules, NACL rules, VPC/subnet sizing.
- **Private IPv4 ranges (RFC1918)**: 
  1. `10.0.0.0/8` [max: `10.255.255.255`, 16 mil IPs], 
  2. `172.16.0.0/12` (AWS's default VPC range) [max: `172.31.255.255` (20 bits), 1 mil IPs] 
  3. `192.168.0.0/16` [max: `192.168.255.255`], 
  4. everything else is public/internet-routable.

#### VPC Basics
- **VPC sizing**:
  - Up to *5 VPCs per region* (soft limit); each VPC can have up to **5 CIDR blocks**, each between `/28` (16 IPs) and `/16` (65,536 IPs); only private IPv4 ranges are allowed.
  - 1 VPC can have up to 200 subnets
  - A VPC's CIDR should *never overlap* another network you'll connect it to (peering, on-prem).
  - Every new AWS account has a *default VPC* with internet connectivity, and new EC2 instances launch into it if no subnet is specified.
- **Subnets**: *tied* to a *single AZ*, each with its own CIDR carved from the VPC range; public (route table sends 0.0.0.0/0 to an Internet Gateway) vs private (no such route).
  - 1 CIDR block can have many subnets.
  - Count of all subnets from the CIDR blocks of 1 VPC <= 200.
  - AWS *reserves 5 IPs per subnet*: **first 4 + last 1**; e.g. for `10.0.0.0/24`: `.0` network address, `.1` VPC router, `.2` DNS, `.3` reserved for future use, `.255` broadcast (unsupported but reserved).
    - So a `/27` (32 IPs) only nets 27 usable, not enough if you need 29; use `/26` instead.
- **Route Tables — the concept**: 
  - 1 subnet maps to 1 Route Table (RT) exactly (the VPC's default "main" route table, unless a custom one is explicitly associated); 
  - each row is `destination CIDR → target` (e.g. `0.0.0.0/0 → igw-xxxx`). 
  - Every RT has a built-in `local` route (can't be edited or deleted) that routes traffic between resources inside the VPC's own CIDR. So the rows you actually configure only matter for traffic *leaving* the VPC.
  - By default, a RT is attached to a subnet and its custom rows are only consulted for outbound traffic. *Inbound traffic* from the internet *doesn't need RT*: the *IGW does 1:1 NAT (public IP → instance's private IP)* before the packet needs routing, so the implicit `local` route alone delivers it.
    - AWS also lets you attach a RT to an IGW/VGW instead (**Ingress Routing**), to force *inbound* traffic through a *network appliance (firewall, IDS)* before it reaches your subnets. But this is opt-in, not the default path.
  - When more than one row could match a packet's destination, AWS always picks the **most specific (longest-prefix) match** . 
    - a Gateway VPC Endpoint's route (a specific AWS-service prefix, e.g. all of S3's IP ranges) silently overrides a table's default `0.0.0.0/0 → IGW` row for that traffic, without you ever touching the default row.
- **Internet Gateway (IGW)**: horizontally scaled, redundant, HA; lets VPC resources *reach in & out* the internet.
  - Exactly *1 IGW -> 1 VPC* ; created separately and attached.
  - *RT* must also *route 0.0.0.0/0* (and `::/0` for IPv6) to *IGW*.
- **Bastion Host**: a public-subnet EC2 used to SSH into private-subnet instances.
  - Its SG must allow inbound 22 from a restricted CIDR (e.g. your corporate IP), and the private instances' SGs must allow the bastion's SG/private IP.
  - RT needs no updates because boths EC2 are in VPC. They are reachable via private IP.
  - Default NACL no update (as it allows all inbound & outbound). But *custom NACL* need to ALLOW inbound TCP 22 & ephemeral ports range.


#### NAT
- **NAT (Network Address Translation) — the concept**: NAT rewrites the source IP (and port) of outbound packets to its own public IP before sending them out, then un-rewrites the reply back to the originating private IP. Net effect: *private subnet instances* can initiate *outbound connections* (e.g. pull OS updates, call an external API). The internet can't initiate a connection back in — *one-way*, by construction
  - This is why a NAT device sits in a **public subnet** (it needs its own route to the Internet Gateway) while the *private subnet's route table* points `0.0.0.0/0` at the NAT device instead of at the IGW.
  - 1 public subnet -> 1 NAT
  - Don't confuse this with a *Bastion Host* (above): a bastion lets *inbound* SSH/RDP reach private instances; NAT only ever carries *outbound* traffic. They solve opposite directions of the same "private subnet has no direct internet path" problem.
- AWS gives you three ways to run the NAT device itself — trade-off is managed/simple vs cheaper/flexible:
  - **NAT Gateway**: AWS-managed appliance, the default choice on the exam and in practice.
    - *Highly available within its AZ* only — it doesn't fail over across AZs, so best practice is *one NAT Gateway per AZ* (each AZ's subnets route to their own local NAT Gateway). 
      - This isn't a gap in the product: if an AZ goes down, every instance that would've used that AZ's NAT Gateway is down too, so there's nothing left needing outbound internet.
    - Scales automatically up to *100 Gbps*, uses an *Elastic IP as its public-facing address*, billed per-hour plus per-GB processed.
    - No security group to manage (translation-only, nothing to configure) and it can't double as a bastion (it doesn't accept inbound connections at all).
  - **NAT Instance**: a regular EC2 instance running NAT software — the old, manual way, effectively legacy (AMI's standard support ended Dec 2020).
    - You manage it like any EC2 instance: pick the instance type (bandwidth = whatever that instance type can push), patch it, and script your own failover if it dies (AWS won't do this for you).
    - Must *disable Source/Destination Check* on the instance — normally EC2 drops any packet whose source/dest IP isn't its own, but a NAT instance is deliberately forwarding *other* instances' traffic, so that check has to be turned off.
    - Upside over NAT Gateway: it's a real EC2 instance with a security group, so it can also be *locked down* and *reused* as a *bastion* host.
  - **Regional NAT Gateway (RNAT)**: a newer variant attached to the **whole VPC** rather than one AZ/subnet. 
    - brings its own route tables, 
    - does *not need a public subnet*, and 
    - automatically extends coverage as you add AZs.

#### VPC security
- **NACL Primer**:
  - **Ephemeral port**: When a client *initiates* a connection, though, it doesn't use a fixed port for itself — the *OS* hands it a temporary, randomly chosen an *ephemeral port* (range 1024–65535 & is not used by other programs) just for that one conversation, freed up again once the connection ends. So a request to a web server looks like `client_IP:54321 → server_IP:443`, and the reply comes back `server_IP:443 → client_IP:54321` — same ephemeral port, because that's how the reply finds its way back to the exact process that asked.
  - *Stateful vs stateless*:  
    - A **stateful** firewall inspects the request as it goes by and keeps a note keyed on that 4-tuple *("connection X just went out to Y")* — when the reply packet comes back, it's matched against that note and let through automatically, no separate rule needed. 
    - A **stateless** firewall keeps no memory of anything — every single packet, in either direction, is checked against the rule list from scratch as if it were the first one it's ever seen. So with a stateless filter, an *outbound request* and its *inbound reply* are two *unrelated events* that *both need* their own *explicit rule*, or the reply gets dropped even though the firewall itself let the request out moments earlier.
  - *TCP vs UDP statefulness*: the port addressing above is identical for both protocols, but what a stateful device is actually tracking differs. 
    - *TCP* is connection-oriented — a *handshake (SYN/SYN-ACK/ACK) opens it* and a *FIN/FIN-ACK closes* it, so the *firewall* has real protocol signals marking the note's start and end. 
    - *UDP* is connectionless — *no handshake, no close signal*. So a "UDP connection" in a stateful firewall's table is a pseudo-session it invents: it sees an outbound UDP packet, creates a temporary entry keyed on the 4-tuple, allows a *matching reply* for some *idle timeout* (e.g. 30s to a few minutes), then just expires the entry since nothing ever signals end of session.
- **NACLs** vs *Security Groups*
  - *Comparison table*:
    | Feature | **NACL** | Security Group |
    |---|---|---|
    | State | Stateless | Stateful |
    | Scope | Subnet-level | Instance-level |
    | Rule types | Allow + deny rules | Allow rules only |
    | Return traffic | Not tracked — must be explicitly allowed | Auto-allowed |
    | Rule numbering/evaluation | Numbered 1–32766, evaluated lowest-first, first-match-wins | all rules evaluated |
    | Default behavior | Default NACL allows everything; new custom NACLs deny everything by default | Deny all inbound, allow all outbound |
    | Unmatched traffic | Final `*` rule denies unmatched traffic | N/A |
  - Because a *Security Group is stateful*, no ephemeral-port rule needed. Can't even see/target ephemeral ports in an SG rule.
  - Because a *NACL is stateless*, it has no memory of the request, so the reply has to be explicitly permitted as if it were a brand-new, unrelated packet. Since it's arriving on whatever ephemeral port the client picked, the rule has to open the *whole* ephemeral range (1024–65535), not just one port. Concretely, for a client hitting a server on port 443: the **server-side NACL** needs inbound allow 443 (from the client) *and* outbound allow 1024–65535 (to the client); the **client-side NACL** needs outbound allow 443 (to the server) *and* inbound allow 1024–65535 (from the server). Miss any one of those four rules and the connection breaks in a way that's easy to misdiagnose, since the "request" half often works fine while only the "reply" half silently gets dropped.


- **VPC Flow Logs**: capture IP traffic metadata (not payload) at the VPC, subnet, or ENI level; also capture traffic for AWS-managed interfaces (ELB, RDS, ElastiCache, Redshift, WorkSpaces, NAT Gateway, Transit Gateway).
  - Need an IAM role with `logs:CreateLogGroup`/`CreateLogStream`/`PutLogEvents` to publish to CloudWatch Logs (can also go to S3 or Kinesis Data Firehose).
  - Key fields are `srcaddr`/`dstaddr` (problem IPs), `srcport`/`dstport` (problem ports), and `action` (ACCEPT/REJECT) — use the action field to tell apart a NACL block (inbound REJECT, or inbound ACCEPT + outbound REJECT since NACL is stateless) from a security group block (any REJECT on a stateful hop).
  - Inbound connection log: INBOUND accept but OUTBOUND reject -> NACL issue
  - Outbound connection log: OUTBOUND accept but INBOUND reject -> NACL issue
  - Query flow logs via Athena (over S3) or CloudWatch Logs Insights.

- **VPC Traffic Mirroring**: copies inbound/outbound traffic from source ENIs to a target (ENI or Network Load Balancer, same or peered VPC) 
  - Use case: 
    1. content inspection, 
    2. threat monitoring, or 
    3. troubleshooting via your own security appliances.

- **AWS Network Firewall**: protects an entire VPC end-to-end (VPC-to-VPC, outbound to internet, inbound from internet, to/from Direct Connect & Site-to-Site VPN) at Layer 3–7, 
  - built **internally** on *Gateway Load Balancer*.
  - Supports: 
    1. thousands of rules (IP/port, protocol, stateful domain lists, regex pattern matching), 
    2. allow/drop/alert actions, 
    3. intrusion-prevention-style active flow inspection, 
    4. logs to S3/CloudWatch/Firehose; 
  - *Centrally* managed *cross-account* via AWS **Firewall Manager**.
  - Complements narrower tools: NACLs, security groups, AWS WAF (app-layer request filtering), AWS Shield/Shield Advanced (DDoS).

#### Connecting VPCs
- **VPC Peering**: privately connects two VPCs so they behave as one network; requires *non-overlapping CIDRs*; *not transitive* (must be created pairwise for every pair that needs to talk).
  - *Peering* works **cross-account** and **cross-region**; route tables in every peered VPC's subnets must be updated.
  - A security group in a peered VPC can be referenced directly (including cross-account, same region).
  - **Not transitive** - with example: if VPC A peers with VPC B, and VPC B peers with VPC C, A and C *cannot* talk to each other through B — even though B can reach both. It never extends through a peered VPC to reach a third one. 
    - Why, mechanically: each *peering connection's routes* live only in the *route tables* of the *two VPCs* on that connection. B's RT has entries pointing at A and C, but A's route table only has an entry for B's CIDR and C's RT has only entry to B. A & C route tables have never been updated to support peering.
    - Visual rep — two separate peering connections (pcx-AB, pcx-BC), each with its own routes; there's no pcx-AC, so no path from A to C exists at all:
      ```
        VPC A                    VPC B                    VPC C
      10.0.0.0/16              10.1.0.0/16              10.2.0.0/16
      +--------+   pcx-AB    +--------+    pcx-BC     +--------+
      |        |=============|        |=============|        |
      |  RT:   |             |  RT:   |             |  RT:   |
      |  ->B   |             |  ->A   |             |  ->B   |
      |        |             |  ->C   |             |        |
      +--------+             +--------+             +--------+
           ^                                              ^
           |___________________ no route ________________|
                       (no pcx-AC exists)
      ```
  - *"Pairwise" means*: for every *pair* of VPCs that needs to talk directly, you must create a separate, dedicated peering connection between exactly those two. 
    - For 3 VPCs that all need to talk to each other, that's 3 connections (A-B, B-C, A-C); for 4 VPCs, that's 6 (every combination of 2). 
    - peering doesn't scale well past a handful of VPCs — the number of connections grows quadratically 
    - **Transit Gateway** exists to solve this issue (a hub-and-spoke design where every VPC connects once to the hub, and the hub *does* route between them).
  
- **VPC Endpoints (AWS PrivateLink)**: connect to *AWS services* over the *private AWS network* instead of the public internet — redundant, horizontally scaled, *remove* the need for an *IGW/NAT/public IP*.
  - Two types: *Gateway Endpoints* & *Interface Endpoints*
  | | **Gateway Endpoints** | **Interface Endpoints** |
    |---|---|---|
    | Services | **S3 and DynamoDB** only | most other AWS services |
    | Cost | *Free* | \$/hour + \$/GB |
    | Mechanism | must be set as a *route table target* | *provisions an ENI* with a private IP as the entry point |
    | Security group | none | needed |
    | Exam guidance | prefer by default/on the exam | — |
  - Prefer an *Interface Endpoint* specifically when *access* is needed from:
    1. *on-premises* via Direct Connect/VPN, 
    2. a *different VPC*, or 
    3. a *different region*.
  - **Peering vs. Endpoints**: Peering gives a VPC private access to *another VPC's resources* (any protocol/port); an Endpoint gives a VPC private access to an *AWS service's API* (S3, DynamoDB, etc.), not to another VPC.

- **Site-to-Site VPN**: fast, cheap encrypted hybrid link 
  - **!!Popular on Exam!!**
  - *on-premises* network (a data center, office) to a *VPC* over an *encrypted IPsec* tunnel that still traverses the *public internet*.
  - Use cases: 
    1. faster, i.e. hours to set up vs. DX's month+ lead time; 
    2. often used as DX's backup/failover path; 
    3. extend on-prem to AWS VPC; 
    4. low/moderate bandwidth usages
  - Require 2 things:
    1. a **Virtual Private Gateway (VGW)** on the AWS side. This is AWS's real endpoint, attached to the VPC, customizable *(Autonomous System Number) ASN* — the ID number a network uses to identify itself in *BGP (Border Gateway Protocol)* route exchange. *Not transitive*.
    2. a **Customer Gateway (CGW)** (not real AWS infra, just AWS's config pointing at your actual on-prem device — software/hardware, needs a public/NAT'd IP) connected over the public internet, IPsec-encrypted.
  - CGW can have 2 conditions:
    1. CGW has a public IP
    2. CGW is private. Thus, have to use company NAT to hook up with CGW.
  - Must enable **Route Propagation** in the route table for the VGW; open ICMP inbound if you need to ping EC2 from on-prem.
  - Not like VPC peering because this crosses internet
  - **AWS VPN CloudHub**: 
    - low-cost **hub-and-spoke** VPN model — *multiple CGW* share *one central VGW* (the hub), so sites/nodes (spokes) can reach each other *transitively* through it
    - unlike **Site-to-Site** which is point-to-point and non-transitive 
    - for primary/secondary connectivity between sites (still goes over the public internet).
- **Direct Connect (DX)**: a dedicated **private** physical connection from *on-prem to a VPC* (via a Virtual Private Gateway) 
  - Connection is not encrypted by default (combine with VPN for IPsec encryption over DX), 
  - supports both public (e.g. S3) and private (EC2) resources on the same connection, IPv4 & IPv6.
  - Connection types: 
    1. **Dedicated DX** (1 Gbps–*400 Gbps*, physical port, ordered via AWS then completed by a DX Partner) or 
    2. **Hosted DX** (50 Mbps–*25 Gbps*, via a DX Partner, capacity adjustable on demand).
  - *Setup* lead time often *1+ month*, so a *Site-to-Site VPN* is the common *interim/backup* connection.
  - **Direct Connect Gateway** is required to reach VPCs in multiple regions (same account) over one DX connection.
  - Resiliency: 
    - single connections at multiple location = high resiliency; 
    - multiple connections across multiple locations = maximum resiliency.
- **Transit Gateway**: *regional hub-and-spoke resource* for *transitive peering* across **thousands** of *VPCs, VPNs, and Direct Connect Gateways* at once — solves the VPC Peering non-transitivity problem at scale.
  - Can be peered *cross-region* and shared *cross-account* via AWS *Resource Access Manager* (RAM); 
  - RTs limit which attachments can reach each other; 
  - the only AWS networking construct supporting *IP Multicast*.
  - **Transit Gateway vs VPN CloudHub**: Transit Gateway is a *general-purpose* regional hub for *VPCs, VPNs, and DX Gateways alike*, while VPN CloudHub is a *VPN-only*, *low-cost* hub-and-spoke built from *multiple CGWs terminating on one VGW* — no VPC/DX attachment support, no RAM sharing.
  - **ECMP (Equal-Cost Multi-Path routing)**: with a Transit Gateway, *multiple* Site-to-Site VPN tunnels to the same destination can be *combined* for *higher aggregate bandwidth* (a single VPN-to-VGW tunnel caps around 1.25 Gbps; VPN-to-Transit-Gateway with ECMP scales roughly *linearly per tunnel* pair).
    - Can have multiple tunnel to Transit Gateway to increase bandwidth.
- **Connectivity services compared** — what connects a VPC to what, side by side:
  | Service | Connects VPC to | Transitive? | Encrypted? | Bandwidth | Setup time | Notes |
  |---|---|---|---|---|---|---|
  | Internet Gateway | Public internet | N/A | No | — | Fast | 1:1 with VPC; needs a `0.0.0.0/0` route |
  | NAT Gateway / Instance | Internet, outbound only | N/A | No | Gateway: scales up to 100 Gbps; Instance: capped by instance type | Fast | Lets private-subnet instances initiate outbound traffic only |
  | Egress-only IGW | Internet, outbound only (IPv6) | N/A | No | — | Fast | IPv6 equivalent of a NAT Gateway |
  | VPC Peering | Another VPC | No — pairwise only | No (private AWS backbone) | — | Fast | Non-overlapping CIDRs required; scales quadratically |
  | VPC Endpoints (PrivateLink) | An AWS service's API | N/A | N/A (private AWS network) | — | Fast | Gateway (S3/DynamoDB, free) vs Interface (most services, ENI + $/hr + $/GB) |
  | Site-to-Site VPN | On-premises network | No (unless via CloudHub or Transit Gateway) | Yes (IPsec) | ~1.25 Gbps per tunnel (to a VGW) | Hours | Over the public internet; VGW (AWS side) + CGW (on-prem side) |
  | AWS VPN CloudHub | Multiple on-prem sites, to each other | Yes (via shared VGW hub) | Yes (IPsec) | — | Hours | Low-cost hub-and-spoke, still over the public internet |
  | Direct Connect | On-premises network | No (unless via Direct Connect Gateway) | No by default (pair with VPN) | Dedicated: 1 Gbps–400 Gbps; Hosted: 50 Mbps–25 Gbps, adjustable on demand | 1+ month | Dedicated private physical line, via a VGW |
  | Transit Gateway | Many **VPCs, VPNs, DX** | Yes | Depends on attachment | Aggregates multiple VPN tunnels via ECMP for higher combined bandwidth | Fast | Regional hub-and-spoke; solves peering's non-transitivity at scale |



#### Misc Topics on VPCs
- **IPv6 in a VPC**: IPv4 can never be disabled for a VPC/subnet; IPv6 can be added for dual-stack operation, and every IPv6 address in AWS is public/internet-routable (no private IPv6 range).
  - If you can't launch an instance, it's an exhausted IPv4 subnet, not IPv6 (create a new IPv4 CIDR).
  - **Egress-only Internet Gateway**: the IPv6 equivalent of a NAT Gateway + IGW. 
    - IPv6 instances can use this to get outbound internet in private subnet. No longer need NAT + public subnet.
    - Let instances initiate outbound IPv6 connections while blocking inbound-initiated ones; 
    - Route tables must be updated (target `::/0` to it in the private subnet).
- **Networking cost notes**: 
  - These *traffic cost* money:
    1. Between AZs
    2. Between Regions
    3. Internet
    4. Elastic IP
  - a NAT Gateway's hourly + per-GB charge for the same path.
  - traffic into AWS is free;
  - same-AZ traffic over private IP is free 
  - prefer *private IPs* and *same-AZ* placement for *savings* (at the cost of availability).
  - A *Gateway VPC Endpoint* to S3/DynamoDB is *free*
- Exam tests heavily: 
  1. designing multi-tier VPC architectures, 
  2. choosing connectivity option based on requirements (security, speed, cost, setup time), and 
  3. reading VPC Flow Logs to diagnose SG vs NACL blocks.

### CloudFront

**[#7 pop]**

- CDN: content is *cached* at hundreds of global Points of Presence (edge locations/regional edge caches), improving read *performance* and user experience; built-in *DDoS* protection (globally distributed) plus integration with AWS *Shield* and *WAF*.
- Use case: global content delivery, reducing load on origin servers, DDoS mitigation (works with AWS Shield).
- **Origins**: 
  1. **S3 bucket** (distributes/caches files, can also upload through CloudFront, secured with **Origin Access Control/OAC** + a bucket policy so only CloudFront can reach the private bucket over the AWS private network); 
  2. **VPC Origin** (delivers content from apps in private subnets — a *private ALB/NLB/EC2* instance — with no need to expose them publicly); 
  3. **Custom Origin (HTTP)** (an S3 static website — bucket enabled as a website first — or any public HTTP backend like a public ALB).
- **Public-network origin security**: *non-VPC-origin's SG* must allow CloudFront's published *edge-location public IPs*; for an ALB origin, the *ALB* itself must be *public* but the EC2 instances behind it can stay private (SG allows the ALB's SG only).
- **CloudFront vs S3 Cross-Region Replication**:

  | | CloudFront | S3 CR Repl |
  |---|---|---|
  | Scope | Global edge network (hundreds of PoPs) | Per-region (specific replica regions you configure) |
  | Update freshness | TTL-based cache (can lag up to ~a day) | Near-real-time replication |
  | Replica type | Cached copy of origin content | Full, independent read-only replica |
  | Best fit | Static content that must be available everywhere | Dynamic content needing low latency in a handful of regions |
- **Geo Restriction**: *allowlist* (only approved countries) or *blocklist* (banned countries), country determined via a 3rd-party Geo-IP database
  - use case: *copyright*/*licensing* law compliance.
- **Cache Invalidations**: updating the origin doesn't refresh edge caches until the TTL expires; force a full (`*`) or partial (`/images/*`) refresh with a CloudFront Invalidation to bypass the TTL immediately.
- Signed URLs/Cookies for private content distribution.


### AWS Global Accelerator
- **!! Popular in exams !!**
- Improves global performance by routing traffic onto the AWS internal network as early as possible, instead of the public internet's unpredictable hops.
- Assigns **2 static Anycast IPs** (announced from multiple edge locations; clients route to the nearest one) that forward traffic over the AWS backbone to your app (Elastic IP, EC2, ALB, or NLB — public or private).
- **Consistent performance**: routes to the lowest-latency healthy endpoint with fast regional failover; no client-side caching issues since the IP never changes.
- **Health checks**: continuously checks app health and reroutes on failure in well under a minute — a strong DR fit.
- **Security**: only the 2 Anycast IPs need allowlisting; DDoS-protected via AWS Shield.
- **vs CloudFront**: both ride the AWS edge network and integrate with Shield. CloudFront caches HTTP(S) content at the edge. Global Accelerator proxies packets (no caching) for TCP/UDP apps — better for non-HTTP cases (gaming, IoT, VoIP) and for HTTP cases needing static IPs or fast regional failover.

### API Gateway

**[#15 pop]**

- Managed API front door (REST/HTTP/WebSocket APIs) — build a *serverless REST API* with Lambda + API Gateway, no infrastructure to manage; 
- supports: 
  1. API versioning (v1, v2), 
  2. multiple environments (dev/test/prod), 
  3. authentication/authorization, API keys, 
  4. request throttling, 
  5. response caching
  6. Swagger/OpenAPI import for quick API definition & SDK generation 
  7. request/response transformation & validation
- **Integrations**: 
  1. **Lambda Function** (invoke a function — the classic way to expose a serverless REST API), 
  2. **HTTP** (expose an existing HTTP backend — internal on-prem API, an ALB — adding rate limiting, caching, auth, API keys in front of it), 
  3. **AWS Service** (expose any AWS API directly, e.g. start a Step Functions execution or post to SQS/Kinesis Data Streams — adds auth, public exposure, and rate control in front of a raw AWS API call).
- **Endpoint types**: 
  1. **Edge-Optimized** (default) — requests routed through CloudFront edge locations for lower latency, but the API Gateway itself still lives in one region — for global clients. 
  2. **Regional** — for clients in the same region; can be manually paired with your own CloudFront distribution for more control over caching. 
  3. **Private** — reachable only from your VPC via an interface VPC endpoint (ENI), access controlled with a resource policy.
- **Security**: 
  - user authentication via: (i) IAM roles - internal applications, (ii) Cognito - external/mobile users, or (iii) a Custom Authorizer - your own auth logic, e.g. validate a JWT. 
  - Custom domain + HTTPS via an ACM certificate 
    - for Edge-Optimized endpoints the cert must be in **us-east-1**; 
    - for Regional endpoints cert must be in the API Gateway's own region; 
  - a CNAME or Alias record in Route 53 completes the setup.

---

## 5. Application Integration & Messaging

### Application communication patterns
- **Synchronous** (direct app-to-app calls) can break under sudden traffic spikes. **Asynchronous/event-based** (app-to-queue-to-app) decouples producer and consumer so each scales independently — via SQS (queue), SNS (pub/sub), or Kinesis (streaming).

### SQS (Simple Queue Service)

**[#8 pop]**

- **!!Popular Exam Question!!**
- Oldest AWS messaging offering (10+ years), fully managed, *decouples applications* (i.e. producers/consumers)
- Producers `SendMessage` (up to 256KB — despite an older 1024KB figure sometimes cited, current limit is 256KB) into the queue. Messages are **persisted** until a consumer explicitly deletes it; 
- Consumers poll (receive up to 10 messages at a time), process, then call `DeleteMessage`.
- *1 queue, 1 consumer* model. To have multiple consumers, use SNS to publish to multiple queues. Thus, multiple consumers.
- Many producers can send messages to 1 queue meant for 1 consumer.
- Use case: 
  1. Decoupling microservices
  2. Buffering requests to smooth out spiky traffic
  3. Fault tolerant database writing (avoid losing transactions)
  4. Long running process

#### SQS mechanics
- **Message Visibility Timeout**: once a *consumer polls* a message, it becomes *invisible* to other consumers for the timeout period. Timeout period default *30s*, i.e. the consumer has 30s to finish processing. 
  - If not processed/deleted in time it becomes visible again and gets redelivered (processed twice) — a consumer can call `ChangeMessageVisibility` for *more time*. 
  - Too-high a timeout means slow reprocessing after a consumer crash; too-low a timeout causes duplicate processing.
- **Long Polling**: a `ReceiveMessage` call optionally waits (`WaitTimeSeconds`, 1–20s, 20s recommended) for a message to arrive rather than returning empty immediately. configurable at the queue or API-call level. 
  - Helps to reduce: 
    1. API call count 
    2. Consumer cost
    3. Latency;
- **Security** knobs: 
  1. in-flight encryption via the HTTPS API, 
  2. at-rest encryption via KMS, or client-side encryption if you want full control; 
  3. IAM policies regulate API access; 
  4. *SQS Access Policies* (like S3 bucket policies) enable *cross-account* access or let *another* service (SNS, S3, etc.) write to the queue.

#### Types of Queues
- Two types: Standard & FIFO. Comparisons:

  | | **Standard Queue** | **FIFO Queue** |
  |---|---|---|
  | Throughput | unlimited | 300 msg/s (3,000 msg/s with *batching*). 10 msg per batch. |
  | Ordering | best-effort (can arrive out of order) | strict — but only *within* a Message Group ID (mandatory parameter); avoid consumers waiting on sequential messages, since some messages may be sequential but others need not be |
  | Delivery | *at-least-once* (occasional duplicates) | exactly-once (via a Deduplication ID) |
  | Retention | default 4 days (max 14 days) | default 4 days (max 14 days) |
  | Latency | <10ms publish/receive | <10ms publish/receive |
  | Naming | any name | must end with `*.fifo` |

#### SQS Scaling & Reliability
- **Scaling consumers**:
  - **!!Popular exam question!!**
  - *multiple consumers* (EC2/Lambda) can *poll* the same queue in *parallel* to increase processing throughput (at-least-once delivery + best-effort ordering still apply)
  - an *ASG* can *scale consumer* count off a *CloudWatch alarm* on the `ApproximateNumberOfMessages` queue-length metric. 
  - SQS as a *buffer* in front of a *database write* path smooths out load spikes to avoid *overwhelming RDS/Aurora/DynamoDB* directly.
- **Dead-Letter Queue (DLQ)** for failed message handling. Messages that repeatedly fail processing get redirected there after a max-receive threshold.

#### When to Use What

- **EventBridge vs SQS vs SNS**: use case comparison (in practice they compose — EventBridge often dispatches *to* SNS or SQS as a destination):

  | | EventBridge | SNS | SQS |
  |---|---|---|---|
  | Role | Event router/switchboard | Pub/sub fan-out | Durable buffer/queue |
  | Best for | Routing events from many AWS services/SaaS partners to multiple targets via content-based filtering (event patterns) | Simple fan-out to a fixed set of subscribers you define (SQS, Lambda, email, HTTP) | Decoupling producer/consumer with backpressure and retry (DLQ) |
  | Extras | Schema Registry; cross-account event aggregation onto one bus | — | — |


### SNS (Simple Notification Service)

**[#20 pop]**

- Pub/sub messaging: a producer publishes once to an SNS **topic**; every subscriber receives a copy 
  - subscriber types include *SQS*, *Lambda*, Kinesis Data *Firehose*, *email*, *SMS/mobile* push, and *HTTP(S) endpoints*. 
  - **12.5M subscriptions/topic, 100k topics/account**
- Many AWS services can publish directly to SNS. Publishers: *CloudWatch Alarms*, AWS *Budgets*, *Auto Scaling* notifications, *S3 Events,* CloudFormation state changes, *DMS*, *RDS* Events, *DynamoDB*, *Lambda*, etc..
- Subscriptions are created via SNS. Filter policies can be created when subscription is being created.
- *Publishing*: 
  1. **Topic Publish** (SDK: create topic → create subscription(s) → publish) 
  2. **Direct Publish** (*mobile* SDK: create platform application → platform endpoint → publish — works with Google GCM, Apple APNS, Amazon ADM).
- **Security**: 
  - same model as SQS — in-flight (HTTPS), at-rest (KMS), client-side encryption; 
  - IAM policies for API access; 
  - *SNS Access Policies* (like S3 bucket policies) for *cross-account* access or letting a *service* (e.g. S3) publish to the topic.
- **Fan-out pattern**: 
  - How it works:
    ```
                        +------------+
                    +-->|  SQS: A    |--> Consumer A
                    |   +------------+
    Producer  +-----------+
    --------->| SNS Topic |
              +-----------+
                    |   +------------+
                    +-->|  SQS: B    |--> Consumer B
                    |   +------------+
                    |   +------------+
                    +-->|  SQS: C    |--> Consumer C
                        +------------+
    ```
  - Common use: 
    1. one *S3 event* rule per (event type, prefix) combination — to fan the same S3 event out to *multiple SQS queues/Lambda* functions, route it through an SNS topic first. 
    2. SNS can also feed Kinesis Data *Firehose* to *land data* in *S3/Redshift/OpenSearch/any Firehose destination*.
- **FIFO Topic**: 
  - same FIFO semantics as SQS FIFO (*ordering* by *Message Group ID*, *deduplication* via *Dedup ID* or *content-based* dedup)
  - same throughput limits as SQS FIFO, i.e. *300 msg/s* or *3,000 msg/s with batching*. 10 msg per batch.
  - subscribers can be SQS Standard or FIFO queues. 
  - Combine an SNS FIFO topic fanned out to multiple SQS FIFO queues when you need fan-out + ordering + deduplication together.
- **Message Filtering**: a *JSON filter policy* on a subscription *restricts* which published messages that subscriber receives (matched against message attributes, e.g. `State: Placed` vs `Cancelled` vs `Declined`)
  - a subscription *without filter* policy *receives every* message.

### Amazon Kinesis Data Streams
- Collects and stores streaming data in real time from producers (apps, IoT devices, Kinesis Agent) for consumers (custom apps, Lambda, Data Firehose, Managed Flink) to process.
- Retention up to 365 days; consumers can replay within that window; data can't be deleted early. Records up to 1MiB; ordering guaranteed only within the same **Partition Key**.
- Security: at-rest KMS encryption, in-flight HTTPS.
- KPL and KCL are the recommended SDKs for producers/consumers.
- **Capacity modes**: **Provisioned** — choose shard count, each shard = 1MB/s in / 2MB/s out, scale manually, billed per shard-hour. **On-demand** — no capacity planning, default 4MB/s in / 4,000 records/s, auto-scales on the observed 30-day peak, billed per stream-hour + data volume.
- Records are read via a shard iterator; data flushes based on buffer size or interval.

- **SQS vs SNS vs Kinesis** quick contrast:

  | | SQS | SNS | Kinesis |
  |---|---|---|---|
  | Model | Consumers pull data | Pushes to up to 12.5M subscribers (pub/sub) | Pull-based |
  | Persistence | Deleted once consumed | Data not persisted (lost if delivery fails) | Replayable; data expires after N days |
  | Consumers | Unlimited consumers | Integrates with SQS for fan-out | Standard: 2MB/s per shard; Enhanced Fan-Out: 2MB/s per shard *per consumer* |
  | Throughput | No throughput provisioning | No throughput provisioning | Provisioned or on-demand capacity |
  | Ordering | Only on FIFO queues | FIFO available via SQS FIFO subscribers | At the shard (partition key) level |
  | Other | Supports per-message delay | — | Built for real-time big data/analytics/ETL |


### Amazon Data Firehose (formerly Kinesis Data Firehose)
- Fully managed, serverless, auto-scaling near-real-time (buffers by size/time before flushing) delivery into destinations: AWS (S3, Redshift, OpenSearch), 3rd-party (Splunk, MongoDB, Datadog, New Relic), or a custom HTTP endpoint.
  - Records up to 1MB; supports CSV/JSON/Parquet/Avro/raw text/binary; can convert to Parquet/ORC and compress (gzip/snappy); can invoke Lambda for mid-pipeline transforms (e.g. CSV→JSON); failed/all records can back up to S3.
- **vs Kinesis Data Streams**:

  | | Kinesis Data Streams | Data Firehose |
  |---|---|---|
  | Consumer code | You write producer/consumer code | Fully managed delivery pipeline (no consumer code) |
  | Latency | True real-time | Near-real-time (buffers before flushing) |
  | Storage | Stores data up to 365 days | Doesn't store data itself |
  | Replay | Replayable | No replay capability |

### Other messaging services

In the 'Additional Notes',  see the section 'Additional Messaging Services'.

### Amazon EventBridge (formerly CloudWatch Events)

**[#21 popular]**

- Best for **routing events** from many *AWS services/SaaS partners* to multiple *targets via content-based filtering* (event patterns)
- Serverless event bus: 
  - **Schedule** rules run cron-like jobs (e.g. hourly → trigger a Lambda); 
  - **Event Pattern** rules react to a service doing something (e.g. an IAM root sign-in event → notify via SNS email). 
    - Sources include *EC2 state* changes, CodeBuild results, *S3 events*, *Trusted Advisor* findings, *CloudTrail* (any API call), or a schedule/cron; 
    - events are JSON, optionally filtered before dispatch to *destinations* across: 
      1. compute (Lambda, Batch, ECS Task), 
      2. integration (SQS, SNS, Kinesis Data Streams), 
      3. orchestration (Step Functions, CodePipeline, CodeBuild), and 
      4. maintenance (SSM, EC2 Actions).
- **Event buses**: 
  - 3 types:
    1. a **Default** bus receives events from *AWS services*; 
    2. a **Partner** bus receives events from AWS *SaaS partners* (Zendesk, Datadog); 
    3. **Custom** buses receive events from your *own applications*. 
  - Buses can be shared *cross-account* via a *resource-based policy* (e.g. to aggregate every account in an Organization's events into one central bus). 
  - Events sent to a bus can be **archived** (all or filtered, indefinitely or for a set period) and later **replayed**.
- **Schema Registry**: EventBridge can *infer/version* the JSON *schema of events* flowing through a bus and *generate code* bindings that know the data shape in advance.
- *Auditing pattern (example)*: 
  - CloudTrail logs any API call (e.g. a `DeleteTable`) → EventBridge rule matches it → alerts via SNS 
  - a general "intercept any API call" pattern, also usable for IAM `AssumeRole` events or `AuthorizeSecurityGroupIngress` (someone opened an inbound SG rule).


### Step Functions
- Builds a serverless **visual workflow** (state machine) to orchestrate Lambda and other steps — sequences, parallel branches, conditions, timeouts, retries, and human-approval steps.
- Can integrate with EC2, ECS, on-prem servers, API Gateway, SQS, and more.
- AWS's answer to Airflow/Temporal — workflow orchestration.
- Use cases: order fulfillment, data pipelines, web app workflows, multi-step business logic.

> **Also in this domain (lower exam frequency)**: Amazon MQ, SQS/SNS→Lambda retry mechanics detail, SES, Pinpoint — see the companion Additional Topics guide. Serverless Architecture Patterns are covered under Solutions Architecture Patterns (§9).

---

## 6. Identity, Access & Governance

### IAM (Identity and Access Management)

**[#11 pop]**

- *Core concepts*: Users, Groups, Roles, Policies (JSON), Managed vs Inline policies. IAM is a **global service** (not region-scoped). *Groups* only contain *users* (never other groups); a *user* can belong to *multiple groups* or none.
- **Policy JSON structure**: 
  ```json
  {
    "Version": "2012-10-17",
    "Id": "<OptionalPolicyId>",
    "Statement": [
      {
        "Sid": "<OptionalStatementId>",
        "Effect": "<Allow/Deny>",
        "Principal": { "AWS": "arn:aws:iam::123456789012:root" },
        "Action": ["s3:GetObject", "s3:PutObject"],
        "Resource": ["arn:aws:s3:::my-bucket/*"],
        "Condition": { "IpAddress": { "aws:SourceIp": "203.0.113.0/24" } }
      }
    ]
  }
  ```
- **Roles vs Users**: Use *roles* for *EC2/Lambda/ECS* to access other *AWS services* — never hardcode access keys in code or instances.
- **Cross-account access**: IAM roles with trust policies let one account *assume a role* in *another* (used heavily in multi-account setups).
- **Policy evaluation logic**: **Explicit Deny > Explicit Allow > Default Deny**. **SCPs** (Organizations) set the *max permission boundary*; IAM policies operate within that.
- **STS (Security Token Service)**: Temporary credentials via `AssumeRole`, used for *federation* and *cross-account* access.
- *Identity Federation*: *SAML 2.0* for corporate *directories*, *Cognito* for web/mobile apps, IAM Identity Center (SSO) for *workforce access across accounts*.
- *MFA*: password (something you know) + security device (something you own); protects the root account and IAM users — if a password is stolen/hacked, the account stays safe. 
  - Device options: 
    1. virtual MFA (Google Authenticator/Authy — supports multiple tokens on one device), 
    2. Universal 2nd Factor security key (e.g. YubiKey — supports multiple root/IAM users on a single key), 
    3. hardware key fob (incl. a GovCloud-specific fob).
- *Password policy*: min length, required character types, allow self-service password changes, expiration, prevent re-use.
- *Access methods*: AWS Management *Console* (password + MFA), *CLI* and *SDK* (both protected by access keys — Access Key ID ≈ username, Secret Access Key ≈ password). Access keys are secret and self-managed; never share them.
- **Audit tools**: 
  1. IAM *Credentials Report* (*account*-level — lists every user and the status of their credentials) vs 
  2. IAM *Access Advisor* (*user*-level — shows service permissions granted to a user and when each was last used, so you can right-size/trim policies).
- Exam tests: 
  1. least privilege, 
  2. when to use a role vs a user, 
  3. policy troubleshooting (*explicit deny* wins).

### AWS Organizations & Control Tower
- **Organizations**: a global service managing multiple AWS accounts. The account that creates it becomes the **management account**; every other account is a **member account** (one org each). **Consolidated Billing** gives one payment method, volume discounts, and shared RI/Savings Plan benefits across accounts. An API automates account creation.
- **Organizational Units (OUs)**: accounts and nested OUs sit under a Root OU beneath the management account — commonly organized by Business Unit, Environment (Prod/Dev/Test), or Project. Multi-account (vs. one account with many VPCs) benefits: consistent tagging, org-wide CloudTrail centralized to one account, centralized CloudWatch Logs, cross-account admin roles.
- **Service Control Policies (SCPs)**: JSON policies attached to an OU/account restricting what its Users/Roles can do (guardrails, not grants) — no implicit allow; an explicit Allow must exist through every OU in the path. SCPs never apply to the management account. A Deny anywhere in the chain blocks it; an "Allowlist strategy" starts from Allow-all and adds Denies, a "Blocklist strategy" grants only specific Allows instead of `FullAWSAccess`.
- **Tag Policies**: standardize tag keys/values org-wide, support Cost Allocation Tags and ABAC, and can flag non-compliant tags (not untagged resources) to EventBridge.
- **Control Tower**: automated, best-practice setup for a secure multi-account environment, built on Organizations. **Guardrails** are **Preventive** (SCPs, e.g. restrict regions) or **Detective** (Config rules, e.g. flag untagged resources), which can trigger SNS or Lambda for remediation.
- Use case: large enterprises separating prod/dev/sandbox accounts with centralized governance.

### AWS IAM Identity Center (successor to AWS Single Sign-On)
- One login (SSO) for every AWS account in an Organization, business apps (Salesforce, Box, Slack, Microsoft 365, Dropbox), any SAML 2.0 app, and EC2 Windows instances. Identities live in the built-in store or sync from a 3rd-party IdP (AD, OneLogin, Okta) — AWS Managed Microsoft AD works out of the box; self-managed on-prem AD needs a two-way trust or an AD Connector.
- **Multi-Account Permissions**: a **Permission Set** is a named bundle of IAM policies assigned to users/groups — the same set (e.g. `ReadOnlyAccess`) can apply across several accounts, provisioning consistent IAM roles everywhere.
- **Application Assignments**: SSO access to SAML 2.0 apps via URLs/certs/metadata.
- **ABAC**: fine-grained permissions from user attributes (cost center, title, locale) instead of per-user rules — change access by changing attributes.

### Amazon Cognito
- Gives web/mobile app users an identity to log in and (optionally) access AWS resources directly — exam triggers: "hundreds of users," "mobile users," "SAML/social login" (vs IAM, for internal/console users).
- **Cognito User Pools (CUP)**: a serverless user directory for sign-up/sign-in — username/email+password, password reset, MFA, and federated logins (Facebook, Google, SAML, OIDC, another User Pool). Integrates with API Gateway (token validation) and ALB (auth before forwarding).
- **Cognito Identity Pools (Federated Identities)**: exchanges a login for **temporary AWS credentials**, letting users hit S3/DynamoDB directly or via API Gateway. IAM policies can be customized per `user_id` (e.g. row-level DynamoDB security via `dynamodb:LeadingKeys`); default roles exist for authenticated vs guest users.
- Use case: a mobile app storing files in a user's own S3 prefix, or restricting DynamoDB rows per user, without a backend in the loop.

---

## 7. Security

### Why Encryption? (the three flavors, seen throughout AWS)
- **Encryption in flight (TLS/SSL)**: encrypted client-side before sending, decrypted server-side after receiving, over HTTPS — prevents man-in-the-middle attacks.
- **Server-side encryption at rest**: data is encrypted after the server receives it and decrypted before it's sent back, using a data key whose keys the server can reach — exactly what KMS provides.
- **Client-side encryption**: the client encrypts before sending; the server never has decrypt access — only a client with the key can. Can use envelope encryption; works against any storage backend, not just AWS-native encryption.

### AWS KMS (Key Management Service)

**[#12 pop]**

- Whenever you hear "encryption" for an AWS service, it's most likely backed by KMS — AWS manages the encryption keys for you (contrast with *CloudHSM*, where AWS only manages the hardware and you own the keys entirely). 
  - Fully integrated with IAM for authorization; auditable via CloudTrail; 
  - seamlessly integrated into most AWS services (EBS, S3, RDS, SSM, ...). 
  - *Never store secrets in plaintext*, especially in code — encrypt them via the KMS API (SDK/CLI) and store only the ciphertext in code/environment variables.
- **KMS Keys** (renamed from "Customer Master Key"): 
  1. **Symmetric (AES-256)** — a *single key* used to both encrypt and decrypt; used by every AWS-integrated service; you never get the key material unencrypted, only via KMS API calls. 
  2. **Asymmetric (RSA & ECC key pairs)** — a *public key (encrypt)* + *private key (decrypt)*, also usable for sign/verify; the public key is downloadable, the private key is never exposed — for encryption/verification done outside AWS by callers who can't call the KMS API.
- **Use case**: Compliance requirements needing *audit trails on key usage* → SSE-KMS.
- **Types of keys & cost**: 
  1. AWS Owned Keys (free — SSE-S3, SSE-SQS, SSE-DynamoDB default key, invisible to you). 
  2. AWS Managed Key (free — named `aws/service-name`, e.g. `aws/rds`, `aws/ebs`). 
  3. Customer Managed Keys, created or imported (**$1/month** each) + $0.03 per 10,000 API calls to KMS.
- **Automatic key rotation**: 
  - AWS-managed keys rotate automatically every year (not configurable). 
  - Customer-managed keys support automatic (must be enabled) and on-demand rotation. 
    - *Imported* key material only supports *manual* rotation (via a key alias).
- **KMS Multi-Region Keys**: 
  - *identical* keys in *multiple regions* sharing the *same key ID* and *key material* (one Primary + Replica keys, kept in sync) 
  - encrypt in one region, decrypt in another, with no re-encryption or cross-region API calls needed; 
  - *not a single global key* — each replica is still managed independently. 
  - Use cases: 
    1. global client-side encryption, 
    2. encrypting *DynamoDB Global Tables* or *Aurora Global Database* attributes client-side so each region's clients get low-latency local KMS calls (e.g. via the Amazon DynamoDB Encryption Client or AWS Encryption SDK). This also lets you protect specific fields from even the database admins.
- *Key Policies*: control access to a KMS key, similar in shape to S3 bucket policies — but unlike IAM alone, you *cannot control access* to a *KMS key* without a key *policy* (no policy = no access, other than via the default). 
  1. The **Default Key Policy** grants the root user  complete access. Auto-created if you don't supply one.
  2. A **Custom Key Policy** defines exactly which users/roles can use or administer the key, and is required for cross-account key access.

#### KMS global/cross-acc cases
- **Copying EBS snapshots across regions**: 
  1. source volume/snapshot encrypted with KMS Key A in region 1 → 
  2. `ReEncrypt` with KMS Key B while copying the snapshot into region 2 → 
  3. new volume in region 2 uses Key B.
- **Copying EBS snapshots across accounts**: 
  1) create a snapshot encrypted with your own customer-managed key (CMK); 
  2) attach a KMS *key policy* authorizing the *target account/role* (`kms:Decrypt`, `kms:CreateGrant`, scoped via conditions like `kms:ViaService`/`kms:CallerAccount`); 
  3) share the encrypted snapshot with the target account; 
  4) in the *target account*, *copy* the snapshot, *re-encrypting* it with a CMK in that account; 
  5) create a volume from the copied snapshot.
- **AMI sharing encrypted via KMS**: 
  1. the source AMI is encrypted with a KMS key in the source account 
  2. add a *Launch Permission* on the AMI for the *target account* 
  3. *share the KMS key(s)* used to encrypt the underlying snapshot with the *target* account/role 
  4. the target account's IAM role/user needs `DescribeKey`, `ReEncrypt*`, `CreateGrant`, `Decrypt` *permissions* 
  5. when *launching* an EC2 instance from the *shared AMI*, the *target* account can optionally specify a *new KMS key* of its own to re-encrypt the resulting volumes.
- **S3 replication + encryption**: 
  - *unencrypted* objects and *SSE-S3*-encrypted (Server-Side Encryption -> SSE) objects replicate by *default*;
  - *SSE-C* (customer-provided-key) objects *can* be replicated; 
  - *SSE-KMS* objects require explicitly:
    1. *enabling KMS replication* support, 
    2. specifying the *destination KMS key*, 
    3. updating that *key policy*, and 
      1. granting the *replication IAM role* `kms:Decrypt` on the *source* key 
      2. grant *replication IAM role* `kms:Encrypt` on the *destination* key (watch for KMS throttling — request a Service Quota increase if needed).
  - *Multi-region KMS keys* can be used, but S3 currently treats *each region's* replica as an *independent key* (still decrypts then re-encrypts, rather than truly reusing the same key material across the copy).
- **SSE-S3** (AWS-managed keys) vs **SSE-KMS** (customer-managed, auditable via CloudTrail, has API call limits/throttling to consider) vs **SSE-C** (customer-provided keys).


### AWS Secrets Manager (as a secrets-rotation service)
- Purpose-built for secrets: forces rotation every X days, auto-generates new values on rotation (via a background Lambda), integrates directly with RDS (MySQL, PostgreSQL, Aurora), and encrypts everything with KMS.
- Mainly used for RDS credentials, though it can store any secret.
- **Multi-Region Secrets**: replicates a secret to secondary regions, kept in sync with the primary; a replica can be promoted to standalone.
- Use cases: multi-region apps, DR, multi-region databases.

### AWS Certificate Manager (ACM)
- Provisions, manages, and deploys TLS certs for in-flight encryption (HTTPS) — supports public and private certs; public certs are free and auto-renew.
- Integrates with ELB (CLB/ALB/NLB), CloudFront, and API Gateway.
- **Requesting a public certificate**: list domain names (FQDN or wildcard), choose validation (DNS via Route 53 CNAME, preferred; or email to WHOIS contacts), wait a few hours. ACM-issued certs auto-renew, sending expiration events via EventBridge 45 days out by default.
- **Importing a certificate**: no auto-renewal — you must re-import before expiry; AWS Config's `acm-certificate-expiration-check` rule flags certs nearing expiry.
- **Region requirements**: ALB needs the cert in its own region. CloudFront (and Edge-Optimized API Gateway, which routes through CloudFront) needs the cert in **us-east-1**. Regional API Gateway needs the cert imported into API Gateway in the API's own region. Finish with a Route 53 CNAME or (better) Alias record.

### AWS WAF (Web Application Firewall)

**[#25 pop]**

- Protects web applications from common **Layer 7 (HTTP)** exploits. Deploys onto: (i) *ALB*, (ii) *API Gateway*, (iii) *CloudFront*, (iv) *AppSync GraphQL APIs* and (v) *Cognito User Pools*.
  - not Layer 4 (TCP/UDP), which *AWS Shield/Network Firewall* handle instead.
- **Web ACL (Web Access Control List) Rules**: 
  1. IP Set (up to 10,000 IPs per rule — chain multiple rules for more), 
  2. rules matching *HTTP headers/body/URI* strings (protects against SQL injection and XSS), 
  3. size constraints, 
  4. *Geo-Match* (block specific countries), and 
  5. *Rate*-based rules (count request occurrences per client — the core building block for DDoS protection at the app layer). 
- Web ACLs are *Regional*. Except when attached to *CloudFront*, where *ACLs are global*. 
- A **Rule Group** is a reusable *bundle* of rules you can attach to multiple *Web ACLs*.
- *WAF* does NOT support the *Network Load Balancer* (Layer 4)
  - To mitigate: pair *AWS Global Accelerator* (for a fixed IP in front of the app) with WAF attached to an *ALB instead of NLB*, to get both a static IP and Layer-7 filtering. Lose Layer 4 routing.
  ```
  ✓ workaround:      Client ─▶ Global Accelerator ─▶ ALB (L7, WAF attached) ─▶ Targets
                                (static/fixed IP)      (Layer-7 filtering)
  ```
  - To keep NLB & WAF in the architecture:
    1. Put ALB + WAF behind NLB
    2. Put Cloudfront + WAF in front of NLB

### AWS Shield
- Protects against DDoS (many requests at once).
- **Shield Standard**: free, active by default for every customer, covers common Layer 3/4 attacks (SYN/UDP floods, reflection).
- **Shield Advanced**: paid ($3,000/month per org), covers EC2/ELB/CloudFront/Global Accelerator/Route 53 against sophisticated attacks, gives 24/7 access to the DDoS Response Team, protects against usage-fee spikes from an attack, and auto-deploys WAF rules for Layer 7 mitigation.

### Amazon GuardDuty
- Intelligent threat detection using ML, anomaly detection, and 3rd-party threat intel — one-click enable (30-day trial), no agents needed for the core feature.
- Input sources: CloudTrail Management/S3 Data Events, VPC Flow Logs, DNS Logs, plus optional EKS Audit Logs, RDS/Aurora login activity, EBS, Lambda network activity, extra S3 Data Events.
- Has a dedicated finding type for crypto-mining compromise.
- Findings can trigger EventBridge rules to Lambda or SNS for automated response.

### Additional Topics

You can find additional topics in "Additional" markdown doc, which covers `CloudHSM`, `Firewall Manager`, `Inspector` & `Macie`.

---

## 8. Monitoring, Management & DevOps

### CloudWatch

**[#23 pop]**

- Use case: triggering Auto Scaling, alerting on thresholds, centralized logging.
- **Metrics**: 
  - a variable to monitor (e.g. `CPUUtilization`, `NetworkIn`), scoped to a namespace, with up to 30 **Dimensions** (attributes like instance ID/environment) and a timestamp; 
  - CloudWatch provides metrics for every AWS service out of the box, 
  - you can publish **Custom Metrics** (e.g. RAM usage, which isn't tracked by default). 
  - Dashboards visualize metrics.
- **CloudWatch Metric Streams**: continually streams metrics near-real-time to a *destination* (Kinesis Data Firehose → *S3/Redshift/OpenSearch*, or a 3rd-party like *Datadog/Dynatrace/New Relic/Splunk/Sumo Logic*), with *optional filtering* to a subset of metrics.
- **CloudWatch Logs**: organized into **Log Groups** (usually one per application) containing **Log Streams** (one per instance/log file/container); 
  - configurable *expiration* (never, or 1 day–10 years); 
  - *encrypted* by default, or with your own KMS key. 
  - Sources: SDK, the (legacy) CloudWatch Logs Agent, the CloudWatch Unified Agent, Elastic Beanstalk, ECS, Lambda, VPC Flow Logs, API Gateway, CloudTrail (filtered), Route 53 (DNS query logs). 
  - Can be sent onward to *S3* (export), Kinesis Data Streams, Kinesis Data Firehose, Lambda, or *OpenSearch*.
  - **CloudWatch Logs Agent vs Unified Agent**: 
    - the (old) Logs Agent only pushes to CloudWatch Logs. 
    - The **Unified Agent** additionally collects system-level metrics: CPU active/guest/idle/system/user/steal, *disk* free/used/total + IO, *RAM* free/inactive/used/total/cached, Netstat *TCP/UDP* connections, *Processes*, Swap Space 
      - none of which are in EC2's out-of-the-box disk/CPU/network metrics
      - supports centralized configuration via SSM Parameter Store; 
      - works on EC2 or on-prem servers.
  - **CloudWatch Logs Insights**: a purpose-built query language to *search/analyze* log data already in CloudWatch Logs.
    - *auto-discovers* fields from AWS services and JSON logs, 
    - can fetch fields/filter/aggregate/sort/limit, 
    - *save* queries to dashboards, and 
    - query *multiple Log Groups* across *different AWS accounts* at once.
  - **S3 Export** (via `CreateExportTask`) takes up to 12 hours for data to become exportable — *NOT real-time or near-real-time*; use **Logs Subscriptions** instead for that.
  - **Logs Subscriptions**: *real-time (via Lambda)* or *near-real-time (via Kinesis Data Firehose)* log event delivery to Lambda, Kinesis Data Streams, Kinesis Data Firehose, or OpenSearch, filtered by a **Subscription Filter**. 
  - **Cross-Account Subscriptions** send log events to a Kinesis stream in a different account (via a destination access policy + an assumable IAM role) — the basis for *multi-account/multi-region* log aggregation (CloudWatch Logs → Subscription Filter → Kinesis Data Streams → Kinesis Data Firehose → S3, near-real-time).
- **CloudWatch Alarms**: trigger notifications for a single metric based on sampling/%/max/min/etc thresholds; 
  - states are *OK, INSUFFICIENT_DATA, ALARM*; 
  - **Period** is the evaluation window in seconds (10s, 30s, or multiples of 60s). 
  - Targets (action from alarms): (i) stop/terminate/reboot/recover an EC2 instance, (ii) trigger an Auto Scaling action, or (iii) notify an *SNS* topic (from which almost anything downstream is possible). 
  - **Composite Alarms** monitor the state of *multiple other alarms with AND/OR logic*. Helps reduce alarm noise from correlated failures. Alarms can also be created directly from a *CloudWatch Logs Metric Filter*. 
  - *EC2 Instance Recovery (use case)*: a `StatusCheckFailed_System` alarm can *automatically recover* the instance onto new hardware, preserving private/public/Elastic IP, metadata, and placement group. Test an alarm via `aws cloudwatch set-alarm-state`.
- **CloudWatch Network Synthetic Monitor**: agentless monitoring of **network paths** between: (i) *AWS-hosted apps* and *on-prem*, (ii) testing ICMP/TCP over *Direct Connect* or *Site-to-Site VPN* to detect packet loss/latency/jitter degradation. Publishes results as CloudWatch Metrics.
- **CloudWatch Insights suite**: 
  1. *Container* Insights (metrics/logs from ECS, EKS, Kubernetes-on-EC2, Fargate — needs a containerized CloudWatch Agent for Kubernetes/EKS). 
  2. *Lambda* Insights (system-level metrics — CPU, memory, disk, network — plus diagnostics like cold starts/worker shutdowns for serverless apps, delivered as a Lambda Layer). 
  3. *Contributor* Insights (time-series of *top-N contributors* from any AWS-generated logs, e.g. VPC Flow Logs — finds bad hosts/heaviest network users/most-erroring URLs, via built-in or custom rules). 
  4. *Application* Insights (SageMaker-powered *automated dashboards* surfacing *problems* for EC2-hosted apps on select technologies — Java, .NET, IIS, databases — plus related resources like *EBS/RDS/ELB/ASG/Lambda/SQS/DynamoDB/S3/ECS/EKS/SNS/API Gateway*. Findings/alerts route to *EventBridge* and *SSM OpsCenter*).


### AWS CloudTrail
- Governance/compliance/audit for an account — enabled by default, logging every API call (Console, SDK, CLI, or other AWS services) to CloudWatch Logs and/or S3. A trail covers all regions by default, or one. If a resource is unexpectedly deleted, check CloudTrail first.
- **Event types**: **Management Events** (resource operations, e.g. IAM `AttachRolePolicy`) — logged by default, split into Read/Write. **Data Events** — high-volume, not logged by default: S3 object-level activity and Lambda `Invoke` calls. **Insights Events** — baselines normal Write-event patterns and flags anomalies (bad provisioning, limit hits, IAM bursts, maintenance gaps); surfaces in console, S3, and EventBridge.
- **Retention**: 90 days in CloudTrail itself; for longer, log to S3 and query with Athena.
- CloudTrail = who did what/when (API audit); CloudWatch = performance metrics/logs.

### AWS Config
- Audits **compliance** of AWS resources and tracks config changes over time — e.g. "is any SG open to SSH?", "do my buckets allow public access?" Per-region, but aggregatable across regions/accounts; can alert via SNS and store config data in S3 for Athena.
- **Config Rules**: 75+ AWS-managed rules, or custom rules backed by Lambda. They evaluate on config change and/or schedule, and only **flag** non-compliance — they don't block actions. Pricing: no free tier, $0.003/config item/region + $0.001/rule evaluation/region.
- **Remediation**: auto-remediates via SSM Automation Documents (which can invoke Lambda), with configurable retries.
- **Notifications**: route non-compliance to EventBridge (→ Lambda/SNS/SQS), or send all events to SNS directly.
- **Worked example (an ELB)**: CloudWatch tracks connections/errors; Config tracks SG changes and compliance drift; CloudTrail tracks who changed what.

### CloudFormation
- **Infrastructure as Code**: declarative JSON/YAML templates — describe the resources you want and CloudFormation creates them in the right order, instead of clicking through the console.
- **Benefits**: nothing created manually (reviewable, tagged-per-stack cost visibility, cost estimable from the template); supports scheduled destroy/recreate for dev savings; declarative, so no manual resource ordering; reuses existing templates; supports nearly all AWS resources plus Lambda-backed custom resources.
- Stacks, Change Sets (preview before applying), StackSets (deploy across accounts/regions).
- **Infrastructure Composer**: a visual canvas of a template's resources and their relationships.
- **CloudFormation Service Role**: an IAM role letting CloudFormation build/update/delete stack resources even for users without direct permissions — supports least privilege.
- Use case: repeatable, version-controlled infrastructure.

### AWS Systems Manager (SSM)
- A hybrid (cloud + on-prem) management/ops toolset for EC2, on-prem, and multi-cloud.
- Most features need the **SSM Agent** (pre-installed on Amazon Linux 2, some Ubuntu AMIs) and the right IAM permissions.
- **Session Manager**: secure shell into EC2/on-prem servers without SSH, a bastion, keys, or port 22 open — supports Linux, macOS, Windows; session logs can go to S3/CloudWatch Logs.
- **Run Command**: runs a script/document or single command across multiple instances at once, no SSH needed — output to console or S3/CloudWatch Logs, SNS status notifications, IAM/CloudTrail integrated, invokable via EventBridge.
- **Patch Manager**: automates OS/native-app patching across EC2 and on-prem (Linux, macOS, Windows) — can't patch third-party apps, mostly package-manager-based. Patches on-demand or via **Maintenance Windows**. Requires either `Default Host Configuration Management` (account-wide, low effort) or the `AmazonSSMManagedInstanceCore` IAM policy (more control). Generates a patch-compliance report.
- **Maintenance Windows**: a schedule (+ duration, instances, tasks) for patching, driver updates, or installs.
- **Automation**: simplifies maintenance tasks (restart, create AMI, EBS snapshot) via **Automation Runbooks**, triggered manually, via EventBridge, on a schedule, or by AWS Config remediation.

#### SSM Parameter Store (less important)
- Secure, serverless config/secrets storage, with optional KMS encryption (app sends/receives plaintext; Parameter Store handles encryption after checking IAM). Supports version tracking, EventBridge change notifications, and CloudFormation integration.
- **Hierarchy**: path-style parameters (e.g. `/my-department/my-app/dev/db-url`), retrievable in bulk via `GetParameters`/`GetParametersByPath`. AWS also publishes reference paths (pull a Secrets Manager secret through Parameter Store) and public paths (latest AMI IDs).
- **Standard vs Advanced tiers**: Standard — 10,000 parameters max, 4KB value, no policies, free. Advanced — 100,000 parameters, 8KB value, supports parameter policies, $0.05/parameter/month.
- **Parameter Policies** (Advanced only): `Expiration` (auto-delete, forces rotation), `ExpirationNotification` (EventBridge event before expiry), `NoChangeNotification` (flags un-rotated secrets).

### AWS Backup
- Fully managed, centralized backup across many services (EC2/EBS, S3, RDS/Aurora, DynamoDB, DocumentDB, Neptune, EFS, FSx, Storage Gateway Volume Gateway) — no custom scripts needed. Supports cross-region/account backups and Point-In-Time Recovery.
- **Backup Plans**: define frequency, backup window, cold-storage transition, and retention, then assign resources — backups land in an S3-backed vault. Only assigned resources get backed up.
- **AWS Backup Vault Lock**: enforces WORM on a vault, blocking even the root user from deleting backups or shortening retention.

> **Also relevant (lower exam frequency)**: Amazon Inspector, AWS Firewall Manager, Amazon Macie — see the companion Additional Topics guide (Security section).

---

## 9. Solutions Architecture Patterns (recurring exam scenarios)

**Useful to go over**

- **Stateless web app progression**: 
  1. single public EC2 with an Elastic IP (simple, has downtime) → 
  2. vertical scaling (bigger instance, still has downtime while resizing) → 
  3. horizontal scaling behind Route 53 with multiple public instances (breaks if an instance is swapped and its DNS record is stale/cached) → 
  4. private EC2 instances behind an ELB with health checks and tight security groups (LB is the only public entry point) → 
  5. wrap the private instances in an ASG for self-healing and elasticity → 
  6. span the ASG across ≥2 AZs for disaster tolerance. 
  - Reserve capacity (RIs/Savings Plans) at the ASG's **minimum** size for guaranteed cost savings, since that capacity always runs.
- **Making a stateful web app scale horizontally (3-tier architecture)**: 
  - introduce ELB *sticky sessions* (session affinity) to keep a user's follow-up requests on the same instance — simplest option but can unbalance load. 
  - Alternative: push session state into *user cookies* — keeps the app "stateless" but makes requests heavier and creates a security risk (cookies must be validated, and are capped at 4KB). 
  - Better: 
    - store session state server-side in **ElastiCache** (or DynamoDB as an alternative) so any instance can retrieve any user's session; 
    - store durable user data (address, profile, etc.) in **RDS**; 
    - scale DB reads with **RDS Read Replicas**, optionally adding ElastiCache as a lazy-loading cache in front of RDS to relieve read load further. 
    - Make every tier Multi-AZ (ELB, ASG, ElastiCache, RDS) to survive an AZ failure. 
    - Layer security groups so each tier only accepts traffic from the tier in front of it (LB ← 0.0.0.0/0, EC2 ← LB's SG, ElastiCache/RDS ← EC2's SG) 
    - this is the standard **3-tier architecture**: 
      1. public subnet (ELB), 
      2. private subnet (app instances in an ASG), 
      3. data subnet (ElastiCache + RDS).
- *Storing user-uploaded files (e.g. a WordPress site)*: a single-instance app can store images on its local **EBS** volume, but that breaks once you scale to multiple instances (each instance only sees its own volume).

  The fix for a distributed/multi-instance app is: 
  
  - a shared **EFS** file system mounted by every instance via an ENI in each AZ — reinforces the general EBS (single instance) vs EFS (many instances, shared) distinction.
- **Instantiating applications quickly**: 
  - for EC2: 
    - use a pre-baked **Golden AMI** (all software/OS deps pre-installed) for fast, static launches, 
    - **User Data bootstrap scripts** for dynamic per-instance configuration, or 
    - a *hybrid* of both (this is what Elastic Beanstalk does under the hood). 
  - For RDS and EBS: 
    - restoring from a snapshot gives you a ready-to-use DB (schema + data) or disk (formatted + data) instead of provisioning from scratch.
- **Blocking a client IP address — pick the tool that matches your layer**: 
  - How a bare *public EC2 instance* can block traffic:
    - behind only a Security Group can't block a specific IP -> SGs are allow-only) 
    - a **NACL** on its subnet is the *only native way (deny rule)*. 
  - Behind an *ALB/NLB*, the load balancer terminates the connection: 
    - so a subnet NACL in front of it can't see/block the original client IP at the instance level 
    - attach **AWS WAF** to the ALB instead (WAF doesn't support NLB, since NLB is Layer 4 and WAF is Layer 7). 
  - If CloudFront is in front of everything, its public IPs are what actually reach the NACL/ALB, so blocking at the NACL is not helpful 
- *Highly available single EC2 instance without a load balancer* (e.g. a legacy app that can't run behind an ELB): 
  - put the instance in an ASG with min=max=desired=1 spanning ≥2 AZs, 
    1. add an Elastic IP (EIP) that gets re-attached to whichever instance is currently running, either via: 
      1. EC2 User Data + an EC2 instance role (calls the API to attach the EIP on boot) or 
      2. via a CloudWatch Alarm/Event that triggers a Lambda function to start a standby instance and reattach the EIP on failure. 
    2. Optionally pair with an EBS snapshot taken on the ASG's Terminate lifecycle hook and restored onto the new instance's volume via the Launch lifecycle hook, to preserve local disk state across failover.
- **High Perf Computing** considerations:
  - Data transfer services: Direct Connect (VPC), Snowmobile & Data Sync
  - Compute: CPU & GPU optimized EC2, Spot instances
  - Networking for compute: 
    - EC2 cluster for faster networking between instances
    - Elastic Network Adapter (ENA) - 100 Gbps; also known as enhanced networking
    - Elastic Fabric Adapter (EFA) - Linux only; tightly coupled workload; uses Message Passing Interface (MPI), which bypass Linux OS to reduce latency
  - Storage:
    - Instance-attached storage: EBS (256k IOPS) & Instance Storage (millions IOPS)
    - Network storage: S3, EFS (scale by storage size or provisioned), FSX Lustre (millions IOPS)
  - Automation & Orchestration:
    - AWS Batch: run job on multiple EC2 instances
    - AWS Parallel Cluster: deploy HPC
- **Layered caching for a typical web stack**:

  ```
  client
    │
    ▼
  CloudFront          (edge cache: static/cacheable responses)
    │
    ▼
  API Gateway         (response caching)
    │
    ▼
  App logic           (EC2 / Lambda)
    │
    ▼
  ElastiCache / DAX   (data cache)
    │
    ▼
  RDS / DynamoDB
  ```

  - Each layer trades some staleness/TTL risk for less network hops, less compute, lower cost, and lower latency; 
  - choose how many layers based on how cacheable and how latency-sensitive the data actually is.

### Serverless Architecture Patterns (recurring exam scenarios)
- **Serverless REST API**: 
  ```
  Client 
  |
  v
  API Gateway (REST + HTTPS) → 
  |
  v
  Lambda (business logic) → 
  |
  v
  DynamoDB (CRUD)
  ```
- **Direct-to-AWS mobile access**: 
  - use *Cognito Identity Pools* to hand mobile clients temporary AWS credentials scoped by IAM policy, so they can talk to *S3* (e.g. store/retrieve files in their own prefix) or *DynamoDB* directly
  - bypassing the API Gateway/Lambda hop entirely for simple storage operations while still using API Gateway+Lambda for business logic.
- **High read throughput on static-ish data**: 
  1. add a DAX caching layer between Lambda and DynamoDB for microsecond reads, and/or 
  2. enable API Gateway response caching to avoid re-invoking Lambda for repeated identical requests.
- **Serverless static + dynamic website (e.g. a blog)**: 
  - serve static assets globally via CloudFront in front of a private *S3* bucket, secured with Origin Access Control (OAC) + a bucket policy that only authorizes the CloudFront distribution; 
  - add a serverless REST API (*API Gateway + Lambda + DynamoDB*, no Cognito needed if the API is public) for the dynamic parts; 
  - use *DynamoDB Global Tables* (or Aurora Global Database) so data is served with low latency in every region.
- **Reacting to data changes (e.g. welcome email on signup)**: 
  1. enable DynamoDB Streams on the table → 
  2. trigger a Lambda function (with an IAM role permitting SES) → 
  3. send the email via **Amazon SES**, entirely serverless.
- **Processing uploads (e.g. thumbnail generation)**: 
  1. client uploads via CloudFront (with Transfer Acceleration) to an S3 bucket → 
  2. S3 event triggers a Lambda function → 
  3. Lambda writes a thumbnail to another S3 bucket → 
  4. optionally fan out a notification via SQS/SNS.
- **Microservices**: 
  - split each capability into its own service, potentially with its own architecture/stack & fronted by Route 53 DNS per subdomain 
    - e.g. service1 = ALB+ECS+DynamoDB, service2 = API Gateway+Lambda+ElastiCache, service3 = ELB+ASG+RDS. 
    - Synchronous inter-service calls use API Gateway/Load Balancers; asynchronous calls use SQS/Kinesis/SNS/S3 Lambda triggers. 
  - Challenges: 
    1. per-service creation overhead, 
    2. server density/utilization tuning, 
    3. running multiple versions of multiple services at once, 
    4. client-side integration sprawl
  - serverless patterns mitigate several of the above challenges, e.g.:
    1. API Gateway + Lambda auto-scale and bill per use, 
    2. APIs are easy to clone/reproduce, and 
    3. Swagger-generated SDKs cut client integration work
- **Offloading a non-serverless app's static traffic**: 
  - if an *EC2/ASG-backed* app mostly serves *static*, unchanging files (e.g. software update downloads) that spike unpredictably, put *CloudFront* in front of it 
    - no architecture changes needed, CloudFront caches the static files at the edge and is itself serverless/auto-scaling, so the ASG scales less and you save on EC2, availability, and network bandwidth cost. 
    - A general pattern for making an existing non-serverless app *cheaper* and *more scalable* without a rewrite.

---

## 10. Cost Optimization Concepts

- **Right-sizing** instances based on utilization (Compute Optimizer, Trusted Advisor).
- **S3 storage class transitions** and **lifecycle policies**.
- **Reserved Instances/Savings Plans** for predictable workloads; **Spot** for flexible/fault-tolerant ones.
- **Cost Explorer**: visualize, understand, and manage AWS cost/usage over time; build custom reports; analyze at a high level (total cost/usage across all accounts) or drill down to monthly/hourly/resource-level granularity; get a recommended **Savings Plan** commitment based on the last 60 days of usage (an alternative view to buying Reserved Instances directly); forecast usage up to 18 months ahead based on historical trends.
- **AWS Cost Anomaly Detection**: continuously monitors cost/usage with ML to flag unusual spend (one-time spikes or continuous increases) — no manual thresholds to define; monitor at the level of AWS services, member accounts, cost allocation tags, or cost categories; delivers an anomaly report with root-cause analysis, with individual or daily/weekly-summary alerts via SNS.
- **AWS Budgets** for tracking and alerting on spend against a threshold.
- **Data transfer costs**: same-AZ traffic over a private IP is free; cross-AZ (same region) costs ≈$0.01/GB each way; cross-region and internet egress cost more (e.g. ≈$0.09/GB S3-to-internet in the US) — architecture decisions should minimize unnecessary cross-AZ/region transfer and prefer private IPs; a Gateway VPC Endpoint to S3/DynamoDB is free, vs a NAT Gateway's hourly + per-GB charge for the same path; CloudFront-to-internet is typically slightly cheaper than S3-to-internet directly, on top of its caching benefit.

> **Also relevant (lower exam frequency)**: Outposts, Batch, AppFlow, Amplify, Instance Scheduler, HPC building blocks — see the companion Additional Topics guide's "Specialized / Hybrid Services" section.

---

## 11. AWS Well-Architected Framework (conceptual, tested throughout)

### 6 Pillars
1. Operational Excellence
2. Security
3. Reliability
4. Performance Efficiency
5. Cost Optimization
6. Sustainability
- The 6 pillars are **not trade-offs to balance against each other — they're meant to work as a synergy**. General guiding principles: 
  - stop guessing capacity needs, 
  - test systems at production scale, 
  - automate to make architectural experimentation easier, 
  - allow architectures to evolve with changing requirements, 
  - drive architecture decisions from data, and 
  - improve through "game days" (simulating real conditions, e.g. a flash-sale traffic spike).
- **AWS Well-Architected Tool** (free, in-console): a self-service way to run the same kind of review AWS Solutions Architects perform. The steps:
  1. select a workload, 
  2. answer a structured questionnaire, 
  3. get your answers reviewed against the 6 pillars, and 
  4. receive advice (docs, videos, a generated report, a risk dashboard)

### Trusted Advisor
- No installation needed — a high-level, automated assessment of your AWS account against 6 categories: Cost Optimization, Performance, Security, Fault Tolerance, Service Limits, and Operational Excellence.
- **Support plan tiers**: full set of checks + programmatic access via the AWS Support API require a **Business or Enterprise** support plan (Basic/Developer plans see only a limited core set of checks).


---

