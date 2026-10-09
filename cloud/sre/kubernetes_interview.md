# Kubernetes & Helm: Interview Questions for Lead SRE (Platform)

Companion to [kubernetes.md](kubernetes.md). "Section N" in the answer outlines refers to the numbered sections in that file; Helm is in [helm.md](helm.md).

---

## 1. Likely Questions with Answer Outlines

**Fundamentals**

1. *What happens when you run `kubectl apply` for a Deployment?*
    <details><summary>Answer</summary>

    - kubectl sends the manifest to the API server: authentication, RBAC authorisation, mutating then validating admission, then persisted to etcd.
    - Deployment -> ReplicaSet -> Pods -> Node assignment
    - Kubelet on that node: pulls images (CRI), gets a pod IP (CNI), starts containers, runs probes.
    - Pod is added to EndpointSlices -> kube-proxy updates rules.
    - Key point: no component calls another. Each controller watches the API and reconciles.

    </details>

2. *Deployment vs StatefulSet vs DaemonSet?* 
    <details><summary>Answer</summary>

    - **Deployment:** stateless, interchangeable pods; rolling updates through ReplicaSets.
    - **StatefulSet:** stable identity (`pod-0`), stable DNS via a headless Service, one PVC per pod, ordered start and update. For databases and quorum systems.
    - **DaemonSet:** one pod per matching node. For node agents: CNI, log shippers, node-exporter.
    - Prefer a managed service (RDS/Aurora, MSK) for state: backups, failover and patching become someone else's toil. Run it in-cluster only with a mature operator and a team that owns it.

    </details>

3. *Requests vs limits, and what happens when each is exceeded?* 
    <details><summary>Answer</summary>

    - **Requests:** what the scheduler uses to place the pod; also the CPU share under contention.
    - **Limits:** enforced at runtime by cgroups.
    - CPU over limit: throttled, not killed. Shows up as latency.
    - Memory over limit: OOMKilled (exit 137) and restarted.
    - Over request but under limit: fine until the node is under pressure, then evicted by QoS order: BestEffort, Burstable, Guaranteed (requests = limits).
    - Practice: set memory request = limit; always set CPU requests; consider no CPU limit to avoid throttling.

    </details>

4. *Liveness vs readiness vs startup?* Restart vs remove from endpoints vs delay the others. Name the downstream-dependency anti-pattern.
    <details><summary>Answer</summary>

    - **Liveness** fails: kubelet restarts the container. For deadlocks.
    - **Readiness** fails: pod is removed from Service endpoints, not restarted. For temporary inability to serve.
    - **Startup:** holds off the other two until it passes. For slow starters, instead of a long `initialDelaySeconds`.
    - Anti-pattern: checking a downstream dependency (e.g. the database) in liveness. One dependency outage restarts every pod and cascades. In readiness it removes all pods at once.
    - Keep liveness local and cheap.

    </details>

5. *How does a Service route traffic?* Label selector → EndpointSlices → kube-proxy rules → per-connection balancing.
    <details><summary>Answer</summary>

    - A Service is a stable ClusterIP and DNS name with a label selector.
    - The EndpointSlice controller tracks the IPs of Ready pods that match.
    - kube-proxy on every node programs iptables or IPVS (eBPF with Cilium) to DNAT the ClusterIP to a pod IP.
        - **Pod IP:** a real address on the pod's network interface, routable across the cluster. Ephemeral: it changes whenever the pod is replaced.
        - **ClusterIP:** a virtual IP from the Service CIDR, stable for the life of the Service. No interface owns it.
    - Balancing is L4 and per connection, so long-lived connections (gRPC, HTTP/2) do not rebalance. Fix with an L7 proxy or mesh, or a headless Service with client-side balancing.
    - Types: ClusterIP, NodePort, LoadBalancer; headless returns pod IPs directly.

    </details>

**Networking / EKS**

6. *How does pod networking work on EKS?* 
    <details><summary>Answer</summary>

    - The VPC CNI (`aws-node` DaemonSet) attaches ENIs to the node and gives pods secondary IPs from them.
    - Pods get real VPC IPs: no overlay, native routing, flow logs, and ALBs can target pods directly.
    - Cost: it is IP hungry. Max pods per node is bounded by ENIs × IPs per ENI for the instance type.
    - *Prefix delegation* assigns a /28 per IP slot, raising pod density a lot.
    - A warm pool keeps spare IPs so pods start fast.
    - Security groups for pods and NetworkPolicy are both available.

    </details>

