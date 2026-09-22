# DevSecOps Interview Q&A

## 1. How would you secure a CI/CD pipeline end to end? (Cover source, build, artifact, deploy, runtime.)

I treat the pipeline as production infrastructure and secure each stage. 

**Source:** enforce branch protection, mandatory code review, signed commits, and pre-commit/push secret scanning; use least-privilege repo access with SSO and MFA. 

**Build:** run on ephemeral, isolated runners with no long-lived credentials; pin dependencies and base images by digest, run SAST, SCA and IaC scanning, and keep pipeline definitions themselves under review so a PR cannot silently change the security checks.

**Artifact:** generate an SBOM (software bill of material), scan images for vulnerabilities, then sign artifacts (Sigstore/cosign) and record build provenance (SLSA). Store them in a private registry with immutable tags and access controls. 

**Deploy:** the cluster admission controller (Kyverno/OPA Gatekeeper) only admits signed images from trusted registries that meet policy. Use GitOps or short-lived OIDC-federated credentials for deployment rather than static keys, and require approvals for production.

**Runtime:** apply Pod Security standards, network policies, read-only root filesystems and non-root users, and monitor with runtime detection (Falco, cloud-native threat detection) plus centralized logging and alerting. Run DAST against staging and continuously rescan deployed images, since new CVEs appear after release. 

The overarching principles are least privilege, verifiable provenance, and fast feedback so findings reach developers early.

## 2. Difference between SAST, DAST, IAST and SCA, and where each fits in the pipeline?

**SAST (Static Application Security Testing)** (static analysis) inspects source code without running it to find flaws such as injection or insecure crypto use. It fits at the IDE, pre-commit and pull-request stages and gives fast, line-level feedback, but it can produce false positives and cannot see runtime or configuration issues. Example: SonarQube.

**SCA** (software composition analysis) inventories third-party and open-source dependencies and matches them against known CVEs and license rules. It also runs at PR and build time, and it generates the SBOM. Example: Dependabot.

**DAST (Dynamic Application Security Testing)** tests a running application from the outside, black-box style, by sending crafted requests to find issues like XSS, auth flaws and misconfigurations. It needs a deployed environment, so it belongs in staging/QA (or against ephemeral preview environments), and it is slower but has few false positives because it proves exploitability. Example: OWASP ZAP.

**IAST (Interactive Application Security Testing)** places an agent inside the running app, typically during functional or integration tests, and observes code paths and data flow in real time. It combines SAST's code-level precision with DAST's runtime context, but it depends on test coverage and language support. Example: DongTai IAST (open source; most other IAST tools, such as Contrast Assess, are commercial).

In practice they are complementary, not interchangeable: SAST and SCA "shift left" for cheap early fixes, while DAST and IAST validate real behavior later. I would add *secret scanning, IaC and container scanning* alongside them, and tune each tool's severity thresholds to *keep noise low*.

## 3. How do you handle secrets in pipelines and Kubernetes? (Vault, OIDC, sealed/external secrets, rotation.)

The first goal is to eliminate long-lived secrets. 
  - In pipelines I use **OIDC federation** so the CI job exchanges its signed identity token for short-lived cloud credentials (AWS IAM roles, Azure and GCP workload identity) scoped to a specific repo, branch and environment. Use AWS Security Token Service (STS).
  - Where a secret is truly needed, I fetch it at runtime from a central manager such as HashiCorp Vault or **AWS Secrets Manager**, mask it in logs, and never bake it into images or repos. Secret scanning (pre-commit and in CI) catches accidents.

In Kubernetes, native Secrets are only base64-encoded, so I enable **etcd encryption** at rest, restrict access with RBAC, and avoid putting plaintext in Git. 

For GitOps I use **Sealed Secrets** or SOPS to commit encrypted values, or the **External Secrets Operator** / Secrets Store CSI driver to sync from Vault or a cloud secret manager. 

Pods authenticate using workload identity (IRSA, Vault Kubernetes auth) rather than static credentials, and Vault dynamic secrets give each workload unique, short-lived database credentials.

**Rotation and auditing** complete the picture: automate rotation on a schedule and on any suspected exposure, design apps to reload secrets without restarts, and audit every access. Short TTLs limit the blast radius, so a leaked credential expires quickly, which shrinks response time.

## 4. How do you balance security gates with developer velocity? (Risk-based thresholds, fast feedback, champions.)

- Gates should be **risk-based**: only block on high-confidence, high-severity findings (critical/high with a known exploit or reachable code path, exposed secrets, unsigned images), while lower-severity issues create tracked tickets with SLAs instead of failing the build. 
- **Onboarding** process: I start new controls in *audit/warn mode*, *measure* false-positive rates, *tune* rules, and only then *enforce* them, so developers trust the tools.
- **Fast feedback** matters most. Put lightweight checks (secret scan, SAST on changed files, SCA) in the IDE and PR where fixes are cheap, run heavy scans (full DAST, deep scans) asynchronously or nightly, and cache results to keep pipelines fast. Findings should appear in the tools developers already use, with clear remediation guidance, auto-generated fix PRs (Dependabot/Renovate), and secure-by-default templates and "paved roads" that make the safe path the easy path.
- Culturally, I build a **security champions** program embedded in teams, share success stories transparently.
- Also, provide a documented exception process with expiry dates and risk acceptance for cases where a gate must be bypassed. I track pipeline duration and deployment frequency alongside security metrics to make sure controls aren't quietly degrading delivery.

