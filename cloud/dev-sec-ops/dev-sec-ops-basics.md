# DevSecOps Basics — Interview Concepts

Each concept is kept to a short description (max 3 lines) for quick revision.

## 1. Core Principles

- **DevSecOps** — Integrating security into every phase of the DevOps lifecycle rather than bolting it on at the end.
  Security is a shared responsibility across dev, sec and ops, backed by automation.
- **Shift Left** — Move security testing earlier (design, coding, commit) where defects are cheaper and faster to fix.
  Examples: threat modeling, IDE linting, pre-commit secret scanning, PR-time SAST.
- **Shift Right** — Continue security validation in production via monitoring, runtime protection and chaos/red-team exercises.
  Complements shift left, since not every issue is catchable pre-deploy.
- **CIA Triad** — Confidentiality, Integrity, Availability: the three core goals of information security.
  Every control and trade-off can be framed as protecting one or more of these.
- **Defense in Depth** — Layer multiple independent controls so failure of one doesn't cause compromise.
  E.g. network segmentation + WAF + authN/Z + encryption + monitoring.
- **Least Privilege** — Grant identities (users, services, pipelines) only the minimum permissions needed, for the minimum time.
  Reduces blast radius when credentials are stolen or misused.
- **Zero Trust** — "Never trust, always verify": authenticate and authorize every request regardless of network location.
  Relies on strong identity, device posture, micro-segmentation and continuous validation.
- **Security as Code / Policy as Code** — Express security rules (IAM, network, compliance) as versioned, testable code.
  Enables automated enforcement and audit trails (e.g. OPA/Rego, Sentinel, Kyverno).

## 2. Threat Modeling & Risk

- **Threat Modeling** — Structured analysis of a system to identify what can go wrong and how to mitigate it, ideally at design time.
  Common methods: STRIDE, PASTA, attack trees, data-flow diagrams.
- **STRIDE** — Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege.
  A mnemonic for categorizing threats against each component in a data-flow diagram.
- **Risk = Likelihood × Impact** — Prioritize remediation by how probable and how damaging an issue is, not by severity alone.
  Drives risk acceptance, mitigation, transfer or avoidance decisions.
- **CVE / CVSS / EPSS** — CVE identifies a known vulnerability, CVSS scores its severity (0–10), EPSS estimates exploit likelihood.
  Combine with asset criticality and reachability to prioritize patching.
- **OWASP Top 10** — Community list of the most critical web app risks (injection, broken access control, misconfiguration, etc.).
  Also see OWASP API Top 10 and OWASP Top 10 for LLM apps.
- **MITRE ATT&CK** — Knowledge base of real-world adversary tactics and techniques.
  Used for threat modeling, detection engineering and red/purple-team planning.

## 3. Secure SDLC & Pipeline Testing

- **SAST (Static Application Security Testing)** — Analyzes source code without running it to find flaws like injection or hardcoded secrets.
  Fast and early in the pipeline, but can produce false positives (e.g. SonarQube, Semgrep, CodeQL).
- **DAST (Dynamic Application Security Testing)** — Attacks a running app from the outside to find runtime vulnerabilities.
  Language-agnostic but later in the cycle and gives less precise code location (e.g. OWASP ZAP, Burp).
- **IAST (Interactive AST)** — Instruments the running app during tests to observe vulnerabilities from inside.
  Higher accuracy than SAST/DAST but needs agents and test coverage.
- **SCA (Software Composition Analysis)** — Scans third-party/open-source dependencies for known CVEs and license issues.
  Tools: Dependabot, Snyk, Trivy, OWASP Dependency-Check.
- **RASP** — Runtime Application Self-Protection: an in-app agent that detects and blocks attacks in real time.
  Sits inside the application, unlike a WAF at the perimeter.
- **Secret Scanning** — Detects API keys, tokens and passwords committed to repos or present in images/logs.
  Use pre-commit hooks and CI checks (gitleaks, trufflehog) and rotate anything leaked.
- **Fuzzing** — Feeds malformed or random input to a program to find crashes and security bugs.
  Effective for parsers, protocols and memory-unsafe code.