7. *You are running out of IPs (on subnet). What do you do?* Prefix delegation, secondary CIDR with custom networking, tune warm pool, IPv6. Monitor free IPs per subnet.
    <details><summary>Answer</summary>

    - Confirm first: free IPs per subnet, and how many are held idle in warm pools (the default keeps a whole spare ENI per node).
        - Free IPs per subnet: `aws ec2 describe-subnets --filters "Name=vpc-id,Values=<vpc-id>" --query 'Subnets[].[SubnetId,AvailabilityZone,CidrBlock,AvailableIpAddressCount]' --output table`
        - Warm pool settings: `kubectl describe ds aws-node -n kube-system | grep -E 'WARM|MINIMUM|PREFIX'`
        - Assigned vs in-use IPs on a node (run on the node): `curl -s http://localhost:61679/v1/enis`
    - Quick win: set `WARM_IP_TARGET` / `MINIMUM_IP_TARGET` to stop hoarding.
      - A node holds `max(MINIMUM_IP_TARGET, pods + WARM_IP_TARGET)`
    - Medium term: add a secondary CIDR (100.64.0.0/10) with custom networking so pods use different subnets from nodes.
    - Prefix delegation raises density but needs contiguous /28 blocks, so it fails in fragmented subnets.
    - Long term: IPv6 clusters.
    - Prevent recurrence: alert on free IPs per subnet.

    </details>

8. *Trace a request from the internet to a pod.* 
    <details><summary>Answer</summary>

    - Route 53 resolves to an ALB in public subnets. WAF and TLS termination (ACM certificate) happen here.
    - Listener rule picks a target group. IP mode goes straight to the pod IP; instance mode goes to a NodePort, then a kube-proxy hop.
    - Security groups: ALB SG allows 443 from the internet; node or pod SG allows the app port from the ALB SG only.
    - NetworkPolicy must also allow it.
    - If end-to-end encryption is required: re-encrypt ALB to pod, or mTLS in a mesh.
    - Pod readiness gates keep the ALB and Kubernetes in agreement about health.

    </details>

9. *Ingress vs Gateway API? ALB vs in-cluster NGINX?* Role separation; cost and feature trade-offs; shared ALB via IngressGroup.
    <details><summary>Answer</summary>

    - **Ingress:** one resource, HTTP only, anything advanced is controller-specific annotations.
    - **Gateway API:** GatewayClass (provider), Gateway (platform team), HTTPRoute (app team). Role separation, cross-namespace routes, native traffic splitting.
    - **ALB:** managed, no in-cluster data plane, WAF and ACM built in. Costs per ALB, so share one with IngressGroup; has rule limits.
    - **In-cluster proxy:** one NLB in front, richer routing, cheaper at scale. You own patching and scaling, and it is a shared failure point.
    - Community ingress-nginx was retired in March 2026, so new builds should target Gateway API.

    </details>

10. *How does a pod get AWS permissions?* IRSA (OIDC, IAM, ARN, STS). Pod Identity (EKS).
    <details><summary>Answer</summary>

    - **IRSA:** the cluster's OIDC issuer is registered as an IAM identity provider.
    - The ServiceAccount is annotated with a role ARN; a webhook injects a projected token and the AWS env vars.
    - The SDK calls `sts:AssumeRoleWithWebIdentity`; the role's trust policy checks issuer and `system:serviceaccount:<ns>:<name>`.
    - Result: short-lived credentials per service account, not the node role.
    - **Pod Identity:** an agent add-on plus an association made through the EKS API. No OIDC provider per cluster, the same role is reusable across clusters, and session tags allow ABAC.
    - Also block pod access to node IMDS.

    </details>

**Security / multi-tenancy**

11. *How would you isolate tenants on a shared cluster?* 
    <details><summary>Answer</summary>

    - **Namespace** per tenant as the unit of isolation.
    - RBAC scoped to the namespace; no cluster-wide roles for tenants.
    - Default-deny **NetworkPolicy**, then explicit allows.
    - ResourceQuota and LimitRange.
    - **Pod Security Standards** at restricted, plus Kyverno for registries, hostPath and similar.
    - A separate IAM role per service account.
    - Namespaces are soft isolation: the kernel, API server and CRDs are still shared.
    - Step up to *dedicated node* pools for noisy neighbours or container-escape risk; *dedicated clusters or accounts* for compliance, untrusted tenants, or blast radius.

    </details>

