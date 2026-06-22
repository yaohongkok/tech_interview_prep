# Kubernetes Interview Preparation Guide

---

## Part 1: Core Kubernetes Concepts

### 1.1 What is Kubernetes?

Kubernetes (K8s) is an open-source container orchestration platform that automates the deployment, scaling, and management of containerized applications. Originally developed by Google, it is now maintained by the Cloud Native Computing Foundation (CNCF).

Key responsibilities of Kubernetes:
- Scheduling containers onto nodes
- Self-healing (restarting failed containers, replacing unhealthy nodes)
- Horizontal scaling based on load
- Service discovery and load balancing
- Rolling updates and rollbacks
- Secret and configuration management

---

### 1.2 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Control Plane                        │
│  ┌─────────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │ API Server  │  │  etcd    │  │Scheduler │  │  CCM   │  │
│  └─────────────┘  └──────────┘  └──────────┘  └────────┘  │
│         │                Controller Manager                 │
└─────────┼───────────────────────────────────────────────────┘
          │
┌─────────┼───────────────────────────────────────────────────┐
│         │              Worker Nodes                         │
│  ┌──────┴──────┐     ┌─────────────┐     ┌──────────────┐  │
│  │   kubelet   │     │  kube-proxy │     │Container RT  │  │
│  └─────────────┘     └─────────────┘     └──────────────┘  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │   Pod  [ Container A ]  [ Container B ]              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

#### Control Plane Components

| Component | Role |
|---|---|
| **kube-apiserver** | Central entry point; all components communicate through it |
| **etcd** | Distributed key-value store; holds all cluster state |
| **kube-scheduler** | Assigns Pods to Nodes based on resource needs and constraints |
| **kube-controller-manager** | Runs controllers (Node, ReplicaSet, Endpoints, etc.) |
| **cloud-controller-manager (CCM)** | Interfaces with cloud provider APIs (load balancers, storage) |

#### Worker Node Components

| Component | Role |
|---|---|
| **kubelet** | Agent on each node; ensures containers are running as specified |
| **kube-proxy** | Maintains network rules for Pod communication |
| **Container Runtime** | Runs containers (containerd, CRI-O) |

---

### 1.3 Core Objects

#### Pod
The smallest deployable unit in Kubernetes. A Pod encapsulates one or more containers that share network and storage.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
    - name: app
      image: nginx:1.25
      ports:
        - containerPort: 80
```

- Containers in a Pod share the same IP address and port space.
- Pods are ephemeral — they are not self-healing on their own.

#### ReplicaSet
Ensures a specified number of Pod replicas are running at any time. Usually managed by a Deployment rather than directly.

#### Deployment
Wraps a ReplicaSet to provide declarative updates, rollouts, and rollbacks.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: app
          image: my-app:v2
```

#### Service
Provides a stable network endpoint to reach a set of Pods, regardless of their IP changes.

| Service Type | Description |
|---|---|
| **ClusterIP** | Internal only (default) |
| **NodePort** | Exposes port on each Node's IP |
| **LoadBalancer** | Provisions a cloud load balancer |
| **ExternalName** | Maps to a DNS name |

#### ConfigMap & Secret
- **ConfigMap**: Stores non-sensitive configuration as key-value pairs.
- **Secret**: Stores sensitive data (passwords, tokens) encoded in base64. Use external secret managers (Vault, AWS Secrets Manager) for production.

#### Namespace
Logical partitioning of cluster resources. Useful for isolating environments (dev, staging, prod) within a single cluster.

---

### 1.4 Scheduling & Resource Management

#### Resource Requests vs Limits

```yaml
resources:
  requests:
    cpu: "250m"     # Guaranteed allocation
    memory: "128Mi"
  limits:
    cpu: "500m"     # Maximum allowed
    memory: "256Mi"
```

- **Requests**: Used by the scheduler to find a suitable node.
- **Limits**: Enforced at runtime; exceeding CPU is throttled, exceeding memory causes OOMKill.

#### Node Affinity & Taints/Tolerations

