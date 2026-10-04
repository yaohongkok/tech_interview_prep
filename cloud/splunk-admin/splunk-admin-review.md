# Splunk Admin Interview Prep

## 0. Positioning: user/governance side → admin side

**My honest starting point:** I have used Splunk heavily and helped govern log ingestion (which sources come in, naming, sourcetypes, what is worth indexing), but I didn't have admin permissions on the platform itself.

**How to frame it in the interview:**
- "I've been the *customer* of the Splunk platform team. I know what good ingestion looks like from the consumer side: consistent sourcetypes, correct timestamps, sensible index separation, no noisy data burning license. I now want to own the platform that enforces it."
- Map each governance activity to the admin mechanism behind it (table below). This shows I understand *how* the admins implemented what I asked for.
- Be upfront about hands-on gaps and back it with a lab ([§14](#14-hands-on-lab-plan-do-this-before-the-interview)): "I haven't run a production indexer cluster, but I've built one in a lab with a cluster manager, 3 peers, RF=3/SF=2, and practised a rolling restart and a bundle push."

| What I did as a user/governor | What the admin actually configured |
|---|---|
| Asked for a new log source to be onboarded | `inputs.conf` on UF, deployed via deployment server `serverclass.conf` |
| Agreed on sourcetype/index naming standards | `indexes.conf` on indexers, `sourcetype=` in inputs, `props.conf` stanzas |
| Reported broken timestamps / multi-line events | `props.conf`: `TIME_PREFIX`, `TIME_FORMAT`, `LINE_BREAKER`, `SHOULD_LINEMERGE` |
| Requested dropping noisy debug logs | `props.conf` + `transforms.conf` → `nullQueue` (or ingest actions) |
| Requested masking of PII/tokens | `SEDCMD` or transforms rewriting `_raw` |
| Asked for access to an index | Role in `authorize.conf` with `srchIndexesAllowed`, mapped to an LDAP/SAML group |
| Asked "how long do we keep this?" | `frozenTimePeriodInSecs`, `maxTotalDataSizeMB` per index |
| Complained about slow dashboards | Search concurrency limits, accelerations, scheduler skipped searches |
| License usage reviews | License manager, `license_usage.log` in `_internal` |

---

## 1. Splunk architecture & components

```
Sources: servers/apps, syslog, cloud/APIs
      │
      ▼
Collection tier
  • Universal Forwarder (UF)
  • syslog-ng + UF, or SC4S → HEC
  • Heavy Forwarder (HF) / HEC
      │
      │ 9997 (forwarders) / 8088 (HEC)
      ▼
Indexing tier
  • Indexers (cluster peers)
      ▲
      │ search dispatched, results back
      │
Search tier
  • Search Head(s): standalone or SHC

Management
  • Deployment Server → forwarders
  • Cluster Manager   → indexers
  • Deployer          → SHC members
  • License Manager
  • Monitoring Console
```

| Component | Role |
|---|---|
| **Universal Forwarder (UF)** | Lightweight agent. Collects & forwards. Does **not** parse (except structured data via `INDEXED_EXTRACTIONS`, and `EVENT_BREAKER` for load balancing). No UI, no Python. |
| **Heavy Forwarder (HF)** | Full Splunk instance with forwarding. **Parses** data, so can filter/route/mask before indexing. Used for API inputs (add-ons), syslog aggregation, routing to multiple destinations. |
| **Indexer** | Parses (if not already parsed), indexes, stores data in buckets, and executes the map part of searches. |
| **Search Head (SH)** | UI, dispatches searches to indexers (map-reduce: indexers do the map, SH does the reduce), hosts knowledge objects (dashboards, saved searches, field extractions). |
| **Cluster Manager (CM)** *(formerly "master")* | Coordinates an indexer cluster: replication, bucket fix-ups, config bundle distribution. |
| **Search Head Cluster (SHC)** | ≥3 SHs. A **captain** (elected via RAFT) schedules jobs and coordinates replication of knowledge objects. |
| **Deployer** | Pushes apps/config to SHC members. Not part of the SHC. |
| **Deployment Server (DS)** | Pushes apps to forwarders (and standalone instances). |
| **License Manager** | Central license tracking; other instances are license peers. |
| **Monitoring Console (MC)** | Health dashboards for the whole deployment (indexing rate, queues, search load, KV store, license). |
| **HEC (HTTP Event Collector)** | Token-authenticated HTTP(S) ingestion (default port 8088). Common for cloud/app/container logs. |

**Deployment sizes**
- *Single instance*: everything on one box (labs, small).
- *Distributed*: separate UFs → indexers → SHs.
- *Clustered*: indexer cluster (HA of data) + SHC (HA of search/knowledge objects), optionally **multisite** for DR.

**Terminology changes to know** (Splunk renamed these): master → **manager**, slave → **peer**, `master-apps` → `manager-apps`, `slave-apps` → `peer-apps`. Splunk is now part of Cisco (acquisition completed 2024).

---

## 2. Directory layout & config files

`$SPLUNK_HOME` (usually `/opt/splunk` or `/opt/splunkforwarder`)

```
$SPLUNK_HOME/
├── bin/                     # splunk CLI
├── etc/
│   ├── system/default/      # NEVER edit — overwritten on upgrade
│   ├── system/local/        # instance-wide overrides
│   ├── apps/<app>/default/  # shipped by app author
│   ├── apps/<app>/local/    # your overrides for that app
│   ├── users/<user>/<app>/local/   # private knowledge objects
│   ├── deployment-apps/     # (DS) apps to send to forwarders
│   ├── manager-apps/        # (CM) bundle to push to peers
│   ├── peer-apps/           # (peers) bundle received from CM
│   └── shcluster/apps/      # (deployer) bundle to push to SHC
└── var/lib/splunk/          # index data (default SPLUNK_DB)
```

**Golden rule:** never edit `default/`. Put changes in `local/`, ideally inside a dedicated app (e.g. `org_all_indexes`, `org_uf_base`), so config is versioned, portable and deployable.

### Key .conf files

| File | Purpose | Where it lives |
|---|---|---|
| `inputs.conf` | What to collect (`[monitor://]`, `[tcp://]`, `[udp://]`, `[splunktcp://9997]`, `[http://]`, scripted, WinEventLog) | UF/HF; `splunktcp` on indexers |
| `outputs.conf` | Where to send (`[tcpout:group]`, `server=idx1:9997,idx2:9997`, `useACK`, `indexerDiscovery`) | Forwarders |
| `props.conf` | Per sourcetype/source/host: line breaking, timestamps, extractions, which transforms to call | Parsing tier (HF/indexer) **and** search heads (search-time parts) |
| `transforms.conf` | Regex-based actions: routing, filtering, masking, field extraction, lookups | Same as props |
| `indexes.conf` | Index definitions, paths, retention, size limits, SmartStore volumes | Indexers (+ SH so index names autocomplete) |
| `server.conf` | Clustering, SHC, KV store, SSL, general settings | All |
| `authentication.conf` | Auth method: Splunk native, LDAP, SAML; role mapping | SH |
| `authorize.conf` | Roles, capabilities, index access, search quotas | SH |
| `serverclass.conf` | DS: which clients get which apps | DS |
| `deploymentclient.conf` | Tells a client where its DS is | Clients |
| `limits.conf` | Search concurrency, memory, result limits | SH/indexers |
| `savedsearches.conf` | Reports & alerts | SH |
| `web.conf` | Splunk Web settings (port, SSL) | SH |

### Config precedence (btool is your friend)

- **Global/index-time context** (inputs, outputs, indexes, index-time props): `system/local` > `apps/*/local` > `apps/*/default` > `system/default`. Between apps, precedence is by app directory name in lexicographic (ASCII) order — so naming like `000_org_base` is sometimes used deliberately.
- **App/user (search-time) context**: current user's dir > current app (`local` > `default`) > other apps that export objects globally > `system`.
- Within one file, more specific stanzas win: `[source::...]` > `[host::...]` > `[sourcetype]`.

```bash
splunk btool props list my_sourcetype --debug     # merged result + which file each line came from
splunk btool check                                # syntax check all conf files
splunk btool inputs list --debug | grep monitor
```

**Reload vs restart:** many changes need a `splunk restart`; some can reload via `/debug/refresh` or `splunk reload deploy-server`, `splunk reload index` etc. Index-time props changes need a restart (or bundle push/rolling restart on a cluster).

---

## 3. The data pipeline: index time vs search time

This is the #1 conceptual topic. Know **which phase** a setting belongs to, because that decides **where** to deploy it.

```
Input      ← UF (or first instance)
  │ parsingQueue
  ▼
Parsing    ← HF or indexer
  │ aggQueue
  ▼
Merging    ← HF or indexer
  │ typingQueue
  ▼
Typing     ← HF or indexer
  │ indexQueue
  ▼
Indexing   ← indexer
```

| Phase | What happens | Key settings | Runs on |
|---|---|---|---|
| **Input** | Read data, attach `host`, `source`, `sourcetype`, `index`; character set | `inputs.conf`, `CHARSET` | UF / first Splunk instance |
| **Parsing** | Break stream into lines/events | `LINE_BREAKER`, `TRUNCATE` | First *full* instance: HF or indexer |
| **Merging** | Merge lines into multi-line events; extract timestamp | `SHOULD_LINEMERGE`, `BREAK_ONLY_BEFORE`, `TIME_PREFIX`, `TIME_FORMAT`, `MAX_TIMESTAMP_LOOKAHEAD`, `TZ` | HF / indexer |
| **Typing** | Regex transforms: mask, route, filter, index-time fields. E.g. dropping/modifying events | `SEDCMD`, `TRANSFORMS-*` | HF / indexer |
| **Indexing** | Write raw data (compressed journal) + tsidx files into buckets | `indexes.conf` | Indexer |
| **Search time** | Field extraction and enrichment when searching | `EXTRACT-`, `REPORT-`, `KV_MODE`, `FIELDALIAS-`, `EVAL-`, `LOOKUP-`, tags, eventtypes | Search head |

**Key consequences**
- If data passes through an HF, parsing happens **there**; the indexer does not re-parse it ("cooked" data). So index-time props must go on the HF, not the indexer. Classic gotcha.
- Index-time changes only affect **new** data. Fixing a broken timestamp config won't fix already-indexed events (you'd need to re-ingest).
- Prefer **search-time** extraction: flexible, no reindex, no index bloat. Use index-time fields only when needed for performance (e.g. `tstats` on a field).

### The "Magic 6/8" props for a well-behaved sourcetype (governance favourite)

```ini
# props.conf
[acme:app:json]
SHOULD_LINEMERGE = false
LINE_BREAKER = ([\r\n]+)
# Max bytes per line. Anything longer is cut
# off (and a warning is logged in _internal).
# Default 10000; 0 = unlimited (risky).
TRUNCATE = 10000
# Regex for the text just BEFORE the timestamp.
# Splunk starts reading the timestamp right
# after this match, instead of guessing.
TIME_PREFIX = "timestamp":''
TIME_FORMAT = %Y-%m-%dT%H:%M:%S.%3N%z
MAX_TIMESTAMP_LOOKAHEAD = 30
# optional but good practice
# on UF, for clean load balancing:
EVENT_BREAKER_ENABLE = true
EVENT_BREAKER = ([\r\n]+)
# search time, on SH:
KV_MODE = json
```

> ⚠️ Comments in `.conf` files must be on their own line. A `#` after a value becomes part of the value.

**What "line merging" means:** Splunk builds events in two steps.
1. **Line breaking:** `LINE_BREAKER` (a regex) splits the incoming stream into chunks, which are normally lines.
2. **Line merging:** if `SHOULD_LINEMERGE = true` (the default), Splunk then glues consecutive lines back together into one multi-line event, such as a Java stack trace. By default it starts a new event at any line that contains a date (`BREAK_ONLY_BEFORE_DATE`). You can change that with rules like `BREAK_ONLY_BEFORE` or `MUST_BREAK_AFTER`.

Step 2 runs rules on every line, which is slow, and it is a common reason events get glued together or split wrongly. The best practice is to set `SHOULD_LINEMERGE = false` and make `LINE_BREAKER` produce whole events in one step. For a multi-line log where each event starts with a date:
```ini
SHOULD_LINEMERGE = false
# break only where the next line starts with a date
LINE_BREAKER = ([\r\n]+)(?=\d{4}-\d{2}-\d{2})
```
Only the text in the first capture group is thrown away (here, the newlines). The lookahead keeps the date in the next event.

Why it matters: without explicit settings, Splunk *guesses* line-merging and timestamps, which is CPU-expensive and error-prone (events glued together, wrong `_time`, data "missing" because it's timestamped in the future/past).

### Common index-time recipes

**Drop noisy events (e.g. DEBUG):**
```ini
# props.conf
[acme:app]
TRANSFORMS-drop_debug = drop_debug

# transforms.conf
[drop_debug]
REGEX = \sDEBUG\s
DEST_KEY = queue
FORMAT = nullQueue
```

#### How nullQueue filtering actually works

- **`nullQueue`** is Splunk's "trash bin": a special queue that throws away whatever reaches it. Data dropped there is never indexed, so it **doesn't count against the license**.
- **`indexQueue`** is the normal route. It's the last queue in the pipeline (see §3), and data that reaches it gets written to disk.
- **Each event carries a routing label.** The label is a metadata key called `queue`, and it defaults to `indexQueue`.
- **A transform only changes the label; it doesn't move the event.**
  - `DEST_KEY = queue` means "the thing I'm changing is the routing label".
  - `FORMAT = nullQueue` is the new value.
  - `REGEX` decides whether the transform applies to this event. If the regex doesn't match, the label is left as it is.
- **Transforms run in the order listed**, and each one can overwrite the label set by an earlier one.
- **Only after all transforms have run** does Splunk read the final label and send the event there.

So nothing is "rescued" from the nullQueue. The event never went there. The first transform set its label to `nullQueue`, and a later one changed it back to `indexQueue` before Splunk acted on it.

**Keep only certain events** (label everything as trash, then relabel the ones you want to keep; order matters):
```ini
# props.conf
[acme:app]
TRANSFORMS-filter = setnull, keep_errors

# transforms.conf
# Step 1: REGEX "." matches any event,
# so every event is labelled nullQueue.
[setnull]
REGEX = .
DEST_KEY = queue
FORMAT = nullQueue

# Step 2: events containing ERROR or WARN
# are relabelled indexQueue (kept).
[keep_errors]
REGEX = ERROR|WARN
DEST_KEY = queue
FORMAT = indexQueue
```

Walking three events through it:

| Event | After `setnull` | After `keep_errors` | Result |
|---|---|---|---|
| `... ERROR db timeout` | nullQueue | indexQueue (regex matched) | **Indexed** |
| `... WARN retrying` | nullQueue | indexQueue (regex matched) | **Indexed** |
| `... INFO request ok` | nullQueue | nullQueue (no match, label unchanged) | **Dropped** |

If you reverse the order (`keep_errors, setnull`), `setnull` runs last and overwrites every label with nullQueue, so **everything is dropped**. That's why order matters.

Compare with the "drop DEBUG" recipe above. It only sets the label on matching events, so everything else keeps the default `indexQueue`. Use a **denylist** ("drop X") when most data is useful, and an **allowlist** ("keep only Y", this recipe) when most data is noise.

**Route to a different index:**
```ini
[route_security]
REGEX = auth_failure
DEST_KEY = _MetaData:Index
FORMAT = security
```

**Mask sensitive data:**
```ini
# props.conf
[acme:payments]
SEDCMD-mask_card = s/\d{12}(\d{4})/XXXXXXXXXXXX\1/g
```

**Modern alternative (Enterprise 9.0+):** *Ingest Actions* (UI-based filter/mask/route, can also send to S3). Worth mentioning to show awareness, but know the classic props/transforms way thoroughly.

---

## 4. Getting data in & forwarder management

UF is typically for VMs or bare metal servers. Containers typically is geared towards HECs.

### The flow at a glance
The DS tells the UF what to do. The UF's `inputs.conf` says what to read, its `outputs.conf` says where to send it, and the indexer listens on 9997 and indexes the data.

```
                 ┌─────────────────────────────────────────────┐
                 │  DEPLOYMENT SERVER (DS)  :8089              │
                 │  etc/deployment-apps/                       │
                 │   ├─ org_uf_outputs   (outputs.conf)        │
                 │   └─ acme_web_inputs  (inputs.conf)         │
                 │  serverclass.conf: which hosts → which apps │
                 └───────────────────┬─────────────────────────┘
                                     │ ② UF phones home (phoneHomeIntervalInSecs)
                                     │    downloads apps → restartSplunkd = true
                                     ▼
 ① One-time setup on the host:
   install UF (/opt/splunkforwarder)
   splunk set deploy-poll ds:8089 ──────────────►  (the UF is now a deployment client)

 ┌──────────────────────────────────────────────────────────────────┐
 │  UNIVERSAL FORWARDER (on the log-source host)                    │
 │                                                                  │
 │  ③ inputs.conf: WHAT to collect                                  │
 │     monitor:///var/log/app/app.log  index=app_prod  st=acme:app  │
 │     (the fishbucket tracks read position; crcSalt for rotation)  │
 │                         │                                        │
 │                         ▼                                        │
 │  ④ outputs.conf: WHERE to send it                                │
 │     [tcpout:primary_indexers]                                    │
 │     server = idx1,idx2,idx3:9997  (or indexer discovery via CM)  │
 │     autoLBFrequency = 30   useACK = true                         │
 └─────────────────────────┬────────────────────────────────────────┘
                           │ ⑤ load-balanced over TCP :9997
                           │    (the indexer ACKs, so no data is lost)
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
     ┌───────────┐  ┌───────────┐  ┌───────────┐
     │   idx1    │  │   idx2    │  │   idx3    │   ⑥ inputs.conf on the indexer:
     │ :9997     │  │ :9997     │  │ :9997     │      [splunktcp://9997]
     └─────┬─────┘  └─────┬─────┘  └─────┬─────┘      (no outputs.conf needed)
           └──────────────┼──────────────┘
                          ▼
            ⑦ parse → index → stored in index=app_prod
                          │
                          ▼
                 searchable from the search head


 OTHER WAYS IN (they skip the UF monitor path):
   Syslog devices ──► syslog-ng/rsyslog writes files ──► UF ──► indexers
   Syslog devices ──► SC4S ──► HEC ──► indexers
   Apps / scripts ──► HEC (token, behind a load balancer) ──► indexers
   Cloud APIs (AWS/Azure/O365) ──► TA on a Heavy Forwarder ──► indexers
   K8s containers (stdout) ──► OTel Collector DaemonSet (1 per node) ──► HEC ──► indexers
```

### UF basics
All of these run **on the forwarder host** (the machine whose logs you're collecting), using the UF's own CLI: `$SPLUNK_HOME/bin/splunk`, where `SPLUNK_HOME` is usually `/opt/splunkforwarder`. They write to the UF's local config (`etc/system/local/outputs.conf`, `inputs.conf`, `deploymentclient.conf`). `add forward-server` names the indexer to send to, and `set deploy-poll` names the deployment server to check in with. Both commands point *outward* from the UF. Once the UF is managed by a deployment server, push inputs/outputs as DS apps instead of running CLI commands on each host.

```bash
# install then:
splunk add forward-server idx1.example.com:9997
splunk add monitor /var/log/app/app.log -index app_prod -sourcetype acme:app
splunk list forward-server          # active vs configured-but-inactive
splunk list monitor
splunk list inputstatus             # file read positions
splunk set deploy-poll ds.example.com:8089
```

On indexers: enable receiving on 9997 (`[splunktcp://9997]` or `splunk enable listen 9997`).

### outputs.conf essentials
This lives **on the forwarder** (the sending side). Any Splunk instance that forwards data has one, including UFs, heavy forwarders, and search heads/CM/DS that forward their own `_internal` logs to the indexers. The indexers don't need an outputs.conf to receive; they need an `inputs.conf` `[splunktcp://9997]` stanza. On UFs it's usually pushed as a DS app (e.g. `org_all_forwarder_outputs`), not edited by hand.

```ini
[tcpout]
defaultGroup = primary_indexers

[tcpout:primary_indexers]
server = idx1:9997, idx2:9997, idx3:9997
# indexer acknowledgement -> no data loss on failure
useACK = true
# auto load balancing between indexers
autoLBFrequency = 30
```
With an indexer cluster, prefer **indexer discovery** (forwarders ask the CM for the peer list) so you don't hard-code indexers.

### Deployment server
**The problem:** you have hundreds or thousands of UFs, and you don't want to log into each one to edit `inputs.conf`/`outputs.conf`. Instead, you package config as **apps** on a central deployment server (DS). Each UF (a *deployment client*, pointed there by `set deploy-poll`) regularly **phones home** and downloads whatever apps it's supposed to have.

**serverclass.conf is the mapping:** *which hosts* get *which apps*. A **server class** is a named group of clients.
- `[serverClass:linux_web]` defines a group called `linux_web`.
- `whitelist.0 = web-*.example.com` means clients whose hostname matches `web-*` are in the group (you can add `whitelist.1`, `blacklist.0`, etc.).
- `machineTypesFilter = linux-x86_64` narrows it further to Linux 64-bit hosts only, so a Windows box named `web-01` wouldn't match.
- `[serverClass:linux_web:app:org_uf_outputs]` says members of `linux_web` get the app `org_uf_outputs`, a folder in `etc/deployment-apps/` that holds the `outputs.conf` (where to send data).
- `[serverClass:linux_web:app:acme_web_inputs]` says they also get `acme_web_inputs`, which holds the `inputs.conf` (which web logs to monitor).
- `restartSplunkd = true` restarts the UF after it receives or updates the app. `.conf` changes on a UF only take effect after a restart.

**Net effect:** every Linux web server automatically sends its web logs to the indexers. A new `web-42` host just needs the UF installed and pointed at the DS, and it picks up both apps on its own. To change what's monitored, edit the app once on the DS and run `splunk reload deploy-server`.

**Design pattern:** keep apps small and single-purpose (one for outputs, one per data source) so you can mix and match them across server classes. For example, every server class gets `org_uf_outputs`, but only web servers get `acme_web_inputs`.

```ini
# serverclass.conf on DS
[serverClass:linux_web]
whitelist.0 = web-*.example.com
machineTypesFilter = linux-x86_64

[serverClass:linux_web:app:org_uf_outputs]
restartSplunkd = true
[serverClass:linux_web:app:acme_web_inputs]
restartSplunkd = true
```
- Apps live in `$SPLUNK_HOME/etc/deployment-apps/`. After changes: `splunk reload deploy-server`.
- Clients phone home on an interval (`phoneHomeIntervalInSecs`).
- **Don't** use the DS to manage clustered indexers (use CM) or SHC members (use the deployer).
- Scaling: one DS can handle many thousands of clients; tune phone-home interval for large estates.
- (Newer versions include `whitelist/blacklist` → `allowlist/denylist` naming.)

### Common input types
- `monitor://` files/dirs (tracks position via the **fishbucket** — `_thefishbucket`; `crcSalt = <SOURCE>` to force re-reading rotated files with identical headers; `initCrcLength`).
- `WinEventLog://Security`, `perfmon://`.
- Syslog: best practice is **not** to send syslog directly to indexers (restarts lose UDP data). Use syslog-ng/rsyslog writing to files + UF, or **SC4S** (Splunk Connect for Syslog → HEC).
- HEC: token-based, `[http://token_name]`, optional indexer acknowledgement, put behind a load balancer.
- Add-ons (TAs) from Splunkbase for AWS, Azure, O365 etc., typically on an HF.

### Where does the collector run? VMs vs containers
> **VMs / bare-metal servers → one UF per host. Containers → do NOT put a UF in every container; run one collector per node.**

| Environment | Typical approach |
|---|---|
| **VMs / bare-metal app servers** | Install a **UF on each host**, managed by the **DS**. It monitors log files (`[monitor://...]`) and sends to indexers on :9997. This is the flow diagram above. |
| **Kubernetes** | **Splunk OpenTelemetry Collector** as a **DaemonSet** (one pod per node, and the successor to Splunk Connect for Kubernetes). It reads `/var/log/containers/*.log`, adds k8s metadata (namespace, pod, container), and sends to **HEC**. |
| **Plain Docker hosts** | The Docker **`splunk` logging driver** (stdout/stderr → HEC), *or* a **UF on the Docker host** monitoring `/var/lib/docker/containers/*/*.log`. |
| **ECS / Fargate** | **FireLens** (Fluent Bit sidecar) → HEC, or CloudWatch Logs → Firehose → HEC. |
| **Serverless / managed cloud services** | HEC directly, or a TA pulling from cloud APIs (e.g. Splunk Add-on for AWS: CloudTrail/CloudWatch via S3/SQS). |

**Why not a UF inside each container?** It makes every image bigger, runs an extra process per container, and ties forwarder config to each image. Containers are also short-lived, so you'd end up with lots of short-lived forwarders. The container pattern is for apps to log to **stdout/stderr** (12-factor style), with **one agent per node** collecting everything.

**Exception, the sidecar:** a legacy app that can only write to files *inside* the container gets a sidecar UF or collector in the same pod, reading a shared volume.

**Interview line:** *"On VMs we deploy a UF on each server, managed via the deployment server. In containers we don't bake a forwarder into images. We run a node-level collector as a DaemonSet, like the Splunk OTel Collector, that picks up container stdout and sends to HEC with k8s metadata added. We only use sidecars for legacy apps that log to files."*

### Onboarding process (a great answer for "how would you onboard a new source?")
1. Requirements: owner, use case, volume/day, retention, sensitivity (PII?), who needs access.
2. Get a sample; test in a dev instance with *Add Data* preview to settle line breaking + timestamps.
3. Choose/define sourcetype (reuse a Splunkbase TA/CIM-compliant one where possible), index, and role access.
4. Write props (magic 6/8), filters/masking if required.
5. Deploy: `indexes.conf` via CM bundle → props/transforms to parsing tier → inputs via DS → search-time props to SH/deployer.
6. Validate: event counts, `_time` vs `_indextime` lag, field extraction, license impact.
7. Document and hand over (data dictionary, dashboards, alert on source going silent).

This is exactly where my governance background shines — I've done steps 1, 3, 6, 7 from the other side.

---

## 5. Indexes, buckets & retention

### Bucket lifecycle
```
hot      writable, homePath
  │ rolls on size / age / restart
  ▼
warm     read-only, homePath
  │ maxWarmDBCount or homePath size
  ▼
cold     read-only, coldPath
  │ age (frozenTimePeriodInSecs)
  │ or size (maxTotalDataSizeMB)
  ▼
frozen   deleted by default, or archived
         via coldToFrozenDir/Script
  │ restore archive manually
  ▼
thawed   thawedPath, then splunk rebuild
```
- A bucket = directory with **rawdata** (compressed journal) + **tsidx** (time-series index files) + metadata. Named like `db_<newest>_<oldest>_<id>` (epoch times).
- Data freezes when the **newest** event in the bucket is older than `frozenTimePeriodInSecs` (so a bucket can hold data older than retention until the whole bucket ages out), **or** when the index exceeds `maxTotalDataSizeMB` (oldest buckets frozen first). Whichever comes first.
- Default `frozenTimePeriodInSecs` = 188697600 (~6 years); default `maxTotalDataSizeMB` = 500000 (~500 GB). Always set them explicitly.

```ini
# indexes.conf
[app_prod]
homePath   = volume:hot/app_prod/db
coldPath   = volume:cold/app_prod/colddb
# thawedPath cannot use a volume
thawedPath = $SPLUNK_DB/app_prod/thaweddb
# 90 days
frozenTimePeriodInSecs = 7776000
maxTotalDataSizeMB = 200000
# REQUIRED for it to be replicated in a cluster
repFactor = auto

[volume:hot]
path = /splunk/hot
maxVolumeDataSizeMB = 1500000
```

### Index design principles
- Separate indexes by **access control** (roles are granted per index) and by **retention** (retention is per index). Not by every source — too many indexes = admin overhead; too few = can't restrict access.
- Naming convention (e.g. `<bu>_<env>_<category>`).
- Internal indexes: `_internal` (splunkd.log, metrics.log, license_usage.log, scheduler.log), `_audit` (who searched/did what), `_introspection` (resource usage), `_telemetry`, `_configtracker` (config change history, 9.x).
- `summary` / summary indexes for pre-computed results; **metrics** indexes (`datatype = metric`) for numeric time series — far cheaper to search.

### Sizing rule of thumb
- Raw data compresses to roughly **~50% on disk** (≈15% rawdata + ≈35% tsidx, highly variable).
- Storage ≈ daily ingest × 0.5 × retention days × (RF/SF overhead in a cluster).

### SmartStore
- Warm/cold buckets live in **object storage** (S3 / Azure Blob / GCS); indexers keep hot buckets + a local **cache** managed by the cache manager.
- Decouples compute from storage, cheaper retention, faster peer recovery (buckets don't need full re-replication; only hot buckets replicate).
- Configured with `[volume:remote_store] storageType = remote, path = s3://...` and `remotePath` per index.
- Trade-off: searches over old data not in cache must fetch from S3 (slower); cache sizing matters.

---

## 6. Clustering

### Indexer cluster
- **Replication Factor (RF)**: number of copies of raw data across peers (default 3). Tolerates RF−1 peer failures without data loss.
- **Search Factor (SF)**: number of *searchable* copies (with tsidx) (default 2). SF ≤ RF. Non-searchable copies are smaller but need rebuild time to become searchable.
- **Primary copy**: exactly one searchable copy per bucket is primary and answers searches.
- **Valid / Complete cluster**: *valid* = one primary per bucket (searchable); *complete* = RF and SF met.
- **Bucket fix-up**: when a peer dies, the CM orchestrates re-replication and making copies searchable.
- **Multisite**: `site_replication_factor = origin:2, total:3`, `site_search_factor = origin:1, total:2`. Search affinity keeps searches local to a site.
- The **CM is not in the data path** — if it's down, indexing and searching continue (with limits: no fix-ups, no bundle pushes). Plan standby CM (supported active/standby in recent versions).

**Configuration bundle**
```bash
# on the CM: place apps in $SPLUNK_HOME/etc/manager-apps/
splunk validate cluster-bundle --check-restart
splunk apply cluster-bundle          # pushes to peers' peer-apps/, rolling restart if needed
splunk show cluster-bundle-status
```
Never edit config directly on peers — it gets overwritten/drifts.

**Maintenance**
```bash
splunk enable maintenance-mode       # pause bucket fix-ups during planned work
splunk rolling-restart cluster-peers # (or `searchable` rolling restart to keep search available)
splunk offline                       # on a peer: graceful shutdown, hands off primaries
splunk offline --enforce-counts      # permanent decommission: waits until RF/SF re-met elsewhere
splunk show cluster-status --verbose
```

### Search head cluster
- Minimum **3** members (RAFT needs a majority to elect a captain).
- Captain: schedules saved searches across members, coordinates knowledge object replication and artifacts.
- **Deployer** pushes apps: `$SPLUNK_HOME/etc/shcluster/apps/` → `splunk apply shcluster-bundle -target https://sh1:8089`.
- Runtime changes made in the UI (dashboards, saved searches) replicate between members automatically; baseline config comes from the deployer.
- KV store is replicated across SHC members.
- Useful: `splunk show shcluster-status`, `splunk transfer shcluster-captain`, `splunk resync shcluster-replicated-config` (for a member that drifted).
- Load balancer in front of SHC for users (sticky sessions).

---

## 7. Licensing

- Two main models: **ingest-based** (GB/day indexed, measured at indexing, midnight-to-midnight per License Manager clock) and **workload-based** (licensed by vCPU for Enterprise).
- Only data **indexed** counts. Data dropped to `nullQueue` before indexing does **not** count — that's why filtering on HF/indexer saves license. Internal indexes (`_internal` etc.) and summary indexing (with `stash` sourcetype) do not count. Metrics count per event at a fixed size.
- **License Manager** + license **peers**; licenses grouped in **stacks**, allocated via **pools**.
- **Violations**: exceeding daily quota generates a warning; too many warnings in a rolling 30-day window (e.g. 5 for Enterprise) = violation. Indexing **never stops**. Historically search was blocked on non-internal indexes during violation; for newer versions/larger licenses (≥100 GB/day) search is not blocked — mention "depends on license size and version".
- Monitor: *Settings → Licensing → Usage report* or:

```spl
index=_internal source=*license_usage.log type=Usage
| eval GB=b/1024/1024/1024
| timechart span=1d sum(GB) by idx
```
Governance tie-in: I've been on the "why is this source eating 30% of license?" side. As admin I'd set up this report per index/sourcetype/host plus an alert on day-over-day spikes.

---

## 8. Users, roles & security

- Authentication: **native** Splunk users, **LDAP**, **SAML** (SSO, e.g. Okta/Entra ID), plus MFA via IdP. Map IdP groups → Splunk roles.
- Built-in roles: `admin`, `power`, `user`, `can_delete` (only role that can run `| delete` — assign temporarily and sparingly; `delete` only hides events, doesn't free disk).
- Roles control:
  - **Capabilities** (e.g. `schedule_search`, `edit_user`, `admin_all_objects`, `rest_apps_management`).
  - **Index access**: `srchIndexesAllowed` (can search), `srchIndexesDefault` (searched when no `index=` given).
  - `srchFilter` (row-level restriction, e.g. `host=web*`).
  - Quotas: `srchJobsQuota`, `rtSrchJobsQuota`, `srchDiskQuota`, `srchTimeWin`.
  - **Inheritance**: roles can inherit from others.
- Knowledge object permissions: **private / app / global**, with read/write per role.
- Hardening: change default admin password, TLS for forwarder→indexer (and cert verification), TLS for splunkd/management port, restrict 8089, keep Splunk and apps patched (Splunk security advisories are frequent), audit via `_audit`, least-privilege roles, `pass4SymmKey` for clusters/DS, don't expose Splunk Web directly to the internet.

```ini
# authorize.conf
[role_app_team]
importRoles = user
srchIndexesAllowed = app_prod;app_nonprod
srchIndexesDefault = app_prod
srchJobsQuota = 5
srchDiskQuota = 500
```

---

## 9. Monitoring & troubleshooting (very likely scenario questions)

### Toolkit
- **Monitoring Console** (Settings → Monitoring Console) — configure in distributed mode.
- `_internal` logs: `splunkd.log`, `metrics.log` (throughput, queues), `scheduler.log`, `license_usage.log`.
- `splunk btool ... --debug`, `splunk list forward-server`, `splunk list inputstatus`, `splunk diag` (support bundle), `splunk status`.
- **Health report** (bell icon / `/services/server/health/splunkd`).
- Job Inspector for slow searches.

### Scenario: "A source stopped sending data"
1. Scope it: one host or all hosts? one sourcetype or everything? When did it stop?
   ```spl
   | tstats latest(_time) as last_seen where index=* by index, sourcetype, host
   | eval lag_min=round((now()-last_seen)/60) | where lag_min > 60
   ```
2. Is the forwarder phoning in? `index=_internal host=<uf> sourcetype=splunkd` (UFs send their own logs). No internal logs → forwarder down or network/outputs problem.
3. On the UF: `splunk status`, `splunk list forward-server`, splunkd.log for `TcpOutputProc` errors (connection refused, SSL errors, blocked).
4. Network/firewall to 9997; indexer receiving enabled? Certs expired?
5. Is data arriving but "invisible"? Search `index=* host=<host>` over **All time** — wrong timestamp (future/past) or wrong index; check `_indextime` vs `_time`:
   ```spl
   index=app_prod host=web01 | eval lag=_indextime-_time | stats avg(lag) max(lag) by sourcetype
   ```
6. Index doesn't exist on indexers → events dropped (warning in splunkd.log; or sent to `lastChanceIndex` if set).
7. File input: permissions (UF user can't read file), file rotated, CRC check skipping ("seekptr checksum" messages) → `crcSalt` / `initCrcLength`.
8. Blocked queues downstream (next scenario).

### Scenario: "Indexing is slow / queues blocked"
```spl
index=_internal source=*metrics.log group=queue
| eval pct=round(current_size_kb/max_size_kb*100)
| timechart span=5m max(pct) by name
```
- Look at the **furthest downstream** blocked queue — blocking propagates upstream. `indexQueue` full → disk I/O / storage issue. `typingQueue` → heavy regex transforms. `aggQueue` → timestamp/line-merge work (fix props!). `parsingQueue` → line breaking.
- Fixes: fix props (explicit `LINE_BREAKER`, `SHOULD_LINEMERGE=false`, `TIME_FORMAT`), add indexers, faster disks (hot/warm on SSD), `parallelIngestionPipelines`, check network.

### Scenario: "Searches are slow / scheduled searches are skipped"
```spl
index=_internal sourcetype=scheduler status=skipped
| stats count by savedsearch_name, reason, app
```
- Causes: too many concurrent scheduled searches (limit derived from CPU cores via `limits.conf`: `base_max_searches` + `max_searches_per_cpu` × cores; scheduler gets a % of that), everyone scheduling at `*/5` minute 0.
- Fixes: spread cron schedules, use schedule windows / `schedule_priority`, add SH capacity, accelerate (data model / report acceleration, summary indexing), teach users to use `tstats`, specify `index=`/`sourcetype=`, narrow time ranges, avoid `*` leading wildcards, `transaction`, `join` where `stats` works.
- Search anti-patterns an admin should police: all-time real-time searches, `index=*`, huge `join`s, dashboards with many independent searches instead of base/post-process searches.

### Other useful SPL for admins
```spl
| rest /services/data/indexes | table title currentDBSizeMB maxTotalDataSizeMB frozenTimePeriodInSecs
| rest /services/deployment/server/clients | table hostname lastPhoneHomeTime
| metadata type=sourcetypes index=app_prod
index=_internal sourcetype=splunkd log_level=ERROR | stats count by component
index=_audit action=search info=completed | stats count avg(total_run_time) by user
index=_internal sourcetype=splunkd component=DateParserVerbose   # timestamp problems
index=_internal sourcetype=splunkd component=LineBreakingProcessor # truncation/line-break problems
```

---

## 10. Knowledge objects & performance features (admin view)

- **Knowledge objects**: saved searches, alerts, reports, dashboards, field extractions, lookups, event types, tags, macros, data models, workflow actions.
- **Lookups**: CSV, KV store, external/scripted; automatic lookups via `props.conf LOOKUP-`.
- **KV store**: MongoDB-based, on SHs, port 8191. Backup with `splunk backup kvstore`. Check `| rest /services/kvstore/status`.
- **CIM (Common Information Model)** & **data models**: normalise field names across sources; required by Enterprise Security. Data model acceleration builds tsidx summaries → `| tstats` searches are extremely fast.
- **Summary indexing / report acceleration**: pre-compute for heavy recurring reports.
- **Apps & add-ons**: App = UI/knowledge; TA (Technology Add-on) = inputs + props/transforms for a technology. Know which parts of a TA go on which tier (inputs → forwarder/HF; index-time props → HF/indexers; search-time props → SH). Many TAs are installed on all three.

---

## 11. Upgrades, backup & DR

**Upgrade order (distributed/clustered)** — check the version compatibility matrix first, read release notes, test in non-prod:
1. License manager, Monitoring Console, deployment server (management components).
2. Cluster manager (enable maintenance mode).
3. Search heads / SHC (deployer first, then members, rolling upgrade).
4. Indexer peers (rolling / searchable rolling upgrade).
5. Heavy forwarders, then universal forwarders (UFs can generally be older than indexers — within compatibility).

Rule of thumb: management components ≥ search tier ≥ indexing tier ≥ forwarders in version.

**Backup**
- `$SPLUNK_HOME/etc` (config, apps, users) — critical and small; keep it in Git too.
- KV store (`splunk backup kvstore`).
- Index data: in a cluster, RF gives resilience (not a backup against deletion/corruption); warm/cold buckets can be snapshotted. SmartStore relies on object-store durability/versioning.
- Frozen archive (`coldToFrozenDir`) for compliance retention.

**DR**: multisite indexer cluster across DCs/AZs, SHC spread across sites, standby CM, forwarders with multiple indexer targets/indexer discovery.

---

## 13. Quick reference

**Default ports**
| Port | Use |
|---|---|
| 8000 | Splunk Web |
| 8089 | splunkd management / REST API (DS, CM, license, SHC all talk over this) |
| 9997 | Forwarder → indexer receiving (convention) |
| 8088 | HEC |
| 8080 | Index replication between peers (convention, configurable) |
| 8191 | KV store |
| 514 | Syslog (should land on a syslog server, not Splunk) |

**CLI**
```bash
splunk start|stop|restart|status
splunk btool <conf> list [stanza] --debug
splunk btool check
splunk list forward-server | monitor | inputstatus
splunk add forward-server <host>:9997
splunk enable listen 9997
splunk reload deploy-server
splunk apply cluster-bundle ; splunk show cluster-bundle-status
splunk enable|disable maintenance-mode
splunk rolling-restart cluster-peers [-searchable true]
splunk show cluster-status --verbose
splunk offline [--enforce-counts]
splunk apply shcluster-bundle -target https://<member>:8089
splunk show shcluster-status
splunk backup kvstore
splunk diag
splunk rebuild <bucket_dir>          # after thawing
```

**Key internal logs/sourcetypes**: `splunkd` (errors), `splunkd_access`, `scheduler`, `metrics.log` (group=queue, per_sourcetype_thruput, tcpin_connections), `license_usage.log`, `_audit`.

---

## 14. Hands-on lab plan (do this before the interview)

The biggest gap is hands-on admin; a weekend lab closes most of it and gives concrete stories.

1. **Single instance** via Docker (`splunk/splunk` image) or tarball. Splunk Enterprise trial = 60 days, 500 MB/day (can also request a free **developer license**).
2. Add a **UF** container; configure `outputs.conf` → 9997 and a monitor input. Deliberately break it (wrong port, missing index) and fix it using `_internal`.
3. Onboard a messy multi-line log: write props from scratch (magic 6/8), verify with `btool` and `_indextime - _time`.
4. Filter DEBUG to nullQueue, mask a fake card number with SEDCMD, route an event to a different index. Compare license usage before/after.
5. Create indexes with short retention; watch buckets roll (`| dbinspect index=...`).
6. Roles: create a role restricted to one index, test as that user.
7. Deployment server: move UF config into a deployment app + server class.
8. **Mini cluster** (docker-compose / `splunk/splunk` supports `SPLUNK_ROLE`s): 1 CM + 3 peers + 1 SH. Push an `indexes.conf` bundle, kill a peer, watch fix-up in the CM UI, enable maintenance mode, rolling restart.
9. Monitoring Console: set up distributed mode, look at the indexing/search dashboards.
10. Free training: Splunk's free eLearning (*Intro to Splunk*, *Using Fields*, etc.) and the docs: *Distributed Deployment Manual*, *Managing Indexers and Clusters*, *Getting Data In*, *Securing Splunk*. Related certs: **Splunk Core Certified Power User** → **Splunk Enterprise Certified Admin**.

---

## 15. Questions to ask them
- Which Splunk Enterprise version, and any plans to move to Splunk Cloud? Daily ingest volume and license model (ingest vs workload)?
- Deployment topology: clustered? multisite? SmartStore?
- How is config managed — Git/CI, or hand-edited? How are new data sources requested and onboarded?
- Is Enterprise Security / ITSI / Observability in scope?
- Biggest current pain: license, performance, data quality, or platform stability?
- Size of the Splunk team and split between platform admin vs content/use-case engineering?

---

## 16. Splunk Cloud (reference only — target company runs Splunk Enterprise)

| | Splunk Enterprise | Splunk Cloud Platform |
|---|---|---|
| Infra | You run it (on-prem/IaaS) | Splunk runs indexers/SHs |
| Access | Full CLI, conf files, OS | No backend/CLI; UI + **Admin Config Service (ACS)** API/CLI for indexes, HEC tokens, IP allowlists, apps |
| Apps | Anything | Must pass **AppInspect** vetting |
| Role | `admin` | `sc_admin` |
| You still own | Everything | Forwarders, HFs/IDM inputs, data onboarding, props, roles, knowledge objects, search governance, license/SVC usage |

Much of the Splunk Cloud admin job is exactly what I've done: data onboarding quality, access, and usage governance — the infra side is Splunk's responsibility.

**Cloud-only items moved here from the sections above:**
- **Data pipeline (§3):** *Edge Processor* / *Ingest Processor* — SPL2-based pipelines that run outside/before the indexers.
- **Getting data in (§4):** API/modular inputs can run on the *Inputs Data Manager (IDM)* instead of your own HF.
- **Licensing (§7):** workload-based pricing is measured in *SVCs* (Splunk Virtual Compute) rather than vCPUs.
- **Roles (§8):** customers get `sc_admin` instead of the full `admin` role.
- **Q&A #10 (retention):** long-term archive uses *DDAA* (Dynamic Data Active Archive, Splunk-managed) or *DDSS* (Dynamic Data Self Storage, your own S3/Blob bucket) instead of `coldToFrozenDir`.
- **Certification:** **Splunk Cloud Certified Admin**.