- **Penetration Testing / Red Teaming** — Authorized simulated attacks to find exploitable weaknesses.
  Pen tests are scoped and time-boxed; red teams emulate a realistic adversary end to end.
- **Security Gates / Quality Gates** — Pipeline checks that fail or block a build when findings exceed a defined threshold.
  Balance strictness with developer velocity to avoid alert fatigue and bypasses.
- **Security Champions** — Developers embedded in teams who advocate for and help scale security practices.
  Bridge the gap between the central security team and engineering.

## 4. Supply Chain Security

- **Software Supply Chain Security** — Protecting code, dependencies, build systems and artifacts from tampering.
  Notable incidents: SolarWinds, Log4Shell, codecov, xz-utils.
- **SBOM (Software Bill of Materials)** — Inventory of all components and versions inside a piece of software.
  Enables fast impact analysis for new CVEs; formats: SPDX, CycloneDX.
- **SLSA** — Framework of incremental levels for build integrity and provenance.
  Higher levels require hardened, isolated builds and verifiable provenance.
- **Artifact Signing & Provenance** — Cryptographically sign builds/images and attest how they were built.
  Verified at deploy time (Sigstore/cosign, in-toto, Notary).
- **Dependency Pinning & Lockfiles** — Fix exact dependency versions and hashes for reproducible, tamper-evident builds.
  Mitigates dependency confusion, typosquatting and malicious upgrades.
- **Trusted/Private Registries** — Pull only from vetted sources and proxy public registries through an internal mirror.
  Allows scanning, caching and blocking of known-bad packages.

## 5. Infrastructure as Code (IaC) & Configuration Security

- **IaC Scanning** — Static analysis of Terraform, CloudFormation, Kubernetes manifests, Helm, etc. for misconfigurations.
  Catches public buckets, open security groups, missing encryption (Checkov, tfsec, KICS).
- **Configuration Drift** — Divergence between declared IaC state and actual deployed resources.
  Detect with drift detection and remediate by reapplying or enforcing GitOps.
- **Immutable Infrastructure** — Replace rather than patch running servers/containers with freshly built, known-good images.
  Reduces configuration drift and persistence opportunities for attackers.
- **Hardening / CIS Benchmarks** — Reduce attack surface by removing unnecessary services and applying secure baselines.
  CIS Benchmarks provide prescriptive settings for OSes, cloud and Kubernetes.
- **GitOps** — Git is the single source of truth for desired state, applied by a controller (ArgoCD, Flux).
  Gives auditability, peer review and easy rollback of infrastructure changes.

## 6. Container & Kubernetes Security

- **Image Scanning** — Scan container images for OS/package vulnerabilities and misconfigurations in build and registry.
  Use minimal base images (distroless, alpine) to shrink the attack surface.
- **Container Isolation Primitives** — Namespaces, cgroups, seccomp and capabilities limit what a container can see and do.
  Containers share the host kernel, so isolation is weaker than VMs.
- **Run as Non-root / Read-only FS** — Drop root, drop capabilities and mount the root filesystem read-only.
  Limits impact of container breakout or code execution.
- **Kubernetes RBAC** — Role-based control over who/what can perform which API actions on which resources.
  Apply least privilege; avoid cluster-admin and default service account tokens.
- **Pod Security Standards / Admission Control** — Enforce Privileged/Baseline/Restricted profiles via admission controllers.
  Policy engines (OPA Gatekeeper, Kyverno) block non-compliant workloads before they run.
- **Network Policies** — Kubernetes firewall rules that restrict pod-to-pod and egress traffic.
  Default-deny plus explicit allow rules implements micro-segmentation.
- **Service Mesh / mTLS** — Sidecar or ambient proxies (Istio, Linkerd) provide mutual TLS and fine-grained authZ between services.
  Delivers encryption in transit and workload identity without app changes.
- **Runtime Security** — Detect anomalous behavior in running containers/hosts via syscall or eBPF monitoring.
  Tools: Falco, Tetragon; often paired with automated response.

