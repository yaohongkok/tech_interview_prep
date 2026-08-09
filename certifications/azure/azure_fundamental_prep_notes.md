# AZ-900: Microsoft Azure Fundamentals — Exam Prep Notes

Exam domains and weights (current AZ-900 skills outline):
1. Describe cloud concepts — 25–30%
2. Describe Azure architecture and services — 35–40%
3. Describe Azure management and governance — 30–35%

---

## 1. Describe Cloud Concepts (25–30%)

### Benefits of cloud computing
- **High availability** — service stays up and reachable, minimal downtime.
- **Scalability** — add/remove resources to match load (do more of the same work).
- **Elasticity** — automatically scale out/in in response to load (dynamic).
- **Agility** — provision/deprovision resources quickly.
- **Fault tolerance** — ability to continue operating despite failure (via redundancy).
- **Disaster recovery** — restoring access/functionality after a disruptive event.

### CapEx vs OpEx
- **CapEx** (Capital Expenditure): upfront spending on physical infrastructure, depreciates over time. Traditional on-prem model.
- **OpEx** (Operational Expenditure): pay-as-you-go spending on services, no upfront cost, spend based on need. Cloud model.
- Cloud shifts CapEx → OpEx.

### Consumption-based model
- Pay only for what you use.
- No upfront infra cost; stop paying when you stop using.
- Costs are variable, tied to demand.

### Cloud service models
| Model | Who manages what | Example use |
|---|---|---|
| **IaaS** (Infrastructure as a Service) | You manage OS, runtime, apps, data. Provider manages virtualization, servers, storage, networking. | Azure VMs |
| **PaaS** (Platform as a Service) | You manage apps/data. Provider manages OS, runtime, middleware. | Azure App Service |
| **SaaS** (Software as a Service) | Provider manages everything; you just use the app. | Microsoft 365 |

Shared responsibility: **security responsibility shifts to the provider** as you move IaaS → PaaS → SaaS. You *always* retain responsibility for data, endpoints, accounts, and access management, regardless of model.

### Cloud deployment models
- **Public cloud** — resources owned/operated by third-party provider, over the internet, shared infra. No CapEx, high scalability.
- **Private cloud** — dedicated to a single org, on-prem or hosted. More control, more responsibility for maintenance/security.
- **Hybrid cloud** — combination of public + private, allows data/apps to move between. Useful for compliance, legacy systems, gradual migration.
- **Multi-cloud** — using more than one cloud provider.

---

## 2. Describe Azure Architecture and Services (35–40%) — *priority review*

