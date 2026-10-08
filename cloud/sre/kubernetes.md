# Kubernetes: Review Notes for Lead SRE (Platform) Interview

Target role: Guidewire, Lead Site Reliability Engineer (Platform). Multi-tenant SaaS on AWS/EKS.

**What the JD asks for, and where it is covered here:**

| JD line | Section |
|---------|---------|
| Kubernetes primitives and patterns (deployments, services, operators) | 1, 2, 3, 10 |
| EKS, CNI, Ingress networking | 5, 6 |
| Helm | [helm.md](helm.md) |
| IRSA, RBAC, network policies, pod security standards, secrets | 7 |
| GitOps (FluxCD), CI/CD | 11 |
| KubeVela (OAM), Crossplane (preferred) | 10 |
| Multi-tenant platform, reliability, self-healing | 4, 8, 12 |
| Observability (Prometheus, Datadog, OTel), SLOs | 13 |
| Troubleshooting, incident response | 14, 15 |

Terms and acronyms are defined in [kube-glossary.md](kube-glossary.md).

---

## Part 1: Core Concepts

### 1. Architecture

**Control plane**

| Component | Job |
|-----------|-----|
| `kube-apiserver` | The only component that talks to etcd. Stateless, horizontally scaled. Everything else is a client of it. In practice: every `kubectl` command (get, apply, logs, exec) is a request to it, which it authenticates, authorizes (RBAC), validates, then reads from or writes to etcd. |
| `etcd` | Consistent key-value store (Raft). Needs a quorum: 3 members tolerate 1 failure, 5 tolerate 2. |
| `kube-scheduler` | Assigns a node to each unscheduled pod (filter, then score). |
| `kube-controller-manager` | Runs the built-in reconcile loops (Deployment, ReplicaSet, Node, Job, EndpointSlice...). |
| `cloud-controller-manager` | Cloud-specific loops: node lifecycle, load balancers, routes. |

**Node**

| Component | Job |
|-----------|-----|
| `kubelet` | Watches pods bound to its node, drives the container runtime via CRI, runs probes, reports status. |
| Container runtime | `containerd` (Docker shim was removed in 1.24). |
| `kube-proxy` | Programs Service VIP to pod IP rules. Modes: iptables (default), IPVS (legacy), nftables (newer). Some CNIs (Cilium) replace it with eBPF. |
| CNI plugin | Gives the pod a network interface and an IP. |

**The core idea: declarative reconciliation.** You write desired state to the API. Controllers watch, compare desired with actual, and act to close the gap, forever. Level-triggered, not edge-triggered: a controller that misses an event still converges on the next sync. This is the same pattern behind operators, Flux and Crossplane.

**API request path:** authentication → authorization (RBAC) → mutating admission → schema validation → validating admission → etcd.

**What happens on `kubectl apply -f deployment.yaml`:**
1. API server authenticates, authorizes, runs admission, persists the Deployment.
2. Deployment controller creates a ReplicaSet; ReplicaSet controller creates Pod objects (no node yet).
3. Scheduler picks a node for each pod and writes the binding.
4. Kubelet on that node sees the pod, asks CNI for networking, pulls images, starts init containers, then app containers.
5. Once readiness passes, the EndpointSlice controller adds the pod IP to the Service's endpoints and kube-proxy on every node updates its rules.

```
kubectl apply -f deployment.yaml
            │
            ▼
┌─ kube-apiserver ─────────────────────────────────────────┐
│ 1. authn → authz (RBAC) → admission → persist Deployment │ ⇄ etcd
└──────────────────────────────────────────────────────────┘
          ▲ │   Every component below WATCHES the API server and WRITES
          │ ▼   its result back to it. None of them call each other.

CONTROL PLANE
┌────────────────────────────┐
│ 2. Deployment controller   │  sees Deployment → creates ReplicaSet
│    ReplicaSet controller   │  sees ReplicaSet → creates Pods (no node, Pending)
└────────────────────────────┘
            │
            ▼
┌────────────────────────────┐
│ 3. kube-scheduler          │  sees unscheduled Pod → filter, score
│                            │                       → writes binding (sets nodeName)
└────────────────────────────┘
            │
WORKER NODE ▼
┌────────────────────────────┐
│ 4. kubelet                 │  sees Pod bound to its node
│                            │    → CRI: create pod sandbox
│                            │    → CNI: network interface + pod IP
│                            │    → pull images
│                            │    → init containers → app containers
│                            │    → run probes, report status
└────────────────────────────┘
            │  readiness passes, Pod condition Ready=True
            ▼
┌────────────────────────────┐
│ 5. EndpointSlice controller│  sees Ready Pod       → adds pod IP to the Service's EndpointSlice
│    kube-proxy (every node) │  sees EndpointSlice   → updates iptables / IPVS / nftables rules
└────────────────────────────┘
            │
            ▼
   Pod receives Service traffic
```

