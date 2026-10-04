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



---


## 12. Old Interview Q&A

### 1. Walk me through what happens from a log line being written to it being searchable.
The UF monitoring the file reads new data (tracking its position in the fishbucket), tags it with host/source/sourcetype/index, and sends it in blocks over TCP 9997 (optionally TLS + indexer acknowledgement) load-balanced across indexers. The first full Splunk instance (HF or indexer) parses it: breaks the stream into events using `LINE_BREAKER`, merges lines if configured, extracts the timestamp into `_time`, and applies index-time transforms (masking, routing, filtering to nullQueue). The indexer then writes the compressed raw data and tsidx files into a hot bucket of the target index and, in a cluster, streams copies to peers per RF/SF. At search time, the SH dispatches the search to indexers, which use tsidx and bloom filters to find matching events in relevant buckets by time range, apply search-time extractions, and return partial results that the SH merges.

### 2. What's the difference between a universal and heavy forwarder? When would you use an HF?
UF is a lightweight agent that forwards unparsed data with minimal resources; it's the default on endpoints. HF is a full Splunk Enterprise instance that parses data. Use an HF when you need to filter/mask/route **before** data leaves a network segment, for modular/API inputs (cloud add-ons, DB Connect), as an intermediate aggregation point for isolated networks, or for syslog aggregation. Downside: more resources, and it moves parsing (so props must live there).

### 3. How would you reduce license usage without losing valuable data?
First measure: license usage by index, sourcetype and host to find top consumers and spikes. Then work with owners: drop low-value events (DEBUG, health checks) with nullQueue transforms or ingest actions on the parsing tier; trim verbose fields (SEDCMD) or unnecessary JSON attributes; convert numeric telemetry to metrics indexes; route bulk/low-value data to cheaper storage (e.g. ingest actions to S3) instead of indexing; fix duplicate ingestion (same file from two inputs, overlapping add-ons). Put governance in place: onboarding requires volume estimates and an owner, and alerts on sudden volume spikes. *(This is my strongest area — use a real example from my governance work.)*

### 4. Events have the wrong timestamp. How do you troubleshoot and fix it?
Confirm with `_indextime - _time` lag and search over all time for events landing in the future/past. Check `_internal` `DateParserVerbose` warnings. Look at the raw event and the sourcetype's props via `btool --debug` on the **parsing tier** (HF if one is in the path). Set explicit `TIME_PREFIX`, `TIME_FORMAT`, `MAX_TIMESTAMP_LOOKAHEAD`, and `TZ` if the source doesn't log a timezone. Test in a dev instance with sample data, deploy, and note that already-indexed events won't change — re-ingest if the data matters.

### 5. Explain RF and SF. What happens when an indexer in a cluster goes down?
RF = copies of the data; SF = searchable copies. With RF=3/SF=2, the cluster tolerates 2 peer losses without data loss. When a peer goes down, the CM notices missing heartbeats, promotes other searchable copies to primary so search continues (possibly with briefly incomplete results), then runs bucket fix-up to re-create copies on remaining peers until RF/SF are met again. For planned work you'd use maintenance mode and `splunk offline` to avoid unnecessary fix-up.

### 6. How do you push config to indexers in a cluster vs forwarders vs a search head cluster?
Indexers: via the cluster manager's `manager-apps` and `splunk apply cluster-bundle`. Forwarders: deployment server with server classes. SHC: deployer's `shcluster/apps` and `splunk apply shcluster-bundle`. Never mix them up (e.g. DS managing peers) and never hand-edit members. Ideally all of these source from Git with CI validation (btool check, AppInspect).

### 7. Where do props.conf settings need to go?
Depends on the phase. Index-time (line breaking, timestamps, TRANSFORMS, SEDCMD) → the first full instance in the path: HF or indexers. Search-time (EXTRACT, REPORT, KV_MODE, FIELDALIAS, LOOKUP) → search heads. `INDEXED_EXTRACTIONS` for structured files and `EVENT_BREAKER` → the UF. Often the simplest safe approach is to deploy the same TA everywhere and let each tier use what applies.

### 8. How do you control who can see which data?
Put data with different audiences into different indexes. Create roles with `srchIndexesAllowed` per index, inherit from `user`, map roles to LDAP/SAML groups so access is managed through the IdP and joiner/mover/leaver processes. Use `srchFilter` only for finer restrictions (less robust than index separation). Audit access with `_audit`. For PII, mask at index time so it never lands in the index at all.

### 9. Users complain that dashboards are slow. What do you do?
Check the Monitoring Console for search head/indexer load and skipped searches. Use the Job Inspector on the dashboard's searches to see where time goes (e.g. `command.search.rawdata` → reading lots of raw events). Typical fixes: add `index=`/`sourcetype=` filters and shorter time ranges, use base searches with post-processing, replace raw searches with `tstats` on accelerated data models, schedule the heavy part as a report and have the dashboard load results, and fix search-time extraction inefficiencies. Platform-side: spread scheduled searches, adjust quotas, add capacity if genuinely saturated.

### 10. How would you design retention for an index holding security logs that must be kept for 1 year searchable and 7 years archived?
`frozenTimePeriodInSecs = 31536000` with `maxTotalDataSizeMB` sized with headroom (so size doesn't freeze data earlier than a year — monitor this), hot/warm on fast storage, cold on cheaper storage, and `coldToFrozenDir` (or SmartStore/object store lifecycle) for the 7-year archive. Document restore procedure (thaw → `splunk rebuild`). Remember retention is bucket-based, so data may live slightly longer than the policy.

### 11. What would you check first on your first week as a Splunk admin?
Inventory: architecture diagram, versions, license vs actual usage, index list with retention and size, forwarder count and versions, which forwarders haven't phoned home. Health: Monitoring Console, blocked queues, skipped searches, disk usage, cluster status (RF/SF met?), expiring certificates. Governance: who has `admin`/`can_delete`, config in Git or not, onboarding process. Then prioritise risks.

### 12. What is the fishbucket?
An internal index (`_thefishbucket`) the forwarder uses to track which files it has read and how far (via a CRC of the file's first bytes plus seek pointer). It prevents re-ingesting data after restarts. Log rotation with identical headers can confuse it → use `crcSalt` or `initCrcLength`. `splunk cmd btprobe` can inspect/reset entries.

### 13. Syslog: send straight to indexers?
Preferably not. UDP is lossy, and restarting an indexer drops data. Better: dedicated syslog servers (syslog-ng/rsyslog) writing to disk with a UF monitoring those files, or SC4S sending to HEC. Gives buffering, sourcetype-by-host/port routing, and decoupled restarts.

### 14. Tell me about a time you had to govern data quality / ingestion. *(behavioural — prepare with STAR)*
> Situation: … Task: … Action: (standards for sourcetype/index naming, onboarding checklist, reviewing requests, spotting a noisy source) … Result: (license saved %, fewer broken dashboards, faster onboarding) …
> Close with: "As an admin I'd automate that governance — Git-managed apps, CI checks with btool, alerts on silent sources and volume spikes."

---