## 7. Identity, Access & Secrets Management

- **AuthN vs AuthZ** — Authentication proves who you are; authorization decides what you may do.
  Broken access control is consistently the top web application risk.
- **IAM** — Managing identities, roles and policies across cloud and systems.
  Prefer roles/short-lived credentials over long-lived static keys.
- **RBAC vs ABAC** — RBAC grants permissions via roles; ABAC decides using attributes (user, resource, context).
  ABAC is more flexible/granular but more complex to manage.
- **OAuth 2.0 / OIDC / SAML** — OAuth 2.0 delegates authorization, OIDC adds identity on top, SAML is XML-based enterprise SSO.
  Know tokens (access/refresh/ID), scopes and flows (e.g. auth code + PKCE).
- **JWT** — Signed, self-contained token carrying claims; validate signature, expiry, issuer and audience.
  Avoid `alg: none`, keep tokens short-lived and don't store secrets in the payload.
- **MFA / Passkeys** — Require more than a password (something you know/have/are); passkeys (FIDO2/WebAuthn) are phishing-resistant.
  Enforce for humans, especially privileged and CI/CD access.
- **Secrets Management** — Store and distribute credentials in a vault, never in code, images or plain env files.
  Use HashiCorp Vault, AWS Secrets Manager, etc. with rotation, leasing and audit logging.
- **Workload Identity / OIDC Federation** — Let pipelines and pods assume cloud roles via short-lived tokens instead of static keys.
  E.g. GitHub Actions OIDC to AWS, IRSA on EKS.
- **PAM / JIT Access** — Privileged Access Management with just-in-time, approved, time-bound elevation.
  Reduces standing privilege and provides session recording.

## 8. Cryptography & Data Protection

- **Encryption at Rest / in Transit** — Protect stored data (AES-256, KMS-managed keys) and network traffic (TLS 1.2+/1.3).
  Enforce by default and manage key rotation and access separately from data access.
- **Symmetric vs Asymmetric** — Symmetric uses one shared key (fast, bulk data); asymmetric uses a public/private pair (key exchange, signatures).
  TLS uses asymmetric to negotiate then symmetric for the session.
- **Hashing vs Encryption** — Hashing is one-way (integrity, passwords with bcrypt/argon2 + salt); encryption is reversible with a key.
  Never use fast hashes (MD5/SHA-1) for passwords.
- **KMS / HSM / Envelope Encryption** — Keys live in a managed service or hardware module; data keys are encrypted by a master key.
  Limits key exposure and enables centralized rotation and audit.
- **PKI / Certificates** — CAs issue certs binding identities to public keys; manage lifecycle, expiry and revocation.
  Automate with ACME/cert-manager to avoid outage-causing expiries.
- **Data Classification & Tokenization** — Label data by sensitivity and replace sensitive values (PAN, PII) with tokens.
  Reduces compliance scope and exposure in case of breach.

## 9. Cloud Security

- **Shared Responsibility Model** — Provider secures the cloud itself; the customer secures what they put in it (config, data, IAM).
  The boundary shifts by IaaS/PaaS/SaaS.
- **CSPM / CWPP / CNAPP** — Posture management (misconfigs), workload protection (runtime) and their unification in one platform.
  Examples: Wiz, Prisma Cloud, Defender for Cloud, AWS Security Hub.
- **Network Security** — VPCs, subnets, security groups/NACLs, private endpoints, WAF and DDoS protection.
  Keep workloads private by default and expose only via controlled ingress.
- **Landing Zone / Multi-account Strategy** — Separate accounts/subscriptions per env or team with guardrails (SCPs, org policies).
  Contains blast radius and centralizes logging and governance.
- **Common Cloud Misconfigs** — Public storage buckets, overly permissive IAM, open management ports, unencrypted data, exposed metadata service.
  Mitigate with IaC scanning, CSPM and IMDSv2/least-privilege roles.

## 10. Application & API Security

- **Injection (SQLi, XSS, Command)** — Untrusted input interpreted as code or commands.
  Prevent with parameterized queries, output encoding, input validation and least-privileged DB accounts.