## 5. Walk through responding to a leaked credential or a critical CVE like Log4Shell. (Detect, scope via SBOM, contain, rotate, patch, post-mortem.)

**Leaked credential:** 
  1. detect and confirm (secret scanning alert, cloud provider notice, anomalous activity in logs). 
  2. Contain immediately by **revoking or disabling or rotate the credential** first, since deleting it from Git history does not un-leak it. 
  3. Then scope the blast radius using audit logs (CloudTrail, etc.) to see what it accessed, rotate any related secrets, remove it from the repo history, and look for persistence such as new IAM users, keys or backdoors. 
  4. Fix the root cause, for example moving to OIDC or short-lived credentials and adding pre-commit scanning.

**Critical CVE like Log4Shell:** 
  1. detect via threat intel or scanner alerts, 
  2. then use **SBOMs** and dependency inventories to find every affected service, including transitive dependencies, and prioritize by internet exposure and data sensitivity. Ideally, step 1 to 2 should be an automated process. 
  3. Contain with compensating controls right away (WAF rules, disabling the vulnerable feature or JNDI lookups, network isolation, egress filtering) while the patch is prepared. 
  4. Then patch or upgrade, rebuild, redeploy through the pipeline, and verify by rescanning, while hunting for signs of prior exploitation in logs and runtime telemetry.

Both scenarios end with a **blameless post-mortem**: build a timeline, measure time to detect, contain and remediate, and identify what allowed it (missing scanning, poor inventory, overly broad permissions). I then turn findings into concrete improvements such as better SBOM coverage, automated dependency updates, and rehearsed incident runbooks, and communicate status clearly to stakeholders throughout.

## 6. How would you implement least privilege and zero trust in a cloud/Kubernetes environment?

**Least privilege:** start with identity. Give every human and workload its own identity with narrowly scoped IAM roles and Kubernetes RBAC (namespaced Roles, no wildcard verbs, minimal use of cluster-admin), and use short-lived, just-in-time elevated access with approvals instead of standing admin rights. Use *per-pod service accounts* with workload identity (IRSA/EKS Pod Identity Workload Identity), permission boundaries and SCPs as guardrails, and regularly review access using tools such as IAM Access Analyzer to remove unused permissions.

**Zero trust** means never trusting network location and verifying every request:
  1. Enforce default-deny **NetworkPolicies** and, ideally, a service mesh (**Istio**/Linkerd) for **mutual TLS** and identity-based authorization between services. 
  2. Authenticate users through an SSO/IdP with MFA and device posture checks, expose internal apps through an identity-aware proxy rather than a flat VPN, and segment environments by account/VPC and by namespace.

Reinforce it with policy as code and continuous verification: Pod Security Standards (non-root, no privileged containers, dropped capabilities), admission controllers (Kyverno/OPA) to enforce signed images and baseline configs, encrypted data in transit and at rest, and comprehensive audit logging with anomaly detection. The assumption throughout is breach, so each layer limits lateral movement and blast radius.

## 7. How do you measure DevSecOps success? (MTTR, vuln SLA adherence, coverage, escaped defects, deployment frequency.)

I combine security outcome metrics with delivery metrics, because success means becoming more secure *without* slowing down. 

On the security side: 

- **MTTR** (mean time to remediate vulnerabilities, and to detect and respond to incidents), 
- **SLA adherence** (percentage of critical/high vulns fixed within their target windows, such as 7 or 30 days), the size and age of the vulnerability backlog, and 
- **escaped defects** (vulnerabilities found in production or by external parties versus those caught earlier in the pipeline).

On the process side: 
- **coverage** (percentage of repos and services with SAST, SCA, secret scanning and SBOM generation, and percentage of images signed), false-positive rate, and how often policy gates block builds. 

On the delivery side, I track the DORA (DevOpsResearchAssessment) metrics to confirm security controls aren't harming velocity. These include:
1. **deployment frequency**. High standard: < 1 month.
2. lead time = Production Deploy Time - Code Commit Time. High standard: < 1 week.
3. Change failure rate. High standard: < 30%. 
4. failed deployment time to restore (MTTR). High standard: < 1 day.

I look at trends rather than raw numbers, segment by team/app and by risk tier, and avoid vanity metrics such as total findings count, which can incentivize the wrong behavior. 

egular reviews with engineering leadership, plus outcomes like fewer repeat vulnerability classes and faster incident response, show whether the culture and tooling are actually working.
