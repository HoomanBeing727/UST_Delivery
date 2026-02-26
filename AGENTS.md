# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-26
**Commit:** df6fdfb
**Branch:** main

## OVERVIEW

Peer-to-peer McDonald's delivery platform for HKUST students. Pre-development — specs only, no code yet. Planned stack: React Native (mobile) + FastAPI (backend) + PostgreSQL + Redis + PaddlePaddle OCR.

## STATUS

**Phase: Pre-development (planning/spec docs only)**

No source code, configs, tests, CI/CD, or build system exist. The repo contains two specification documents that define the full product.

## STRUCTURE

```
UST_Delivery/
├── requirements.md        # System overview, tech stack, workflow, dev guidelines
└── datailed_plan.md       # Detailed product spec, app flow, page-by-page design
```

## WHERE TO LOOK

| Task | File | Notes |
|------|------|-------|
| Understand the product | `requirements.md` | High-level: problem, solution, workflow, components |
| Understand app flow | `datailed_plan.md` | Page-by-page: login, profile, dashboard, upload, tracking, payment, ratings |
| Tech stack decisions | `requirements.md` §System Components | Table of all layers + chosen tech |
| Fee calculation formula | `requirements.md` §Delivery Fee | `α×P + β×D + γ` with tunable constants |
| User roles & restrictions | `datailed_plan.md` §4-5 | Orderer vs Deliverer flows, one-active-order rule |
| Payment/escrow flow | `datailed_plan.md` §7 | Pay → escrow hold → delivery confirm → release |
| Project timeline/phases | `requirements.md` §Project Timeline | 5 phases from research to ops dashboard |

## PLANNED ARCHITECTURE

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React Native | Cross-platform mobile (iOS/Android) |
| Backend | FastAPI | Auth, queue, verification, payments |
| Database | PostgreSQL | Users, orders, transactions |
| Cache | Redis | Real-time queue, live delivery status |
| OCR | PaddlePaddle | Receipt screenshot text extraction |
| Storage | Firebase / AWS S3 | Screenshots and proof images |
| Notifications | FCM / OneSignal | Delivery progress updates |
| Payments | PayMe / AlipayHK / WeChat Pay | Peer-to-peer with escrow |
| Auth | JWT + Firebase Auth | Email (`@connect.ust.hk`) / SMS OTP |
| CI/CD | GitHub Actions | Pipeline (not yet configured) |

## CONVENTIONS (FROM SPECS)

- **Auth**: JWT-based only. School email (`@connect.ust.hk`) or phone OTP.
- **Roles**: Strict separation — `user`, `deliverer`, `admin`. No role mixing.
- **Orders**: One active order per user. Must complete/cancel before creating another.
- **Verification**: Photo proof required at both pickup AND delivery. GPS within McDonald's radius.
- **Payments**: Escrow-first. Funds release only after both-party confirmation.
- **Privacy**: GDPR-like handling for user data and screenshots.
- **Code style**: Specs call for "scalability and modular code" — no specific linter/formatter chosen yet.

## ANTI-PATTERNS (THIS PROJECT)

- **No direct payments** — always escrow. Never release funds without delivery confirmation.
- **No multi-order abuse** — enforce one-active-order constraint per user.
- **No unverified deliveries** — photo + GPS proof mandatory. No shortcuts.
- **No role blending** — keep orderer/deliverer/admin cleanly separated.
- **Blacklist enforcement** — no-shows and fraud must trigger blacklist system.

## DOMAIN CONCEPTS

| Term | Meaning |
|------|---------|
| Orderer | Student who places a McDonald's order and wants delivery |
| Deliverer | Student heading to McDonald's who picks up others' orders |
| Hall matching | Orders grouped by dormitory hall proximity |
| Escrow wallet | Payment held by platform until delivery confirmed by both parties |
| OCR upload | Screenshot of McDonald's app receipt → auto-extract order details |
| Reputation score | Cumulative rating (1-5 stars) visible on profiles |
| Smart timer | Dynamic ETA based on historical queue/delivery data |

## WORKFLOW (CRITICAL PATH)

```
Order placed in McDonald's app
  → Screenshot uploaded to platform
    → OCR extracts order details
      → User confirms/corrects extracted data
        → Order enters pending queue
          → Deliverer in same hall accepts order
            → Deliverer picks up (photo + GPS proof)
              → Deliverer delivers (photo proof)
                → Both parties confirm
                  → Escrow releases payment
                    → Both rate each other
```

## NOTES

- This is a **greenfield project** — no existing code patterns to follow. When development begins, establish configs (linter, formatter, tsconfig, etc.) before writing feature code.
- The two spec docs are comprehensive. Read both fully before implementing anything.
- Fee formula uses tunable constants (`α`, `β`, `γ`) — these need to be configurable, not hardcoded.
- OCR engine choice (PaddlePaddle) is unusual — `datailed_plan.md` §9 also mentions Google Vision / Tesseract as alternatives.
- Payment integrations (PayMe, AlipayHK, WeChat Pay) are HK-specific — SDK availability and sandbox testing will need early validation.