> **Interview tip:** this question is a favourite. Walk the chain and name the component at each step. On EKS, add that the control plane is AWS-managed so you only see it through API server metrics and control plane logs in CloudWatch.

---

### 2. Workloads

| Kind | Use | Key points |
|------|-----|-----------|
| Deployment | Stateless services | Owns ReplicaSets. Rolling update with `maxSurge` / `maxUnavailable` (both default 25%). `kubectl rollout undo` switches back to an older ReplicaSet. |
| StatefulSet | Databases, Kafka, anything needing identity | Stable name (`app-0`), stable DNS via a headless Service, one PVC (Presistent Vol Claim) per pod from `volumeClaimTemplates`, ordered rollout. PVCs are not deleted by default when you scale down. |
| DaemonSet | One pod per node | Log shippers, CNI, node exporters, Datadog agent. |
| Job / CronJob | Run to completion | See [Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/) and [CronJobs](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/). |

**Pod lifecycle**

- Phases: `Pending` → `Running` → `Succeeded` / `Failed`. `CrashLoopBackOff` and `ImagePullBackOff` are container states, not phases.
- **Init containers** run in order to completion before app containers. **Native sidecars** are init containers with `restartPolicy: Always`: they start before the app and stop after it.
- **Probes**
  - `startupProbe`: holds off the other probes until the app has booted. Use it for slow starters instead of a huge `initialDelaySeconds`.
  - `readinessProbe`: failing removes the pod from Service endpoints. No restart.
  - `livenessProbe`: failing restarts the container. Keep it cheap and never make it depend on a downstream service, or one database blip restarts the whole fleet.

**Graceful shutdown (frequent source of 502s during deploys)**

1. Pod is marked Terminating. Two things happen in parallel: endpoint removal, and the kubelet starts shutdown.
2. Kubelet runs the `preStop` hook, then sends SIGTERM.
3. After `terminationGracePeriodSeconds` (default 30s) it sends SIGKILL.

Because endpoint removal and SIGTERM race, the app can stop while load balancers still send traffic. Fix: a short `preStop` sleep (5 to 15s), an app that drains in-flight requests on SIGTERM, and an ALB deregistration delay shorter than the grace period.

---

### 3. Configuration and Storage

