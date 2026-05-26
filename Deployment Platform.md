# Deployment Delivery —  Requirements

> **Vision:** A single place where a user can connect a code repository, configure a target cloud, deploy it, and then observe it — *and* a dashboard view that surfaces everything that has been set up across environments. Everything configurable.
>
> **Positioning:** This platform replaces Harness for all infra-providing setup — cloud connectors, environments, deployment targets, pipelines, approvals, secrets, and observability hookup are owned end-to-end here. Teams should not need Harness (or any third-party CD control plane) alongside this.

---

## 1. Scope (what we are building)

**In scope (v1):**
- Connect a source repository
- Build the app (containerize or package)
- Pick & configure a target cloud / runtime
- Deploy with a chosen strategy
- Centralized logs, metrics, deployment history
- A dashboard view of all apps, environments, and recent activity
- Full replacement for Harness in the infra-provisioning + deploy + observe loop



## 2. Personas

Only two personas. Everything in the product collapses to one of these.

| Persona | What they do here |
|---|---|
| **Admin** | Sets up cloud connectors, container registries, secret managers, environments, notification channels, RBAC, governance/approval rules; manages users; sees org-wide dashboard and audit log |
| **User** | Connects a repo, configures the build, picks an environment, deploys, watches the live execution, reads logs and metrics for apps they own or have access to |

Journey 1 below is primarily for **User** (with **Admin** doing one-time setup of cloud connectors and environments in steps 4–7). Journey 2 (dashboard) is used by both, with Admin seeing org-wide and User seeing their scoped view.

---

## 3. Core domain model

These are the entities the entire platform revolves around. Get these right early — retrofitting hierarchy later is painful.

```
Organization
└── Project
    ├── Connector            (Repo, Cloud, Registry, SecretManager, Notification)
    ├── Environment          (dev / staging / prod / custom)
    ├── Application
    │   ├── Service          (a deployable unit — usually one repo or one component)
    │   │   ├── Build config
    │   │   ├── Deploy config (per environment)
    │   │   └── Triggers     (on-push, on-tag, manual, scheduled)
    │   └── Pipeline         (build → test → deploy stages, a DAG)
    └── Execution            (a single run of a pipeline; immutable, time-stamped)
```

**Why this matters:** Every API, every permission check, every dashboard filter pivots on this hierarchy. Designing the URL structure (`/org/{org}/project/{proj}/app/{app}`) and the row-level security on day one saves months later.

---

## 4. User Journey 1 — Onboard & deploy a new app

This is the "happy path" wizard the user walks through the first time. Each step must be **resumable** (they save progress and come back) and **editable** (they revisit a step later).

### Step-by-step

| # | Step | What the user does | What the system does | Required configurable inputs |
|---|---|---|---|---|
| 1 | **Create / pick project** | Names a project | Creates Org/Project scoping | Name, description |
| 2 | **Connect repo** | Picks GitHub / GitLab / Bitbucket / Azure Repos / generic Git; authorizes | Stores OAuth token or PAT (in secret store, not DB), lists repos | Provider, auth method (OAuth / PAT / SSH key), repo URL, branch |
| 3 | **Detect / configure build** | Confirms autodetected stack or overrides | Detects language (Node, Java, Python, Go, .NET, WaveMaker app, static site…), suggests Dockerfile or buildpack | Build tool (Dockerfile / Buildpack / custom script), build command, output artifact (image / WAR / zip / static folder), registry destination |
| 4 | **Pick target cloud** | Chooses AWS / Azure / GCP / on-prem / Kubernetes-anywhere | Loads the connector form for that cloud | Cloud provider |
| 5 | **Cloud connector** | Provides credentials | Validates with a `whoami`-style call, stores reference in secret manager | AWS: access key + secret OR IAM role / OIDC; Azure: service principal OR managed identity; GCP: service account JSON OR workload identity; K8s: kubeconfig OR in-cluster |
| 6 | **Pick deployment target** | Chooses the runtime within that cloud | Shows only options valid for that cloud | AWS: ECS, EKS, EC2, Lambda, App Runner, Elastic Beanstalk · Azure: AKS, App Service, Container Apps, VMSS · GCP: GKE, Cloud Run, Compute Engine · K8s: any cluster · On-prem: SSH/VM |
| 7 | **Pick / create environment** | dev / staging / prod | Creates the environment record | Name, type (non-prod / prod), approval required? |
| 8 | **Deploy configuration** | Resources, replicas, env vars, ports | Renders the right form for the target | Replicas, CPU/memory, env vars, secrets refs, port mapping, health check path, ingress/domain |
| 9 | **Deployment strategy** | Picks how the rollout happens | Generates the right manifest/script | Rolling (default), Blue-Green, Canary (with %), Recreate |
| 10 | **Observability hookup** | Picks where logs/metrics go | Wires log shipper / metrics scraper | Logs: platform-default / Datadog / CloudWatch / ELK / Loki · Metrics: platform-default / Prometheus / CloudWatch · Alerts: Slack / email / PagerDuty / webhook |
| 11 | **Triggers** | When should this deploy run? | Creates webhooks / cron entries | On push to branch X · On tag matching pattern · Manual only · Scheduled (cron) · On PR merge |
| 12 | **Review & launch** | Sees a summary | Persists pipeline, kicks first run | — |
| 13 | **Live execution view** | Watches step-by-step logs | Streams logs from the executor | — |