12. *How do you manage secrets?* External source of truth + ESO or CSI, KMS encryption, RBAC, rotation.
    <details><summary>Answer</summary>

    - Source of truth outside the cluster (Secrets Manager, Vault); never plaintext in Git.
    - Sync with External Secrets Operator (creates Secrets) or the Secrets Store CSI driver (mounts files, no Secret object).
    - Envelope-encrypt etcd with KMS. Envelope-encrypt: main data encrypt with DEK & DEK is encrypt with KEK (the final key stored in KMS). Encrypted DEK can be stored in etcd.
    - RBAC: restrict `get`/`list` on secrets. Anyone who can create pods in a namespace can read its secrets.
    - Rotation: rotate at the source and let ESO refresh. Mounted files update but env vars do not, so trigger a rolling restart.
    - Best: short-lived credentials (IRSA, IAM database auth) so there is nothing to store.

    </details>

13. *How do you roll out Pod Security Standards to an existing cluster?* Audit and warn first (similar to WAF), fix offenders, enforce per namespace, exemptions for system namespaces.
    <details><summary>Answer</summary>

    - Pod Security Admission is built in and driven by namespace labels: `enforce`, `audit`, `warn`, at privileged, baseline or restricted.
    - Start with `audit` and `warn` at the target level. Nothing breaks.
    - Enforce *namespace by namespace*, baseline first, then restricted.
    - Exempt system namespaces (CNI and CSI need privileges).
    - Collect violations from audit logs; a server-side dry-run of the `enforce` label lists pods that would fail.
    - Fix workloads, ideally once in the shared chart: non-root, drop capabilities, seccomp, no privilege escalation.
    - Enforce only affects new pods; use Kyverno for fine-grained exceptions.

    </details>

**Helm / GitOps**

14. *How does `helm upgrade` work, and how do you recover a failed one?* Three-way merge, release Secrets, `--atomic`, `helm rollback`, stuck `pending-upgrade`.
    <details><summary>Answer</summary>

    - Helm renders the templates into new manifests, then compares three things: (1) what it applied last time, (2) what it is about to apply, and (3) what is running in the cluster now (the three-way merge).
    - It only patches what changed between the last release and the new one. Fields the chart does not set are left alone, so a manual `kubectl edit` to one of them survives the upgrade.
    - Each revision is stored as a Secret in the release namespace.
        - Why a Secret: the record holds the full rendered manifests and the supplied values, which often include credentials, so it gets Secret-level RBAC and encryption at rest (Helm 2 used ConfigMaps, readable by far more users).
    - `--atomic` (Helm 4: `--rollback-on-failure`) waits for readiness and rolls back automatically on failure.
    - Manual recovery: `helm history`, then `helm rollback <release> <revision>`.
    - Stuck in `pending-upgrade` (the process died mid-upgrade): roll back to the last deployed revision, or delete the pending release Secret.
    - Rollback *does not* undo *CRD changes, data migrations or hook side effects*.

    </details>

15. *How do you manage one chart across many environments and tenants?* Layered values files, schema validation, Flux `HelmRelease` + `valuesFrom`, chart versioning and promotion through environments.
    <details><summary>Answer</summary>

    - **One chart**, SemVer versioned, published to an OCI registry. Never fork per environment.
    - **Layered values**: chart defaults → environment → region → tenant, later wins.
    - `values.schema.json` fails fast on bad input; CI runs `helm lint`, `helm template` with kubeconform, and policy checks.
    - Flux: one `HelmRelease` per tenant, with shared layers pulled in through `valuesFrom`. Generate them from a tenant list.
    - Promotion: bump the chart version dev → staging → prod by PR. Same artefact, only values differ.
    - Keep the values surface small; too many knobs is a fork in disguise.

    </details>

16. *How do you handle CRDs in Helm?* `crds/` limitations; separate CRD chart or Flux CRD policy; order with `dependsOn`.
    <details><summary>Answer</summary>

    - The `crds/` directory is installed on first install only: never upgraded, never deleted, not templated. 
    - Option 1: a separate CRD chart with CRDs as normal templates. Upgradeable, but uninstall deletes the CRDs and every custom resource, so add the keep resource policy.
    - Option 2: apply CRDs outside Helm with server-side apply or a Flux Kustomization.
    - Flux can resolve this limitation: `install.crds` / `upgrade.crds: CreateReplace` on the `HelmRelease`.
    - Order with `dependsOn`: CRDs, then operator, then custom resources.
    - Watch stored versions when removing an old API version.

    </details>

17. *Push-based CD vs GitOps?* Section 11. Mention break-glass: `flux suspend`, fix, then back-port to Git.
    <details><summary>Answer</summary>

    - **Push:** the CI pipeline runs `helm` or `kubectl` against the cluster. Simple, with immediate feedback. But CI holds cluster credentials, there is no drift detection, and the cluster diverges from Git over time.
    - **GitOps:** an in-cluster agent pulls from Git and reconciles continuously. Git is the audit log and the rollback; no inbound credentials; drift is corrected; scales to many clusters.
    - Costs of GitOps: feedback is asynchronous, so you need notifications back to the PR; secrets and cross-dependency ordering need a pattern.
    - Break-glass: `flux suspend`, fix by hand, back-port to Git, `flux resume`. Otherwise Flux reverts the fix. Mainly for disaster recovery. May introduce drift again.

    </details>