### Core architectural components
- **Regions** — geographic area containing one or more datacenters, connected via low-latency network. Deploy resources into a specific region.
- **Region pairs** — each Azure region is paired with another region ≥300 miles away within the same geography (for disaster recovery; one region prioritized for recovery, updates rolled out to one region at a time).
- **Availability Zones** — physically separate datacenters within a region, each with independent power, cooling, networking. Minimum of 3 per enabled region. Protects against datacenter-level failure.
- **Geographies** — a defined area of the world containing ≥1 region; ensures data residency, sovereignty, compliance boundaries (e.g., data doesn't leave the geography).
- **Resource groups** — logical containers for resources sharing the same lifecycle; resources can belong to only **one** resource group.
- **Subscriptions** — billing + access control boundary; groups resource groups; tied to an Azure AD (Entra ID) tenant.
- **Management groups** — organize multiple subscriptions; apply governance (policy, RBAC) across subscriptions hierarchically.
- **Availability Sets** — logical grouping of VMs across fault domains (separate racks/power/network) and update domains (separate maintenance reboot groups) within a **single datacenter**. Protects against hardware/maintenance failure, but not datacenter-level failure — that's what Availability Zones are for.

**Hierarchy:** Management Groups → Subscriptions → Resource Groups → Resources.

### Compute services
- **Virtual Machines (VMs)** — IaaS, full control over OS. Use **VM Scale Sets** to autoscale identical VMs.
- **App Service** — PaaS for hosting web apps, REST APIs, mobile backends. Supports multiple languages, built-in autoscale, deployment slots.
- **Azure Functions** — serverless, event-driven, **consumption-based billing** (pay per execution), good for short-lived tasks/triggers.
- **Azure Container Instances (ACI)** — run containers without managing VMs/orchestration; fastest way to run a single container.
- **Azure Kubernetes Service (AKS)** — managed Kubernetes for container orchestration at scale.
- **Azure Batch** — large-scale parallel/batch compute jobs.
- **Windows Virtual Desktop / Azure Virtual Desktop** — virtualized desktop/app experience.

Rule of thumb: **VMs** = most control; **App Service** = web apps without managing OS; **Functions** = event-driven small pieces of code; **AKS** = container orchestration; **ACI** = simplest single-container option.

### Networking services
- **Virtual Network (VNet)** — private network in Azure; resources communicate securely. Used to logically isolate and control resources within Azure, and to control routing/traffic between them and the internet or on-prem.
- **Subnets** — segment a VNet. Used to divide a VNet into smaller ranges (e.g., public vs private) so routing and security policies (NSGs) can be applied per segment, isolating resources like databases from public-facing tiers.
- **VPN Gateway** — encrypted connection over public internet between VNet and on-prem.
- **ExpressRoute** — private, dedicated, high-bandwidth connection to Azure (does NOT go over public internet); more reliable/faster/more secure than VPN, but costlier.
- **Azure DNS** — hosts DNS domains.
- **Load Balancer** — distributes traffic at Layer 4 (transport) within a region.
- **Application Gateway** — Layer 7 (application) load balancer, includes Web Application Firewall (WAF), URL-based routing.
- **Azure Front Door** — global, Layer 7 load balancing/routing + CDN-like acceleration across regions.
- **Traffic Manager** — DNS-based traffic routing across regions (not a proxy, just DNS redirection).
- **Network Security Groups (NSGs)** — filter inbound/outbound traffic at subnet/NIC level (allow/deny rules).
- **Azure Firewall** — managed, stateful **network firewall as a service**, protects an entire VNet (not per-subnet/NIC like NSGs); centralized policy across subscriptions/VNets.
- **Azure Bastion** — provides secure RDP/SSH to VMs **via the browser/Azure Portal**, over TLS, without exposing the VM's public IP. No need to give VMs a public IP just to manage them.
- **Virtual network peering** — connects two VNets together (can be cross-region) so resources communicate as if on the same network, using the Microsoft backbone (not the public internet).
- **Service endpoints** — extend a VNet's private identity to an Azure PaaS service (e.g., Storage, SQL DB) over the Azure backbone, so traffic never traverses the public internet. Secures the service to only accept traffic from specific subnets, but the service still has a public IP (vs. **Private Link/Private Endpoint**, which gives the service a private IP inside your VNet).

Key distinction: **Load Balancer** = regional, L4. **Application Gateway** = regional, L7, WAF. **Front Door/Traffic Manager** = global, cross-region. **NSG** = allow/deny rules per subnet/NIC. **Azure Firewall** = managed stateful firewall for a whole VNet. **Bastion** = secure browser-based admin access (RDP/SSH), no public IP needed.

#### Diagram 1 — how a user request reaches your app (global → regional)

```
                          Internet Users
                                │
                           Azure DNS
                    (resolves your domain name)
                                │
              ┌─────────────────┴─────────────────┐
              │                                     │
      Azure Front Door                       Traffic Manager
   (global, L7 PROXY — traffic          (global, DNS-only REDIRECT —
    actually flows through it;           just tells the client which
    WAF, CDN caching, URL routing)        region's IP to go to directly)
              │                                     │
              └─────────────────┬─────────────────┘
                                 │
                     client lands in ONE region
                                 ▼
                  ──────────────────────────────
                   REGION (e.g. East US)
                  ──────────────────────────────
                                 │
                        Application Gateway
                   (regional, L7, WAF, URL-based routing)
                                 │
                           Load Balancer
                       (regional, L4, TCP/UDP)
                                 │
                        ┌────────┴────────┐
                        │                 │
                   VM / VMSS          VM / VMSS
                (Subnet A, NSG)     (Subnet B, NSG)
```

Note: Front Door *proxies* traffic (sees/modifies it, can do WAF+caching); Traffic Manager only *redirects* via DNS (never touches the actual traffic). That's the key exam distinction.

#### Diagram 2 — hybrid connectivity (on-prem ↔ Azure)

```
On-Premises Datacenter
        │
        ├──> VPN Gateway ───────────────┐   encrypted tunnel,
        │    (cheaper, less reliable)    │   over the PUBLIC internet
        │                                │
        └──> ExpressRoute ───────────────┤   private dedicated circuit,
             (pricier, most reliable/     │   bypasses public internet
              fastest/most secure)        │
                                          ▼
                         ┌───────────────────────────────┐
                         │      Virtual Network (VNet)     │
                         │                                  │
                         │  ┌───────────┐   ┌────────────┐  │
                         │  │ Subnet A  │   │ Subnet B   │  │
                         │  │  [NSG]    │   │  [NSG]     │  │
                         │  │  VMs      │   │  VMs       │  │
                         │  └───────────┘   └────────────┘  │
                         └───────────────────────────────┘
```

Only one of VPN Gateway / ExpressRoute is typically used at a time (or both, for failover) — pick VPN for cost/simplicity, ExpressRoute when you need guaranteed bandwidth/latency/security (e.g. regulated workloads).

#### Diagram 3 — where NSGs filter traffic (zoomed into one subnet)

```
                  Traffic (inbound or outbound)
                              │
                              ▼
                    ┌───────────────────┐
                    │  NSG on Subnet     │  filters traffic crossing
                    └───────────────────┘  the subnet boundary
                              │
                              ▼
                    ┌───────────────────┐
                    │  NSG on NIC        │  filters traffic to/from
                    └───────────────────┘  that specific VM's NIC
                              │
                              ▼
                             VM
```

NSGs can be attached at the subnet level, the NIC level, or both — traffic must pass both sets of allow/deny rules if both are present.

### Storage services
- **Azure Storage account** — umbrella for Blob, File, Queue, Table storage.
  - **Blob storage** — unstructured object storage (Hot/Cool/Archive tiers).
    - Hot = frequent access; Cool = infrequent (min 30 days); Archive = rarely accessed, offline, cheapest, highest retrieval latency (hours).
  - **Azure Files** — managed file shares via SMB/NFS.
  - **Queue storage** — messaging between app components.
  - **Table storage** — NoSQL key-value store.
- **Disk storage** — for VM disks (managed disks): HDD, Standard SSD, Premium SSD, Ultra Disk.
- **Redundancy options** (durability):
  - **LRS** (Locally Redundant Storage) — 3 copies within one datacenter.
  - **ZRS** (Zone Redundant Storage) — copies across 3 availability zones in a region.
  - **GRS** (Geo-Redundant Storage) — LRS + async copy to paired region.
  - **RA-GRS** (Read-Access GRS) — GRS + read access to the secondary region.
  - **GZRS** — ZRS + geo-replication to paired region.
- **Migration tools**: **Azure Migrate** (assessment + migration), **Azure Data Box** (offline bulk data transfer via physical device), **AzCopy**, **Azure Storage Explorer**.

### Database services
- **Azure SQL Database** — managed relational DB (PaaS), based on SQL Server.
- **Azure Database for MySQL/PostgreSQL/MariaDB** — managed OSS relational DBs.
- **Azure Cosmos DB** — globally distributed, multi-model NoSQL DB, low latency, multiple consistency levels.
- **Azure SQL Managed Instance** — near-100% SQL Server compatibility, PaaS.
- **Azure Database Migration Service** — migrate on-prem DBs to Azure with minimal downtime.

### Identity services
- **Microsoft Entra ID** (formerly Azure Active Directory) — cloud-based identity and access management; authentication + authorization.
- **Microsoft Entra Domain Services** — provides **managed AD DS** (domain join, group policy, LDAP, Kerberos/NTLM) **without deploying/managing domain controllers**. Different from Entra ID, which is cloud identity only and has no classic AD DS functionality.
- **Microsoft Entra Connect (Sync)** — syncs identities from an **on-prem** AD DS domain to Microsoft Entra ID, enabling **hybrid identity** (SSO, MFA, self-service password reset across both systems).
- **Self-Service Password Reset (SSPR)** — lets users reset their own password without help desk; also blocks known-compromised passwords.
- **Multi-factor authentication (MFA)** — requires 2+ verification methods.
- **Conditional Access** — policies that grant/block access based on conditions (location, device, risk); e.g., only allow access from approved client apps, or require MFA from specific locations.
- **Single Sign-On (SSO)** — one login for multiple apps.
- Entra ID is **identity**, distinct from **Azure RBAC** which is **access management** for Azure resources.

### Security concepts & tools
- **Defense in depth** — layering multiple security controls (physical, identity, perimeter, network, compute, app, data) so no single point of failure exposes data to unauthorized access.
- **Azure Key Vault** — centralized, secure storage for application secrets, keys, and certificates (avoids hardcoding secrets in app config/code).

### AI / ML services (high level, be able to name category)
- **Azure Machine Learning** — build/train/deploy ML models.
- **Cognitive Services** (now Azure AI Services) — pre-built AI: vision, speech, language, decision.
- **Azure Bot Service** — build conversational bots.

### IoT
- **IoT Hub** — bidirectional communication with IoT devices.
- **IoT Central** — SaaS for IoT app building.
- **Azure Sphere** — secured, high-level IoT devices/microcontrollers.

### Serverless
- Serverless = no server management, automatic scaling, pay only for execution time. Examples: **Azure Functions**, **Logic Apps** (workflow automation, event-driven, low-code).

---

## 3. Describe Azure Management and Governance (30–35%)

### Cost management
- **Pricing calculator** — estimate cost of Azure products before deploying.
- **Total Cost of Ownership (TCO) calculator** — compare cost of on-prem vs Azure.
- **Azure Cost Management + Billing** — monitor, allocate, optimize cloud spend; set budgets and alerts.
- Factors affecting cost: resource type, region, bandwidth (egress costs money, ingress usually free), subscription type.

### Governance tools
- **Azure Policy** — enforce organizational standards/rules on resources (e.g., "only allow specific VM SKUs", "require tags"). Evaluates existing + new resources; can deny, audit, or append.
  - **Initiative** — a grouping of related policies managed/assigned together as a single set.
- **Azure Blueprints** — package policies, role assignments, resource templates together for repeatable environment setup (compliance-focused).
- **Resource locks** — prevent accidental delete/modify. Types: **CanNotDelete** and **ReadOnly**. Applies regardless of RBAC permissions, inherited down the hierarchy.
- **Tags** — key-value metadata on resources for organization, cost tracking, automation.

### Access management
- **Role-Based Access Control (RBAC)** — assign roles (e.g., Owner, Contributor, Reader) to users/groups/service principals at a scope (management group, subscription, resource group, resource). Roles are **additive only** (deny assignments exist but are rare/special-case).
  - **Owner** — full access incl. managing access.
  - **Contributor** — full access, but cannot manage access (can't grant roles).
  - **Reader** — view only.
- Scope inheritance: permissions granted at a higher scope are inherited by child scopes.
- **Principle of least privilege** — grant minimum access needed.

### Compliance
- **Microsoft Purview Compliance Manager** — assess compliance risk, actionable recommendations, compliance score.
- **Service Trust Portal** — access audit reports, compliance guides.
- **Azure geographies/sovereign clouds** — Azure Government, Azure China — for regulatory/data residency needs.

### Monitoring
- **Azure Monitor** — collect, analyze, act on telemetry (metrics, logs) from Azure + on-prem resources.
  - **Application Insights** — a feature of Azure Monitor; APM for web apps — auto-detects performance anomalies, tracks usage/user behavior.
- **Azure Advisor** — personalized recommendations across cost, security, reliability, performance, operational excellence.
- **Service Health** — status of Azure services affecting your resources/region; notifies of region-wide outages and publishes **Root Cause Analysis (RCA)** reports after an incident.
- **Azure Status** — global health of all Azure services.

### Deployment / management tools
- **Azure Portal** — GUI, web-based.
- **Azure PowerShell** — scripting via PowerShell cmdlets.
- **Azure CLI** — cross-platform command-line tool.
- **Azure Cloud Shell** — browser-based shell (has both Bash & PowerShell), preconfigured with tools.
- **Azure Resource Manager (ARM)** — deployment and management layer; all requests go through ARM regardless of tool used. Enables **ARM templates** (JSON, declarative, idempotent Infrastructure-as-Code) and **Bicep** (simplified DSL that compiles to ARM templates).
- **Azure Arc** — extends Azure management/governance (policy, RBAC, monitoring) to servers, Kubernetes clusters, and resources **outside Azure** — on-prem or other clouds — **without migrating them**.
- **Azure Mobile App** — manage/monitor resources from phone.

---

## Quick-Reference Cheat Sheet (last-minute review)

| Term | One-liner |
|---|---|
| Region pair | 2 regions ≥300 mi apart, same geography, for DR |
| Availability Zone | Physically separate DC within a region, ≥3 per region |
| Resource group | Container, resource belongs to exactly 1 |
| Management group | Groups subscriptions for governance |
| LRS/ZRS/GRS/RA-GRS | Storage redundancy: local → zone → geo → geo+read |
| ExpressRoute | Private dedicated connection, not over public internet |
| VPN Gateway | Encrypted connection over public internet |
| Load Balancer | Regional, Layer 4 |
| Application Gateway | Regional, Layer 7, has WAF |
| Front Door / Traffic Manager | Global, cross-region routing |
| Azure Policy | Enforces rules/standards on resources |
| Resource Lock | Prevents delete/modify (CanNotDelete, ReadOnly) |
| RBAC | Who can do what, on which resource scope |
| Entra ID | Identity/authentication (who are you) |
| CapEx → OpEx | Cloud shifts spend model |
| IaaS/PaaS/SaaS | Increasing provider responsibility, decreasing yours |
| Consumption model | Pay only for what you use |
| Azure Advisor | Recommendations (cost/security/reliability/perf) |
| Azure Monitor | Telemetry collection & analysis |
| ARM | Deployment/management layer under all tools |
| Bicep | DSL that compiles down to ARM templates |
| Availability Set | Fault/update domains within one datacenter (VM-level resiliency) |
| Azure Bastion | Browser-based secure RDP/SSH, no public IP on VM |
| Azure Firewall | Managed stateful firewall for a whole VNet |
| VNet Peering | Connects two VNets over Microsoft backbone |
| Entra Domain Services | Managed AD DS, no domain controllers to manage |
| Entra Connect | Syncs on-prem AD to Entra ID (hybrid identity) |
| Azure Key Vault | Centralized secrets/keys/certificates storage |
| Policy Initiative | Group of Azure Policies managed as one set |
| Azure Arc | Manage on-prem/multi-cloud servers via Azure, no migration |
| Application Insights | Azure Monitor feature — APM for web apps |

## Common gotchas / things practice tests like to trick you on
- **ExpressRoute ≠ over the internet** — it's a private connection.
- **Resource can only be in ONE resource group**, but a resource group can span multiple regions.
- **Contributor ≠ Owner** — Contributor cannot manage access/permissions.
- **Availability Zones require region support** — not all regions have them.
- **Archive tier storage** — cheapest but data isn't immediately accessible; must rehydrate first.
- **Azure Policy vs RBAC** — Policy = what configurations are *allowed*; RBAC = who can *do* what.
- **Elasticity vs Scalability** — elasticity is automatic/dynamic; scalability can be manual.
- Free trial vs Pay-As-You-Go vs Enterprise Agreement — know these are different subscription/offer types, not deployment models.
- **Availability Set ≠ Availability Zone** — Availability Set = fault/update domains *within one datacenter* (protects against rack/host/maintenance failure); Availability Zone = *separate datacenters* in a region (protects against datacenter-level failure).
- **Entra ID ≠ Entra Domain Services** — Entra ID is cloud identity only, no classic AD DS features (no domain join/group policy/LDAP); Entra Domain Services gives you managed AD DS without running your own domain controllers.
- **NSG vs Azure Firewall vs Bastion** — NSG = allow/deny rules at subnet/NIC; Azure Firewall = managed stateful firewall protecting a whole VNet; Bastion = secure browser-based RDP/SSH to VMs (not a firewall, an access method).
- **Resource locks apply at**: subscription, resource group, or individual resource — **not** at management group or region level.

## Study plan suggestion
1. Re-review **Azure architecture and services** section above in depth (your weak area) — focus on networking (LB vs App Gateway vs Front Door) and storage redundancy tiers, these are common trip-ups.
2. Do another Microsoft Learn practice assessment and compare score delta.
3. Skim Management & Governance section once more the day before the exam — RBAC vs Policy vs Locks distinctions are frequently tested.
4. Exam day: 40–60 questions, ~60 minutes, passing score 700/1000.