### Visual — the onboarding flow

```mermaid
flowchart TD
    A([Start]) --> B[1 Create or pick Project]
    B --> C[2 Connect Repo]
    C --> C1{Auth method}
    C1 -->|OAuth| C2[Authorize via provider]
    C1 -->|PAT / SSH| C3[Paste credential]
    C2 --> D
    C3 --> D
    D[3 Configure Build] --> D1{Autodetect succeeded?}
    D1 -->|Yes| D2[Confirm or tweak]
    D1 -->|No| D3[Manual: tool, command, artifact]
    D2 --> E
    D3 --> E
    E[4 Pick Cloud] --> E1{Which cloud?}
    E1 -->|AWS| F1[5a AWS Connector]
    E1 -->|Azure| F2[5b Azure Connector]
    E1 -->|GCP| F3[5c GCP Connector]
    E1 -->|K8s anywhere| F4[5d Kubeconfig]
    E1 -->|On-prem VM| F5[5e SSH credential]
    F1 --> G
    F2 --> G
    F3 --> G
    F4 --> G
    F5 --> G
    G[6 Pick Deployment Target<br/>filtered by cloud] --> H[7 Pick or create Environment]
    H --> H1{Prod?}
    H1 -->|Yes| H2[Require approval]
    H1 -->|No| I
    H2 --> I
    I[8 Deploy config<br/>replicas, env vars, secrets, ports] --> J[9 Deployment Strategy<br/>Rolling / Blue-Green / Canary]
    J --> K[10 Observability<br/>Logs, Metrics, Alerts]
    K --> L[11 Triggers<br/>push / tag / manual / cron]
    L --> M[12 Review and Launch]
    M --> N[13 Live Execution View]
    N --> Z([Deployed])

    style A fill:#1f6feb,color:#fff
    style Z fill:#1a7f37,color:#fff
    style M fill:#bf8700,color:#fff
```

---

## 5. User Journey 2 — Dashboard / discovery

The dashboard answers: *"What do we have, where is it, is it healthy?"*

### Information architecture

```
Dashboard (landing)
├── Overview tiles
│   ├── Total Applications
│   ├── Total Environments
│   ├── Deployments today / week
│   ├── Success rate (7-day)
│   └── Active executions (live count)
│
├── Environment view
│   ├── dev  → list of apps + version + last deployed + health
│   ├── staging → ...
│   └── prod → ...
│
├── Application view
│   ├── Per app: current versions across all envs
│   ├── Deployment history (timeline)
│   ├── Logs (last N minutes, filterable)
│   ├── Metrics (CPU, mem, request rate, error rate)
│   └── Alerts (open / resolved)
│
├── Activity feed
│   ├── Who deployed what, where, when
│   └── Filters: user, app, env, status
│
└── Connectors & settings
    ├── Cloud connectors (health check status)
    ├── Repo connectors
    ├── Secret managers
    └── Notification channels
```

### Visual — dashboard navigation

