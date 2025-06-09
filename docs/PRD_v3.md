# YardVision Pro – Coding-Ready PRD (v3.0)

**Scope note** – Product will launch only in the continental U S outside California; CCPA/GDPR requirements have been removed. General best-practice privacy, security, and data deletion controls remain.

⸻

## 1. Purpose & Strategic Objectives

| ID  | Objective                              | 12‑Mo KPI                                                   |
| --- | -------------------------------------- | ----------------------------------------------------------- |
| O‑1 | Shorten landscaper sales cycle         | ‑35 % avg. days from site visit → signed contract           |
| O‑2 | Raise proposal win rate                | +25 % (baseline confirmed at 20 % via pilot)                |
| O‑3 | Achieve profitable SaaS unit economics | Gross margin ≥ 65 %; CAC payback ≤ 9 mo                     |
| O‑4 | Build defensible data asset            | ≥ 50 k confirmed‑installed designs feeding model retraining |
| O‑5 | Expand to five Sun‑Belt metros         | DFW → Houston → Phoenix → Tampa → Atlanta by M12            |

⸻

## 2. Market Context (abridged)

* TAM (Sun‑Belt 5 metros): ≈ 17 k firms, $27 B rev.
* Gap: Existing CRMs (Jobber, LMN) lack automated photoreal renders, risk scoring, and credit‑based AI usage.

⸻

## 3. Personas

| Persona    | Core Goals                           | Key Pain                             |
| ---------- | ------------------------------------ | ------------------------------------ |
| Crew Lead  | Capture site data once, no paperwork | Juggling phone photos + scribbles    |
| Estimator  | Quote fast & accurately              | Manual take‑offs, excel errors       |
| Owner / GM | Grow revenue, control margin         | No visibility to funnel, weak upsell |
| Admin      | Manage users, prices, branding       | N/A today                            |
| Homeowner  | Visualize result & price             | Fear of poor plant survival          |

⸻

## 4. End‑to‑End Workflows (delta‑enhanced)

### 4.1 Capture (Mobile PWA / React Native wrapper)

1. **New Project** → auto‑tags GPS, date, crew ID.
2. **Photo sweep**: min 6 photos; app enforces 30° overlap for photogrammetry.
3. **Scale reference**: user scans a YardVision QR‑marker (12 in) or inputs a baseline dimension.
4. **Sketch layer** (Red = remove, Green = add, Blue = hardscape).
5. **Voice note** → text; NLP tags species.
6. **Offline queue** capped 250 MB; syncs on connectivity.

### 4.2 AI Design Job (async)

* `POST /v1/design-jobs` returns `job_id`.
* Pipeline: Annotation → Plant‑Detect (YOLOv8‑Landscape) → Design Grammar engine (see §10) → SDXL preview (1024²) in ≤ 45 s P95 → HD render (4096²) queued; average 120 s.
* Risk Engine pulls climate/soil zone (Köppen API, SoilGrids) and computes severity.
* Upsell Generator produces 3 high‑margin concepts; preview renders on demand.

### 4.3 Proposal & Acceptance

* Estimator adjusts BOM, labor hrs, overhead multipliers.
* “Publish Proposal” → PDFs + interactive microsite (Next.js static w/ client‑side toggles).
* Status webhooks (signed HMAC) to Jobber / LMN; accepted jobs push final design to **Confirm & Finalize** step (crew marks actual install).
* Final design + outcome feed back into training store.

⸻

## 5. Functional Requirements (selected)

| ID       | Detail                                                                                     |
| -------- | ------------------------------------------------------------------------------------------ |
| F‑CAP‑03 | Photogrammetry engine must infer ±5 % accuracy on distances ≤ 40 ft using scale reference. |
| F‑DES‑01 | Design Grammar engine must respect spacing, layer, color‑contrast rules (see appendix).    |
| F‑REN‑03 | HD render P95 ≤ 180 s under 500 concurrent jobs (GPU auto‑scale).                          |
| F‑RSK‑03 | Risk Engine pluggable zones; must support any US zip code south of USDA 6.                 |
| F‑ADM‑01 | Admin portal: user CRUD, brand settings, rate‑card editor, credit wallet.                  |

