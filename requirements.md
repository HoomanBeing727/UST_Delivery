# 🍔 HKUST McDelivery Peer-to-Peer System

## 🎯 Project Overview
A community-driven McDelivery system for HKUST students to reduce long wait times and delivery inconvenience by connecting students who can pick up and deliver other students’ McDonald’s orders while returning to their halls.  

**Core Idea:**  
Student A (delivery partner) picks up multiple nearby orders and delivers them to other students in HKUST halls, earning small rewards.

---

## 🧩 Problem Statement
- McDonald’s pickup queues during meal rush hours are long.  
- Students living in Halls must walk 10+ minutes to collect orders.  
- Existing delivery platforms charge high fees and are inefficient for short distances.

---

## 🚀 Proposed Solution
A lightweight, HKUST-internal app that allows:
1. **Order upload and verification** (via OCR on McDonald’s app screenshot).  
2. **Peer delivery matching** (students heading back to same hall group orders).  
3. **Secure payments** with anti-fraud mechanisms.  
4. **Rating and reputation** system to ensure trust.

---

## 🧠 Workflow Overview

1. **User places order in the McDonald’s app.**
2. **User uploads screenshot → OCR extracts details.**
3. **Backend verifies data → adds to queue.**
4. **Deliverer accepts order → travels to McDonald’s.**
5. **At pickup:**  
   - Deliverer must confirm pickup with photo + location proof.  
6. **At delivery:**  
   - User confirms receipt → funds released to deliverer.  
7. **Both sides rate each other → improves trust network.**

---

## 🏗️ System Components

| Layer | Technology | Description |
|-------|-------------|-------------|
| **Frontend (Mobile)** | React Native | Cross-platform mobile app for orderers & deliverers |
| **Backend (API)** | FastAPI | Manages auth, queue, verification, payments |
| **Database** | PostgreSQL | Structured storage for users, orders, transactions |
| **Cache** | Redis | Real-time queue, live delivery status |
| **OCR Engine** | PaddlePaddle | Extracts text and metadata from McDonald’s receipt screenshots |
| **Storage** | Firebase / AWS S3 | For storing screenshots and proof images |
| **Notification System** | Firebase Cloud Messaging / OneSignal | Updates users on delivery progress |
| **Payment Gateway** | PayMe / AlipayHK / WeChat Pay / Credit Card | Secure peer-to-peer payments |

---

## 🔒 Verification and Safety Mechanisms

1. **Photo verification** on pickup and delivery.  
2. **GPS proof** required within McDonald’s location radius.  
3. **Smart Timer** — adjusts wait time based on historical data.  
4. **Escrow Wallet Logic** — users pay first; funds released post-confirmation.  
5. **Blacklist System** for no-shows or fraud.  
6. **Delivery/Order Rating** to build reputations.  

---

## 💸 Fee and Reward Model

| Component | Description |
|-----------|--------------|
| **Delivery Fee** | ~8–10 HKD/order depending on distance |
| **Platform Fee** | ~1–2 HKD for system maintenance |
| **Deliverer Reward** | Receives remainder (approx. 80–90%) |
| **Bonus Model** | Leaderboard for top weekly deliverers |

---

## 🧮 Delivery Fee Calculation Formula

\[
\text{Delivery Fee} = \alpha \times P + \beta \times D + \gamma
\]
Where:  
- \(P\) = base meal price  
- \(D\) = scaled hall distance (e.g., Hall 1 = 1, Hall 6 = 3)  
- \(\alpha, \beta, \gamma\) = tunable constants for base rate, distance, and service fee  

---

## 🗓️ Project Timeline

| Phase | Duration | Deliverables |
|-------|-----------|--------------|
| **Phase 1: Research & Design** | Requirement gathering, architecture diagram |
| **Phase 2: MVP Development** | OCR module, upload verification, manual matching |
| **Phase 3: Internal Beta** | Hall 1 pilot test with 10 users |
| **Phase 4: Payment & Ratings** | Escrow system, feedback module |
| **Phase 5: Expansion + Ops Dashboard** | Delivery analytics, moderator panel |

---

## 🧰 Development Guidelines

- Maintain **separate roles:** `user`, `deliverer`, `admin`.  
- Implement **JWT-based auth**.  
- Use **GitHub Actions** for CI/CD pipeline.  
- Focus on **scalability and modular code**.  
- Follow **GDPR-like privacy** for user data and screenshots.

---

## 📊 Future Roadmap

- AI-based delivery optimization (cluster detection, route grouping).  
- Expand to other eateries (Starbucks, Subway, etc.).  
- Integrate **campus food locker** delivery points.  
- Potential open-source or student-managed pilot under HKUST ITSC club collaboration.

---