```mermaid
flowchart LR
    DASH[Dashboard Home] --> OV[Overview Tiles]
    DASH --> ENV[By Environment]
    DASH --> APP[By Application]
    DASH --> ACT[Activity Feed]
    DASH --> SET[Connectors and Settings]

    ENV --> ENV1[dev]
    ENV --> ENV2[staging]
    ENV --> ENV3[prod]
    ENV1 --> APPLIST1[Apps in dev<br/>version, health, last deploy]
    ENV2 --> APPLIST2[Apps in staging]
    ENV3 --> APPLIST3[Apps in prod]

    APP --> APPDETAIL[App detail page]
    APPDETAIL --> AD1[Versions across envs]
    APPDETAIL --> AD2[Deployment history]
    APPDETAIL --> AD3[Logs]
    APPDETAIL --> AD4[Metrics]
    APPDETAIL --> AD5[Alerts]

    APPLIST1 -.click app.-> APPDETAIL
    APPLIST2 -.click app.-> APPDETAIL
    APPLIST3 -.click app.-> APPDETAIL

    style DASH fill:#1f6feb,color:#fff
    style APPDETAIL fill:#1a7f37,color:#fff
```

### Example: "dev instance — how many apps are there?"

The user lands on dashboard → clicks **By Environment → dev**. They see a table:

| App | Version | Last deployed | Deployed by | Health | Logs |
|---|---|---|---|---|---|
| billing-api | v1.4.2 | 2h ago | jane@... | ● Healthy | [view] |
| customer-ui | v0.9.0-rc3 | 30m ago | mike@... | ● Healthy | [view] |
| reports-job | v2.1.0 | 1d ago | jane@... | ⚠ Degraded | [view] |

Clicking an app row opens its detail page (right side of the diagram above).

---

## 6. Screens

The screens below are the full UI surface for v1. Each screen lists its primary persona, what it does, and the key actions on it. Screens marked **Admin** are gated by RBAC; screens marked **User** are visible to both personas (Admin sees an org-wide variant).

### 6.1 Auth & onboarding

| # | Screen | Persona | Purpose | Primary actions |
|---|---|---|---|---|
| S1 | **Sign in** | Both | SSO / SAML / email login | Sign in, forgot password |
| S2 | **Org switcher / picker** | Both | Choose org if user belongs to multiple | Pick org, create org (first-time admin) |
| S3 | **Project list** | Both | All projects in the current org | Open project, create project, search |
| S4 | **Create / edit project** | User | Name, description, owners | Save, cancel |

### 6.2 Onboarding wizard (Journey 1)

One screen per wizard step. The wizard has a persistent **left rail** showing all 13 steps with status (done / current / pending) so the user can jump between them. Every step is resumable.

| # | Screen | Persona | Purpose |
|---|---|---|---|
| S5 | **Step 1 — Project basics** | User | Name, description (re-uses S4) |
| S6 | **Step 2 — Connect repo** | User | Pick provider, authorize, pick repo & branch |
| S7 | **Step 3 — Build config** | User | Autodetect result + override (Dockerfile / Buildpack / custom / WaveMaker); registry target |
| S8 | **Step 4 — Pick cloud** | User | AWS / Azure / GCP / K8s / on-prem cards |
| S9 | **Step 5 — Cloud connector picker** | User | Pick from existing connectors (set up by Admin) **or** request Admin add one |
| S10 | **Step 6 — Pick deployment target** | User | Target cards filtered by chosen cloud (ECS, EKS, Cloud Run, etc.) |
| S11 | **Step 7 — Pick / create environment** | User | Pick existing env or request a new one (prod creation is Admin-only) |
| S12 | **Step 8 — Deploy config** | User | Replicas, CPU/mem, env vars, secret refs, ports, health checks, ingress |
| S13 | **Step 9 — Deployment strategy** | User | Rolling / Blue-Green / Canary / Recreate + rollback rules |
| S14 | **Step 10 — Observability hookup** | User | Logs sink, metrics sink, alert channels |
| S15 | **Step 11 — Triggers** | User | On push / on tag / manual / cron / on PR merge |
| S16 | **Step 12 — Review & launch** | User | Full summary, edit any step, launch |
| S17 | **Step 13 — Live execution view** | User | Streaming logs, per-step status, cancel, retry |

### 6.3 Dashboard (Journey 2)

| # | Screen | Persona | Purpose |
|---|---|---|---|
| S18 | **Dashboard home** | Both | Overview tiles: total apps, envs, deploys today/week, 7-day success rate, active executions |
| S19 | **By Environment — env list** | Both | dev / staging / prod tiles with rollup health |
| S20 | **Environment detail** | Both | Table of apps in that env (version, last deploy, deployed by, health, logs link) |
| S21 | **By Application — app list** | Both | All apps in the project, filterable |
| S22 | **Application detail** | Both | Tabs: Versions across envs · Deployment history · Logs · Metrics · Alerts · Config |
| S23 | **Live logs viewer** | Both | WebSocket tail with filter, time range, download |
| S24 | **Metrics viewer** | Both | Pre-baked charts (CPU, mem, RPS, error rate) with deployment markers overlaid |
| S25 | **Activity feed** | Both | Who deployed what, where, when; filterable by user/app/env/status |
| S26 | **Execution detail** | Both | Re-open any past execution; logs, artifacts, approver, duration |

