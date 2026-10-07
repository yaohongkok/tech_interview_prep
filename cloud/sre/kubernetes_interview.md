# Kubernetes & Helm: Interview Questions for Lead SRE (Platform)

Companion to [kubernetes.md](kubernetes.md). "Section N" in the answer outlines refers to the numbered sections in that file; Helm is in [helm.md](helm.md).

---

## 1. Likely Questions with Answer Outlines

**Fundamentals**

1. *What happens when you run `kubectl apply` for a Deployment?* Section 1 chain.
2. *Deployment vs StatefulSet vs DaemonSet?* Section 2 table. Add when you would not run stateful workloads in Kubernetes at all (prefer RDS/Aurora, MSK).
3. *Requests vs limits, and what happens when each is exceeded?* Throttle vs OOMKill; QoS; scheduling is by requests.
4. *Liveness vs readiness vs startup?* Restart vs remove from endpoints vs delay the others. Name the downstream-dependency anti-pattern.
5. *How does a Service route traffic?* Label selector → EndpointSlices → kube-proxy rules → per-connection balancing.

**Networking / EKS**

6. *How does pod networking work on EKS?* VPC CNI, ENIs, real VPC IPs, max pods, prefix delegation.
7. *You are running out of IPs. What do you do?* Prefix delegation, secondary CIDR with custom networking, tune warm pool, IPv6. Monitor free IPs per subnet.
8. *Trace a request from the internet to a pod.* Section 5 path. Say where TLS terminates and which security groups apply.
9. *Ingress vs Gateway API? ALB vs in-cluster NGINX?* Role separation; cost and feature trade-offs; shared ALB via IngressGroup.
10. *How does a pod get AWS permissions?* IRSA mechanics end to end, then Pod Identity as the newer option.

**Security / multi-tenancy**

11. *How would you isolate tenants on a shared cluster?* Section 8 checklist, then when you would move to node or cluster isolation (compliance, noisy neighbour, blast radius).
12. *How do you manage secrets?* External source of truth + ESO or CSI, KMS encryption, RBAC, rotation.
13. *How do you roll out Pod Security Standards to an existing cluster?* Audit and warn first, fix offenders, enforce per namespace, exemptions for system namespaces.

**Helm / GitOps**

14. *How does `helm upgrade` work, and how do you recover a failed one?* Three-way merge, release Secrets, `--atomic`, `helm rollback`, stuck `pending-upgrade`.
15. *How do you manage one chart across many environments and tenants?* Layered values files, schema validation, Flux `HelmRelease` + `valuesFrom`, chart versioning and promotion through environments.
16. *How do you handle CRDs in Helm?* `crds/` limitations; separate CRD chart or Flux CRD policy; order with `dependsOn`.
17. *Push-based CD vs GitOps?* Section 11. Mention break-glass: `flux suspend`, fix, then back-port to Git.

**Operations / design**

18. *How do you upgrade EKS with zero downtime?* Section 6 steps.
19. *How do you do zero-downtime deployments?* Rolling update settings, readiness, graceful shutdown, PDBs, then canary with automated analysis.
20. *Cluster Autoscaler vs Karpenter?* Section 4.
21. *Pods are restarting across the cluster. Walk me through it.* Scope first, events, `logs --previous`, exit codes, what changed, mitigate.
22. *Latency went up after a deploy but CPU is fine.* Throttling, GC, connection pools, DNS, downstream; compare canary vs baseline.
23. *What is an operator and when would you write one?* Section 10. When ops knowledge is repetitive and stateful; not when a Helm chart or Job will do.
24. *Design a platform that lets product teams self-serve deployments.* Golden-path chart or OAM abstraction, GitOps, policy guardrails (Kyverno), per-team namespaces with quotas, built-in observability and SLO templates, Crossplane for infra claims.
25. *How do you define SLOs for the platform itself?* API server availability and latency, pod startup time, deploy success rate and lead time, ingress availability, DNS success rate.

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