**Operations / design**

18. *How do you upgrade EKS with zero downtime?* 
    <details><summary>Answer</summary>

    - Prepare: release notes, scan for removed APIs (EKS upgrade insights, pluto), check add-on and controller compatibility, rehearse in a lower environment.
    - *Control plane* first, one minor version at a time. It is upgraded in place and the API stays up.
    - Then add-ons: *VPC CNI, CoreDNS, kube-proxy, then controllers*.
    - Then *nodes*: new node groups or Karpenter drift, draining with PDBs (Pod Disruption Budget) respected and surge capacity available.
    - Workloads need 2+ replicas, PDBs, readiness probes, graceful shutdown.
    - Across the fleet: canary cluster first, watch SLOs between waves.
    - The control plane cannot be rolled back, so rehearsal matters.

    </details>

19. *How do you do zero-downtime deployments?* Rolling update settings, readiness, graceful shutdown, PDBs, then canary with automated analysis.
    <details><summary>Answer</summary>

    - **Rolling update** with `maxUnavailable: 0` and a surge, so capacity never drops. Add new apps, then drop old ones. Lastly, turn on feature via config.
    - Graceful shutdown: a `preStop` sleep so endpoints and the load balancer deregister before SIGTERM, the app drains in-flight requests, and `terminationGracePeriodSeconds` exceeds the drain time.
    - With ALB IP targets: pod readiness gates, and deregistration delay aligned with the above.
    - PDBs protect against node drains during the rollout.
    - Apps should have backwards-compatible schema and API changes (expand, then contract).
    - Next level: canary with Flagger or Argo Rollouts, automated analysis and rollback.
    - Readiness probe gates traffic; `minReadySeconds` catches pods that crash soon after start.

    </details>

20. *Cluster Autoscaler vs Karpenter?* Section 4.
    <details><summary>Answer</summary>

    - **Cluster Autoscaler:** scales Auto Scaling Groups. Needs node groups predefined per instance shape and AZ; slower; many groups to maintain. Predictable and cloud-neutral.
    - **Karpenter:** reads pending pods' requirements and launches right-sized instances directly, from many instance types, across spot and on-demand. Configured by NodePool and EC2NodeClass.
    - Karpenter also consolidates under-used nodes and replaces drifted or expired ones, which handles AMI rollouts.
    - Cost: more disruption. You need PDBs, disruption budgets, and `do-not-disrupt` for sensitive pods.
    - On EKS I would pick Karpenter, running the controller itself on a small managed node group.

    </details>

21. *Pods are restarting across the cluster. Walk me through it.* Scope first, events, `logs --previous`, exit codes, what changed, mitigate.
    <details><summary>Answer</summary>

    - Scope: every namespace or one? One node, AZ or node pool? One image? Since when?
    - Look: pods sorted by restart count, events sorted by time, `describe pod` for last state and reason.
    - Exit code: 137 is OOMKilled or a liveness kill, 143 is SIGTERM, 1 is an app error. Then `logs --previous`.
    - **Cluster-wide suspects**: 
      1. node pressure, node churn (spot, consolidation), 
      2. liveness probes tied to a shared dependency, 
      3. CoreDNS, 
      4. IP exhaustion, 
      5. a bad DaemonSet or sidecar rollout.
    - What changed: deploys, config, node AMI, cluster upgrade.
    - Mitigate first (**roll back, scale out**), then root-cause.

    </details>

22. *Latency went up after a deploy but CPU is fine.* Throttling, GC, connection pools, DNS, downstream; compare canary vs baseline.
    <details><summary>Answer</summary>

    - Check for CPU  **throttling**. See if pod CPU has flatten out. Check throttled periods: a lower limit or more threads gives p99 spikes at low average usage.
    - Look out for **downstream** dependency latency.
    - Use *traces* to see whether time is in the app or downstream.
    - **Other suspects**: 
      1. Noisy neighbors
      1. Single thread saturation. Look at event log lap or thread metrics.
      2. Connection or thread pool saturation or lost keep-alive;
      2. Rate limiting or API gateqay queue problems. 
      3. DNS (`ndots:5`, CoreDNS latency); 
      4. a new downstream call or N+1 query; 
      5. changed retries or timeouts; 
      6. cold caches.
      7. GC pauses near the memory limit;
    - Diff the deploy: code, config, resource settings, sidecar versions.
    - If the SLO is burning, roll back first and investigate afterwards.

    </details>