- **ConfigMap / Secret** as env vars or mounted files. Mounted files update in place (with a delay); env vars need a pod restart. Neither triggers a rollout by itself.
- **Secrets are base64, not encrypted.** Protect with RBAC, encryption at rest (KMS envelope encryption on EKS), and ideally keep the source of truth outside the cluster (see 7).
- **Storage:** `StorageClass` → `PersistentVolumeClaim` → `PersistentVolume`, provisioned by a CSI driver. The one gotcha to remember: an EBS volume is **bound to one AZ**, so its pod can only schedule there (use `volumeBindingMode: WaitForFirstConsumer`). Details: [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/), [EKS storage](https://docs.aws.amazon.com/eks/latest/userguide/storage.html).

---

### 4. Scheduling, Resources and Autoscaling

**Requests and limits**

- **Request** = what the scheduler reserves. **Limit** = the runtime cap.
- CPU over limit → **throttled** (CFS quota), shows up as latency. Memory over limit → **OOMKilled** (exit code 137).
- Common practice: always set memory request = limit; set a CPU request, and be deliberate about CPU limits since they cause throttling even when the node has spare CPU.

| QoS class | Condition | Eviction order under node pressure |
|-----------|-----------|-----------------------------------|
| Guaranteed | requests = limits for every container | Last |
| Burstable | some requests set | Middle |
| BestEffort | nothing set | First |

**Namespace guardrails (multi-tenancy):** `ResourceQuota` caps the total per namespace; `LimitRange` sets defaults and min/max per container.

**Placement controls**

| Tool | Purpose |
|------|---------|
| `nodeSelector` / node affinity | Attract pods to nodes |
| Taints and tolerations | Repel pods from nodes unless they tolerate |
| Pod anti-affinity | Keep replicas apart (hard or soft) |
| `topologySpreadConstraints` | Spread evenly across zones / nodes; usually better than anti-affinity |
| `PriorityClass` | Higher priority pods preempt lower ones |
| `PodDisruptionBudget` | Limits **voluntary** disruption (drain, upgrade, Karpenter consolidation). Does not protect against node failure. A PDB with `maxUnavailable: 0`, or `minAvailable` equal to replicas, blocks node drains forever. |

**Autoscaling**

| Layer | Tool | Notes |
|-------|------|-------|
| Pods, horizontal | HPA | Scales on CPU/memory (needs metrics-server; percentages are of **requests**) or custom/external metrics. `behavior` block tunes scale-down stabilisation. |
| Pods, other | [KEDA](https://keda.sh/docs/latest/concepts/), [VPA](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler) | KEDA: event-driven (queue depth, Kafka lag), scales to zero. VPA: right-sizes requests; not with HPA on the same metric. |
| Nodes | Cluster Autoscaler | Works on node groups / ASGs. Slower, needs a group per instance shape. |
| Nodes | Karpenter | Provisions right-sized EC2 directly from pending pod requirements (`NodePool`, `EC2NodeClass`). Faster, consolidates underused nodes, handles Spot well. |

Both node autoscalers act on **pending pods**, which are driven by requests. Wrong requests mean wrong scaling.

---

### 5. Networking

**The model:** every pod has its own IP; pods reach each other without NAT; containers in a pod share a network namespace (localhost).

**Services**

| Type | What it does |
|------|-------------|
| `ClusterIP` | Virtual IP reachable inside the cluster. Default. |
| `NodePort` | Opens a port on every node. |
| `LoadBalancer` | Provisions a cloud LB (NLB on AWS). |
| Headless (`clusterIP: None`) | No VIP; DNS returns pod IPs directly. Used by StatefulSets. |
| `ExternalName` | DNS CNAME. |

- A Service selects pods by label; ready pod IPs live in **EndpointSlices**.
- `kube-proxy` load-balances **per connection**, not per request. Long-lived HTTP/2 or gRPC connections stick to one pod; this needs L7 balancing (mesh, ALB, or client-side).
- `externalTrafficPolicy: Local` preserves client source IP and avoids an extra hop, at the cost of uneven spread.

**DNS**

- CoreDNS serves `<svc>.<ns>.svc.cluster.local`.
- Pods default to `ndots:5`, so `api.example.com` is tried against every search domain first. That is 4 or more wasted lookups per external name. Mitigate with a trailing dot (FQDN), lower `ndots`, or NodeLocal DNSCache.
- DNS trouble at scale: CoreDNS under-provisioned, conntrack races on UDP, upstream throttling (VPC resolver limit is 1024 packets/sec per ENI).

**CNI**

The CNI plugin is called by the kubelet (through the runtime) on pod create/delete to set up the interface, IP and routes.

EKS defaults to the **AWS VPC CNI** (pods get real VPC IPs, no overlay). The common alternatives are [Calico](https://docs.tigera.io/calico/latest/about/) (BGP or overlay, strong NetworkPolicy) and [Cilium](https://docs.cilium.io/en/stable/overview/intro/) (eBPF, can replace kube-proxy, L7 policy).

**AWS VPC CNI details (very likely to come up)**

- Each node attaches ENIs and assigns secondary IPs to pods. **Max pods per node is bounded by ENIs × IPs per ENI** for the instance type.
- **IP exhaustion** is the classic failure: pods stuck in `ContainerCreating` with "failed to assign an IP address". The warm pool (`WARM_ENI_TARGET`, `WARM_IP_TARGET`) also hoards IPs.
- Fixes: **prefix delegation** (assign /28 prefixes per ENI slot, far higher pod density), **custom networking** (pods use a separate secondary CIDR, often 100.64.0.0/10), bigger subnets, or IPv6 clusters.
- **Security groups for pods**: a pod gets its own branch ENI and SG. Useful for locking down RDS access per workload.
- Pod IPs are routable in the VPC, so ALB/NLB can target pods directly (`target-type: ip`).

**Ingress and Gateway API**

- **Ingress**: L7 HTTP routing rules (host, path, TLS). Needs a controller to do anything.
- **AWS Load Balancer Controller**: `Ingress` → ALB, `Service type=LoadBalancer` → NLB.
  - `target-type: ip` sends traffic straight to pod IPs (use with pod readiness gates). `instance` goes through NodePort.
  - `group.name` shares one ALB across many Ingresses, which matters for cost and limits in a multi-tenant cluster.
- **In-cluster controllers** (NGINX, Traefik, Envoy-based): one NLB in front, routing done in pods. The community `ingress-nginx` project has been retired, so expect migration questions.
- **Gateway API** is the successor: `GatewayClass` (infra provider) → `Gateway` (platform team owns listeners) → `HTTPRoute` (app team owns routes). The role split fits multi-tenant platforms well.
- **external-dns** syncs hostnames to Route 53; **cert-manager** or ACM handles certificates.

**Request path, internet to pod (EKS, ALB, ip mode):**
Route 53 → ALB (TLS terminate, listener rules) → pod IP in the VPC → container. In instance mode: ALB → NodePort → kube-proxy DNAT → pod.

---

### 6. EKS Specifics

- **Control plane** is managed and multi-AZ. You pay per cluster and never see etcd.
- **Compute options:** managed node groups (ASG-backed), self-managed nodes, Karpenter, Fargate (pod per micro-VM, no DaemonSets), EKS Auto Mode (AWS runs nodes and core add-ons).
- **Core add-ons:** VPC CNI, CoreDNS, kube-proxy, EBS CSI driver, Pod Identity agent. Managed as EKS add-ons with their own versions.
- **Cluster access:** IAM authenticates, Kubernetes RBAC authorizes. **Access entries** are the current way to map IAM principals; the `aws-auth` ConfigMap is the legacy way (and easy to break).
- **Endpoint access:** public, private, or both. Private-only is common for production.

**Upgrades (expect a "how do you upgrade a cluster" question)**

1. Read the release notes. Scan for removed APIs (`pluto`, `kubent`, EKS upgrade insights).
2. Upgrade a non-prod cluster first and let it soak.
3. Control plane first, **one minor version at a time**. It cannot be downgraded.
4. Add-ons (CNI, CoreDNS, kube-proxy, CSI) to compatible versions.
5. Data plane: roll node groups, or let Karpenter replace nodes by drift. PDBs and topology spread keep services up during drains.
6. Verify: node versions, pending pods, error rates, SLO burn.

- Kubelet may be older than the API server (skew policy), never newer.
- Standard support per version is about 14 months; extended support costs significantly more. Falling behind is a real cost issue.
- Alternative for risky jumps: **blue/green clusters**, shifting traffic by DNS weight. Easier when everything is in GitOps.

---

### 7. Security

**RBAC**

- `Role` / `ClusterRole` = verbs on resources. `RoleBinding` / `ClusterRoleBinding` = grant to a user, group, or ServiceAccount.
- A `RoleBinding` can reference a `ClusterRole`; this grants it in one namespace only. Good pattern for reusable tenant roles.
- Check with `kubectl auth can-i <verb> <resource> --as <subject> -n <ns>`.
- Dangerous grants: `*` on anything, `secrets` read, `pods/exec`, `escalate` / `bind` / `impersonate`, and create pods (lets you mount any secret or SA in the namespace).

**Pod to AWS identity**

| | IRSA | EKS Pod Identity |
|--|------|------------------|
| Mechanism | Cluster OIDC issuer is an IAM identity provider. SA is annotated with a role ARN. A webhook injects a projected SA token; the SDK calls `sts:AssumeRoleWithWebIdentity`. | Agent DaemonSet on each node. An association (cluster, namespace, SA → role) is created through the EKS API. |
| Trust policy | Per cluster OIDC provider, with `sub` condition `system:serviceaccount:<ns>:<sa>` | One generic trust to `pods.eks.amazonaws.com`, reusable across clusters |
| Notes | Works anywhere, including Fargate. OIDC provider per cluster; trust policy size limits bite at scale. | Simpler at fleet scale; supports session tags. |

Both give **per-ServiceAccount least privilege** instead of sharing the node instance role. Also block pod access to node IMDS (hop limit 1) so pods cannot fall back to the node role.

Debugging IRSA: check the SA annotation, check `AWS_ROLE_ARN` and `AWS_WEB_IDENTITY_TOKEN_FILE` in the pod, check the trust policy `sub` and `aud` conditions, check the SDK version, and confirm the pod was restarted after the annotation was added.

**NetworkPolicy**

- Pods are **allow-all by default**. A policy selecting a pod makes it default-deny for the listed direction; policies are additive allow-lists.
- Needs a CNI that enforces it (VPC CNI has built-in support; Calico and Cilium too).
- Standard baseline: default-deny ingress and egress per namespace, then explicit allows. **Remember to allow DNS egress** to kube-system, or everything breaks.
- L3/L4 only. L7 rules need Cilium or a service mesh.

**Pod Security Standards (PSS)**

- Three levels: `privileged`, `baseline` (blocks known privilege escalations), `restricted` (hardened: non-root, drop all capabilities, seccomp, no privilege escalation).
- Enforced by **Pod Security Admission** through namespace labels: `pod-security.kubernetes.io/enforce|audit|warn: <level>`. PodSecurityPolicy was removed in 1.25.
- For anything finer-grained (allowed registries, required labels, mutating defaults): **Kyverno**, **OPA Gatekeeper**, or built-in `ValidatingAdmissionPolicy` (CEL).
- Roll out with `warn` and `audit` first, then `enforce`.

**Secrets management**

| Approach | How |
|----------|-----|
| External Secrets Operator | Syncs AWS Secrets Manager / SSM / Vault into Kubernetes Secrets. |
| Secrets Store CSI Driver | Mounts secrets as files directly from the provider; optional sync to a Secret. |
| SOPS / Sealed Secrets | Encrypted secrets committed to Git; fits Flux well (Flux decrypts SOPS natively). |

Plus: KMS envelope encryption for etcd, tight RBAC on `secrets`, rotation, and never putting secrets in Helm values in plain text.

**Supply chain and runtime:** scan and sign images, run minimal images with a read-only root filesystem, and add runtime detection. See [EKS best practices: image security](https://docs.aws.amazon.com/eks/latest/best-practices/image-security.html), [cosign](https://docs.sigstore.dev/cosign/signing/overview/), [Falco](https://falco.org/docs/).

---

### 8. Multi-Tenancy

Guidewire runs a multi-tenant SaaS platform, so expect design discussion here.

| Model | Isolation | Cost / ops |
|-------|-----------|-----------|
| Namespace per tenant | Soft. Shared control plane, nodes and kernel. | Cheapest, densest |
| Node pool per tenant (taints + affinity) | Stronger compute isolation | More waste |
| Virtual clusters (vcluster) | Separate API server per tenant, shared nodes | Middle ground |
| Cluster per tenant | Hard isolation, per-tenant upgrades | Most expensive, needs fleet automation |

**Namespace tenancy checklist:** RBAC scoped per namespace, `ResourceQuota` + `LimitRange`, default-deny NetworkPolicy, PSS `restricted`, per-tenant IAM role via IRSA/Pod Identity, separate ingress hostnames, per-tenant cost and metrics labels, API Priority and Fairness to stop one tenant flooding the API server.

**Noisy neighbour sources:** CPU without requests, shared CoreDNS, shared ingress controller, API server load from a bad controller, disk IO and ephemeral storage, IP space.

**Blast radius thinking:** cells / shards of tenants, progressive rollout by cell, per-cell SLOs.

---

### 9. Helm

Moved to [helm.md](helm.md).

---

### 10. Operators, CRDs, Crossplane and KubeVela

**Operator = CRD + controller.** A `CustomResourceDefinition` extends the API with a new kind; a controller reconciles instances of it. It encodes operational knowledge (provision, upgrade, backup, failover) as code.

- Built with **controller-runtime / Kubebuilder / Operator SDK** (Go), or `kopf` (Python).
- Reconcile loops must be **idempotent** and level-based: read desired state, read actual, act, requeue.
- **Finalizers** block deletion until cleanup is done. A namespace or resource stuck in `Terminating` almost always means a finalizer whose controller is gone.
- **Owner references** drive garbage collection of child objects.
- `status` subresource and `conditions` report progress; `observedGeneration` shows whether the controller has seen the latest spec.
- **Admission webhooks** (validating / mutating) often ship with operators. A webhook with `failurePolicy: Fail` whose backing pods are down can block all matching API writes, a well-known cluster-wide outage cause.
- Leader election keeps one active replica.
- Examples: cert-manager, external-dns, Prometheus Operator, Strimzi (Kafka), External Secrets, Karpenter.

**Crossplane and KubeVela** (JD preferred, overview only)

- **[Crossplane](https://docs.crossplane.io/latest/):** manages cloud infrastructure through Kubernetes CRDs. You define your own platform API (an XRD such as `PostgresInstance`) and a Composition maps it to real AWS resources. Versus Terraform: continuous drift correction and no state file, but harder to debug.
- **[KubeVela](https://kubevela.io/docs/)** (implements [OAM](https://oam.dev/)): developers write one `Application` made of Components and Traits; platform engineers define what those expand to. A small app-centric API instead of raw YAML.

> **How to frame both:** they are platform-engineering tools for building an internal "paved road". If you have not used them, say so and connect them to what you know: Crossplane ≈ Terraform as a reconciling controller, KubeVela ≈ a higher-level abstraction over what you would otherwise template with Helm.

---

### 11. GitOps and FluxCD

**Principles:** desired state is declarative, versioned in Git, pulled automatically by an in-cluster agent, and continuously reconciled.

**Why pull beats push (CI running `kubectl apply`):** no cluster credentials in CI, drift is corrected, Git history is the audit log, rollback is `git revert`, and rebuilding a cluster is a bootstrap.

**Flux controllers and CRDs**

| Controller | CRDs | Job |
|-----------|------|-----|
| source-controller | `GitRepository`, `OCIRepository`, `HelmRepository`, `HelmChart`, `Bucket` | Fetches artifacts |
| kustomize-controller | `Kustomization` | Applies manifests (server-side apply), prunes, health-checks, decrypts SOPS |
| helm-controller | `HelmRelease` | Runs Helm install/upgrade/test/rollback declaratively |
| notification-controller | `Provider`, `Alert`, `Receiver` | Slack/Teams alerts, inbound webhooks |
| image-reflector / image-automation | [image CRDs](https://fluxcd.io/flux/components/image/) | Bumps image tags in Git |

**Key features to mention**

- `dependsOn` orders things (CRDs → controllers → apps).
- `prune: true` deletes what was removed from Git.
- `HelmRelease` remediation: retries and automatic rollback on failed upgrade; **drift detection** for Helm-managed objects.
- `valuesFrom` pulls values from ConfigMaps/Secrets; `postBuild.substituteFrom` injects per-cluster variables.
- Multi-tenancy: per-tenant `Kustomization` running under a restricted `serviceAccountName`.
- Repo layout: `clusters/<name>/` entry points, `infrastructure/`, `apps/` with base + overlays.

**Day-to-day commands**

```bash
flux get all -A
flux reconcile kustomization apps --with-source
flux suspend|resume helmrelease <name> -n <ns>     # pause during an incident
```

Full list: [Flux CLI reference](https://fluxcd.io/flux/cmd/).

**Flux vs [Argo CD](https://argo-cd.readthedocs.io/en/stable/):** Flux is CLI-first composable controllers doing real Helm releases; Argo CD has a strong UI and renders Helm to plain manifests.

**Progressive delivery:** [Flagger](https://docs.flagger.app/) (pairs with Flux) or [Argo Rollouts](https://argoproj.github.io/argo-rollouts/) for canaries with automated analysis and rollback.

---

### 12. Reliability Patterns

Checklist for a production-ready service on Kubernetes:

- At least 2 to 3 replicas, spread across AZs with `topologySpreadConstraints`.
- A `PodDisruptionBudget` that allows at least one disruption.
- Requests set from real usage; memory limit = request.
- Readiness, liveness and startup probes that mean something.
- Graceful shutdown: `preStop`, SIGTERM handling, sensible grace period.
- HPA with headroom; node autoscaling that can actually satisfy it.
- Rollout strategy that keeps capacity (`maxUnavailable: 0` for small replica counts) or a canary.
- Timeouts, retries with backoff and jitter, circuit breaking to dependencies.
- Dashboards, alerts tied to SLOs, and a runbook.

**Self-healing** (JD: "drive improvements toward self-healing systems") comes at several layers: the kubelet restarts containers, controllers replace pods, node auto-repair replaces nodes, GitOps reverts drift, and operators handle app-specific recovery. The lead-level point: self-healing hides problems unless you also alert on the healing rate (restarts, evictions, node replacements).

**Cluster-level failure modes worth being able to discuss**

| Failure | Effect |
|---------|--------|
| API server / etcd down | Running workloads keep serving. No scheduling, scaling, deploys or self-healing. |
| CoreDNS degraded | Widespread timeouts that look like app failures. |
| CNI / IP exhaustion | New pods cannot start; scale-out fails exactly when needed. |
| Admission webhook down with `Fail` policy | Pod creation blocked cluster-wide. |
| AZ outage | Survive only if replicas, nodes and volumes were spread; EBS-backed pods in that AZ are stuck. |
| Bad rollout pushed everywhere | Argument for progressive, cell-by-cell delivery. |
| Certificate expiry | Webhooks, ingress TLS, kubelet certs. |

---

### 13. Observability

**Three pillars plus events:** metrics, logs, traces, and Kubernetes events (kept only about 1 hour by default, so export them).

| Source | Gives you |
|--------|-----------|
| `metrics-server` | Live CPU/memory for `kubectl top` and HPA. Not a monitoring system. |
| `kube-state-metrics` | Object state: desired vs ready replicas, pod phase, restarts, job status. |
| cAdvisor (in kubelet) | Per-container CPU, memory, throttling, network, filesystem. |
| `node-exporter` | Node-level OS metrics. |
| API server metrics | Request rate, latency, errors, etcd latency, APF queueing. |

- **Prometheus Operator:** `ServiceMonitor` / `PodMonitor` select scrape targets, `PrometheusRule` holds alerts. Long-term storage via Thanos, Mimir, or Amazon Managed Prometheus.
- **Datadog:** Agent DaemonSet + Cluster Agent; autodiscovery by annotations; unified service tagging (`env`, `service`, `version`).
- **OpenTelemetry:** Collector as DaemonSet (agent) and/or Deployment (gateway); OTLP in, any backend out. The Operator can auto-instrument.
- **Logs:** stdout/stderr → node files → Fluent Bit DaemonSet → backend. Structured JSON logs with a trace ID.

**Signals to alert on**

- Service level: **RED** (rate, errors, duration) per service; SLO burn rate.
- Resource level: **USE** (utilisation, saturation, errors) per node.
- Kubernetes-specific: pods not ready vs desired, restart rate, `OOMKilled`, CPU throttling ratio, pending pods, node `NotReady`, PVC (Persistent Vol Claim) usage, HPA at max replicas, certificate expiry, free IPs per subnet.

**SLOs:** SLI = good events / valid events. Error budget = 1 − SLO (99.9% over 30 days ≈ 43 minutes). **Multi-window, multi-burn-rate alerts**: page on fast burn (e.g. 14.4× over 1h and 5m), ticket on slow burn (e.g. 1× over 3 days). The error budget is also the tool for negotiating release pace with product teams.

---

## Part 2: Troubleshooting

### 14. Method

Go outside-in and narrow down:

1. **What changed?** Deploys, Flux reconciliations, node replacements, config, upstream.
2. **Scope:** one pod, one node, one AZ, one namespace, the whole cluster?
3. `kubectl get` → `describe` (read the **Events** at the bottom) → `logs` (`--previous` for the crashed container) → `exec` / `debug`.
4. Mitigate first (rollback, scale, shift traffic), root-cause after.

### 15. Symptom Playbook

| Symptom | Likely causes | Check |
|---------|---------------|-------|
| `Pending` | Not enough CPU/memory, taints, affinity, PVC (Presistent Vol Claim) unbound or wrong AZ, quota exceeded, max pods per node | `describe pod` events; `kubectl get events`; Karpenter / autoscaler logs |
| `ContainerCreating` (stuck) | CNI cannot assign IP, volume attach/mount failure, missing Secret/ConfigMap | Events; `aws-node` logs; subnet free IPs |
| `ImagePullBackOff` | Wrong tag, registry auth, ECR permissions on node role, rate limit, no network path | Events show the exact error |
| `CrashLoopBackOff` | App crashes on start, bad config, missing dependency, liveness probe too aggressive | `logs --previous`; exit code; `describe` last state |
| `OOMKilled` (137) | Memory limit too low, leak, JVM heap not sized to the container | `describe` last state; memory graphs; node-level OOM in `dmesg` |
| Running but not Ready | Readiness probe failing, dependency down | Probe config; `exec` and curl the endpoint |
| `Evicted` | Node memory or disk pressure | `describe node` conditions; ephemeral storage |
| Stuck `Terminating` | Finalizers, unresponsive node, long grace period | `get -o yaml` finalizers; node status |
| Service unreachable | Selector does not match labels, no ready endpoints, wrong `targetPort`, NetworkPolicy | `kubectl get endpointslices`; test from a debug pod |
| Intermittent 5xx during deploys | Shutdown race, missing readiness gates, deregistration delay | See graceful shutdown in section 2 |
| 502/503/504 at ALB | Unhealthy targets, SG blocks ALB → pod, idle timeout mismatch (app keep-alive shorter than ALB's 60s) | Target group health; ALB logs |
| DNS failures | CoreDNS overloaded, `ndots`, NetworkPolicy blocks port 53 | `nslookup` from a pod; CoreDNS metrics and logs |
| High latency, CPU looks fine | CPU throttling, noisy neighbour, conntrack exhaustion | `container_cpu_cfs_throttled_periods_total`; node metrics |
| Node `NotReady` | Kubelet down, disk/memory/PID pressure, network partition, instance failure | `describe node`; SSM into node; `journalctl -u kubelet` |
| AWS `AccessDenied` from pod | IRSA / Pod Identity misconfigured, falling back to node role | See IRSA debugging in section 7 |
| HPA not scaling | No requests set, metrics-server down, already at max, metric missing | `describe hpa` conditions |
| Flux not applying | Source fetch failed, build error, health check timeout, dependency not ready, suspended | `flux get all -A`; `describe` the Kustomization / HelmRelease |

### 16. kubectl Cheat Sheet

The basics are in the official [kubectl quick reference](https://kubernetes.io/docs/reference/kubectl/quick-reference/) and [debugging guide](https://kubernetes.io/docs/tasks/debug/debug-application/). The ones worth memorising for incidents:

```bash
kubectl get events -A --sort-by=.lastTimestamp | tail -30
kubectl logs <p> -c <container> --previous
kubectl get pod <p> -o jsonpath='{.status.containerStatuses[*].lastState}'
kubectl debug -it <p> --image=nicolaka/netshoot --target=<container>   # ephemeral container
kubectl debug node/<node> -it --image=busybox                          # node shell
kubectl rollout status|history|undo|restart deploy/<d>
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data
kubectl auth can-i --list --as system:serviceaccount:<ns>:<sa>
```

---

Interview questions, answer outlines and stories to prepare: [kubernetes_interview.md](kubernetes_interview.md)
