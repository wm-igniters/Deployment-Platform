#!/usr/bin/env python3
"""Generate the 38-screen HTML prototype for the Deployment Delivery platform.

Run: python3 build.py
Output: index.html + S1-...html ... S38-...html in this directory.
"""
from pathlib import Path

OUT = Path(__file__).parent

WIZARD_STEPS = [
    ("S5",  "step1-basics",     "Project basics"),
    ("S6",  "step2-repo",       "Connect repo"),
    ("S7",  "step3-build",      "Build config"),
    ("S8",  "step4-cloud",      "Pick cloud"),
    ("S9",  "step5-connector",  "Cloud connector"),
    ("S10", "step6-target",     "Deployment target"),
    ("S11", "step7-env",        "Environment"),
    ("S12", "step8-deploy-cfg", "Deploy config"),
    ("S13", "step9-strategy",   "Strategy"),
    ("S14", "step10-observ",    "Observability"),
    ("S15", "step11-triggers",  "Triggers"),
    ("S16", "step12-review",    "Review & launch"),
    ("S17", "step13-live",      "Live execution"),
]

def slug_for(sid):
    for sx, sl, _ in WIZARD_STEPS:
        if sx == sid: return sl
    return None

def wizard_nav(current_sid):
    # current_sid is one of S5..S17
    pieces = []
    cur_idx = next((i for i, (sid, _, _) in enumerate(WIZARD_STEPS) if sid == current_sid), -1)
    for i, (sid, sl, lbl) in enumerate(WIZARD_STEPS):
        n = i + 1
        if i < cur_idx:
            cls = "step done"
        elif i == cur_idx:
            cls = "step current"
        else:
            cls = "step"
        href = f"{sid}-{sl}.html"
        pieces.append(f'<a class="{cls}" href="{href}">{n}. {lbl}</a>')
    return '<div class="stepper">' + "".join(pieces) + '</div>'

def sidebar(persona, active=""):
    user_items = [
        ("Projects", "S3-project-list.html"),
        ("Dashboard", "S18-dashboard.html"),
        ("By Environment", "S19-env-list.html"),
        ("By Application", "S21-app-list.html"),
        ("Activity", "S25-activity.html"),
    ]
    admin_items = [
        ("Cloud connectors", "S27-connectors.html"),
        ("Container registries", "S29-registries.html"),
        ("Repo connectors", "S30-repos.html"),
        ("Secret managers", "S31-secret-mgrs.html"),
        ("Secrets", "S32-secrets.html"),
        ("Environments", "S33-envs.html"),
        ("Notifications", "S34-notif.html"),
        ("Users & RBAC", "S35-users.html"),
        ("Approvals", "S36-approvals.html"),
        ("Audit log", "S37-audit.html"),
        ("Org settings", "S38-org.html"),
    ]
    def render_group(label, items):
        out = [f'<div class="nav-label">{label}</div>']
        for nm, href in items:
            cls = "nav-item active" if href == active else "nav-item"
            out.append(f'<a class="{cls}" href="{href}"><span class="nav-icon"></span>{nm}</a>')
        return "\n".join(out)
    html = ['<aside class="sidebar">']
    html.append('<div class="nav-group">')
    html.append(render_group("Workspace", user_items))
    html.append("</div>")
    if persona == "Admin":
        html.append('<div class="nav-group">')
        html.append(render_group("Admin", admin_items))
        html.append("</div>")
    html.append("</aside>")
    return "\n".join(html)

def page(sid, slug, title, persona, crumb_html, body, active="", show_chrome=True):
    """Render a screen page. `crumb_html` may include <b>...</b> tags."""
    persona_class = "admin" if persona == "Admin" else ""
    persona_label = persona
    chrome_top = f"""<div class="logo-area"><div class="logo-dot"></div>Deployment Delivery</div>
<header class="appbar">
  <div class="crumb">{crumb_html}</div>
  <input class="search" placeholder="Search apps, envs, executions…">
  <span class="persona-badge {persona_class}">{persona_label}</span>
  <div class="avatar">GK</div>
</header>
{sidebar(persona, active=active)}"""
    if not show_chrome:
        chrome_top = ""

    file_name = f"{sid}-{slug}.html"
    html = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<title>{sid} — {title} · Deployment Delivery</title>
<link rel="stylesheet" href="styles.css">
</head><body>
{chrome_top}
<main class="content">
  <span class="screen-id">{sid}</span>
  <h1>{title}</h1>
  {body}
  <div class="back-link"><a href="index.html">← All screens</a></div>
</main>
</body></html>"""
    (OUT / file_name).write_text(html, encoding="utf-8")
    return file_name

def wizard_page(sid, title, body_inner, help_html=None):
    """Wizard screen: stepper + two-col (form + help) + prev/next."""
    slug = slug_for(sid)
    idx = next(i for i, (s, _, _) in enumerate(WIZARD_STEPS) if s == sid)
    prev_sid, prev_slug, prev_lbl = WIZARD_STEPS[idx-1] if idx > 0 else (None, None, None)
    next_sid, next_slug, next_lbl = WIZARD_STEPS[idx+1] if idx < len(WIZARD_STEPS)-1 else (None, None, None)
    prev_html = f'<a href="{prev_sid}-{prev_slug}.html" class="btn">← {prev_lbl}</a>' if prev_sid else '<span></span>'
    next_html = f'<a href="{next_sid}-{next_slug}.html" class="btn primary">{next_lbl} →</a>' if next_sid else '<a href="S17-step13-live.html" class="btn primary">Launch →</a>'
    help_block = help_html or ""
    body = f"""
    <p class="subtitle">Step {idx+1} of 13 · Onboarding wizard · billing-api</p>
    {wizard_nav(sid)}
    <div class="two-col">
      <div>{body_inner}</div>
      <div>{help_block}</div>
    </div>
    <div class="wiz-nav">{prev_html}{next_html}</div>
    """
    crumb = '<a href="S3-project-list.html">payments-platform</a> / <a href="S21-app-list.html">Applications</a> / <b>New app · billing-api</b>'
    return page(sid, slug, title, "User", crumb, body, active="S3-project-list.html")


# ─── INDEX ────────────────────────────────────────────────────

INDEX_SECTIONS = [
    ("Auth & onboarding", "S1–S4", [
        ("S1", "signin", "Sign in", "Both"),
        ("S2", "org-switcher", "Org switcher / picker", "Both"),
        ("S3", "project-list", "Project list", "Both"),
        ("S4", "project-create", "Create / edit project", "User"),
    ]),
    ("Onboarding wizard (Journey 1)", "S5–S17", [
        (sid, slug, lbl, "User") for sid, slug, lbl in WIZARD_STEPS
    ]),
    ("Dashboard (Journey 2)", "S18–S26", [
        ("S18", "dashboard",     "Dashboard home", "Both"),
        ("S19", "env-list",      "By Environment — list", "Both"),
        ("S20", "env-detail",    "Environment detail", "Both"),
        ("S21", "app-list",      "By Application — list", "Both"),
        ("S22", "app-detail",    "Application detail", "Both"),
        ("S23", "logs",          "Live logs viewer", "Both"),
        ("S24", "metrics",       "Metrics viewer", "Both"),
        ("S25", "activity",      "Activity feed", "Both"),
        ("S26", "exec-detail",   "Execution detail", "Both"),
    ]),
    ("Admin", "S27–S38", [
        ("S27", "connectors",    "Cloud connectors list", "Admin"),
        ("S28", "connector-edit","Add / edit cloud connector", "Admin"),
        ("S29", "registries",    "Container registries", "Admin"),
        ("S30", "repos",         "Repo connectors", "Admin"),
        ("S31", "secret-mgrs",   "Secret managers", "Admin"),
        ("S32", "secrets",       "Secrets browser", "Admin"),
        ("S33", "envs",          "Environments management", "Admin"),
        ("S34", "notif",         "Notification channels", "Admin"),
        ("S35", "users",         "Users & RBAC", "Admin"),
        ("S36", "approvals",     "Approval inbox", "Admin"),
        ("S37", "audit",         "Audit log", "Admin"),
        ("S38", "org",           "Org settings", "Admin"),
    ]),
]

def build_index():
    sections_html = []
    for label, range_lbl, items in INDEX_SECTIONS:
        cards = []
        for sid, slug, lbl, persona in items:
            pp_cls = "pp admin" if persona == "Admin" else "pp"
            cards.append(f"""<a class="idx-card" href="{sid}-{slug}.html">
                <span class="sid">{sid} · {range_lbl.split('–')[0] if False else ''}</span>
                <span class="nm">{lbl}</span>
                <span class="{pp_cls}">{persona}</span>
            </a>""")
        sections_html.append(f"""<section class="index-section">
            <h2><span>{label}</span><span class="muted small">{range_lbl}</span></h2>
            <div class="index-grid">{''.join(cards)}</div>
        </section>""")
    body = "\n".join(sections_html)
    html = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<title>Deployment Delivery — Screen prototype</title>
<link rel="stylesheet" href="styles.css">
<style>
  body {{ display: block; }}
  .content {{ max-width: 1200px; margin: 0 auto; padding: 24px 36px 80px; }}
  .top {{ display: flex; align-items: center; padding: 14px 36px; border-bottom: 1px solid var(--border); background: var(--panel); }}
  .top .logo-dot {{ margin-right: 10px; }}
  .top .brand {{ font-weight: 600; }}
  .top .meta {{ margin-left: auto; color: var(--muted); font-size: 13px; }}
</style>
</head><body>
<div class="top">
  <div class="logo-dot"></div>
  <span class="brand">Deployment Delivery</span>
  <span class="meta">Static screen prototype · 38 screens</span>
</div>
<main class="content">
  <div class="index-hero">
    <h1>Screen prototype</h1>
    <p>Clickable mock of every screen in §6 of the requirements doc. Each screen is static — buttons and links navigate between screens but do not call APIs. Use this to walk product/eng/design through the surface area before backend work starts.</p>
  </div>
  {body}
</main>
</body></html>"""
    (OUT / "index.html").write_text(html, encoding="utf-8")


