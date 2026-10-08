# Kubernetes Glossary

Quick reference for the terms used in [kubernetes.md](kubernetes.md). Acronyms are expanded in the Term column. Terms that a section there explains in full are not repeated here.

**Cluster and control plane**

| Term | What it is |
|------|-----------|
| Cluster | A set of nodes run by one control plane. The unit you create, upgrade and secure. |
| Control plane | The components that store desired state and drive the cluster towards it. On EKS, AWS runs it for you. |
| Node | A worker machine (EC2 instance, VM or Fargate micro-VM) that runs pods. |
| CRI (Container Runtime Interface) | The API the kubelet uses to talk to a container runtime. Lets runtimes be swapped without changing the kubelet. |
| kubectl | The command-line client for the API server. |
| Namespace | A named scope inside a cluster for grouping objects. The basic unit for RBAC, quotas and tenancy. |
| Label / Selector | Labels are key-value tags on objects; selectors query them. How Services, Deployments and policies find their pods. |
| Annotation | Key-value metadata that is not used for selection. Often configures controllers (e.g. ALB settings). |
| Event | A short-lived record of something that happened to an object (scheduled, pulled, killed). Kept about 1 hour by default. |

**Workloads**

| Term | What it is |
|------|-----------|
| Pod | The smallest deployable unit: one or more containers sharing a network namespace and volumes. Pods are disposable and replaced, not repaired. |
| ReplicaSet | Keeps a fixed number of identical pods running. Usually managed by a Deployment, not created directly. |
| Job / CronJob | A Job runs pods until a task completes successfully. A CronJob creates Jobs on a schedule. |
| Sidecar container | A helper container running alongside the app in the same pod (proxy, log shipper). Native sidecars are init containers with `restartPolicy: Always`. |
| Ephemeral container | A temporary container added to a running pod for debugging (`kubectl debug`). |
| SIGTERM / SIGKILL (signal terminate / signal kill) | SIGTERM asks the process to shut down gracefully; SIGKILL kills it immediately. Kubernetes sends SIGKILL after the grace period expires. |
| CrashLoopBackOff | Container state when it keeps crashing and the kubelet waits longer between each restart. Not a pod phase. |
| OOMKilled (Out Of Memory killed) | The container exceeded its memory limit and the kernel killed it. Exit code 137. |

**Configuration and storage**

| Term | What it is |
|------|-----------|
| Volume | A directory mounted into a pod's containers. Can be temporary (`emptyDir`) or backed by persistent storage. |
| PV (PersistentVolume) | A piece of real storage (e.g. an EBS volume) represented as a cluster object. |
| PVC (PersistentVolumeClaim) | A pod's request for storage of a given size and class. Gets bound to a PV. |
| StorageClass | Describes a type of storage and how to provision it dynamically. `volumeBindingMode: WaitForFirstConsumer` delays creation until the pod is scheduled. |
| CSI (Container Storage Interface) | The plugin standard for storage drivers. The EBS CSI driver creates and attaches EBS volumes. |
| EBS (Elastic Block Store) | AWS block storage volumes. Each volume lives in one AZ. |
| KMS (Key Management Service) | AWS service for managing encryption keys. EKS uses it for envelope encryption of Secrets in etcd. |

**Scheduling, resources and autoscaling**

| Term | What it is |
|------|-----------|
| QoS (Quality of Service) class | Guaranteed, Burstable or BestEffort, derived from requests and limits. Decides eviction order when a node runs low on resources. |
| Eviction | The kubelet or API removing a pod from a node, due to resource pressure or a drain. |
| Drain / Cordon | Cordon marks a node unschedulable; drain also evicts its pods (respecting PDBs). |
| HPA (Horizontal Pod Autoscaler) | Adds or removes pod replicas based on CPU, memory or custom metrics. |
| VPA (Vertical Pod Autoscaler) | Adjusts a pod's CPU and memory requests based on observed usage. |
| KEDA (Kubernetes Event-Driven Autoscaling) | Scales workloads on external events like queue depth or Kafka lag. Can scale to zero. |
| ASG (Auto Scaling Group) | AWS group of EC2 instances kept at a desired count. Backs EKS managed node groups. |

**Networking**

| Term | What it is |
|------|-----------|
| VIP (Virtual IP) | An IP not tied to one machine, translated to real pod IPs by kube-proxy rules. |
| CNI (Container Network Interface) | The plugin standard that gives each pod a network interface and IP. Examples: AWS VPC CNI, Calico, Cilium. |
| VPC (Virtual Private Cloud) | Your isolated network in AWS. With the AWS VPC CNI, pods get real VPC IPs. |
| ENI (Elastic Network Interface) | A virtual network card attached to an EC2 instance. Limits how many pod IPs a node can hold. |
| CIDR (Classless Inter-Domain Routing) | Notation for an IP range, e.g. `10.0.0.0/16`. Subnet CIDR size limits how many pods you can run. |
| NAT / DNAT (Network Address Translation / Destination NAT) | Rewriting IP addresses on packets. kube-proxy uses DNAT to send Service traffic to a pod IP. |
| IPVS (IP Virtual Server) | A Linux kernel load balancer; one of kube-proxy's modes. |
| eBPF (extended Berkeley Packet Filter) | Runs sandboxed programs inside the Linux kernel. Cilium uses it for fast networking and can replace kube-proxy. |
| BGP (Border Gateway Protocol) | The routing protocol that exchanges routes between networks. Calico can use it to route pod traffic without an overlay. |
| conntrack (connection tracking) | Kernel table tracking network connections for NAT. Can fill up or race under load, causing drops. |
| DNS (Domain Name System) / CoreDNS | DNS resolves names to IPs; CoreDNS is the cluster DNS server for `<svc>.<ns>.svc.cluster.local` names. |
| FQDN (Fully Qualified Domain Name) | A complete domain name ending with a dot, e.g. `api.example.com.`. Skips the search-domain lookups caused by `ndots`. |
| L4 / L7 (Layer 4 / Layer 7) | OSI layers: L4 routes by IP and port (TCP/UDP), L7 by application content (HTTP host, path, headers). |
| TLS (Transport Layer Security) | The encryption protocol behind HTTPS. Certificates come from cert-manager or ACM. |
| ACM (AWS Certificate Manager) | AWS service that issues and renews TLS certificates for load balancers. |
| SG (Security Group) | An AWS stateful firewall attached to ENIs. With security groups for pods, a pod gets its own SG. |
| Service mesh | A proxy layer (Istio, Linkerd) that adds L7 routing, retries, mTLS (mutual TLS) and telemetry between services. |
| gRPC (gRPC Remote Procedure Calls) | A high-performance RPC framework over HTTP/2. Long-lived connections need L7 load balancing. |