- **Node Affinity**: Attracts Pods to nodes with specific labels.
- **Taints**: Repel Pods from nodes unless the Pod has a matching Toleration.
- **Tolerations**: Allow Pods to schedule onto tainted nodes.

#### Pod Priority & Preemption
Higher-priority Pods can evict lower-priority ones when the cluster is resource-constrained.

---

### 1.5 Networking

- Every Pod gets a unique cluster-internal IP.
- The **CNI (Container Network Interface)** plugin (Calico, Flannel, Cilium) handles Pod-to-Pod networking.
- **kube-proxy** implements Service networking via iptables or IPVS rules.

#### Ingress
An API object that manages external HTTP/HTTPS access to Services, typically via an Ingress Controller (NGINX, Traefik).

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
spec:
  rules:
    - host: example.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 80
```

#### Network Policy
Restricts traffic between Pods using label selectors — acts as a firewall within the cluster.

---

### 1.6 Storage

| Concept | Description |
|---|---|
| **Volume** | Attached to a Pod lifecycle; dies with the Pod |
| **PersistentVolume (PV)** | Cluster-level storage resource |
| **PersistentVolumeClaim (PVC)** | Request for storage by a Pod |
| **StorageClass** | Defines dynamic provisioning (SSD, HDD, cloud disk) |

Access modes: `ReadWriteOnce`, `ReadOnlyMany`, `ReadWriteMany`.

---

### 1.7 Workload Controllers

| Controller | Use Case |
|---|---|
| **Deployment** | Stateless apps with rolling updates |
| **StatefulSet** | Stateful apps (databases); stable network IDs and storage |
| **DaemonSet** | Run one Pod per node (log collectors, monitoring agents) |
| **Job** | Run a task to completion |
| **CronJob** | Scheduled Jobs |
| **HorizontalPodAutoscaler (HPA)** | Scale Pods based on CPU/memory metrics |
| **VerticalPodAutoscaler (VPA)** | Adjust resource requests/limits automatically |

---

### 1.8 Health Probes

```yaml
livenessProbe:       # Restart container if it fails
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5

readinessProbe:      # Remove from Service endpoints if it fails
  httpGet:
    path: /ready
    port: 8080

startupProbe:        # Disables liveness/readiness until app has started
  httpGet:
    path: /started
    port: 8080
  failureThreshold: 30