# ─── SCREEN BODIES ────────────────────────────────────────────
# Each function returns (sid, body, crumb, persona, active, slug_override?)

def build_S1():
    body = """
    <div style="max-width:380px;margin:8vh auto;text-align:center">
      <div class="logo-dot" style="width:48px;height:48px;margin:0 auto 16px;border-radius:12px"></div>
      <h1 style="margin-bottom:6px">Welcome back</h1>
      <p class="muted" style="margin-top:0">Sign in to Deployment Delivery</p>
      <div class="card" style="text-align:left;margin-top:24px">
        <a class="btn" style="width:100%;justify-content:center;margin-bottom:8px">Continue with SSO (SAML)</a>
        <a class="btn" style="width:100%;justify-content:center;margin-bottom:18px">Continue with Google</a>
        <div class="field"><label>Email</label><input value="gayathri@wavemaker.com"></div>
        <div class="field"><label>Password</label><input type="password" value="••••••••"></div>
        <a class="btn primary" href="S2-org-switcher.html" style="width:100%;justify-content:center">Sign in</a>
        <p class="small muted" style="text-align:center;margin:14px 0 0"><a href="#">Forgot password?</a></p>
      </div>
    </div>
    """
    return page("S1", "signin", "Sign in", "Both", "<b>Sign in</b>", body, show_chrome=False)

def build_S2():
    body = """
    <p class="subtitle">Pick the organization you want to work in.</p>
    <div class="choice-grid">
      <a class="choice selected" href="S3-project-list.html"><span class="ico">🏢</span><div class="nm">WaveMaker</div><div class="desc">12 projects · You are Admin</div></a>
      <a class="choice" href="S3-project-list.html"><span class="ico">🏢</span><div class="nm">wm-igniters</div><div class="desc">3 projects · User</div></a>
      <a class="choice" href="S3-project-list.html"><span class="ico">🏢</span><div class="nm">Acme Corp</div><div class="desc">5 projects · User</div></a>
      <a class="choice" href="#"><span class="ico">＋</span><div class="nm">Create new organization</div><div class="desc">Admin only</div></a>
    </div>
    """
    return page("S2", "org-switcher", "Switch organization", "Both",
                '<b>Organizations</b>', body)

def build_S3():
    body = """
    <div class="row" style="margin-bottom:16px">
      <input class="search" placeholder="Search projects…" style="width:320px">
      <div class="spacer"></div>
      <a class="btn primary" href="S4-project-create.html">+ New project</a>
    </div>
    <div class="card" style="padding:0">
      <table>
        <thead><tr><th>Project</th><th>Apps</th><th>Environments</th><th>Last deploy</th><th>Owner</th></tr></thead>
        <tbody>
          <tr><td><a href="S18-dashboard.html"><b>payments-platform</b></a><div class="small muted">Billing, customer-ui, reports-job</div></td><td>3</td><td>dev · staging · prod</td><td>30m ago</td><td>jane@…</td></tr>
          <tr><td><a href="S18-dashboard.html"><b>identity</b></a><div class="small muted">Auth + SSO services</div></td><td>2</td><td>dev · prod</td><td>4h ago</td><td>mike@…</td></tr>
          <tr><td><a href="S18-dashboard.html"><b>data-pipelines</b></a><div class="small muted">Ingest, transform, warehouse loaders</div></td><td>7</td><td>dev · staging · prod · eu-prod</td><td>2d ago</td><td>priya@…</td></tr>
          <tr><td><a href="S18-dashboard.html"><b>internal-tools</b></a><div class="small muted">Ops dashboards, runbooks</div></td><td>4</td><td>dev · prod</td><td>1w ago</td><td>gayathri@…</td></tr>
        </tbody>
      </table>
    </div>
    """
    return page("S3", "project-list", "Projects", "Admin",
                '<b>WaveMaker</b> / Projects', body, active="S3-project-list.html")

def build_S4():
    body = """
    <p class="subtitle">A project groups applications, environments, and connectors. Name it for your team or product area.</p>
    <div class="card" style="max-width:640px">
      <div class="field"><label>Project name</label><input value="payments-platform"><div class="hint">Used in URLs: /org/wavemaker/project/payments-platform</div></div>
      <div class="field"><label>Description</label><textarea rows="3">All services that power billing, invoicing, and payouts.</textarea></div>
      <div class="field"><label>Owners</label><input value="jane@wavemaker.com, mike@wavemaker.com"></div>
      <div class="field"><label>Default region</label><select><option>us-east-1</option><option>eu-west-1</option><option>ap-south-1</option></select></div>
      <div class="wiz-nav"><a class="btn" href="S3-project-list.html">Cancel</a><a class="btn primary" href="S5-step1-basics.html">Create project →</a></div>
    </div>
    """
    return page("S4", "project-create", "Create project", "User",
                '<a href="S3-project-list.html">Projects</a> / <b>New project</b>', body, active="S3-project-list.html")

# Wizard screens (S5-S17) ------------------------------------------

def build_S5():
    inner = """
    <div class="card">
      <div class="field"><label>App name</label><input value="billing-api"><div class="hint">Letters, digits, dashes. Becomes the slug for URLs and deployments.</div></div>
      <div class="field"><label>Description</label><textarea rows="3">REST API for invoicing, payments, and webhooks from Stripe.</textarea></div>
      <div class="field"><label>Owners</label><input value="jane@wavemaker.com"></div>
    </div>
    """
    help_ = """<div class="help-card"><h4>What is an app?</h4><p>A deployable unit. Usually one repo or one component.</p><ul><li>Has its own build, deploy, and triggers</li><li>Lives inside one project</li><li>Can be deployed to multiple environments</li></ul></div>"""
    return wizard_page("S5", "Project basics", inner, help_)

def build_S6():
    inner = """
    <div class="card">
      <h3>Source provider</h3>
      <div class="choice-grid">
        <div class="choice selected"><span class="ico">⬛</span><div class="nm">GitHub</div></div>
        <div class="choice"><span class="ico">🦊</span><div class="nm">GitLab</div></div>
        <div class="choice"><span class="ico">🔵</span><div class="nm">Bitbucket</div></div>
        <div class="choice"><span class="ico">⏶</span><div class="nm">Azure Repos</div></div>
        <div class="choice"><span class="ico">＋</span><div class="nm">Generic Git</div></div>
      </div>
      <h3>Auth method</h3>
      <div class="field"><select><option>GitHub App (recommended)</option><option>OAuth</option><option>Personal access token</option><option>SSH key</option></select></div>
      <h3>Repository</h3>
      <div class="field"><input value="wm-igniters/billing-api"></div>
      <h3>Branch</h3>
      <div class="field"><select><option>main</option><option>develop</option><option>release/*</option></select></div>
      <p class="small"><span class="pill healthy">Connected · webhook installed</span></p>
    </div>
    """
    help_ = """<div class="help-card"><h4>Why GitHub App?</h4><p>Finer-grained scopes than OAuth, and the token isn't tied to a single user.</p></div>"""
    return wizard_page("S6", "Connect repo", inner, help_)