**Security and identity**

| Term | What it is |
|------|-----------|
| RBAC (Role-Based Access Control) | Kubernetes authorization: Roles define allowed verbs on resources, RoleBindings grant them to subjects. Cluster-wide variants are ClusterRole and ClusterRoleBinding. |
| ServiceAccount (SA) | The identity a pod uses to talk to the API server, and to AWS via IRSA or Pod Identity. |
| IAM (Identity and Access Management) | AWS's permission system. On EKS it authenticates users; RBAC then authorizes them. |
| IRSA (IAM Roles for Service Accounts) | Lets a pod assume an IAM role through its ServiceAccount using the cluster's OIDC provider. Gives per-workload AWS permissions. |
| OIDC (OpenID Connect) | An identity protocol built on OAuth 2.0. EKS publishes an OIDC issuer that IAM trusts for IRSA. |
| STS (Security Token Service) | AWS service that issues temporary credentials when a role is assumed. |
| ARN (Amazon Resource Name) | The unique identifier of an AWS resource, e.g. an IAM role. |
| IMDS (Instance Metadata Service) | Endpoint on every EC2 instance that serves its metadata and node-role credentials. Block pod access to it so pods cannot borrow the node role. |
| Admission controller / webhook | Code that can change (mutating) or reject (validating) requests before they are stored. Webhooks call out to your own service. |
| Kyverno / OPA (Open Policy Agent) Gatekeeper | Policy engines run as admission webhooks to enforce custom rules like allowed registries or required labels. |
| CEL (Common Expression Language) | Small expression language used by `ValidatingAdmissionPolicy` to write policies without a webhook. |
| SSM (AWS Systems Manager) | AWS ops service. Parameter Store holds config/secrets, Session Manager gives shell access to nodes. |
| SOPS (Secrets OPerationS) | Encrypts values in YAML/JSON files so secrets can be committed to Git. Flux decrypts it natively. |
| Sealed Secrets | Controller that decrypts secrets encrypted with the cluster's public key, so they can be stored in Git. |

**Extensibility and platform**

| Term | What it is |
|------|-----------|
| Helm | Package manager for Kubernetes. A chart is a templated bundle of manifests; a release is an installed instance. |
| Kustomize | Template-free way to customise YAML with bases and overlays. Built into `kubectl`. |
| Crossplane | Manages cloud infrastructure as Kubernetes custom resources. XRDs (Composite Resource Definitions) define your own APIs and Compositions map them to real resources. |
| OAM (Open Application Model) | A spec describing apps as Components plus Traits, separating developer and platform concerns. |

**Delivery and GitOps**

| Term | What it is |
|------|-----------|
| CI/CD (Continuous Integration / Continuous Delivery) | Automated build/test (CI) and release/deploy (CD) pipelines. |
| OCI (Open Container Initiative) | Standards for container images and registries. Flux can pull manifests and Helm charts as OCI artifacts. |
| Drift | Difference between what is in Git and what is running. GitOps tools detect and correct it. |
| Rolling update | Replace pods gradually, controlled by `maxSurge` and `maxUnavailable`. The Deployment default. |
| Canary / Blue-green | Canary sends a small share of traffic to the new version first; blue-green switches all traffic between two full environments. |

**Observability and reliability**

| Term | What it is |
|------|-----------|
| cAdvisor (Container Advisor) | Built into the kubelet; reports per-container CPU, memory, network and throttling. |
| Prometheus | Pull-based metrics system and time-series database. The Prometheus Operator manages it with CRDs like ServiceMonitor. |
| OTel (OpenTelemetry) | Vendor-neutral standard and SDKs for traces, metrics and logs. The Collector receives OTLP and exports to any backend. |
| OTLP (OpenTelemetry Protocol) | The wire protocol for sending OpenTelemetry data. |
| SLI (Service Level Indicator) | A measured ratio of good events to valid events, e.g. successful requests. |
| SLO (Service Level Objective) | The target for an SLI over a window, e.g. 99.9% over 30 days. |
| SLA (Service Level Agreement) | A contractual promise to customers, with penalties. Usually looser than the internal SLO. |
| Burn rate | How fast the error budget is being consumed relative to plan. Used for multi-window alerting. |
| MTTR (Mean Time To Recovery) | Average time to restore service after an incident. |
