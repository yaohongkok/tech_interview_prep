# Helm: Review Notes for Lead SRE (Platform) Interview

Companion to [kubernetes.md](kubernetes.md). Flux `HelmRelease` is covered in section 11 of that file.

---

## What It Is

A templating engine plus a release manager. Chart + values → rendered manifests → a versioned **release** in a namespace.

## Chart Layout

```
mychart/
  Chart.yaml          # name, version (chart), appVersion (app), dependencies
  values.yaml         # defaults
  values.schema.json  # optional JSON Schema validation of values
  templates/
    _helpers.tpl      # named templates, not rendered as manifests
    deployment.yaml
    NOTES.txt
  crds/               # installed once, never upgraded or templated
  charts/             # vendored subcharts
```

## Values Precedence

Lowest to highest: chart `values.yaml` → parent chart's values for the subchart → `-f` files in order (last wins) → `--set`.

## Templating Essentials

- Objects: `.Values`, `.Release`, `.Chart`, `.Capabilities`, `.Files`.
- `include` vs `template`: `include` returns a string, so it can be piped (`{{ include "x.labels" . | nindent 4 }}`). Prefer it.
- Handy functions: `default`, `required`, `quote`, `toYaml`, `nindent`, `tpl` (render a string from values as a template), `lookup` (read live cluster objects; returns empty in `helm template`).
- Scope: `with` and `range` rebind `.`; use `$` to reach the root.
- Whitespace: `{{-` and `-}}` trim.
- **Roll pods on config change:**
  ```yaml
  annotations:
    checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
  ```

## Release Mechanics

- Helm 3+ has no Tiller. Release state is stored as **Secrets in the release namespace** (`sh.helm.release.v1.<name>.v<rev>`).
- Upgrade uses a **three-way merge**: previous manifest, new manifest, and live state. Manual `kubectl edit` drift on fields the chart does not change tends to survive.
- Helm 4 moves towards server-side apply and renames some flags (`--atomic` → `--rollback-on-failure`). Worth knowing which major version the team runs.
- **Hooks:** `pre-install`, `post-install`, `pre-upgrade`, `post-upgrade`, `pre-delete`, `pre-rollback`, `test`. Ordered by `helm.sh/hook-weight`; cleaned up by `helm.sh/hook-delete-policy`. Typical use: DB migration Job before upgrade. Hook resources are not managed as part of the release.
- **Dependencies:** declared in `Chart.yaml`, with `condition` / `tags` to toggle. **Library charts** share helpers without rendering anything. An **umbrella chart** bundles several subcharts.
- **Distribution:** OCI registries (ECR supports it): `helm push`, `oci://...`.

## Commands Worth Knowing Cold

```bash
helm lint ./chart
helm template rel ./chart -f values-prod.yaml          # render locally
helm upgrade --install rel ./chart -n ns -f v.yaml --wait --timeout 5m --atomic
helm diff upgrade rel ./chart -f v.yaml                # plugin; preview changes
helm history rel -n ns
helm rollback rel 3 -n ns
helm get values rel -n ns [--all]
helm get manifest rel -n ns
helm status rel -n ns
```

## Common Pitfalls

| Problem | Cause / fix |
|---------|-------------|
| `another operation (install/upgrade/rollback) is in progress` | Release stuck in `pending-upgrade` after an interrupted run. `helm rollback` to the last good revision, or delete the pending release Secret. |
| CRDs not updated on upgrade | Files in `crds/` are install-only. Manage CRDs separately (own chart, or Flux `crds: CreateReplace`). |
| Upgrade fails on immutable field | e.g. Deployment `spec.selector`, StatefulSet `volumeClaimTemplates`. Needs delete and recreate, planned. |
| `--wait` times out | Pods never become ready. The problem is the workload, not Helm: check events and probes. |
| Secrets in values | Use External Secrets, SOPS, or CSI driver instead. |
| `helm uninstall` leaves PVCs and CRDs | By design. Clean up explicitly. |
| Too many revisions | Set `--history-max`. |

## Helm vs Kustomize

Helm = parameterised packaging and release lifecycle, good for distributing to many consumers. Kustomize = patch-based overlays with no templating, good for per-environment variation. They combine well: Flux `HelmRelease` for the chart, Kustomize overlays for per-cluster values.