def build_S7():
    inner = """
    <div class="card">
      <p><span class="pill healthy">Autodetected · Dockerfile found at repo root</span></p>
      <h3>Build tool</h3>
      <div class="choice-grid">
        <div class="choice selected"><span class="ico">🐳</span><div class="nm">Dockerfile</div><div class="desc">./Dockerfile</div></div>
        <div class="choice"><span class="ico">📦</span><div class="nm">Buildpacks</div><div class="desc">Paketo / Heroku</div></div>
        <div class="choice"><span class="ico">⚙</span><div class="nm">Custom script</div></div>
        <div class="choice"><span class="ico">🌊</span><div class="nm">WaveMaker WAR</div></div>
      </div>
      <h3>Build command (override)</h3>
      <div class="field"><input value="docker build -t billing-api ." class="mono"></div>
      <h3>Artifact</h3>
      <div class="field"><select><option>Container image</option><option>WAR</option><option>Zip</option><option>Static folder</option></select></div>
      <h3>Registry destination</h3>
      <div class="field"><select><option>ECR · wm-prod (default)</option><option>Docker Hub · wmlabs</option><option>GHCR · wm-igniters</option><option>+ Add new registry</option></select></div>
    </div>
    """
    help_ = """<div class="help-card"><h4>Autodetect looks for</h4><ul><li>Dockerfile</li><li>package.json, pom.xml, go.mod, requirements.txt, *.csproj</li><li>wm-project.xml (WaveMaker)</li></ul></div>"""
    return wizard_page("S7", "Build config", inner, help_)

def build_S8():
    inner = """
    <div class="card">
      <h3>Target cloud</h3>
      <div class="choice-grid">
        <div class="choice selected"><span class="ico">☁</span><div class="nm">AWS</div><div class="desc">ECS · EKS · Lambda · App Runner</div></div>
        <div class="choice"><span class="ico">🅰</span><div class="nm">Azure</div><div class="desc">AKS · App Service · Container Apps</div></div>
        <div class="choice"><span class="ico">🟢</span><div class="nm">GCP</div><div class="desc">GKE · Cloud Run · Compute Engine</div></div>
        <div class="choice"><span class="ico">⎈</span><div class="nm">Kubernetes anywhere</div><div class="desc">Any cluster via kubeconfig</div></div>
        <div class="choice"><span class="ico">🖥</span><div class="nm">On-prem VM</div><div class="desc">SSH-to-host</div></div>
      </div>
    </div>
    """
    return wizard_page("S8", "Pick cloud", inner)

def build_S9():
    inner = """
    <div class="card">
      <h3>Pick an existing AWS connector</h3>
      <div class="card" style="background:var(--panel-2)">
        <div class="row"><div><b>wm-prod-aws</b><div class="small muted">arn:aws:iam::488...:role/wm-deploy · us-east-1</div></div><span class="pill healthy">Healthy</span></div>
      </div>
      <div class="card" style="background:var(--panel-2)">
        <div class="row"><div><b>wm-dev-aws</b><div class="small muted">access key · us-west-2</div></div><span class="pill healthy">Healthy</span></div>
      </div>
      <a class="btn" href="S28-connector-edit.html">+ Add new AWS connector</a>
      <p class="small muted" style="margin-top:14px">Connectors are set up by your Admin. <a href="#">Request a new one</a> if what you need isn't listed.</p>
    </div>
    """
    help_ = """<div class="help-card"><h4>Validated how?</h4><p>Each connector ran <span class="mono">sts:GetCallerIdentity</span> on save and is rechecked every 5 min.</p></div>"""
    return wizard_page("S9", "Cloud connector", inner, help_)

def build_S10():
    inner = """
    <div class="card">
      <p class="subtitle" style="margin:0 0 14px">Targets shown are filtered to AWS — your selected cloud.</p>
      <div class="choice-grid">
        <div class="choice selected"><span class="ico">🚢</span><div class="nm">ECS Fargate</div><div class="desc">Serverless containers</div></div>
        <div class="choice"><span class="ico">⎈</span><div class="nm">EKS</div><div class="desc">Managed Kubernetes</div></div>
        <div class="choice"><span class="ico">💻</span><div class="nm">EC2</div><div class="desc">SSH / SSM</div></div>
        <div class="choice"><span class="ico">λ</span><div class="nm">Lambda</div><div class="desc">Zip or image</div></div>
        <div class="choice"><span class="ico">🏃</span><div class="nm">App Runner</div></div>
        <div class="choice"><span class="ico">🌱</span><div class="nm">Elastic Beanstalk</div></div>
        <div class="choice"><span class="ico">📁</span><div class="nm">S3 + CloudFront</div><div class="desc">Static sites</div></div>
      </div>
    </div>
    """
    return wizard_page("S10", "Deployment target", inner)

def build_S11():
    inner = """
    <div class="card">
      <h3>Pick environment</h3>
      <table style="margin:-8px 0">
        <tbody>
          <tr><td><input type="radio" checked></td><td><b>dev</b></td><td><span class="pill muted">non-prod</span></td><td class="muted">Cluster: wm-dev-us-east-1</td></tr>
          <tr><td><input type="radio"></td><td><b>staging</b></td><td><span class="pill muted">non-prod</span></td><td class="muted">Cluster: wm-stg-us-east-1</td></tr>
          <tr><td><input type="radio"></td><td><b>prod</b></td><td><span class="pill" style="background:rgba(218,54,51,0.15);color:#f85149">prod · approval required</span></td><td class="muted">Cluster: wm-prod-us-east-1</td></tr>
        </tbody>
      </table>
      <p class="small muted">Need a new environment? <a href="#">Request it from Admin</a> — only Admins can create prod environments.</p>
    </div>
    """
    return wizard_page("S11", "Environment", inner)

def build_S12():
    inner = """
    <div class="card">
      <div class="card-row">
        <div class="card" style="background:var(--panel-2)">
          <h3>Resources</h3>
          <div class="field"><label>Replicas</label><input value="3"></div>
          <div class="field"><label>CPU</label><input value="500m"></div>
          <div class="field"><label>Memory</label><input value="512Mi"></div>
        </div>
        <div class="card" style="background:var(--panel-2)">
          <h3>Networking</h3>
          <div class="field"><label>Container port</label><input value="8080"></div>
          <div class="field"><label>Health check path</label><input value="/healthz"></div>
          <div class="field"><label>Ingress host</label><input value="billing-api.dev.wm.io"></div>
        </div>
      </div>
      <h3>Environment variables</h3>
      <div class="card" style="background:var(--panel-2);padding:0">
        <table>
          <thead><tr><th>Key</th><th>Value</th><th>Secret?</th><th></th></tr></thead>
          <tbody>
            <tr><td class="mono">LOG_LEVEL</td><td>info</td><td></td><td><a href="#">remove</a></td></tr>
            <tr><td class="mono">DB_URL</td><td class="mono muted">${secret:dev-db-url}</td><td>🔒</td><td><a href="#">remove</a></td></tr>
            <tr><td class="mono">STRIPE_KEY</td><td class="mono muted">${secret:stripe-test}</td><td>🔒</td><td><a href="#">remove</a></td></tr>
          </tbody>
        </table>
      </div>
      <a class="btn" style="margin-top:10px">+ Add variable</a>
    </div>
    """
    return wizard_page("S12", "Deploy config", inner)

def build_S13():
    inner = """
    <div class="card">
      <h3>Deployment strategy</h3>
      <div class="choice-grid">
        <div class="choice selected"><span class="ico">↻</span><div class="nm">Rolling</div><div class="desc">Default · surge & unavailable knobs</div></div>
        <div class="choice"><span class="ico">🔵🟢</span><div class="nm">Blue-Green</div><div class="desc">Two stacks · traffic swap</div></div>
        <div class="choice"><span class="ico">🐤</span><div class="nm">Canary</div><div class="desc">% traffic with auto-promote</div></div>
        <div class="choice"><span class="ico">⏹</span><div class="nm">Recreate</div><div class="desc">For stateful workloads</div></div>
      </div>
      <h3>Rolling knobs</h3>
      <div class="card-row">
        <div class="card" style="background:var(--panel-2)"><div class="field"><label>Max surge</label><input value="25%"></div></div>
        <div class="card" style="background:var(--panel-2)"><div class="field"><label>Max unavailable</label><input value="0"></div></div>
        <div class="card" style="background:var(--panel-2)"><div class="field"><label>Progress timeout</label><input value="10m"></div></div>
      </div>
      <h3>Rollback</h3>
      <div class="field"><label>On health-check failure</label><select><option>Auto-rollback to last healthy</option><option>Pause and notify</option><option>Manual only</option></select></div>
    </div>
    """
    return wizard_page("S13", "Strategy", inner)

def build_S14():
    inner = """
    <div class="card">
      <h3>Logs</h3>
      <div class="field"><select><option>Platform-default (built-in store, 14d retention)</option><option>Datadog</option><option>CloudWatch Logs</option><option>Loki</option><option>ELK</option></select></div>
      <h3>Metrics</h3>
      <div class="field"><select><option>Platform-default (Prometheus scrape)</option><option>CloudWatch Metrics</option><option>Datadog</option></select></div>
      <h3>Alerts</h3>
      <div class="field"><label>Channels</label><input value="#payments-oncall (Slack), oncall@wavemaker.pagerduty"></div>
      <p class="small"><label><input type="checkbox" checked> Emit deployment markers on metric charts</label></p>
    </div>
    """
    return wizard_page("S14", "Observability", inner)

