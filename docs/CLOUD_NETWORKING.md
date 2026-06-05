# Cloud Networking Architecture — CloudERP CRM/WMS Platform

> **Note for the report writer:** This file documents the *technical design* of the
> platform's AWS network. Use it as the evidence base for your Unit 6 written report,
> but write the analytical sections (benefits/constraints, comparisons, justifications)
> in your own words — the assessor expects your reasoning, not copied documentation.

---

## 1. Business context

A wholesale clothing distributor is migrating its **ERP, CRM and WMS** systems from an
ageing on-premises setup to AWS. The drivers are growth the current LAN cannot absorb,
the need for secure access from regional warehouses, and the wish to pay for capacity
only when it is used. The network below isolates the business data, exposes only what
must be public, and scales automatically under load.

---

## 2. High-level deployment architecture

```
                                   Internet
                                       │
                          ┌────────────▼────────────┐
                          │   Amazon Route 53 (DNS)  │   erp.company.com
                          └────────────┬────────────┘
                                       │
                              ┌────────▼────────┐
                              │  Internet Gateway │
                              └────────┬────────┘
        ┌──────────────────────────────┼──────────────────────────────┐
        │  VPC  10.0.0.0/16             │                              │
        │                ┌─────────────▼──────────────┐               │
        │   PUBLIC       │  Application Load Balancer  │  (HTTPS:443)  │
        │   SUBNETS      └──────┬───────────────┬──────┘               │
        │  10.0.1.0/24          │               │                      │
        │  10.0.2.0/24     ┌────▼────┐     ┌────▼────┐   NAT Gateway   │
        │  (AZ-a / AZ-b)   │  (route) │     │ (route) │   (egress only) │
        │                  └────┬────┘     └────┬────┘        ▲         │
        │ ─────────────────────┼───────────────┼─────────────┼──────── │
        │   PRIVATE        ┌────▼────┐     ┌────▼────┐        │         │
        │   APP SUBNETS    │  EC2 #1 │     │  EC2 #2 │  Auto Scaling     │
        │  10.0.11.0/24    │ Django  │ ... │ Django  │  Group (2..N)     │
        │  10.0.12.0/24    └────┬────┘     └────┬────┘                   │
        │ ─────────────────────┼───────────────┼──────────────────────  │
        │   PRIVATE        ┌────▼───────────────▼────┐                  │
        │   DB SUBNETS     │  Amazon RDS PostgreSQL   │  (Multi-AZ)      │
        │  10.0.21.0/24    │  primary  +  standby     │                 │
        │  10.0.22.0/24    └──────────────────────────┘                 │
        └───────────────────────────────────────────────────────────────┘
                                       ▲
                         ┌─────────────┴─────────────┐
                         │  Site-to-Site VPN          │  Regional warehouses
                         │  Client-to-Site VPN        │  Remote employees
                         └────────────────────────────┘
```

**Traffic story:** a user hits `erp.company.com` → Route 53 resolves it to the ALB →
the ALB terminates TLS and forwards to a healthy Django EC2 instance in a **private**
subnet → that instance talks to **RDS PostgreSQL** in an even more isolated DB subnet.
The EC2 instances have **no public IP**; they reach the internet (for OS updates, package
installs) only outbound through the **NAT Gateway**.

---

## 3. VPC and subnet design

| Tier | CIDR | AZ | Internet route | Purpose |
|------|------|----|----------------|---------|
| Public  | 10.0.1.0/24 / 10.0.2.0/24 | a / b | via Internet Gateway | ALB, NAT Gateway |
| Private App | 10.0.11.0/24 / 10.0.12.0/24 | a / b | outbound via NAT | Django EC2 (ASG) |
| Private DB | 10.0.21.0/24 / 10.0.22.0/24 | a / b | none | RDS PostgreSQL |

The VPC (`10.0.0.0/16`) is the company's private slice of AWS, isolated from every other
tenant. Spreading each tier across **two Availability Zones** means the loss of one data
centre does not take the business offline.

### Route tables
- **Public route table:** `0.0.0.0/0 → Internet Gateway`. Attached to the public subnets.
- **Private app route table:** `0.0.0.0/0 → NAT Gateway`. Outbound only; nothing on the
  internet can initiate a connection inward.
- **Private DB route table:** no `0.0.0.0/0` route at all — the database can never reach,
  or be reached from, the internet.

### Internet Gateway vs NAT Gateway
- **Internet Gateway (IGW):** allows *inbound and outbound* traffic for the public subnets
  (so the ALB is reachable).
- **NAT Gateway:** allows *outbound-only* traffic for private subnets, so EC2 can download
  patches without ever being exposed to inbound connections.

---

## 4. Security groups (stateful firewalls)