```

---

### 1.9 RBAC (Role-Based Access Control)

| Object | Scope | Purpose |
|---|---|---|
| **Role** | Namespace | Grants permissions within a namespace |
| **ClusterRole** | Cluster-wide | Grants permissions across all namespaces |
| **RoleBinding** | Namespace | Binds a Role to a user/group/ServiceAccount |
| **ClusterRoleBinding** | Cluster-wide | Binds a ClusterRole cluster-wide |

---

### 1.10 Helm

Helm is the Kubernetes package manager. A **Chart** is a collection of YAML templates for deploying an application. Key commands:

```bash
helm install my-release bitnami/nginx
helm upgrade my-release bitnami/nginx --set replicaCount=3
helm rollback my-release 1
helm uninstall my-release
```

---

## Part 2: Popular Kubernetes Interview Questions & Answers

---

### Architecture & Fundamentals

**Q1: What is the difference between a Pod and a container?**

A container is a runtime instance of an image. A Pod is the Kubernetes abstraction that wraps one or more containers, giving them a shared network namespace (same IP, same localhost) and optional shared storage volumes. Kubernetes manages Pods, not containers directly. Co-located containers in a Pod are tightly coupled — they always run on the same node and are scheduled together.

---

**Q2: What happens when you run `kubectl apply -f deployment.yaml`?**

1. `kubectl` sends the manifest to the **kube-apiserver** via a REST call.
2. The API server validates and persists the desired state to **etcd**.
3. The **Deployment controller** (inside kube-controller-manager) detects the new object and creates a ReplicaSet.
4. The ReplicaSet controller creates the required number of Pods.
5. The **kube-scheduler** assigns each Pod to a suitable node.
6. The **kubelet** on the target node pulls the image and starts the containers.
7. **kube-proxy** updates network rules so the Service can reach the new Pods.

---

**Q3: What is etcd and why is it critical?**

etcd is the distributed key-value store that acts as Kubernetes' single source of truth for all cluster state — nodes, Pods, Secrets, ConfigMaps, RBAC rules, and more. If etcd is unavailable, the cluster cannot make scheduling decisions or update state, though running workloads continue. This is why etcd is run as a highly available cluster (typically 3 or 5 nodes) and backed up regularly.

---

**Q4: Explain the role of kubelet.**

The kubelet is a node-level agent that:
- Watches the API server for Pods scheduled to its node.
- Instructs the container runtime (containerd/CRI-O) to start/stop containers.
- Reports node and Pod status back to the API server.
- Enforces resource limits via cgroups.
- Runs health probes and restarts containers that fail liveness checks.

---

### Networking

**Q5: How does Kubernetes Service discovery work?**

Kubernetes runs a CoreDNS Pod in the `kube-system` namespace. Every Service gets a DNS entry:

```
<service-name>.<namespace>.svc.cluster.local
```

Pods can reach a Service by its short name (`my-service`) within the same namespace or by the FQDN across namespaces. kube-proxy maintains iptables/IPVS rules that load-balance traffic to healthy Pod IPs behind the Service.

---

**Q6: What is the difference between ClusterIP, NodePort, and LoadBalancer?**

| Type | Accessibility | Typical Use |
|---|---|---|
| **ClusterIP** | Within cluster only | Internal microservice communication |
| **NodePort** | External via `<NodeIP>:<NodePort>` (30000–32767) | Dev/testing; not suitable for production |
| **LoadBalancer** | External via cloud LB | Production external traffic |

LoadBalancer is a superset — it creates a NodePort and ClusterIP automatically, then provisions a cloud load balancer pointing to those NodePorts.

---

**Q7: What is an Ingress and when would you use it over a LoadBalancer Service?**

An Ingress routes external HTTP/HTTPS traffic to multiple Services based on host or path rules using a single external IP, managed by an Ingress Controller. A LoadBalancer Service gives each Service its own external IP, which is costly at scale. Use Ingress when you need:
- Path-based or host-based routing (`/api` → service-a, `/web` → service-b).
- TLS termination in one place.
- Cost efficiency (one load balancer for many Services).

---

**Q8: What is a Network Policy? Can you give an example use case?**

A Network Policy is a Kubernetes resource that controls which Pods can communicate with each other and with external endpoints, using label selectors. By default all Pods can talk to all other Pods. A common use case is isolating namespaces — for example, preventing the `dev` namespace from accessing the `prod` database:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-from-dev
  namespace: prod
spec:
  podSelector:
    matchLabels:
      role: db
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              environment: prod
```

Network Policies require a CNI plugin that supports them (Calico, Cilium).

---

### Scheduling & Resources

**Q9: What is the difference between resource requests and limits?**

- **Requests** are what the scheduler uses to find a node with enough available capacity. The container is guaranteed at least this much.
- **Limits** are the maximum the container can consume. Exceeding the CPU limit causes throttling; exceeding the memory limit causes the container to be OOM-killed.

Setting requests without limits can cause noisy-neighbour problems. Always set both in production.

---

**Q10: What are Taints and Tolerations? How are they different from Node Affinity?**

**Taints** are placed on nodes to repel Pods:
```bash
kubectl taint nodes node1 dedicated=gpu:NoSchedule
```

**Tolerations** are placed on Pods to allow them onto tainted nodes:
```yaml
tolerations:
  - key: "dedicated"
    operator: "Equal"
    value: "gpu"
    effect: "NoSchedule"
```

**Node Affinity** *attracts* Pods to nodes based on labels — it is a preference or requirement from the Pod's side. Taints/Tolerations work from the node's side to push Pods away. They are complementary: taints repel, affinity attracts.

---

**Q11: How does the HorizontalPodAutoscaler work?**

The HPA controller polls the Metrics Server (or custom metrics adapter) at regular intervals and compares current metrics to the target. It then adjusts the `replicas` field of the Deployment or StatefulSet:

```
desiredReplicas = ceil(currentReplicas × (currentMetric / desiredMetric))
```

Example: scale when average CPU exceeds 50%:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 50
```

---

### Storage

**Q12: Explain the relationship between PersistentVolume, PersistentVolumeClaim, and StorageClass.**

- **PersistentVolume (PV)**: A piece of storage provisioned in the cluster (manually or dynamically). It exists independently of any Pod.
- **PersistentVolumeClaim (PVC)**: A Pod's request for storage specifying size and access mode. Kubernetes binds the PVC to a matching PV.
- **StorageClass**: Defines how storage is dynamically provisioned (e.g., AWS EBS `gp3`, GCE PD SSD). When a PVC references a StorageClass, Kubernetes automatically creates a PV on demand.

This separation allows developers to request storage without needing to know the underlying infrastructure details.

---

### Deployments & Updates

**Q13: What deployment strategies does Kubernetes support?**

| Strategy | Behaviour | Downtime |
|---|---|---|
| **RollingUpdate** (default) | Gradually replaces old Pods with new ones | None |
| **Recreate** | Terminates all old Pods before starting new ones | Yes |

For more advanced strategies, use external tooling:
- **Blue/Green**: Run two full environments; switch traffic atomically.
- **Canary**: Route a small percentage of traffic to the new version first.

RollingUpdate parameters:
```yaml
strategy:
  rollingUpdate:
    maxSurge: 1        # Extra Pods above desired count
    maxUnavailable: 0  # Pods that can be unavailable during update
```

---

**Q14: How do you roll back a Deployment?**

```bash
# View rollout history
kubectl rollout history deployment/my-app

# Roll back to previous revision
kubectl rollout undo deployment/my-app

# Roll back to a specific revision
kubectl rollout undo deployment/my-app --to-revision=2
```

Kubernetes stores previous ReplicaSets (controlled by `revisionHistoryLimit`) which enables this rollback.

---

### Security

**Q15: What is a ServiceAccount and why does it matter?**

A ServiceAccount provides an identity for processes running inside Pods to authenticate with the Kubernetes API server. By default, Pods use the `default` ServiceAccount of their namespace, which often has broad permissions. Best practice:
- Create dedicated ServiceAccounts per application.
- Grant minimal permissions via RBAC (least-privilege principle).
- Disable token auto-mounting for Pods that don't need API access: `automountServiceAccountToken: false`.

---

**Q16: How would you store and access sensitive data (like a database password) in Kubernetes?**

Use a **Secret**:
```bash
kubectl create secret generic db-creds \
  --from-literal=password=supersecret
```

Access in a Pod as an environment variable or volume mount:
```yaml
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db-creds
        key: password
```

Important caveats:
- Secrets are base64-encoded, not encrypted, by default in etcd. Enable **Encryption at Rest** for etcd.
- In production, prefer external secret managers (HashiCorp Vault, AWS Secrets Manager) integrated via the Secrets Store CSI Driver or an operator.

---

**Q17: What is the difference between a Role and a ClusterRole?**

A **Role** grants permissions within a single namespace. A **ClusterRole** grants permissions cluster-wide or on non-namespaced resources (nodes, PersistentVolumes). You bind them using **RoleBinding** (namespace-scoped) or **ClusterRoleBinding** (cluster-scoped). A ClusterRole can also be bound with a RoleBinding to limit its scope to a specific namespace.

---

### Observability & Troubleshooting

**Q18: A Pod is stuck in `CrashLoopBackOff`. How do you debug it?**

```bash
# 1. Check Pod status and recent events
kubectl describe pod <pod-name>

# 2. Check current container logs
kubectl logs <pod-name>

# 3. Check logs of the previous (crashed) container
kubectl logs <pod-name> --previous