23. *What is an operator and when would you write one?* When ops knowledge is repetitive and stateful; not when a Helm chart or Job will do.
    <details><summary>Answer</summary>

    - A **CRD plus a controller**: the custom resource declares desired state and the controller reconciles towards it in a loop. Operational knowledge as code.
    - Good for **stateful lifecycle**: provisioning, failover, backup, upgrades (Postgres operators, cert-manager).
    - Write one when the work is *repetitive*, must react to *state changes* continuously, and cannot be expressed as static manifests.
    - Do **not** when a **Helm chart, Job or CronJob will do**, or an existing operator or Crossplane composition covers it.
    - It is software you own: API versioning, upgrades, RBAC blast radius, testing, on-call.
    - Reconcile must be **idempotent** and **level-triggered** (i.e. when `desired_state != actual_state`).

    </details>

24. *Design a platform that lets product teams self-serve deployments.* 
    <details><summary>Answer</summary>

    - *Interface:* a small app spec (image, port, replicas, resources) through a **golden-path chart** or KubeVela Application. The platform expands it into Deployment, Service, HPA, PDB, ingress and monitors.
    - *Delivery:* **GitOps** (Flux). A PR is the interface, with promotion across environments.
    - *Tenancy:* **namespace per team** and **environment**, with quotas, RBAC and default-deny networking, created by automation at onboarding.
    - *Policy Guardrails:* Kyverno automatically enforces cluster rules by validating, mutating, or generating Kubernetes resources at admission, replacing manual reviews with YAML policies.
    - *Infrastructure:* **Crossplane** claims let developers self-serve cloud databases, buckets, and queues via kubectl/GitOps, without tickets or separate Terraform pipelines.
    - *Built in:* dashboards, alerts, SLO templates, logs, tracing.
    - Gather dev team feedback; Allow escape hatches; Measure onboarding time, lead time and ticket volume.

    </details>

25. *How do you define SLOs for the platform itself?* API server availability and latency, pod startup time, deploy success rate and lead time, ingress availability, DNS success rate.
    <details><summary>Answer</summary>

    - Start from the *product team's* view: can they deploy, and do their workloads run and receive traffic?
    - Metrics: **USE** (Util, Sat, Err) & **RED** (Rate, Err, Duration)
    - SLIs: 
      - API server availability and latency; 
      - pod startup time, including node provisioning; 
      - deploy success rate and lead time from merge to running; 
      - ingress availability and latency; 
      - DNS success rate.
    - Measure with synthetic probes as well as real traffic.
    - Set targets from historical data, while moving slowly to aspiration.
    - **Alert** on multi-window burn rate; an *error budget policy pauses platform changes* when the budget is spent.
    - Keep platform SLOs separate from tenant app SLOs and exclude tenant-caused failures.

    </details>

## 2. Lead-Level Framing

Interviewers for a Lead role listen for judgement, not only recall:

- **Trade-offs.** Say what you would pick, why, and what it costs. "It depends" should be followed by what it depends on.
- **Scale and blast radius.** How does this behave with hundreds of tenants and many clusters? What breaks first?
- **Toil reduction.** Tie answers to automation: what did you remove from a human's plate?
- **Production readiness.** How would another team know their service is ready? Checklists, policy, paved roads.
- **Incidents.** Mitigate, communicate, then root-cause; blameless postmortem with tracked actions.
- **Honesty about gaps.** For KubeVela or Crossplane, state your exposure level and reason from fundamentals.

## 3. Stories to Prepare (fill in from your own experience)

Use STAR, with numbers where possible.

- [ ] A Kubernetes production incident you debugged: symptom, how you narrowed it, fix, prevention.
- [ ] A Helm chart you built or refactored: why, structure, how it was rolled out.
- [ ] A cluster or major component upgrade you ran.
- [ ] Something manual you automated, and the time saved.
- [ ] A reliability improvement you drove with a measurable result (SLO, MTTR, page volume).
- [ ] A time you influenced a development team's design.
- [ ] How you have used AI tools to work faster (the JD asks for this explicitly).

## 4. Questions to Ask Them

- How is tenancy modelled: namespaces, clusters, or cells? How many clusters does the platform team run?
- What does the paved road for a product team look like today, and where does KubeVela or Crossplane fit?
- How are EKS upgrades done across the fleet, and how often?
- What are the platform's SLOs, and who owns the error budget?
- What does the follow-the-sun rotation look like, and what is the page volume?
- What is the largest source of toil for the team right now?