def build_S15():
    inner = """
    <div class="card">
      <h3>When should this deploy?</h3>
      <div class="field"><label><input type="checkbox" checked> On push to <b class="mono">main</b></label></div>
      <div class="field"><label><input type="checkbox"> On tag matching <input class="mono" value="v*" style="width:160px;display:inline-block"></label></div>
      <div class="field"><label><input type="checkbox"> On PR merge to <b class="mono">main</b></label></div>
      <div class="field"><label><input type="checkbox"> Scheduled (cron) <input class="mono" value="0 2 * * *" style="width:160px;display:inline-block"></label></div>
      <div class="field"><label><input type="checkbox" checked> Manual run allowed</label></div>
    </div>
    """
    return wizard_page("S15", "Triggers", inner)

def build_S16():
    inner = """
    <div class="card">
      <h3>Review</h3>
      <div class="kv">
        <span class="k">App</span><span>billing-api</span>
        <span class="k">Repo</span><span>github.com/wm-igniters/billing-api · main</span>
        <span class="k">Build</span><span>Dockerfile → ECR (wm-prod)</span>
        <span class="k">Cloud / target</span><span>AWS · ECS Fargate (connector: wm-dev-aws)</span>
        <span class="k">Environment</span><span>dev</span>
        <span class="k">Resources</span><span>3 × (500m CPU, 512Mi mem)</span>
        <span class="k">Strategy</span><span>Rolling · 25% surge · auto-rollback</span>
        <span class="k">Observability</span><span>Platform-default logs + metrics · Slack #payments-oncall</span>
        <span class="k">Triggers</span><span>On push to main · manual</span>
      </div>
      <p class="small muted" style="margin-top:14px">All steps are editable — click any pill in the stepper above to revisit.</p>
    </div>
    """
    return wizard_page("S16", "Review & launch", inner)

def build_S17():
    inner = """
    <div class="card">
      <div class="row" style="margin-bottom:14px"><span class="pill" style="background:rgba(31,111,235,0.18);color:#58a6ff">● Running · 1m 24s</span><div class="spacer"></div><a class="btn">Pause</a><a class="btn danger">Cancel</a></div>
      <div class="drawer" style="padding:8px 14px">
        <div class="exec-step"><span class="status ok"></span><div class="nm">Checkout</div><div class="dur">3s</div></div>
        <div class="exec-step"><span class="status ok"></span><div class="nm">Build container image</div><div class="dur">52s</div></div>
        <div class="exec-step"><span class="status ok"></span><div class="nm">Push to ECR</div><div class="dur">11s</div></div>
        <div class="exec-step"><span class="status run"></span><div class="nm">Deploy · ECS Fargate · rolling</div><div class="dur">18s</div></div>
        <div class="exec-step"><span class="status pending"></span><div class="nm">Health check</div><div class="dur">—</div></div>
        <div class="exec-step"><span class="status pending"></span><div class="nm">Smoke test</div><div class="dur">—</div></div>
      </div>
      <h3 style="margin-top:20px">Live logs</h3>
      <div class="logs">
<span class="ts">12:04:18</span> <span class="ok">▶ checkout: wm-igniters/billing-api@d4f8e1</span>
<span class="ts">12:04:21</span>   Cloned in 3.1s
<span class="ts">12:04:21</span> <span class="ok">▶ build: docker build -t billing-api .</span>
<span class="ts">12:04:53</span>   Step 6/8 — RUN go build -o /app/bin
<span class="ts">12:05:13</span>   Step 8/8 — CMD ["/app/bin/server"]
<span class="ts">12:05:13</span>   <span class="ok">Successfully built 4f8e91a2</span>
<span class="ts">12:05:14</span> <span class="ok">▶ push: 488...dkr.ecr.us-east-1.amazonaws.com/billing-api:d4f8e1</span>
<span class="ts">12:05:25</span>   Pushed 8 layers, 142 MB
<span class="ts">12:05:26</span> <span class="ok">▶ deploy: ecs update-service --service billing-api --task-def billing-api:42</span>
<span class="ts">12:05:33</span>   <span class="warn">Rolling: 1/3 tasks replaced…</span>
<span class="ts">12:05:38</span>   Rolling: 2/3 tasks replaced…
      </div>
    </div>
    """
    return wizard_page("S17", "Live execution", inner)


# Dashboard ------------------------------------------

def build_S18():
    body = """
    <p class="subtitle">payments-platform · all environments</p>
    <div class="tiles">
      <div class="tile"><div class="lbl">Applications</div><div class="num">12</div><div class="delta">+2 this week</div></div>
      <div class="tile"><div class="lbl">Environments</div><div class="num">4</div><div class="delta muted">unchanged</div></div>
      <div class="tile"><div class="lbl">Deploys today</div><div class="num">38</div><div class="delta">+11 vs avg</div></div>
      <div class="tile"><div class="lbl">7-day success</div><div class="num">94.2%</div><div class="delta">+1.4%</div></div>
      <div class="tile"><div class="lbl">Active executions</div><div class="num">3</div><div class="delta">live</div></div>
    </div>
    <div class="card-row">
      <div class="card">
        <h3>Deploys per day (14d)</h3>
        <div class="bars">
          <div class="bar" style="height:30%"></div>
          <div class="bar" style="height:45%"></div>
          <div class="bar" style="height:55%"></div>
          <div class="bar" style="height:40%"></div>
          <div class="bar amber" style="height:70%"></div>
          <div class="bar" style="height:60%"></div>
          <div class="bar" style="height:35%"></div>
          <div class="bar" style="height:50%"></div>
          <div class="bar" style="height:65%"></div>
          <div class="bar" style="height:80%"></div>
          <div class="bar" style="height:55%"></div>
          <div class="bar" style="height:75%"></div>
          <div class="bar green" style="height:90%"></div>
          <div class="bar" style="height:60%"></div>
        </div>
      </div>
      <div class="card">
        <h3>Recent activity</h3>
        <table style="margin:-8px 0">
          <tbody>
            <tr><td>billing-api</td><td>prod</td><td class="muted">30m ago · jane</td><td><span class="pill healthy">success</span></td></tr>
            <tr><td>customer-ui</td><td>staging</td><td class="muted">1h ago · mike</td><td><span class="pill healthy">success</span></td></tr>
            <tr><td>reports-job</td><td>dev</td><td class="muted">2h ago · jane</td><td><span class="pill degraded">degraded</span></td></tr>
          </tbody>
        </table>
      </div>
    </div>
    """
    return page("S18", "dashboard", "Dashboard", "Admin",
                '<a href="S3-project-list.html">payments-platform</a> / <b>Dashboard</b>', body,
                active="S18-dashboard.html")

def build_S19():
    body = """
    <p class="subtitle">Pick an environment to drill into its apps.</p>
    <div class="card-row">
      <a class="card" href="S20-env-detail.html" style="text-decoration:none;color:var(--text)">
        <h3 style="color:var(--text)">dev</h3>
        <div class="row"><div><div class="num" style="font-size:22px;font-weight:600">12 apps</div><div class="small muted">all healthy</div></div><div class="spacer"></div><span class="pill healthy">Healthy</span></div>
      </a>
      <a class="card" href="S20-env-detail.html" style="text-decoration:none;color:var(--text)">
        <h3 style="color:var(--text)">staging</h3>
        <div class="row"><div><div class="num" style="font-size:22px;font-weight:600">9 apps</div><div class="small muted">1 degraded</div></div><div class="spacer"></div><span class="pill degraded">Degraded</span></div>
      </a>
      <a class="card" href="S20-env-detail.html" style="text-decoration:none;color:var(--text)">
        <h3 style="color:var(--text)">prod</h3>
        <div class="row"><div><div class="num" style="font-size:22px;font-weight:600">8 apps</div><div class="small muted">approval required for deploys</div></div><div class="spacer"></div><span class="pill healthy">Healthy</span></div>
      </a>
      <a class="card" href="S20-env-detail.html" style="text-decoration:none;color:var(--text)">
        <h3 style="color:var(--text)">eu-prod</h3>
        <div class="row"><div><div class="num" style="font-size:22px;font-weight:600">6 apps</div><div class="small muted">EU customers</div></div><div class="spacer"></div><span class="pill healthy">Healthy</span></div>
      </a>
    </div>
    """
    return page("S19", "env-list", "By Environment", "Admin",
                '<a href="S3-project-list.html">payments-platform</a> / <b>Environments</b>', body,
                active="S19-env-list.html")