# 4. If the container exits too fast to exec into, override the entrypoint
kubectl run debug --image=my-app --command -- sleep 3600
kubectl exec -it debug -- /bin/sh
```

Common causes: application error on startup, missing ConfigMap/Secret, wrong image, insufficient memory (OOMKill), failed liveness probe.

---

**Q19: A Pod is in `Pending` state. What are possible causes?**

Run `kubectl describe pod <pod-name>` and look at the `Events` section. Common causes:

| Cause | Symptom in Events |
|---|---|
| Insufficient CPU/memory | `0/3 nodes are available: 3 Insufficient cpu` |
| No matching node (affinity/taint) | `0/3 nodes available: 3 node(s) had taint` |
| PVC not bound | `persistentvolumeclaim "..." not found` |
| Image pull failure | `ErrImagePull` / `ImagePullBackOff` |
| Resource quota exceeded | `exceeded quota` |

---

**Q20: How do you debug network connectivity between two Pods?**

```bash
# 1. Check if the Service endpoints are populated
kubectl get endpoints <service-name>

# 2. Exec into a Pod and test DNS resolution
kubectl exec -it <pod> -- nslookup my-service.default.svc.cluster.local

# 3. Test TCP connectivity
kubectl exec -it <pod> -- curl http://my-service:8080/health

# 4. Check Network Policies — a policy might be blocking traffic
kubectl get networkpolicy -n <namespace>

# 5. Use a debug container (ephemeral)
kubectl debug -it <pod> --image=nicolaka/netshoot --target=app
```

---

### Stateful Applications

**Q21: When would you use a StatefulSet over a Deployment?**

Use a **StatefulSet** when your application requires:
- **Stable, unique network identifiers** (Pods get names like `app-0`, `app-1` rather than random hashes).
- **Stable, persistent storage** (each Pod gets its own PVC that survives rescheduling).
- **Ordered deployment and scaling** (Pods start and terminate in order).

Typical use cases: databases (MySQL, Cassandra, Elasticsearch), distributed coordination services (ZooKeeper), message brokers (Kafka).

---

**Q22: What is a Headless Service and why is it used with StatefulSets?**

A Headless Service (`clusterIP: None`) does not assign a virtual IP. Instead, DNS queries return the IPs of all backing Pods directly. This allows StatefulSet Pods to be addressed individually:

```
app-0.my-service.default.svc.cluster.local → Pod app-0 IP
app-1.my-service.default.svc.cluster.local → Pod app-1 IP
```

This is essential for databases that need peer-to-peer communication and leader election (e.g., each MySQL replica needs to know the master's specific address).

---

### Advanced Topics

**Q23: What is a DaemonSet? Give real-world examples.**

A DaemonSet ensures exactly one Pod runs on every node (or a subset of nodes). It is used for cluster-wide infrastructure concerns:
- **Log collection**: Fluentd, Filebeat
- **Monitoring agents**: Prometheus Node Exporter, Datadog agent
- **Networking**: CNI plugins (Calico node, Cilium)
- **Security scanning**: Falco, Sysdig

When a new node joins the cluster, the DaemonSet automatically schedules a Pod on it.

---

**Q24: What is a CRD (CustomResourceDefinition) and what is an Operator?**

A **CRD** extends the Kubernetes API with custom resource types, so you can manage domain-specific objects (e.g., `kind: RedisCluster`) the same way you manage Pods or Deployments.

An **Operator** is a controller that watches these custom resources and automates the lifecycle management of complex stateful applications — provisioning, scaling, backups, failover. Examples: Prometheus Operator, Strimzi (Kafka), PostgreSQL Operator.

The pattern: CRD defines *what* the resource looks like; the Operator implements the *how*.

---

**Q25: How does Kubernetes handle zero-downtime deployments?**

Several mechanisms work together:
1. **RollingUpdate strategy** replaces Pods gradually, keeping some always running.
2. **readinessProbe** ensures new Pods only receive traffic once they are healthy.
3. **minReadySeconds** adds a buffer before the next Pod is replaced.
4. **PodDisruptionBudget (PDB)** guarantees a minimum number of Pods remain available during voluntary disruptions (rolling updates, node drains):

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: my-app-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: my-app
```

5. **preStop hooks** give containers time to finish in-flight requests before termination.
6. **terminationGracePeriodSeconds** controls how long Kubernetes waits for graceful shutdown.

---