Security groups act as instance-level firewalls; they reference each other instead of IP
ranges, so the rules stay valid as instances scale.

```
ALB-SG    : inbound 443 (HTTPS) from 0.0.0.0/0
WEB-SG    : inbound 8000 ONLY from ALB-SG        (no public access to app)
DB-SG     : inbound 5432 ONLY from WEB-SG        (only the app may reach Postgres)
```

This produces a layered "defence in depth": even if the ALB were misconfigured, the DB
security group still refuses any source other than the application tier.

---

## 5. DNS (Route 53)

Route 53 maps human-friendly domains (`erp.company.com`, `crm.company.com`) to the ALB via
an **alias A-record**. Health checks let Route 53 fail traffic over to a secondary region
in a disaster-recovery scenario. Internally, RDS is reached through its private DNS
endpoint, so application config never hard-codes an IP.

---

## 6. Load balancing

An **Application Load Balancer (Layer 7)** sits in the public subnets and distributes
incoming HTTP/HTTPS requests across the Django instances using *round-robin with least
outstanding requests*. It performs **health checks** against the app's `/health/` endpoint
(implemented in `dashboard/views.py`); an instance that stops returning `200 OK` is removed
from rotation automatically. TLS is terminated at the ALB so certificates live in one place
(AWS Certificate Manager).

---

## 7. Auto scaling

An **Auto Scaling Group (ASG)** keeps the application tier between a minimum and maximum
number of instances behind the ALB.

```
Scaling policy (target tracking):
    Target  : average CPU utilisation = 60%
    Scale-out: +1 instance when CPU > 60% for 3 minutes
    Scale-in : -1 instance when CPU < 30% for 10 minutes
    Min = 2   Desired = 2   Max = 6
```

Because each instance is **stateless** (sessions in the DB, static files served by
WhiteNoise/S3), any new instance launched from the launch template can serve traffic
immediately. This is what lets the platform absorb a Black-Friday-style spike and then
shrink back down to save cost.

---

## 8. VPN connectivity

| Type | Connects | Use case |
|------|----------|----------|
| **Site-to-Site VPN** | Head office & regional warehouses ↔ VPC | Always-on encrypted tunnel so warehouse WMS terminals reach the cloud as if on the LAN |
| **Client-to-Site VPN** | Individual remote employee ↔ VPC | A sales rep on a laptop authenticates and gets a secure tunnel into private resources |

Both terminate at an AWS VPN Gateway attached to the VPC, encrypting traffic with IPsec so
order and customer data never crosses the public internet in clear text.

---

## 9. Cloud service models (where this project sits)

| Model | Meaning | This project |
|-------|---------|--------------|
| **IaaS** | You manage OS + runtime; AWS manages hardware | EC2 + VPC + EBS |
| **PaaS** | You manage code; provider manages OS/runtime | RDS PostgreSQL (managed DB) |
| **SaaS** | You just consume the finished app | The CRM/ERP/WMS *is* the SaaS the staff use |

The platform deliberately mixes models: **IaaS** for full control of the app servers,
**PaaS (RDS)** to offload database patching/backups, delivering a **SaaS** experience to
end users.

---

## 10. On-premises vs In-cloud vs Hybrid (decision summary)

- **On-premises:** lowest latency on the LAN but high capital cost, hard to scale, single
  site is a disaster-recovery risk. Rejected for the growth scenario.
- **Fully in-cloud:** elastic, pay-as-you-go, multi-AZ resilience — chosen for ERP/CRM/WMS.
- **Hybrid:** keep only latency-sensitive shop-floor scanning on-prem and connect via the
  Site-to-Site VPN; a sensible transition state during migration.

---

## 11. Mapping to Unit 6 assessment criteria

| Criterion | Where it is evidenced |
|-----------|------------------------|
| A.P1 / A.M1 / A.D1 | §2–§7 network architecture, standards and performance impact |
| A.P2 | §2 "traffic story", §6 ALB request flow |
| B.P3 / B.M2 | Dockerised OS image (`Dockerfile`), gunicorn workers, ASG optimisation §7 |
| B.P4 | §5 DNS, §6 ALB, §8 VPN — how remote clients reach the cloud |
| C.P5 / C.P6 | This whole document + the running Dockerised app |
| C.M3 / C.D2 | Load test the `/health/` + dashboard endpoints; record ASG scale-out |
| D.P7 / D.P8 / D.M4 / D.D3 | §7 auto scaling and §4 security-group hardening as enhancements |

> To claim the testing criteria (C.M3, C.D2, D.M4) you must run a load test
> (e.g. `locust`, `k6` or Apache Bench) against the deployed app, capture the response-time
> and instance-count graphs, and discuss them. See README §"Performance testing".