def build_S20():
    body = """
    <p class="subtitle">Apps deployed to <b>dev</b> · cluster wm-dev-us-east-1</p>
    <div class="card" style="padding:0">
      <table>
        <thead><tr><th>App</th><th>Version</th><th>Last deployed</th><th>Deployed by</th><th>Health</th><th></th></tr></thead>
        <tbody>
          <tr><td><a href="S22-app-detail.html"><b>billing-api</b></a></td><td class="mono">v1.4.2</td><td>2h ago</td><td>jane@…</td><td><span class="pill healthy">Healthy</span></td><td><a href="S23-logs.html">logs</a></td></tr>
          <tr><td><a href="S22-app-detail.html"><b>customer-ui</b></a></td><td class="mono">v0.9.0-rc3</td><td>30m ago</td><td>mike@…</td><td><span class="pill healthy">Healthy</span></td><td><a href="S23-logs.html">logs</a></td></tr>
          <tr><td><a href="S22-app-detail.html"><b>reports-job</b></a></td><td class="mono">v2.1.0</td><td>1d ago</td><td>jane@…</td><td><span class="pill degraded">Degraded</span></td><td><a href="S23-logs.html">logs</a></td></tr>
          <tr><td><a href="S22-app-detail.html"><b>auth-svc</b></a></td><td class="mono">v3.0.1</td><td>3h ago</td><td>priya@…</td><td><span class="pill healthy">Healthy</span></td><td><a href="S23-logs.html">logs</a></td></tr>
          <tr><td><a href="S22-app-detail.html"><b>webhooks-svc</b></a></td><td class="mono">v0.7.4</td><td>4h ago</td><td>mike@…</td><td><span class="pill healthy">Healthy</span></td><td><a href="S23-logs.html">logs</a></td></tr>
        </tbody>
      </table>
    </div>
    """
    return page("S20", "env-detail", "Environment · dev", "Admin",
                '<a href="S3-project-list.html">payments-platform</a> / <a href="S19-env-list.html">Environments</a> / <b>dev</b>', body,
                active="S19-env-list.html")

def build_S21():
    body = """
    <div class="row" style="margin-bottom:16px"><input class="search" placeholder="Search apps…"><div class="spacer"></div><a class="btn primary" href="S5-step1-basics.html">+ New app</a></div>
    <div class="card" style="padding:0">
      <table>
        <thead><tr><th>App</th><th>Type</th><th>Envs</th><th>Latest version</th><th>Last activity</th></tr></thead>
        <tbody>
          <tr><td><a href="S22-app-detail.html"><b>billing-api</b></a><div class="small muted">REST API · Go</div></td><td>Container</td><td>dev · staging · prod</td><td class="mono">v1.4.2</td><td>30m ago</td></tr>
          <tr><td><a href="S22-app-detail.html"><b>customer-ui</b></a><div class="small muted">WaveMaker app</div></td><td>Static</td><td>dev · staging · prod</td><td class="mono">v0.9.0-rc3</td><td>1h ago</td></tr>
          <tr><td><a href="S22-app-detail.html"><b>reports-job</b></a><div class="small muted">Scheduled job · Python</div></td><td>Container</td><td>dev · prod</td><td class="mono">v2.1.0</td><td>1d ago</td></tr>
          <tr><td><a href="S22-app-detail.html"><b>webhooks-svc</b></a><div class="small muted">Event consumer · Node</div></td><td>Container</td><td>dev · staging · prod</td><td class="mono">v0.7.4</td><td>4h ago</td></tr>
        </tbody>
      </table>
    </div>
    """
    return page("S21", "app-list", "Applications", "Admin",
                '<a href="S3-project-list.html">payments-platform</a> / <b>Applications</b>', body,
                active="S21-app-list.html")

def build_S22():
    body = """
    <p class="subtitle">REST API · Go · github.com/wm-igniters/billing-api</p>
    <div class="tabs">
      <span class="tab active">Versions</span>
      <a class="tab" href="S26-exec-detail.html">Deployment history</a>
      <a class="tab" href="S23-logs.html">Logs</a>
      <a class="tab" href="S24-metrics.html">Metrics</a>
      <span class="tab">Alerts</span>
      <span class="tab">Config</span>
    </div>
    <div class="card-row">
      <div class="card"><h3>dev</h3><div class="mono">v1.4.2</div><div class="small muted">deployed 2h ago by jane</div><div style="margin-top:8px"><span class="pill healthy">Healthy</span></div></div>
      <div class="card"><h3>staging</h3><div class="mono">v1.4.1</div><div class="small muted">deployed 1d ago by mike</div><div style="margin-top:8px"><span class="pill healthy">Healthy</span></div></div>
      <div class="card"><h3>prod</h3><div class="mono">v1.4.0</div><div class="small muted">deployed 3d ago by jane</div><div style="margin-top:8px"><span class="pill healthy">Healthy</span></div></div>
    </div>
    <h2>Recent deployments</h2>
    <div class="card" style="padding:0">
      <table>
        <thead><tr><th>Version</th><th>Env</th><th>When</th><th>By</th><th>Status</th><th>Duration</th></tr></thead>
        <tbody>
          <tr><td class="mono">v1.4.2</td><td>dev</td><td>2h ago</td><td>jane@…</td><td><span class="pill healthy">success</span></td><td>1m 38s</td></tr>
          <tr><td class="mono">v1.4.1</td><td>staging</td><td>1d ago</td><td>mike@…</td><td><span class="pill healthy">success</span></td><td>2m 04s</td></tr>
          <tr><td class="mono">v1.4.0</td><td>prod</td><td>3d ago</td><td>jane@… · approved by gayathri@…</td><td><span class="pill healthy">success</span></td><td>3m 12s</td></tr>
          <tr><td class="mono">v1.3.9</td><td>prod</td><td>5d ago</td><td>jane@…</td><td><span class="pill degraded">rolled back</span></td><td>4m 50s</td></tr>
        </tbody>
      </table>
    </div>
    """
    return page("S22", "app-detail", "billing-api", "Admin",
                '<a href="S3-project-list.html">payments-platform</a> / <a href="S21-app-list.html">Apps</a> / <b>billing-api</b>', body,
                active="S21-app-list.html")

def build_S23():
    body = """
    <p class="subtitle">billing-api · dev · last 15 minutes · live tail</p>
    <div class="card">
      <div class="row" style="margin-bottom:10px">
        <select style="background:var(--bg);border:1px solid var(--border);color:var(--text);padding:6px 10px;border-radius:6px"><option>All levels</option><option>error</option><option>warn</option><option>info</option></select>
        <input class="search" placeholder="Filter: payload, request id, error…" style="width:340px">
        <div class="spacer"></div>
        <a class="btn">Pause tail</a>
        <a class="btn">Download</a>
      </div>
      <div class="logs">
<span class="ts">12:14:02</span> INFO  request_id=8f1a method=POST path=/v1/charges status=200 dur=42ms
<span class="ts">12:14:02</span> INFO  request_id=8f1b method=GET path=/healthz status=200 dur=1ms
<span class="ts">12:14:03</span> <span class="warn">WARN  webhook retry attempt=2 provider=stripe event_id=evt_3O...</span>
<span class="ts">12:14:04</span> INFO  request_id=8f1c method=POST path=/v1/invoices status=201 dur=88ms
<span class="ts">12:14:05</span> <span class="err">ERROR request_id=8f1d failed to charge: card_declined (4242…4242)</span>
<span class="ts">12:14:05</span> INFO  request_id=8f1d method=POST path=/v1/charges status=402 dur=130ms
<span class="ts">12:14:06</span> INFO  request_id=8f1e method=GET path=/v1/customers/cust_42 status=200 dur=14ms
<span class="ts">12:14:07</span> INFO  request_id=8f1f method=GET path=/healthz status=200 dur=1ms
<span class="ts">12:14:08</span> <span class="ok">INFO  reconcile job complete · 1,204 invoices processed in 4.2s</span>
      </div>
    </div>
    """
    return page("S23", "logs", "Logs · billing-api", "Admin",
                '<a href="S3-project-list.html">payments-platform</a> / <a href="S22-app-detail.html">billing-api</a> / <b>Logs</b>', body,
                active="S21-app-list.html")

def build_S24():
    body = """
    <p class="subtitle">billing-api · dev · last 6 hours · deployment markers shown</p>
    <div class="card-row">
      <div class="card"><h3>Requests / sec</h3><div class="bars"><div class="bar" style="height:30%"></div><div class="bar" style="height:55%"></div><div class="bar" style="height:48%"></div><div class="bar" style="height:62%"></div><div class="bar" style="height:50%"></div><div class="bar amber" style="height:80%"></div><div class="bar" style="height:60%"></div><div class="bar" style="height:55%"></div><div class="bar" style="height:65%"></div><div class="bar" style="height:70%"></div></div><p class="small muted" style="margin:6px 0 0">▼ deploy v1.4.2 at 12:04</p></div>
      <div class="card"><h3>Error rate</h3><div class="bars"><div class="bar green" style="height:10%"></div><div class="bar green" style="height:8%"></div><div class="bar green" style="height:12%"></div><div class="bar amber" style="height:25%"></div><div class="bar green" style="height:10%"></div><div class="bar green" style="height:8%"></div><div class="bar green" style="height:10%"></div><div class="bar green" style="height:9%"></div><div class="bar green" style="height:11%"></div><div class="bar green" style="height:7%"></div></div><p class="small muted" style="margin:6px 0 0">0.42% over window</p></div>
    </div>
    <div class="card-row">
      <div class="card"><h3>CPU</h3><div class="bars"><div class="bar" style="height:40%"></div><div class="bar" style="height:55%"></div><div class="bar" style="height:48%"></div><div class="bar" style="height:62%"></div><div class="bar" style="height:80%"></div><div class="bar" style="height:65%"></div><div class="bar" style="height:55%"></div><div class="bar" style="height:50%"></div></div></div>
      <div class="card"><h3>Memory</h3><div class="bars"><div class="bar" style="height:42%"></div><div class="bar" style="height:45%"></div><div class="bar" style="height:48%"></div><div class="bar" style="height:50%"></div><div class="bar" style="height:55%"></div><div class="bar" style="height:54%"></div><div class="bar" style="height:53%"></div><div class="bar" style="height:55%"></div></div></div>
    </div>
    """
    return page("S24", "metrics", "Metrics · billing-api", "Admin",
                '<a href="S3-project-list.html">payments-platform</a> / <a href="S22-app-detail.html">billing-api</a> / <b>Metrics</b>', body,
                active="S21-app-list.html")

