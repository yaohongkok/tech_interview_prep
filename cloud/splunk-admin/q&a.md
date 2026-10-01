# Splunk Admin Interview Q&A

## Table of Contents

1. [Architecture and Sizing](#1-architecture-and-sizing)
2. [Indexer Clusters](#2-indexer-clusters)
3. [Search Head Clusters](#3-search-head-clusters)
4. [Forwarders and Deployment Server](#4-forwarders-and-deployment-server)
5. [Data Onboarding and Parsing](#5-data-onboarding-and-parsing)
6. [Retention, Storage, and Licensing](#6-retention-storage-and-licensing)
7. [Performance Tuning and SPL](#7-performance-tuning-and-spl)
8. [Upgrades and Lifecycle](#8-upgrades-and-lifecycle)
9. [Troubleshooting Scenarios](#9-troubleshooting-scenarios)
10. [Automation and Integration](#10-automation-and-integration)
11. [Senior-Level and Behavioral](#11-senior-level-and-behavioral)

---

## 1. Architecture and Sizing

### Q1. Walk me through the largest Splunk environment you've run end to end.

- State the numbers: daily ingest (GB/TB), indexer count, search head count, sites
- Data paths in: UFs → HFs/indexers, HEC, syslog → HF
- Why it was designed that way (scale, DR, compliance)
- One thing you'd change in hindsight

### Q2. How would you size a new deployment for 2 TB/day with 90 days hot/warm and 1 year total retention?

- Disk ≈ 50% of raw: ~15% compressed rawdata + ~35% index files
- Multiply rawdata by RF, index files by SF
- ~100–300 GB/day per indexer depending on search load → roughly 8–15 indexers
- 90 days on fast storage, rest on cheaper cold/SmartStore
- SH count driven by concurrent users and scheduled searches

### Q3. When would you choose multisite indexer clustering, and what does it cost you?

- Use for DR or multiple data centers
- Configure `site_replication_factor` and `site_search_factor`
- Search affinity keeps searches on local site
- Cost: more storage, cross-site bandwidth, extra complexity

### Q4. What is SmartStore, and when would you use it or avoid it?

- Warm/cold buckets stored in remote object storage (S3); indexers keep a local cache
- Use: long retention, lower storage cost, faster indexer replacement
- Size the cache manager for the common search window
- Avoid: frequent searches over old data (cache misses are slow)

---

## 2. Indexer Clusters

### Q5. Explain replication factor versus search factor. What happens when a peer goes down?

- **RF** = number of bucket copies; **SF** = number of searchable copies
- Peer down → cluster manager starts bucket fixup
- Remaining peers make new copies to restore RF/SF
- Non-searchable copies are made searchable if needed

### Q6. How do you push a config change to cluster peers without a full outage?

- Put the change in `manager-apps` (older: `master-apps`) on the cluster manager
- Run `splunk validate cluster-bundle` first
- Then `splunk apply cluster-bundle`
- Know which changes cause a rolling restart vs. a reload

### Q7. When would you put the cluster in maintenance mode?

- During upgrades or planned peer restarts
- Stops needless bucket fixup while peers are briefly down

---

## 3. Search Head Clusters

### Q8. How does an SHC elect a captain, and what's the minimum sensible member count?

- RAFT-based majority vote
- Minimum 3 members
- Use odd numbers, and plan member placement across sites to keep majority

### Q9. How do you deploy an app to an SHC? What if someone edits config directly on a member?

- Use the deployer: `splunk apply shcluster-bundle`
- Some config replicates between members (UI changes); some doesn't (deployer-pushed files)
- Direct edits cause drift or get overwritten on next push

### Q10. An SHC has a flapping captain and KV store errors. How do you troubleshoot?

- `splunk show shcluster-status` and `splunk show kvstore-status`
- Check network latency between members
- Check clock sync (NTP)
- Resync the bad member (`splunk resync shcluster-replicated-config`, KV store resync)

---

## 4. Forwarders and Deployment Server

### Q11. Universal vs. Heavy Forwarder: when do you use each, and where does parsing happen?

- **UF**: lightweight, default for collecting data, no parsing
- **HF**: routing, filtering, masking, modular inputs/add-ons
- Parsing happens at the first full Splunk instance (HF or indexer)
- Trade-off: HFs use more resources and add a hop

### Q12. How do you structure serverclasses and apps on a Deployment Server for thousands of forwarders?

- Small, single-purpose apps (outputs, inputs per source)
- Serverclasses use whitelists by hostname, IP or OS
- Tune phone-home interval to reduce load
- Scale with a dedicated DS or multiple DSs

### Q13. Why shouldn't the Deployment Server manage indexer peers or SHC members?

- Indexer peers are managed by the cluster manager
- SHC members are managed by the deployer
- Mixing them causes conflicts and inconsistent configs

### Q14. How do you handle forwarder load balancing and prevent data loss?

- Auto load balancing across indexers (`autoLBFrequency`)
- Indexer acknowledgment: `useACK = true`
- Indexer discovery via the cluster manager

---

## 5. Data Onboarding and Parsing

### Q15. Take me through onboarding a new custom log source from request to production.

- Get sample data and requirements
- Test in a dev/test index
- Define sourcetype (`props.conf`/`transforms.conf`)
- Validate line breaking, timestamps, fields
- Map to CIM, document, then promote to production

### Q16. Which `props.conf` settings do you always set for a new sourcetype, and why?

- `LINE_BREAKER` and `SHOULD_LINEMERGE = false`: correct, fast event breaking
- `TIME_PREFIX`, `TIME_FORMAT`, `MAX_TIMESTAMP_LOOKAHEAD`: accurate timestamps
- `TRUNCATE`: cap event size
- `EVENT_BREAKER` on UFs: safe load balancing

### Q17. How would you drop noisy events or mask sensitive data before indexing?

- Drop: transforms routing to `nullQueue`
- Mask: `SEDCMD` or regex transforms
- Must run at the parsing tier (HF or indexer), not on a UF

### Q18. Index-time vs. search-time field extraction: which is the default, and when would you break it?

- Search-time is the default
- Index-time only for specific performance needs
- Cost: more storage, less flexibility (needs reindexing to change)

---

## 6. Retention, Storage, and Licensing

### Q19. How do you control retention for an index?

- `frozenTimePeriodInSecs`: age limit
- `maxTotalDataSizeMB`: size limit
- Volume-level limits too
- Whichever limit hits first rolls data to frozen (deleted or archived)

### Q20. A team's ingest suddenly doubles and you're heading toward a license violation. What do you do?

- Find the source: license usage in `_internal` (`license_usage.log`)
- Short-term: filter or drop the noisy data
- Talk to the data owner about root cause
- Know the license enforcement policy (warnings vs. search blocking)

---

## 7. Performance Tuning and SPL

### Q21. Users say searches are slow. Is it the platform or the search?

- Monitoring Console: indexer/SH load, CPU, I/O
- Job Inspector: where the search spends time
- Check skipped/deferred searches and concurrency limits

### Q22. Rewrite for performance: `index=* error | stats count by host`

- Specify index and sourcetype
- Narrow the time range
- Use `tstats` where possible, e.g. `| tstats count where index=app_logs TERM(error) by host`

### Q23. When would you use `tstats`, accelerated data models, or summary indexing?

- `tstats`: fast queries over indexed fields/metadata
- Data model acceleration: CIM/ES dashboards, costs extra storage
- Summary indexing: pre-computed results for custom reports, cheaper but needs maintenance

### Q24. How do you deal with too many scheduled searches being skipped?

- Stagger cron schedules (avoid everything at `:00`)
- Use schedule windows and priorities
- Fix or retire badly written searches
- Review concurrency limits

---

## 8. Upgrades and Lifecycle

### Q25. What's your upgrade order for a clustered environment, and how do you minimize downtime?

- Order: cluster manager → search heads → peers (rolling/searchable upgrade) → forwarders
- Before: backups, app compatibility checks
- Have a rollback plan

### Q26. Tell me about an upgrade or migration that went wrong. What did you learn?

- Be honest: what happened
- Root cause
- Process changes afterward (checklists, testing, rollback steps)

---

## 9. Troubleshooting Scenarios

### Q27. A source stopped sending data an hour ago. How do you troubleshoot?

- Check forwarder `splunkd.log`
- Search `index=_internal host=<host>`
- Test output connectivity to indexers (port 9997)
- Look for blocked queues in `metrics.log`
- Check if data is landing with wrong timestamp or in the wrong index

### Q28. Events show up with timestamps days in the future. What's going on?

- Timestamp extraction misconfigured
- Wrong timezone (`TZ`)
- `MAX_TIMESTAMP_LOOKAHEAD` picking up the wrong value

### Q29. How do you find out which config file is actually winning for a setting?

- `splunk btool <conf> list --debug`
- Understand config precedence (system/local > app/local > app/default > system/default)

### Q30. Indexing queues are blocked on your indexers. What are the likely causes?

- Slow disk I/O
- Expensive regex or transforms
- Downstream saturation (e.g. indexer can't write fast enough)

---

## 10. Automation and Integration

### Q31. What have you automated around Splunk with Python or the REST API?

- Health checks
- User or app provisioning
- Bulk knowledge-object changes

### Q32. How would you manage Splunk configuration as code?

- Apps in Git repos
- Ansible for installs and upgrades
- CI to validate configs
- Avoid ad-hoc UI changes

### Q33. Have you run Splunk components in containers or Kubernetes?

- Splunk Operator for Kubernetes
- Persistent storage is the main concern for indexers
- Forwarders and search heads suit containers better than indexers

---

## 11. Senior-Level and Behavioral

### Q34. How do you balance onboarding requests from many teams with platform stability and license limits?

- Standard intake process with sizing estimates
- Prioritize by business value
- Set per-team quotas and show back usage

### Q35. Tell me about a time you pushed back on a stakeholder about how they wanted to use Splunk.

- Situation and their request
- Why it was a risk (cost, performance, license)
- Alternative you offered and the outcome

### Q36. How do you document and hand over the platform so you're not a single point of failure?

- Runbooks and architecture diagrams
- Config as code in Git
- Pair work and knowledge-sharing sessions

### Q37. What does your ideal monitoring and alerting setup for Splunk itself look like?

- Monitoring Console in distributed mode
- Alerts on: blocked queues, skipped searches, license usage, disk space, missing forwarders
- Cluster health (RF/SF met) and KV store status