⸻

## 6. Non‑Functional Requirements

| Category      | Requirement                                                                               |
| ------------- | ----------------------------------------------------------------------------------------- |
| Performance   | Non‑render API P95 ≤ 300 ms; design job queue throughput ≥ 3 k/hr.                        |
| Availability  | 99.7 % monthly.                                                                           |
| Security      | SSO (O365/Google), TLS 1.3, row‑level tenant isolation; signed JWT (24 h life) + refresh. |
| Privacy       | Photos stored 365 d by default; tenant admin may purge at any time.                       |
| Compliance    | SOC 2 Type I by M9, Type II by M15.                                                       |
| Accessibility | WCAG 2.1 AA.                                                                              |
| Localization  | ES‑MX UI in M6.                                                                           |

⸻

## 7. System Architecture (updated)

```mermaid
flowchart TD
  subgraph Mobile
    A[React‑Native / PWA]
  end
  A -->|REST| B[API Gateway]
  B --> C[Capture Service]
  B --> D[Design Job Queue (SQS)]
  D --> E[Worker Fleet – GPU (SDXL, YOLO)]
  E --> F[Design Grammar Engine]
  F --> G[Risk Engine]
  F --> H[Upsell GPT‑4o]
  H --> I[Cost Estimator]
  G & I --> J[(PostgreSQL + S3)]
  B --> K[Proposal Service]
  K --> L[PDF / Microsite Builder]
  L --> S3
  B --> M[Admin Service]
  J -->|CDC| N[Model Registry (MLflow)]
  N --> O[Training Pipeline (ECS Batch)]
  O --> P[Model Versions]
  P --> E
  G -->|events| Q[(Kafka)]
  Q --> Grafana & Metabase
```

* **GPU pool auto‑scale** via AWS AutoScaling (g5.xlarge baseline 2 → 20).
* **Observability**: OpenTelemetry traces, Grafana Cloud; business funnel metrics via Kafka stream.
* **Deployment**: GitHub Actions → ECR; Blue‑Green on ECS; IaC with Terraform.

⸻

## 8. Data Model (additions)

| Table                         | Key Columns                                                                          |
| ----------------------------- | ------------------------------------------------------------------------------------ |
| `users`                       | id, tenant_id, name, email, role ENUM('admin','estimator','crew'), pw_hash, status |
| `credit_wallets`              | tenant_id, balance_int (AI credits), updated_at                                   |
| `rate_card_items`             | id, tenant_id, item_type, unit, base_cost, labor_hours, category                 |
| `audit_log`                   | id, user_id, action, meta_json, ts                                                 |
| *(all prior tables retained)* |                                                                                      |

⸻

## 9. API Spec (delta)

| Method | Endpoint                  | Params                           | Notes                                      |
| ------ | ------------------------- | -------------------------------- | ------------------------------------------ |
| POST   | /v1/design‑jobs           | project_id, preview_only(bool) | Returns job_id                            |
| GET    | /v1/design‑jobs/{job_id} | –                                | QUEUED / RUNNING / COMPLETE / ERROR + urls |
| POST   | /v1/credits/purchase      | plan_id                         | Stripe checkout session                    |
| POST   | /v1/credits/deduct        | tenant_id, amount               | Idempotent; called by Design Service       |
| GET    | /v1/rate‑card             | tenant_id                       | Structured rates                           |

⸻

## 10. AI & ML Components

| Component       | Model                             | Metric                | Ops                                    |
| --------------- | --------------------------------- | --------------------- | -------------------------------------- |
| Plant Detect    | YOLOv8‑Landscape                  | mAP@0.5 ≥ 0.88       | Auto‑retrain monthly on flagged errors |
| Design Grammar  | Rule+GNN hybrid                   | Human QA score ≥ 90 % | Versioned in MLflow; A/B rollout       |
| Risk Classifier | GBM + DistilBERT                  | F1 ≥ 0.80             | Drift monitor (KS‑stat > 0.1)          |
| Upsell LLM      | GPT‑4o w/ system prompt v1        | Acceptance ≥ 90 %     | RLHF feedback loop                     |
| Cost Estimator  | Linear labor model + margin rules | ±8 % vs. actuals      | Refit quarterly                        |