def build_S25():
    body = """
    <p class="subtitle">Every action across the org, filterable. This is the social feed of "what's happening."</p>
    <div class="row" style="margin-bottom:14px">
      <select style="background:var(--bg);border:1px solid var(--border);color:var(--text);padding:6px 10px;border-radius:6px"><option>All users</option></select>
      <select style="background:var(--bg);border:1px solid var(--border);color:var(--text);padding:6px 10px;border-radius:6px"><option>All apps</option></select>
      <select style="background:var(--bg);border:1px solid var(--border);color:var(--text);padding:6px 10px;border-radius:6px"><option>All envs</option></select>
      <select style="background:var(--bg);border:1px solid var(--border);color:var(--text);padding:6px 10px;border-radius:6px"><option>Last 24h</option><option>Last 7d</option></select>
      <div class="spacer"></div>
      <a class="btn">Export CSV</a>
    </div>
    <div class="card" style="padding:0">
      <table>
        <tbody>
          <tr><td>30m ago</td><td><b>jane@…</b></td><td>deployed <a href="S22-app-detail.html">billing-api</a> v1.4.2 to <b>dev</b></td><td><span class="pill healthy">success</span></td></tr>
          <tr><td>1h ago</td><td><b>mike@…</b></td><td>deployed <a href="S22-app-detail.html">customer-ui</a> v0.9.0-rc3 to <b>staging</b></td><td><span class="pill healthy">success</span></td></tr>
          <tr><td>2h ago</td><td><b>jane@…</b></td><td>deployed <a href="S22-app-detail.html">reports-job</a> v2.1.0 to <b>dev</b></td><td><span class="pill degraded">degraded</span></td></tr>
          <tr><td>3h ago</td><td><b>gayathri@…</b></td><td>approved <b>billing-api → prod</b> deploy</td><td><span class="pill muted">approval</span></td></tr>
          <tr><td>4h ago</td><td><b>priya@…</b></td><td>created connector <b>wm-prod-aws</b></td><td><span class="pill muted">config</span></td></tr>
          <tr><td>1d ago</td><td><b>mike@…</b></td><td>added env var <span class="mono">STRIPE_KEY</span> to <b>billing-api · prod</b></td><td><span class="pill muted">config</span></td></tr>
        </tbody>
      </table>
    </div>
    """
    return page("S25", "activity", "Activity", "Admin",
                '<a href="S3-project-list.html">payments-platform</a> / <b>Activity</b>', body,
                active="S25-activity.html")

def build_S26():
    body = """
    <p class="subtitle">billing-api · dev · v1.4.2 · started 12:04 · duration 1m 38s · by jane@…</p>
    <div class="card-row">
      <div class="card" style="flex:2">
        <h3>Pipeline steps</h3>
        <div class="exec-step"><span class="status ok"></span><div class="nm">Checkout · github.com/wm-igniters/billing-api@d4f8e1</div><div class="dur">3s</div></div>
        <div class="exec-step"><span class="status ok"></span><div class="nm">Build · docker</div><div class="dur">52s</div></div>
        <div class="exec-step"><span class="status ok"></span><div class="nm">Push · ECR</div><div class="dur">11s</div></div>
        <div class="exec-step"><span class="status ok"></span><div class="nm">Deploy · ECS Fargate rolling</div><div class="dur">25s</div></div>
        <div class="exec-step"><span class="status ok"></span><div class="nm">Health check</div><div class="dur">5s</div></div>
        <div class="exec-step"><span class="status ok"></span><div class="nm">Smoke test</div><div class="dur">2s</div></div>
      </div>
      <div class="card">
        <h3>Artifacts</h3>
        <ul class="small">
          <li class="mono">488...dkr.ecr.us-east-1/billing-api:d4f8e1</li>
          <li>task-def billing-api:42</li>
          <li>build log (12 KB)</li>
        </ul>
        <h3>Run controls</h3>
        <a class="btn" style="width:100%;justify-content:center;margin-bottom:6px">Replay</a>
        <a class="btn" style="width:100%;justify-content:center">Promote to staging</a>
      </div>
    </div>
    <h2>Logs</h2>
    <div class="logs">
<span class="ts">12:04:18</span> <span class="ok">▶ checkout: wm-igniters/billing-api@d4f8e1</span>
<span class="ts">12:04:53</span>   Step 6/8 — RUN go build -o /app/bin
<span class="ts">12:05:13</span>   <span class="ok">Successfully built 4f8e91a2</span>
<span class="ts">12:05:26</span> <span class="ok">▶ deploy: ecs update-service</span>
<span class="ts">12:05:51</span>   <span class="ok">Rolling complete · 3/3 tasks healthy</span>
<span class="ts">12:05:56</span>   <span class="ok">Smoke test passed</span>
      </div>
    """
    return page("S26", "exec-detail", "Execution detail", "Admin",
                '<a href="S3-project-list.html">payments-platform</a> / <a href="S22-app-detail.html">billing-api</a> / <b>Execution d4f8e1</b>', body,
                active="S21-app-list.html")


# Admin --------------------------------------------------

def build_S27():
    body = """
    <p class="subtitle">All cloud connectors across <b>WaveMaker</b>. Health-checked every 5 min.</p>
    <div class="row" style="margin-bottom:14px"><input class="search" placeholder="Search connectors…"><div class="spacer"></div><a class="btn primary" href="S28-connector-edit.html">+ Add connector</a></div>
    <div class="card" style="padding:0">
      <table>
        <thead><tr><th>Name</th><th>Cloud</th><th>Auth</th><th>Scope</th><th>Last check</th><th>Status</th></tr></thead>
        <tbody>
          <tr><td><a href="S28-connector-edit.html"><b>wm-prod-aws</b></a></td><td>AWS</td><td>IAM role (OIDC)</td><td>us-east-1, eu-west-1</td><td>1m ago</td><td><span class="pill healthy">Healthy</span></td></tr>
          <tr><td><a href="S28-connector-edit.html"><b>wm-dev-aws</b></a></td><td>AWS</td><td>Access key</td><td>us-west-2</td><td>1m ago</td><td><span class="pill healthy">Healthy</span></td></tr>
          <tr><td><a href="S28-connector-edit.html"><b>wm-prod-gcp</b></a></td><td>GCP</td><td>Workload identity</td><td>us-central1</td><td>2m ago</td><td><span class="pill healthy">Healthy</span></td></tr>
          <tr><td><a href="S28-connector-edit.html"><b>customer-azure</b></a></td><td>Azure</td><td>Service principal</td><td>eastus</td><td>14m ago</td><td><span class="pill down">Down · token expired</span></td></tr>
          <tr><td><a href="S28-connector-edit.html"><b>onprem-vm-mumbai</b></a></td><td>On-prem</td><td>SSH key</td><td>10.42.x.x</td><td>3m ago</td><td><span class="pill healthy">Healthy</span></td></tr>
        </tbody>
      </table>
    </div>
    """
    return page("S27", "connectors", "Cloud connectors", "Admin",
                '<a href="S3-project-list.html">WaveMaker</a> / <b>Cloud connectors</b>', body,
                active="S27-connectors.html")

def build_S28():
    body = """
    <p class="subtitle">Form is schema-driven per cloud. AWS shown below.</p>
    <div class="card" style="max-width:720px">
      <div class="field"><label>Connector name</label><input value="wm-prod-aws"></div>
      <div class="field"><label>Cloud</label><select><option>AWS</option><option>Azure</option><option>GCP</option><option>Kubernetes</option><option>On-prem (SSH)</option></select></div>
      <div class="field"><label>Auth method</label><select><option>IAM role (OIDC federation) — recommended</option><option>IAM access key + secret</option><option>Assume role chain</option></select></div>
      <div class="field"><label>Role ARN</label><input class="mono" value="arn:aws:iam::488123456789:role/wm-deploy"></div>
      <div class="field"><label>External ID (optional)</label><input class="mono" value="wm-prod"></div>
      <div class="field"><label>Allowed regions</label><input value="us-east-1, eu-west-1"></div>
      <div class="card" style="background:var(--panel-2);margin:6px 0 12px"><b>Validation</b><br><span class="small muted">Runs <span class="mono">sts:GetCallerIdentity</span> on save and every 5 min thereafter.</span></div>
      <div class="row"><a class="btn">Test connection</a><div class="spacer"></div><a class="btn">Cancel</a><a class="btn primary">Save connector</a></div>
    </div>
    """
    return page("S28", "connector-edit", "Edit AWS connector · wm-prod-aws", "Admin",
                '<a href="S3-project-list.html">WaveMaker</a> / <a href="S27-connectors.html">Connectors</a> / <b>wm-prod-aws</b>', body,
                active="S27-connectors.html")