- **CSRF / SSRF** — CSRF tricks a user's browser into unwanted actions; SSRF tricks the server into making internal requests.
  Use anti-CSRF tokens/SameSite cookies; for SSRF use allowlists and block metadata endpoints.
- **Security Headers / CORS** — CSP, HSTS, X-Content-Type-Options, etc. harden browsers; CORS restricts cross-origin access.
  Misconfigured wildcard CORS with credentials is a common flaw.
- **API Security** — Enforce authN/Z per object (BOLA/IDOR), rate limiting, schema validation and inventory of shadow APIs.
  Use an API gateway for consistent policy enforcement.
- **WAF** — Filters and blocks malicious HTTP traffic at the edge using rules and signatures.
  A compensating control, not a substitute for fixing vulnerable code.
- **Input Validation & Output Encoding** — Validate on the server using allowlists and encode data for its output context.
  Never rely solely on client-side checks.

## 11. Monitoring, Detection & Incident Response

- **Logging & Audit Trails** — Centralize immutable logs (auth events, admin actions, API calls, pipeline runs).
  Essential for detection, forensics and compliance; never log secrets or PII.
- **SIEM / SOAR** — SIEM aggregates and correlates security events for alerting; SOAR automates response playbooks.
  Examples: Splunk, Sentinel, Elastic; tune rules to reduce false positives.
- **IDS/IPS & EDR** — Network intrusion detection/prevention and endpoint detection & response.
  Provide visibility and containment on hosts and traffic.
- **Observability vs Monitoring** — Monitoring watches known signals; observability (logs, metrics, traces) lets you investigate unknowns.
  Security signals should feed the same telemetry pipeline.
- **Incident Response Lifecycle** — Prepare → Detect & Analyze → Contain → Eradicate → Recover → Lessons learned (NIST 800-61).
  Runbooks, on-call and blameless post-mortems make response repeatable.
- **MTTD / MTTR** — Mean time to detect and mean time to respond/recover.
  Key metrics for security operations effectiveness.
- **Vulnerability Management** — Continuous cycle of discover, prioritize, remediate, verify, with defined SLAs by severity.
  Track exposure with asset inventory and patch/upgrade automation.
- **Bug Bounty / VDP** — Programs inviting external researchers to report vulnerabilities responsibly.
  A VDP sets the disclosure process; bounties add monetary rewards.

## 12. Compliance, Governance & Frameworks

- **Compliance as Code / Continuous Compliance** — Automate evidence collection and control checks in the pipeline.
  Reduces audit effort and point-in-time compliance drift.
- **Common Standards** — SOC 2, ISO 27001, PCI DSS, HIPAA, GDPR, NIST CSF/800-53, CIS Controls.
  Know which apply to your data (e.g. PCI for card data, GDPR for EU personal data).
- **NIST SSDF / OWASP SAMM / BSIMM** — Frameworks for secure development practices and maturity measurement.
  Used to benchmark and roadmap a DevSecOps program.
- **Separation of Duties & Change Management** — No single person can write, approve and deploy a change alone.
  Enforced with protected branches, mandatory reviews and pipeline approvals.
- **Data Privacy** — Minimize collection, define retention, honor subject rights and protect PII.
  Privacy-by-design applies alongside security-by-design.

## 13. CI/CD Pipeline Security

- **Pipeline Hardening** — Treat CI/CD as a high-value target: restrict who can edit pipelines, isolate and ephemeral runners.
  Pin third-party actions/plugins by SHA and avoid running untrusted PR code with secrets.
- **Branch Protection & Signed Commits** — Require reviews, status checks and verified commits before merging to main.
  Prevents unreviewed or impersonated code reaching production.
- **Secure Deployment Strategies** — Blue/green, canary and feature flags with automated rollback limit the impact of bad releases.
  Combine with progressive delivery and health/security checks.
- **Environment Separation** — Distinct dev/stage/prod with separate credentials, data and access controls.
  Never use real production data in lower environments without masking.
