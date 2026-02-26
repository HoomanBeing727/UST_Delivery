# 🍟 McDelivery Match App – Product Specification

## 🧩 Overview

The **McDelivery Match App** is a peer-to-peer delivery platform designed for students to coordinate food delivery from McDonald's within their school community.  

Users can act as either:
- **Orderers** — who place and track McDonald’s orders, or  
- **Deliverers** — who accept and deliver orders from others in the same dormitory hall or location.  

The app integrates **real-time tracking**, **automated receipt OCR**, **secure payment**, and a **trust-based rating system**.

---

## 📱 App Flow Summary

1. **Login & Verification**  
2. **Profile Setup**  
3. **Main Dashboard**  
4. **Order Upload & Management**  
5. **Delivery Queue & Tracking**  
6. **Payment & Rating System**

---

## 🔐 1. Login Page

**Purpose:** Authenticate users using school credentials for trust and accountability within the community.

### Features
- **Login Methods:**
  - School email (e.g., `user@connect.ust.hk`) with email verification
  - Phone number (via SMS verification)
- **Verification Flow:**
  - Send a one-time code (OTP) via email or SMS.
  - User enters the received code for authentication.
- **Post-login Redirect:**  
  → Directs users to the **Main Dashboard**.

---

## 👤 2. Profile Setup Page

**Purpose:** Collect relevant user information for verification and accurate matching.

### User Information Fields

| Field | Required | Description |
|--------|-----------|-------------|
| Name | ✅ | Full name of the user |
| Student ID | ✅ | Used for verification and school-only access |
| Dormitory Hall | ✅ | For initial hall-based matching |
| Role | ✅ | Choose between **Deliverer** or **Orderer** |

### Additional Fields (Deliverer Only)

| Field | Required | Description |
|--------|-----------|-------------|
| Availability | ✅ | Time slots available for deliveries |
| Preferred Delivery Times | ✅ | Days and hours preferred for deliveries |

> 💡 Future versions may expand to **location-based matching**, beyond halls.

---

## 🏠 3. Main Dashboard

**Purpose:** Central hub for user navigation and actions.

### Core Features
- Manage profile  
- Logout button  
- Dark mode toggle  
- FAQ / Help center access  

### Primary Action
- **“Upload Receipt” Button**  
  - Initiates a new McDonald’s order submission.

---

## 🧾 4. Receipt Upload & Order Creation

**Purpose:** Capture order details automatically or manually for the delivery queue.

### Upload Process
1. User uploads a **McDonald's receipt screenshot**.  
2. The app performs **OCR scanning** to extract:
   - Order items  
   - Total price  
   - Timestamp / Order ID  
3. Extracted details are displayed for **confirmation or manual correction**.  
4. Once confirmed, the order is added to the **pending queue**.

### Rules & Restrictions
- Users **cannot create another order** until:
  - The current one is **completed** or **cancelled**.  
- **Estimated delivery time** displayed based on:
  - Queue size  
  - User’s hall / location  

---

## 🚴 5. Deliverer Queue & Workflow

**Purpose:** Manage delivery assignments and tracking for deliverers.

### Key Features for Deliverers
- View **available orders** in the same hall.  
- Accept an order (removes it from the queue).  
- GPS navigation to:
  - **McDonald's pickup**  
  - **Customer’s dorm/location**  

### Proof of Delivery Flow

| Step | Required Action |
|------|-----------------|
| Pickup | Upload photo of the receipt and pickup location |
| Delivery | Upload proof of drop-off photo |
| Confirmation | Both parties confirm completion |

### Future Expansion
- Transition from **hall-based** to **geo-location matching**.

---

## 🕒 6. Real-time Order Tracking

**Purpose:** Keep users updated and enhance transparency.

### Notifications
- 🟢 Order accepted by deliverer  
- 🔸 Deliverer en route to pickup  
- 🟣 Order picked up  
- 🔵 Deliverer en route to delivery  
- 🟢 Order completed  

### In-App Communication
- Chat or call between **orderer** and **deliverer**.  
- Real-time location tracking on an integrated map.

---

## 💳 7. Payment and Escrow System

**Purpose:** Secure and manage payments fairly for both roles.

### Flow
1. Orderer pays via integrated payment gateway (e.g., **Alipay HK**).  
2. Funds are held in **escrow** until delivery confirmation.  
3. Upon confirmation:
   - Payment is released to deliverer.  
4. A **small percentage** is deducted as a **service fee** for platform maintenance.

---

## ⭐ 8. Rating & Review System

**Purpose:** Build trust and maintain community standards.

### Rating Flow
- Both **Orderer** and **Deliverer** rate each other post-delivery.  
- Ratings include:
  - ⭐ 1–5 star scale  
  - Optional feedback text  

These ratings contribute to a **reputation score**, visible in user profiles.

---

## 🧭 9. Future Enhancements

- 🌍 Expand beyond halls to **location-based matching**  
- 🤖 Enhance **OCR accuracy** with ML models (e.g., *Google Vision / Tesseract*)  
- 🔔 Add **push notifications** and **live tracking**  
- 🧾 Auto-detect **duplicate receipts**  
- 💰 Introduce **loyalty / reward programs**  
- 🔒 Implement **multi-factor authentication (MFA)** for security  

---

## 🧱 Tech Stack (Suggested)

| Component | Technology |
|------------|------------|
| Frontend | React Native |
| Backend | FastAPI |
| Database | Firebase / PostgreSQL |
| OCR | PaddlePaddle |
| Auth | Firebase Auth (Email/SMS) |
| Payments | Alipay HK SDK |
| Notifications | Firebase Cloud Messaging (FCM) |

---

## 🧮 User Flow Diagram (High-Level)

[Login Page]
↓
[Profile Setup]
↓
[Main Dashboard] → [Upload Receipt]
↓ ↓
[Order Queue] ← [Confirm OCR Data]
↓
[Deliverer Accepts]
↓
[Tracking & Proof of Delivery]
↓
[Payment Release + Ratings]

---