def build_S29():
    body = """
    <p class="subtitle">Container registries used by builds in this org.</p>
    <div class="row" style="margin-bottom:14px"><div class="spacer"></div><a class="btn primary">+ Add registry</a></div>
    <div class="card" style="padding:0">
      <table>
        <thead><tr><th>Name</th><th>Type</th><th>Endpoint</th><th>Default for</th><th>Status</th></tr></thead>
        <tbody>
          <tr><td><b>wm-prod ECR</b></td><td>ECR</td><td class="mono">488...dkr.ecr.us-east-1.amazonaws.com</td><td>prod builds</td><td><span class="pill healthy">Healthy</span></td></tr>
          <tr><td><b>wm-dev ECR</b></td><td>ECR</td><td class="mono">488...dkr.ecr.us-west-2.amazonaws.com</td><td>dev/staging builds</td><td><span class="pill healthy">Healthy</span></td></tr>
          <tr><td><b>wmlabs Docker Hub</b></td><td>Docker Hub</td><td class="mono">docker.io/wmlabs</td><td>public images</td><td><span class="pill healthy">Healthy</span></td></tr>
          <tr><td><b>ghcr-igniters</b></td><td>GHCR</td><td class="mono">ghcr.io/wm-igniters</td><td>—</td><td><span class="pill healthy">Healthy</span></td></tr>
        </tbody>
      </table>
    </div>
    """
    return page("S29", "registries", "Container registries", "Admin",
                '<a href="S3-project-list.html">WaveMaker</a> / <b>Registries</b>', body,
                active="S29-registries.html")

def build_S30():
    body = """
    <p class="subtitle">Source providers configured at the org level.</p>
    <div class="row" style="margin-bottom:14px"><div class="spacer"></div><a class="btn primary">+ Install provider</a></div>
    <div class="card" style="padding:0">
      <table>
        <thead><tr><th>Provider</th><th>Install</th><th>Repos visible</th><th>Webhook</th><th>Status</th></tr></thead>
        <tbody>
          <tr><td><b>GitHub</b></td><td>GitHub App · wavemaker-deploy</td><td>74</td><td>installed</td><td><span class="pill healthy">Healthy</span></td></tr>
          <tr><td><b>GitLab</b></td><td>OAuth</td><td>12</td><td>installed</td><td><span class="pill healthy">Healthy</span></td></tr>
          <tr><td><b>Bitbucket</b></td><td>App password</td><td>3</td><td>installed</td><td><span class="pill degraded">Token expires in 7d</span></td></tr>
          <tr><td><b>Azure Repos</b></td><td>PAT</td><td>5</td><td>installed</td><td><span class="pill healthy">Healthy</span></td></tr>
        </tbody>
      </table>
    </div>
    """
    return page("S30", "repos", "Repo connectors", "Admin",
                '<a href="S3-project-list.html">WaveMaker</a> / <b>Repo connectors</b>', body,
                active="S30-repos.html")

def build_S31():
    body = """
    <p class="subtitle">Where secret values are stored. The platform never holds plaintext values in its own DB.</p>
    <div class="card-row">
      <div class="card"><h3>Built-in vault</h3><div class="row"><div><b>wm-platform-vault</b><div class="small muted">Vault + KMS backed</div></div><div class="spacer"></div><span class="pill healthy">Active</span></div></div>
      <div class="card"><h3>AWS Secrets Manager</h3><div class="row"><div><b>wm-prod-aws-sm</b><div class="small muted">488...:secret:*</div></div><div class="spacer"></div><span class="pill healthy">Linked</span></div></div>
      <div class="card"><h3>HashiCorp Vault</h3><div class="row"><div><b>vault.wm.io</b><div class="small muted">KV v2 mount · /secret/wm</div></div><div class="spacer"></div><span class="pill healthy">Linked</span></div></div>
    </div>
    <p class="small muted">Secrets are referenced by alias in env vars: <span class="mono">${secret:db-password}</span></p>
    """
    return page("S31", "secret-mgrs", "Secret managers", "Admin",
                '<a href="S3-project-list.html">WaveMaker</a> / <b>Secret managers</b>', body,
                active="S31-secret-mgrs.html")

def build_S32():
    body = """
    <p class="subtitle">Values are never displayed in the UI after creation. You can rotate or audit access only.</p>
    <div class="row" style="margin-bottom:14px"><input class="search" placeholder="Search secrets…"><div class="spacer"></div><a class="btn primary">+ Add secret</a></div>
    <div class="card" style="padding:0">
      <table>
        <thead><tr><th>Alias</th><th>Store</th><th>Used by</th><th>Last rotated</th><th></th></tr></thead>
        <tbody>
          <tr><td class="mono">dev-db-url</td><td>built-in vault</td><td>billing-api (dev)</td><td>14d ago</td><td><a href="#">rotate</a> · <a href="#">audit</a></td></tr>
          <tr><td class="mono">prod-db-url</td><td>aws-sm</td><td>billing-api (prod), reports-job (prod)</td><td>62d ago · <span class="pill degraded">overdue</span></td><td><a href="#">rotate</a> · <a href="#">audit</a></td></tr>
          <tr><td class="mono">stripe-live</td><td>aws-sm</td><td>billing-api (prod)</td><td>5d ago</td><td><a href="#">rotate</a> · <a href="#">audit</a></td></tr>
          <tr><td class="mono">stripe-test</td><td>built-in vault</td><td>billing-api (dev, staging)</td><td>30d ago</td><td><a href="#">rotate</a> · <a href="#">audit</a></td></tr>
          <tr><td class="mono">slack-webhook</td><td>built-in vault</td><td>notifications</td><td>90d ago</td><td><a href="#">rotate</a> · <a href="#">audit</a></td></tr>
        </tbody>
      </table>
    </div>
    """
    return page("S32", "secrets", "Secrets", "Admin",
                '<a href="S3-project-list.html">WaveMaker</a> / <b>Secrets</b>', body,
                active="S32-secrets.html")

def build_S33():
    body = """
    <p class="subtitle">Define environments and the rules around deploying to them.</p>
    <div class="row" style="margin-bottom:14px"><div class="spacer"></div><a class="btn primary">+ New environment</a></div>
    <div class="card" style="padding:0">
      <table>
        <thead><tr><th>Name</th><th>Type</th><th>Cluster / target</th><th>Approval</th><th>Apps</th></tr></thead>
        <tbody>
          <tr><td><b>dev</b></td><td><span class="pill muted">non-prod</span></td><td>wm-dev-us-east-1 (EKS)</td><td>none</td><td>12</td></tr>
          <tr><td><b>staging</b></td><td><span class="pill muted">non-prod</span></td><td>wm-stg-us-east-1 (EKS)</td><td>none</td><td>9</td></tr>
          <tr><td><b>prod</b></td><td><span class="pill" style="background:rgba(218,54,51,0.15);color:#f85149">prod</span></td><td>wm-prod-us-east-1 (EKS)</td><td>1 Admin approval</td><td>8</td></tr>
          <tr><td><b>eu-prod</b></td><td><span class="pill" style="background:rgba(218,54,51,0.15);color:#f85149">prod</span></td><td>wm-prod-eu-west-1 (EKS)</td><td>1 Admin approval</td><td>6</td></tr>
        </tbody>
      </table>
    </div>
    """
    return page("S33", "envs", "Environments", "Admin",
                '<a href="S3-project-list.html">WaveMaker</a> / <b>Environments</b>', body,
                active="S33-envs.html")

def build_S34():
    body = """
    <p class="subtitle">Channels we can send pipeline / deploy / connector events to.</p>
    <div class="row" style="margin-bottom:14px"><div class="spacer"></div><a class="btn primary">+ Add channel</a></div>
    <div class="card" style="padding:0">
      <table>
        <thead><tr><th>Channel</th><th>Type</th><th>Events</th><th>Status</th></tr></thead>
        <tbody>
          <tr><td><b>#payments-oncall</b></td><td>Slack</td><td>deploy failed · approval requested · connector unhealthy</td><td><span class="pill healthy">OK</span></td></tr>
          <tr><td><b>oncall@…pagerduty</b></td><td>PagerDuty</td><td>deploy failed (prod only)</td><td><span class="pill healthy">OK</span></td></tr>
          <tr><td><b>platform-team@wavemaker.com</b></td><td>Email</td><td>all events</td><td><span class="pill healthy">OK</span></td></tr>
          <tr><td><b>customer-webhook</b></td><td>Webhook</td><td>deploy succeeded (prod)</td><td><span class="pill degraded">last 3 failed</span></td></tr>
        </tbody>
      </table>
    </div>
    """
    return page("S34", "notif", "Notification channels", "Admin",
                '<a href="S3-project-list.html">WaveMaker</a> / <b>Notifications</b>', body,
                active="S34-notif.html")

