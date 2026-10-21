# Zero-Trust Network Access (ZTNA) Implementation

**Author:** Payal Jangid  
**Program:** Cybersecurity Bootcamp  
**Date:** October 22, 2026  

---

## 📌 Project Overview
This project demonstrates the implementation of a **Zero-Trust Network Access (ZTNA)** architecture to secure internal administration consoles. By replacing traditional, perimeter-based security and inbound public IP dependencies with **Cloudflare Tunnels** and **Multi-Factor Authentication (MFA)** via Cloudflare Access, this setup eliminates open inbound firewall ports and enforces strict identity-based access control.

## 🎯 Objectives & Key Features
- **Zero Public Inbound Ports:** Leverages an outbound-only daemon (`cloudflared`) to connect internal resources to Cloudflare's edge network without exposing public IPs.
- **Identity-Aware Access Control:** Enforces Multi-Factor Authentication (MFA) prior to granting access to sensitive admin consoles.
- **DDoS & Edge Protection:** Absorbs malicious traffic, bot probes, and unauthorized access attempts at the edge before they touch internal infrastructure.
- **Least-Privilege Enforcement:** Restricts administrative application access exclusively to authenticated and authorized personnel.

---

## 📊 Dataset & Configuration Artifacts
- **Dataset / Logs Link:** [Insert Link to Project Logs / Configuration Artifacts / Sample PCAPs]
> *Note: Includes sanitized access logs, authentication logs, and latency metric datasets collected during testing.*

---

## 🛠️ Technologies Used
- **Network & Access:** Cloudflare Zero Trust (Cloudflare Access & Tunnels)
- **Identity Provider (IdP):** Okta / Google Workspace / Azure AD (with MFA enabled)
- **Tunnel Client:** `cloudflared` CLI / Daemon
- **Operating System / Environment:** Linux (Ubuntu/Debian) / Docker Container
- **Documentation & Scripting:** Bash, Markdown, YAML

---

## ⚙️ Setup & Execution Instructions

### Prerequisites
1. A domain managed by Cloudflare DNS.
2. A Cloudflare Zero Trust account.
3. A server hosting an internal admin console (e.g., running locally on `http://localhost:8080`).

### Step 1: Install `cloudflared`
On your local internal server:
```bash
# Download and install cloudflared
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb
```

### Step 2: Authenticate and Create a Tunnel
```bash
# Authenticate with Cloudflare
cloudflared tunnel login

# Create the named tunnel
cloudflared tunnel create admin-console-tunnel
```

### Step 3: Configure Route and Traffic Rules
Create a configuration file at `~/.cloudflared/config.yml`:

```yaml
tunnel: <TUNNEL-UUID>
credentials-file: /root/.cloudflared/<TUNNEL-UUID>.json

ingress:
  - hostname: admin.yourdomain.com
    service: http://localhost:8080
  - service: http_status:404
```

Route your hostname through the tunnel:
```bash
cloudflared tunnel route dns admin-console-tunnel admin.yourdomain.com
```

### Step 4: Run the Tunnel as a Service
```bash
sudo cloudflared service install
sudo systemctl start cloudflared
```

### Step 5: Configure MFA Access Policies
1. Navigate to the **Cloudflare Zero Trust Dashboard** > **Access** > **Applications**.
2. Add a new **Self-hosted Application** with domain `admin.yourdomain.com`.
3. Configure **Access Rules**:
   - Set **Action** to `Allow`.
   - Add identity checks (e.g., emails ending with `@yourorganization.com`).
   - Require **MFA / OTP** authentication via your Identity Provider.

---

## 🔍 Validation & Verification
1. **Inbound Scan:** Run an `nmap` port scan on your public server IP to confirm all inbound ports remain closed or blocked.
2. **Access Flow:** Navigate to `https://admin.yourdomain.com`. Verify that you are immediately redirected to the MFA authentication prompt.
3. **Log Audit:** Check the Cloudflare Access audit logs to verify user identity, timestamp, and device posture status upon successful login.