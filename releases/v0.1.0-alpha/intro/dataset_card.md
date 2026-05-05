# leadforge dataset card

| Field | Value |
|---|---|
| Recipe | `b2b_saas_procurement_v1` |
| Package version | `1.0.0` |
| Seed | `42` |
| Exposure mode | `student_public` |
| Difficulty | `intro` |
| Horizon | 90 days |
| Label window | 90 days |
| Feature snapshot window | 30 days (windowed) |

## Narrative summary

**Vendor:** Veridian Technologies (Series B, founded 2017, Austin, US)

**Product:** Veridian Procure — Procurement & AP Automation. Deployment: cloud_saas. Pricing: per_seat_annual. ACV range: $18,000–$120,000.

**Target market:** 200–2000-employee firms in US, UK. Key industries: manufacturing, logistics, professional_services, healthcare_non_clinical. Average deal size: $42,000. Average sales cycle: 45 days.

**GTM motion:** inbound_marketing, sdr_outbound, partner_referral (45% inbound / 35% outbound / 20% partner).

**Buyer personas:**

- **vp_finance** (economic_buyer) — VP Finance, CFO…
- **ap_manager** (champion) — AP Manager, Accounts Payable Manager…
- **it_director** (technical_evaluator) — IT Director, CTO…
- **procurement_manager** (end_user) — Procurement Manager, Director of Procurement…

## Primary task

**Task:** `converted_within_90_days`

**Label definition:** A lead is considered converted if a `closed_won` event is recorded within 90 days of the lead's snapshot anchor date. The label is event-derived — never sampled directly. All features are pre-anchor (leakage-free by construction).

## Table inventory

| Table | Rows |
|---|---:|
| accounts | 1,500 |
| contacts | 4,200 |
| leads | 5,000 |
| touches | 53,354 |
| sessions | 14,339 |
| sales_activities | 56,643 |
| opportunities | 4,701 |
| customers | 2,110 |
| subscriptions | 2,110 |

## Feature categories

| Category | Count | Examples |
|---|---:|---|
| account | 6 | account_id, industry, region |
| contact | 4 | contact_id, role_function, seniority |
| lead_meta | 4 | lead_id, lead_created_at, lead_source |
| engagement | 11 | touch_count, inbound_touch_count, outbound_touch_count |
| sales | 6 | activity_count, days_since_last_touch, opportunity_created |
| target | 1 |  |

**Leakage-flagged columns:** `total_touches_all`. See `feature_dictionary.csv` for details.

## Suggested use cases

- Teaching binary classification on realistic CRM data
- Portfolio projects demonstrating end-to-end ML pipelines
- Benchmarking lead-scoring models under controlled signal/noise conditions
- Research on causal structure in funnel conversion data

## Caveats

- This is **synthetic** data. It does not represent any real company, product, or market.
- The hidden world structure varies by motif family and stochastic rewiring; no two seeds produce the same DGP.
- The label is evaluated over the full 90-day window from lead creation; event-aggregate features (e.g. `touch_count`, `session_count`, `expected_acv`) observe only the first 30 days of that window. The deliberate exception is `total_touches_all`, which counts touches over the full 90-day horizon as a pedagogical leakage trap.
- In `student_public` mode, the latent world graph, mechanism summary, and full world spec are withheld.