def build_S35():
    body = """
    <p class="subtitle">Two roles: <b>Admin</b> and <b>User</b>. Scope can be set per org, project, or environment.</p>
    <div class="row" style="margin-bottom:14px"><input class="search" placeholder="Search users…"><div class="spacer"></div><a class="btn primary">+ Invite user</a></div>
    <div class="card" style="padding:0">
      <table>
        <thead><tr><th>User</th><th>Role</th><th>Scope</th><th>Last active</th><th></th></tr></thead>
        <tbody>
          <tr><td><b>gayathri@wavemaker.com</b><div class="small muted">Gayathri Kalanadhabatla</div></td><td><span class="pill" style="background:rgba(191,135,0,0.15);color:#d29922">Admin</span></td><td>org-wide</td><td>just now</td><td><a href="#">edit</a></td></tr>
          <tr><td><b>jane@wavemaker.com</b></td><td><span class="pill" style="background:rgba(31,111,235,0.15);color:#58a6ff">User</span></td><td>payments-platform (all envs)</td><td>30m ago</td><td><a href="#">edit</a></td></tr>
          <tr><td><b>mike@wavemaker.com</b></td><td><span class="pill" style="background:rgba(31,111,235,0.15);color:#58a6ff">User</span></td><td>payments-platform (dev, staging)</td><td>1h ago</td><td><a href="#">edit</a></td></tr>
          <tr><td><b>priya@wavemaker.com</b></td><td><span class="pill" style="background:rgba(191,135,0,0.15);color:#d29922">Admin</span></td><td>data-pipelines</td><td>2h ago</td><td><a href="#">edit</a></td></tr>
        </tbody>
      </table>
    </div>
    """
    return page("S35", "users", "Users & RBAC", "Admin",
                '<a href="S3-project-list.html">WaveMaker</a> / <b>Users & RBAC</b>', body,
                active="S35-users.html")

def build_S36():
    body = """
    <p class="subtitle">Prod deploys waiting for an Admin to approve.</p>
    <div class="card">
      <div class="row" style="margin-bottom:8px"><b>billing-api · v1.4.2 → prod</b><div class="spacer"></div><span class="small muted">requested 8m ago by jane@…</span></div>
      <div class="kv">
        <span class="k">Diff vs current</span><span><a href="#">v1.4.0 → v1.4.2 (12 commits)</a></span>
        <span class="k">Pre-deploy checks</span><span><span class="pill healthy">all passed</span></span>
        <span class="k">Strategy</span><span>Canary · 10% / 50% / 100% over 30m</span>
      </div>
      <div class="row" style="margin-top:14px"><a class="btn danger">Reject</a><a class="btn">Comment</a><div class="spacer"></div><a class="btn primary">Approve & deploy</a></div>
    </div>
    <div class="card">
      <div class="row" style="margin-bottom:8px"><b>reports-job · v2.1.1 → prod</b><div class="spacer"></div><span class="small muted">requested 1h ago by jane@…</span></div>
      <div class="kv">
        <span class="k">Diff vs current</span><span><a href="#">v2.1.0 → v2.1.1 (1 commit · "hotfix: null currency")</a></span>
        <span class="k">Pre-deploy checks</span><span><span class="pill healthy">all passed</span></span>
        <span class="k">Strategy</span><span>Rolling · 25% surge</span>
      </div>
      <div class="row" style="margin-top:14px"><a class="btn danger">Reject</a><a class="btn">Comment</a><div class="spacer"></div><a class="btn primary">Approve & deploy</a></div>
    </div>
    """
    return page("S36", "approvals", "Approval inbox", "Admin",
                '<a href="S3-project-list.html">WaveMaker</a> / <b>Approvals</b>', body,
                active="S36-approvals.html")

def build_S37():
    body = """
    <p class="subtitle">Immutable record of every config change and every deploy. Filter by actor, resource, time.</p>
    <div class="row" style="margin-bottom:14px">
      <select style="background:var(--bg);border:1px solid var(--border);color:var(--text);padding:6px 10px;border-radius:6px"><option>All actors</option></select>
      <select style="background:var(--bg);border:1px solid var(--border);color:var(--text);padding:6px 10px;border-radius:6px"><option>All resources</option></select>
      <select style="background:var(--bg);border:1px solid var(--border);color:var(--text);padding:6px 10px;border-radius:6px"><option>Last 7d</option><option>Last 30d</option><option>All time</option></select>
      <div class="spacer"></div>
      <a class="btn">Export CSV</a>
    </div>
    <div class="card" style="padding:0">
      <table>
        <thead><tr><th>When</th><th>Actor</th><th>Action</th><th>Resource</th><th>IP</th></tr></thead>
        <tbody>
          <tr><td class="mono">12:04:18</td><td>jane@…</td><td>deploy.run</td><td>billing-api · dev · v1.4.2</td><td class="mono">10.2.4.9</td></tr>
          <tr><td class="mono">11:58:02</td><td>gayathri@…</td><td>connector.update</td><td>wm-prod-aws (regions added)</td><td class="mono">10.2.4.1</td></tr>
          <tr><td class="mono">11:42:51</td><td>gayathri@…</td><td>approval.granted</td><td>billing-api · prod · v1.4.0</td><td class="mono">10.2.4.1</td></tr>
          <tr><td class="mono">10:18:33</td><td>mike@…</td><td>secret.rotate</td><td>stripe-test</td><td class="mono">10.2.4.12</td></tr>
          <tr><td class="mono">09:55:07</td><td>priya@…</td><td>connector.create</td><td>customer-azure</td><td class="mono">10.2.4.7</td></tr>
        </tbody>
      </table>
    </div>
    """
    return page("S37", "audit", "Audit log", "Admin",
                '<a href="S3-project-list.html">WaveMaker</a> / <b>Audit log</b>', body,
                active="S37-audit.html")

def build_S38():
    body = """
    <p class="subtitle">Organization-level configuration.</p>
    <div class="card-row">
      <div class="card">
        <h3>Single sign-on</h3>
        <div class="kv">
          <span class="k">Method</span><span>SAML 2.0</span>
          <span class="k">IdP</span><span>Okta</span>
          <span class="k">Status</span><span><span class="pill healthy">Active</span></span>
        </div>
        <a class="btn" style="margin-top:10px">Edit SSO</a>
      </div>
      <div class="card">
        <h3>Retention</h3>
        <div class="field"><label>Logs</label><select><option>14 days</option><option>30 days</option><option>90 days</option></select></div>
        <div class="field"><label>Execution history</label><select><option>180 days</option><option>1 year</option><option>Forever</option></select></div>
        <div class="field"><label>Audit log</label><select><option>1 year</option><option>3 years</option><option>7 years</option></select></div>
      </div>
    </div>
    <div class="card-row">
      <div class="card">
        <h3>Defaults</h3>
        <div class="field"><label>Default cloud region</label><select><option>us-east-1</option><option>eu-west-1</option></select></div>
        <div class="field"><label>Default deployment strategy</label><select><option>Rolling</option><option>Blue-Green</option></select></div>
      </div>
      <div class="card">
        <h3>Danger zone</h3>
        <a class="btn danger" style="width:100%;justify-content:center;margin-bottom:6px">Transfer ownership</a>
        <a class="btn danger" style="width:100%;justify-content:center">Delete organization</a>
      </div>
    </div>
    """
    return page("S38", "org", "Organization settings", "Admin",
                '<a href="S3-project-list.html">WaveMaker</a> / <b>Org settings</b>', body,
                active="S38-org.html")


# ─── MAIN ────────────────────────────────────────────────

ALL_BUILDERS = [
    build_S1, build_S2, build_S3, build_S4,
    build_S5, build_S6, build_S7, build_S8, build_S9, build_S10,
    build_S11, build_S12, build_S13, build_S14, build_S15, build_S16, build_S17,
    build_S18, build_S19, build_S20, build_S21, build_S22, build_S23, build_S24,
    build_S25, build_S26,
    build_S27, build_S28, build_S29, build_S30, build_S31, build_S32, build_S33,
    build_S34, build_S35, build_S36, build_S37, build_S38,
]

if __name__ == "__main__":
    build_index()
    names = []
    for fn in ALL_BUILDERS:
        names.append(fn())
    print(f"Wrote index.html + {len(names)} screens")
    for n in names: print(" ", n)