### 6.4 Admin screens

| # | Screen | Persona | Purpose |
|---|---|---|---|
| S27 | **Cloud connectors list** | Admin | All connectors, health-check status (red dot if broken), add/edit/delete |
| S28 | **Add / edit cloud connector** | Admin | Schema-driven form per cloud (AWS / Azure / GCP / K8s / on-prem); validates on save |
| S29 | **Container registries** | Admin | Docker Hub / ECR / ACR / GAR / GHCR / generic OCI; credentials & default registry |
| S30 | **Repo connectors** | Admin | GitHub / GitLab / Bitbucket / Azure Repos / generic Git; org-wide install of GitHub App, etc. |
| S31 | **Secret managers** | Admin | Built-in vault OR reference customer Vault / AWS SM / Azure KV / GCP SM |
| S32 | **Secrets browser** | Admin | List, rotate, audit access; secret values never shown in UI after creation |
| S33 | **Environments management** | Admin | Create/edit envs, mark prod, set approval rules, bind to clusters/clouds, per-env vars |
| S34 | **Notification channels** | Admin | Slack / Teams / email / webhook / PagerDuty; test send |
| S35 | **Users & RBAC** | Admin | Invite users, assign Admin or User, scope to projects/envs |
| S36 | **Approval inbox** | Admin | Pending prod-deploy approvals; approve, reject, comment |
| S37 | **Audit log** | Admin | Immutable record of every config change and deploy; filter by actor, resource, time |
| S38 | **Org settings** | Admin | SSO/SAML config, retention policies, billing (post-v1), default region |

### 6.5 Cross-cutting UI elements

These appear inside many screens, not as standalone routes:

- **Global search** (top bar): apps, envs, executions, users
- **Live execution drawer** (right-side slide-out): tail any in-flight execution from any screen
- **Notification bell**: in-app notifications for approvals, failed deploys, unhealthy connectors
- **Persona-aware nav**: User sees Projects + Dashboard; Admin additionally sees Connectors, Users, Audit, Org Settings

### Screen-to-journey map

```mermaid
flowchart LR
    subgraph J1[Journey 1 — Onboard & deploy]
      S6 --> S7 --> S8 --> S9 --> S10 --> S11 --> S12 --> S13 --> S14 --> S15 --> S16 --> S17
    end
    subgraph J2[Journey 2 — Dashboard]
      S18 --> S19 --> S20
      S18 --> S21 --> S22
      S22 --> S23
      S22 --> S24
      S18 --> S25 --> S26
    end
    subgraph ADMIN[Admin setup — prerequisite to J1]
      S27 --> S28
      S30
      S33
      S35
    end
    ADMIN -.connectors & envs feed.-> J1
    style ADMIN fill:#bf8700,color:#fff
    style J1 fill:#1f6feb,color:#fff
    style J2 fill:#1a7f37,color:#fff
```

---

## 7. Functional requirements by module

### 7.1 Repository integration
- Supported providers: GitHub (cloud + Enterprise), GitLab (cloud + self-hosted), Bitbucket, Azure Repos, generic Git over HTTPS/SSH.
- Auth: OAuth app, PAT, SSH key, GitHub App (recommended for fine-grained perms).
- Capabilities: list repos, list branches, register webhook, fetch file (for autodetect), clone (delegated to executor).
- Webhook events: push, tag, PR merge.

### 7.2 Build configuration
- Autodetect: presence of `Dockerfile`, `package.json`, `pom.xml`, `requirements.txt`, `go.mod`, `*.csproj`, WaveMaker `wm-project.xml`, etc.
- Build modes:
  - **Dockerfile** (preferred default)
  - **Buildpacks** (Paketo / Heroku) — zero-config
  - **Custom script** (shell)
  - **Platform-specific** (WaveMaker WAR build — already exists as a skill in this repo)
- Outputs: container image (push to registry), or artifact (WAR/zip/static).
- Container registries: Docker Hub, ECR, ACR, GAR/GCR, GHCR, generic OCI.

### 7.3 Cloud connectors
- Each connector is a typed plugin. Schema per cloud:

| Cloud | Auth options | Validation |
|---|---|---|
| AWS | IAM access key, IAM role assumption, OIDC federation | `sts:GetCallerIdentity` |
| Azure | Service principal (client id + secret), managed identity, federated credential | `az account show` equivalent |
| GCP | Service account JSON, workload identity | `oauth2/v3/tokeninfo` |
| Kubernetes | Kubeconfig, in-cluster SA token | `kubectl get ns` |
| On-prem VM | SSH key + host | `ssh user@host echo ok` |

- Connectors must support **health check** on a schedule (every 5 min); dashboard shows red dot if a connector is broken.

### 7.4 Deployment targets (per cloud)

| Cloud | Targets |
|---|---|
| AWS | ECS Fargate, EKS, EC2 (via SSH or SSM), Lambda (zip / image), App Runner, Elastic Beanstalk, S3 + CloudFront (static) |
| Azure | AKS, App Service, Container Apps, VMSS, Azure Functions, Static Web Apps |
| GCP | GKE, Cloud Run, Compute Engine, Cloud Functions, Cloud Storage + CDN |
| K8s anywhere | Any reachable cluster via kubeconfig (Helm, raw manifests, Kustomize) |
| On-prem | SSH-to-VM (docker run, systemd, custom script) |

Each target has its own config schema (ports, scaling, ingress, etc.) but the **wizard shape** is identical — pick target, fill schema, validate.

### 7.5 Environments
- Named (dev/staging/prod, but free-form).
- Type: non-prod / prod (governs approval rules).
- Bound to specific clusters/clouds (an env can span multiple, e.g. prod-us-east + prod-eu-west).
- Per-env variable overrides.

### 7.6 Deployment strategies
- **Rolling** — default for K8s/ECS; surge & unavailable knobs.
- **Blue-Green** — two stacks, traffic swap (LB/ingress swap).
- **Canary** — % traffic, time per step, auto-promote on healthy.
- **Recreate** — stop all, then start all (rare, for stateful).
- Strategy must declare **rollback behavior** (auto-rollback on health-check fail? manual?).

### 7.7 Observability
- **Logs:** built-in storage (ship from executor + from running workloads via sidecar/agent) with retention policy. Plus integrations to push to Datadog/CloudWatch/Loki/ELK.
- **Metrics:** Prometheus-compatible scrape from the workload; pre-baked dashboards per target type.
- **Alerts:** rule engine (Prometheus alerting style) + channels (Slack/email/PagerDuty/webhook).
- **Deployment markers:** every deploy emits a marker visible on metric charts — critical for "did this deploy cause the regression?"

### 7.8 Dashboard
- Filters: org, project, app, env, time range, status.
- Live execution count + WebSocket-based live log tailing.
- Saved views per user.
- Exportable (CSV) for management reporting.

### 7.9 Notifications
- Channels: Slack, MS Teams, email, generic webhook, PagerDuty.
- Events: pipeline started/failed/succeeded, deploy started/failed/succeeded, approval requested, connector unhealthy.

### 7.10 RBAC
- Roles: **Admin** and **User** — mirrors the two personas. No other roles in v1.
  - **Admin**: full control over connectors, environments, RBAC, secrets, governance; can deploy to any environment.
  - **User**: can create/edit applications and pipelines within projects they're added to; can deploy to non-prod environments by default; prod requires an Admin approval.
- Scope: per Org, per Project, per Environment (e.g. "User X can deploy to dev/staging in project Y, not prod").
- Audit log of every config change and every deploy.

### 7.11 Secrets
- Never store customer secrets in app DB.
- Either: (a) built-in secret store backed by Vault/KMS, or (b) reference customer's own (AWS SM, Azure KV, GCP SM, HashiCorp Vault).
- Secrets referenced by alias in env vars (`${secret:db-password}`).

---

## 8. Non-functional requirements

| Area | Requirement |
|---|---|
| **Scale** | Day-1: 100 orgs, 10 projects each, 1000 deploys/day. Year-1: 10× that. |
| **Latency** | Dashboard P95 < 1s for cached views; live log lag < 2s. |
| **Reliability** | Control plane 99.9% (≈ 8h/yr down). Pipelines survive control-plane restart mid-run. |
| **Security** | TLS everywhere, secrets never logged, SSO/SAML, audit log immutable, SOC2-ready. |
| **Tenancy** | Hard isolation: tenant A's executor cannot read tenant B's secrets, jobs, or logs. |
| **Extensibility** | New cloud or target = a plugin module, not a core change. |

---