⸻

## 11. Security & Privacy

* **AuthN**: JWT + refresh; revoke via Redis blacklist.
* **AuthZ**: RBAC; signed HMAC on outgoing webhooks.
* **PII**: Names/emails AES‑256 at rest.
* **Content Safety**: AWS Rekognition + C2PA watermark on all renders.
* **Disaster Recovery**: RDS multi‑AZ, 15‑min RPO; S3 cross‑region replicate (us‑east‑2).

⸻

## 12. Analytics & Telemetry

| Metric                | Source                                       | Tool     |
| --------------------- | -------------------------------------------- | -------- |
| Render P95            | GPU worker logs                              | Grafana  |
| Avg. quote time       | event diff (PROJECT_CREATED→PROPOSAL_SENT) | Metabase |
| Win‑rate uplift       | proposals + Jobber webhook                   | Redash   |
| Credits burn / tenant | `credit_wallets`                             | Grafana  |

⸻

## 13. Testing & QA

* **Unit** ≥ 90 % on parsers, cost, risk.
* **E2E** Cypress: capture → accepted job.
* **Load** k6: 1 MB photo upload 300 rps; design job queue spike 1 k concurrent.
* **AI regression**: synthetic benchmark each build; manual audit 200 renders/week (< 5 % error).
* **Security**: OWASP ZAP; Snyk CVE monitor.

⸻

## 14. Rollout & Milestones (quarters)

Q1 | Capture app GA, Design preview, credit billing
Q2 | HD renders, Risk Engine (multi‑zone), Admin portal, Houston launch
Q3 | Upsell engine, Jobber/LMN live sync, Phoenix & Tampa
Q4 | Marketplace (suppliers), Atlanta, SOC‑2 Type I, cost estimator v2

⸻

## 15. Pricing & Packaging (credit‑based)

| Plan                                                                             | Monthly | Included Credits | Seats | Notes                                 |
| -------------------------------------------------------------------------------- | ------- | ---------------- | ----- | ------------------------------------- |
| Starter                                                                          | $99    | 1 000            | 2     | ~25 HD renders + proposals           |
| Pro                                                                              | $249   | 4 000            | 10    | Risk & Upsell, CRM sync               |
| Agency                                                                           | $499   | 10 000           | 30    | API access, multi‑brand, priority GPU |
| Overage: buy credit packs @ $0.035/credit (internal cost $0.02). Annual –10 %. |         |                  |       |                                       |

*1 HD render = 40 credits; SD preview = 10; Upsell quick render = 20.*

⸻

## 16. Risks & Mitigations (top)

| Risk                      | Impact         | Mitigation                                               |
| ------------------------- | -------------- | -------------------------------------------------------- |
| API price hikes           | Margin erosion | Credits buffer + provider redundancy; local SDXL         |
| GPU shortage spring rush  | Queue delays   | Reserved GPU pool + spot burst                           |
| Tech‑averse crews         | Low adoption   | Guided first‑run, stylus kit, live hotline               |
| Design errors kill plants | Refunds        | Confidence scores, mandatory human review if risk = high |

⸻

## 17. Glossary (delta)

* **Credit** – Internal unit (~$0.035) consumed per AI operation.
* **Design Grammar** – Rule/GNN engine encoding landscape design principles.
* **Confirm & Finalize** – Post‑install step supplying ground‑truth for retraining.

⸻

Appendix added below. This version is formatted and ready to be embedded in the final PRD (v3.0):

---

## **Appendix A: Design Grammar v1.0**

### **Purpose**

The Design Grammar Engine transforms sketched user intent into aesthetically cohesive, horticulturally sound landscape layouts. It enforces foundational rules, aesthetic principles, and leverages a GNN for final refinement.

---

### **1. Data Prerequisites**

The `plant_catalog` must contain:

* `growth_habit`: ENUM('clumping', 'spreading', 'upright', 'vining', 'mounding')
* `height_class`: ENUM('groundcover', 'short', 'medium', 'tall', 'specimen')
* `canopy_width_ft`: FLOAT
* `foliage_color_family`: ENUM('green', 'blue-green', 'chartreuse', 'burgundy', 'variegated')
* `flower_color_family`: ENUM('white', 'yellow', 'orange', 'red', 'pink', 'blue', 'purple')
* `seasons_of_interest`: ARRAY['spring', 'summer', 'fall', 'winter']
* `texture`: ENUM('fine', 'medium', 'coarse')
* `is_specimen`: BOOLEAN

---

### **2. Rule Set 1: Spacing & Placement**

**Foundational viability logic:**

* **R1.1 Plant Spacing:**
  `min_distance = (A.canopy_width_ft / 2 + B.canopy_width_ft / 2) * 0.9`
* **R1.2 Hardscape Clearance:**
  `min_distance_from_hardscape = (canopy_width_ft / 2) + 1.0`
* **R1.3 Structure Avoidance:**
  `tall/specimen` plants must not be within 10 ft of structures or directly under lines

---

### **3. Rule Set 2: Composition & Aesthetics**

**Priority-based refinement rules:**

* **R2.1 Layering:**
  Front-to-back: groundcover → short → medium → tall; specimen overrides allowed
* **R2.2 Grouping:**
  Non-specimen plants must be grouped in odd numbers (3, 5, 7)
* **R2.3 Focal Points:**
  Max one `is_specimen = TRUE` per landscape bed
* **R2.4 Color Cohesion:**

  * Max 3 flower color families per bed
  * Avoid clashing adjacency; enforce analogous/complementary color theory
* **R2.5 Texture Variety:**
  5+ plant groupings must include ≥2 different textures

---

### **4. Rule Set 3: GNN Refinement Layer**

* **Graph**

  * *Nodes:* plants, hardscape, photo viewpoints
  * *Edges:* adjacency, visibility, co-location
* **Training Objective**
  Trained on *Confirm & Finalize* dataset:

  * *Positive:* Accepted layouts
  * *Negative:* Deleted/moved placements
* **Inference Workflow**

  * Run Rules 1–2
  * GNN scores arrangement (`Aesthetic_Score: 0.0–1.0`)
  * Generate layout variations → select highest score

---

## **Section 10.1: Upsell Generator Logic**

### **Process Flow**

1. **Trigger:** After base design + risk engine complete

2. **Candidate Sourcing:**

   * `rate_card_items` where category ∈ (`Lighting`, `Hardscape Upgrade`, `Premium Plant`, `Water Feature`, `Maintenance Package`)
   * Include items with `margin_percent > 0.40`

3. **Contextual Filters:**

   * **Project Scale Filter:**

     * If quote < $2k → exclude items > $1k
     * If quote < $10k → exclude items > $5k
   * **Risk Filter:** exclude 'high risk' plant items
   * **Duplication Filter:** exclude items already in BOM

4. **Scoring & Ranking:**

   ```
   Rank_Score = (normalized_margin * 0.6) + (normalized_popularity * 0.4)
   ```

   * Top 3 scored candidates are selected

5. **LLM Prompt (GPT-4o)**
   **System Prompt:**

   ```
   You are YardVision Pro's expert sales assistant... (as provided)
   ```

   **User Message:** Uses project context and structured upsell items list (as provided)

---

## **Section 10.2: Cost Estimator Logic**

### **Inputs**

* `Design_BOM`
* `tenant_rate_card`
* `tenant_settings`

  * `default_labor_rate_per_hour`
  * `default_overhead_multiplier`

### **Formulas**

* **Material Cost:**
  `SUM(quantity * base_cost)`
* **Labor Cost:**
  `SUM(quantity * labor_hours) * labor_rate`
* **Subtotal:**
  `material + labor`
* **Final Quote:**
  `subtotal * (1 + overhead_multiplier)`

### **Output JSON Format**

```json
{
  "baseline_quote_total": 7375.00,
  "components": {
    "total_material_cost": 4250.00,
    "total_labor_cost": 1750.00,
    "total_calculated_hours": 35.0,
    "project_subtotal": 6000.00
  },
  "factors": {
    "labor_rate_applied": 50.00,
    "overhead_multiplier_applied": 0.25
  }
}
```

