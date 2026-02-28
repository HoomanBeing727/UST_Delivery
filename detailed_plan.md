# 🚴 DeliverU – Product Specification

## 🧩 Overview

**DeliverU** is a peer-to-peer delivery coordination app built for **HKUST students** to easily help each other get food from school canteens or nearby restaurants like McDonald’s and Subway.  

Every verified student can be both an **Orderer** and a **Deliverer**, allowing flexible roles within the same dormitory community.  

The app features:
- **School email verification**
- **Smart matching algorithm** for efficient pairing
- **Payment escrow and refund system**
- **Order tracking and auto notifications**
- **Dynamic tip calculation**

---

## 📱 App Flow Summary

1. **Login & School Verification**  
2. **Profile Setup**  
3. **Main Dashboard**  
4. **Order Creation & Management**  
5. **Deliverer Queue & Workflow**  
6. **Payment & Rating System**

---

## 🔐 1. Login Page

**Purpose:** Authenticate users through official school email to ensure trust and exclusivity to university students.

### Features
- **Login Method:**
  - HKUST email (e.g., `abc@connect.ust.hk`)
- **Verification Flow:**
  - Send a one-time verification code via email.
  - Upon successful verification, generate and store a **session token/cookie**, so re-login is not required until session expiry.
- **Post-login Redirect:**  
  → **Profile Setup Page**

---

## 👤 2. Profile Setup Page

**Purpose:** Collect personalized data to optimize delivery matching and user preferences.

### User Information Fields

| Field | Required | Description |
|--------|-----------|-------------|
| Nickname | ✅ | User’s display name within the app (real name optional) |
| School Email | ✅ | Automatically verified field |
| Dormitory Hall | ✅ | For matching nearby orders and deliveries |
| Usually Orders At | ✅ | Typical time ranges when user orders food |
| Delivery Preference | ✅ | For example: “Deliver to room” or “Meet in lobby” |

### Deliverer Additional Fields

| Field | Required | Description |
|--------|-----------|-------------|
| Available Return Times | ✅ | When the user usually goes back to hall |
| Preferred Delivery Halls | ✅ | The halls the deliverer wants to deliver to |

### Verification Step
- One-time **Student ID verification** can be requested for additional security.  
  - The system checks validity but **does not store** the ID data.

### Role Flexibility
- All users can **act as both Orderer and Deliverer**.  
- Users can toggle delivery participation on/off anytime.

---

## 🏠 3. Main Dashboard

**Purpose:** Central hub for navigation and status management.

### Core Features
- Manage profile & preferences  
- View active orders (as Orderer or Deliverer)  
- View completed orders  
- Dark mode toggle  
- FAQ / Help center access  
- Logout button  

### Primary Actions
- **Order Food**  
  Redirects user to order-creation flow.

- **Find Orders to Deliver**  
  Opens filtered deliverer queue.

---

## 🛒 4. Order Creation & Management

**Purpose:** Allow users to place orders directly through canteen or restaurant integrations.

### New Order Flow

#### For School Canteens
1. User selects canteen (e.g., **LG1**, **LG7**, or **LSK**).
2. The app embeds the **canteen ordering webpage** within DeliverU.
3. After selecting items and pressing “Order,” user is redirected back to DeliverU.
4. DeliverU fetches the item list and pricing data from the canteen's webpage.
5. User confirms and pays within app.
6. The order enters a **pending state**, awaiting deliverer acceptance.

#### For External Restaurants (e.g., McDonald's, Subway)
- DeliverU backend hosts an **Android emulator** to listen for menu updates from official apps.
- Menu updates are synced automatically with DeliverU for order placement.

---

### Order Management Rules
- Pending orders stay open until accepted by a deliverer.
- If **no deliverer accepts within 30 minutes**, the user may **cancel the order**, triggering a **full refund**.
- **When a deliverer accepts:**
  - Deliverer **pays upfront** at pickup.
  - Upon successful delivery, the system reimburses the **food cost + tip** from escrow.

---

## 🚴 5. Deliverer Queue & Workflow

**Purpose:** Provide a personalized and efficient way for deliverers to find the best orders.

### Features
- View available orders filtered by:
  - Hall location  
  - Order amount  
  - Preferred range and timings  
- Accept orders directly from the queue.
- Once accepted:
  - Order removed from the public queue.
  - Orderer automatically notified.
  - Deliverer receives order details and any auto-message (e.g., “Deliver to lobby.”).

### Proof of Delivery Flow

| Step | Required Action |
|------|-----------------|
| Pickup | Upload photo of the purchased meal |
| Delivery | Upload photo proof of drop-off |
| Confirmation | Both parties confirm delivery status |
| Payment | Automatically released after confirmation |

---

## 💳 6. Payment and Escrow System

**Purpose:** Ensure transparent, safe, and fair transactions between Orderers and Deliverers.

### Payment Flow
1. Orderer pays when creating the order.  
   (Payment is held in **escrow**.)
2. When deliverer accepts, they pay for the order at pickup point.
3. Upon delivery confirmation:
   - **Escrow releases** full order price + **tip** to deliverer.
4. If no deliverer accepts within 30 min → auto refund to Orderer.

### Tip Formula
\[
\text{Tip} = (\text{Order Price} \times 10\%) + C \times \text{Distance}
\]
> where \( C \) is a constant value determined later.  
Values are rounded to avoid decimals.

### Platform Fee

We will charge a **small platform fee** (around $0.5 - $1.0) to cover operational costs from each order, deducted from the user’s payout.

---

## 💬 7. Temporary Chat Session

**Purpose:** Provide a secure, ephemeral communication channel between the Orderer and Deliverer for coordination.

### Chat Flow
1. When a deliverer accepts an order, a **temporary chat session** is automatically created.
2. The system sends **auto messages** first:
   - Orderer’s delivery preference (e.g., *“Meet in LG7 lobby”*)  
   - Deliverer’s ETA or pickup info
3. After auto messages, both users can freely chat to coordinate any changes or clarifications.

### Key Features
- **End-to-end secured via HTTPS**
- **Session expires** after order completion or cancellation
- **No chat history stored** — messages are deleted once the session closes
- Supports **text and system message types** (no media upload in this version)

### Benefits
- Enhances communication while maintaining privacy  
- Prevents data accumulation and ensures full compliance with privacy policies  
- Auto-injects relevant preference data for smoother coordination

---

## ⭐ 8. Rating & Review System

**Purpose:** Maintain trust and fairness within the DeliverU ecosystem.

### Rating Flow
- Both Orderer and Deliverer rate each other upon delivery completion.
- Ratings include:
  - ⭐ 1–5 stars  
  - Optional written feedback  
- Ratings contribute to a visible **Reputation Score** in each profile.

---

## 🧭 8. Future Enhancements

- 📍 AI-powered **order matching optimization**  
- 🧠 Smarter **menu sync and caching** system  
- 🔒 Enhanced session management and MFA  
- 🔔 Push notifications for order status  
- 💰 Loyalty / reward program for frequent users  
- 🧾 Duplicate order detection and fraud prevention  

---

## 🧱 Tech Stack (Proposed)

| Component | Technology |
|------------|------------|
| Frontend | React Native |
| Backend | FastAPI |
| Database | Firebase / PostgreSQL |
| Auth | Firebase Auth (Email Verification) |
| Payment | Alipay HK / WeChat Pay / PayMe SDK |
| Canteen Integration | Embedded WebView + Data Fetch |
| Notifications | Firebase Cloud Messaging (FCM) |
| Virtualized Restaurant APIs | Android Emulator Listener |

---

## 💰 Server Cost Evaluation

**Goal:** Establish a stable backend infrastructure with minimal cost by leveraging HKUST resources and flexible hosting options.

### Strategy & Priority
1. **University Collaboration (Preferred Option)**  
   - Submit a proposal to **HKUST IT or Entrepreneurship Center** for **approval and support**.  
   - Request permission to access and integrate with the **school email system** (for secure login).  
   - Apply to rent a **small node** on the university’s internal network for backend hosting.  
     > This is likely to be low-cost or free if approved.

2. **Backup Plan: Personal Server on Campus**
   - If approval is not granted, negotiate to **host our own physical server** on campus (e.g., lab or office corner).  
   - Purchase or assemble a low-power **dedicated PC** for backend hosting.

3. **Dorm-based Hosting (Last Resort)**
   - If university hosting is unavailable, host the backend temporarily inside a **dorm room** using a personal PC or mini server.  
   - This approach minimizes cost significantly while maintaining acceptable latency within the HKUST network.

### Expected Benefits
- **Low operational cost** (no commercial cloud instance needed initially)  
- **High performance** due to local campus network proximity  
- **Full control** over server configuration and data access policies  
- **Scalable path** — can migrate to official infrastructure if app gains traction

---

## 🧮 User Flow Diagram (High-Level)

[Login via HKUST Email]  
↓  
[Profile Setup]  
↓  
[Dashboard]  
→ [Order Food] (via Canteen / Restaurant Integration)  
↓  
[Order Pending]  
↓  
[Deliverer Accepts]  
↓  
[Pickup + Proof]  
↓  
[Delivery & Confirmation]  
↓  
[Escrow Release + Rating]  

---

**DeliverU** — Built by students, for students.  
Making canteen and restaurant delivery smarter, fairer, and community-driven.