# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-26
**Commit:** df6fdfb (with code implementation)
**Branch:** main

---

## OVERVIEW

Peer-to-peer McDonald's delivery platform for HKUST students. React Native (Expo) frontend + FastAPI backend with OCR-based receipt processing.

**Status:** Early development — OCR feature implemented, auth/queue/payment pending.

---

## BUILD/RUN/TEST COMMANDS

### Backend (FastAPI + Python)

```bash
# Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run development server
python -m app.main
# OR
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Linting/formatting (if ruff is added to requirements.txt)
ruff check .                    # Lint
ruff check --fix .              # Auto-fix
ruff format .                   # Format code

# Testing (if pytest is added to requirements.txt)
pytest                          # Run all tests
pytest tests/test_ocr.py        # Run single test file
pytest -k "test_function_name"  # Run single test by name
pytest -v                       # Verbose output
pytest --cov=app                # Coverage report
```

### Frontend (React Native + Expo)

```bash
# Setup
cd frontend
npm install

# Run development
npm start                       # Start Expo dev server
npm run android                 # Run on Android emulator
npm run ios                     # Run on iOS simulator
npm run web                     # Run in web browser

# Type checking
npx tsc --noEmit                # Check types without building

# Testing (if jest/testing-library is added to package.json)
npm test                        # Run all tests
npm test -- FormCorrectionScreen.test.tsx  # Run single test file
npm test -- -t "test name"      # Run single test by name
npm test -- --coverage          # Coverage report

# Linting/formatting (if eslint/prettier is configured)
npx eslint . --fix              # Lint and auto-fix
npx prettier --write .          # Format code
```

---

## CODE STYLE GUIDELINES

### Python Backend

**Imports:**
- Group: stdlib → third-party → local
- Use absolute imports for `app.*` modules
- Example:
  ```python
  import re
  import io
  from fastapi import APIRouter, HTTPException
  from app.models.schemas import OCRResponse
  from app.services.ocr_service import extract_text
  ```

**Type Annotations:**
- Use modern Python 3.10+ syntax: `list[str]`, `dict[str, int]`, `float | None`
- NO `from typing import List, Dict, Optional` — use built-in types
- Always annotate function parameters and return types
- Example:
  ```python
  def parse_receipt(text_lines: list[str]) -> dict:
      order_number: str = ""
      items: list[dict] = []
      return {"order_number": order_number}
  ```

**Naming:**
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private/internal: prefix with `_` (e.g., `_extract_price`)

**Docstrings:**
- Use simple `"""..."""` one-liners for small functions
- Example: `"""Extract HK$ price from a text string."""`

**Error Handling:**
- FastAPI: raise `HTTPException(status_code=400, detail="message")`
- Services: return errors in response dict (e.g., `{"errors": ["msg"]}`)

**Formatting:**
- Indent: 4 spaces
- Max line length: ~100 chars (flexible, not strict)
- No trailing whitespace

---

### TypeScript/React Native Frontend

**Imports:**
- Group: React → React Native → third-party → local types → local components
- Example:
  ```typescript
  import React, { useState } from 'react';
  import { View, Text, StyleSheet } from 'react-native';
  import { NativeStackScreenProps } from '@react-navigation/native-stack';
  import { useTheme } from '../context/ThemeContext';
  import { RootStackParamList, OCRResult } from '../types/navigation';
  ```

**Type Annotations:**
- Use TypeScript strict mode (`"strict": true`)
- Prefer `interface` for object shapes, `type` for unions/intersections
- Always type component props (use `NativeStackScreenProps` for screens)
- Avoid `any` — use `unknown` or proper types
- Example:
  ```typescript
  interface OrderItem {
    name: string;
    quantity: number;
    price: number;
  }

  type Props = NativeStackScreenProps<RootStackParamList, 'FormCorrection'>;
  ```

**Naming:**
- Components: `PascalCase` (e.g., `FormCorrectionScreen`)
- Functions/variables: `camelCase`
- Constants: `UPPER_SNAKE_CASE` or `camelCase` (e.g., `API_BASE_URL`, `apiClient`)
- React hooks: prefix with `use` (e.g., `useTheme`)

**Component Structure:**
- Functional components with hooks (no class components)
- Destructure props in function signature
- Define styles with `StyleSheet.create()` at bottom of file
- Example:
  ```typescript
  export default function MyScreen({ navigation, route }: Props) {
    const { colors } = useTheme();
    const [state, setState] = useState('');
    return <View>...</View>;
  }

  const styles = StyleSheet.create({
    container: { flex: 1 },
  });
  ```

**Error Handling:**
- Use `Alert.alert(title, message)` for user-facing errors
- Handle axios errors with try-catch in API calls
- Validate form inputs before submission

**Formatting:**
- Indent: 2 spaces
- Max line length: ~100 chars (flexible)
- Use single quotes for strings
- Trailing commas in multi-line objects/arrays

---

## PROJECT STRUCTURE

```
UST_Delivery/
├── frontend/                   # React Native (Expo) app
│   ├── src/
│   │   ├── screens/            # Screen components (Dashboard, Loading, FormCorrection)
│   │   ├── types/              # TypeScript type definitions
│   │   ├── services/           # API client (axios)
│   │   └── context/            # React context (Theme)
│   ├── App.tsx                 # Main app entry with navigation
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/                # API routes (ocr.py)
│   │   ├── services/           # Business logic (ocr_service, receipt_parser)
│   │   ├── models/             # Pydantic schemas
│   │   └── main.py             # FastAPI app entry
│   └── requirements.txt
│
├── requirements.md             # Product spec
├── detailed_plan.md            # Detailed design doc
└── AGENTS.md                   # This file
```

---

## CONVENTIONS

**API Communication:**
- Backend serves at `http://0.0.0.0:8000`
- Frontend uses `http://localhost:8000` (iOS/web) or `http://10.0.2.2:8000` (Android emulator)
- All endpoints prefixed with `/api` (e.g., `/api/ocr`)
- Use `multipart/form-data` for file uploads, `application/json` for JSON

**OCR Flow:**
- Frontend: User uploads receipt image → POST to `/api/ocr`
- Backend: Extract text with RapidOCR → Parse with regex → Return structured JSON
- Frontend: Display parsed data in FormCorrectionScreen for user review

**Validation:**
- HKUST validation: Check restaurant name for keywords (`"HKUST"`, `"Hong Kong University of Science"`, `"科技大學"`)
- Orders from non-HKUST McDonald's are marked `is_valid: false` and cannot be submitted

**Error Handling:**
- Backend: OCR failures/parsing issues go into `errors` array in response (non-fatal)
- Frontend: Display errors in UI, allow user to manually correct

---

## DOMAIN CONCEPTS

| Term | Meaning |
|------|---------|
| Orderer | Student who places a McDonald's order and wants delivery |
| Deliverer | Student heading to McDonald's who picks up others' orders |
| Hall matching | Orders grouped by dormitory hall proximity (NOT YET IMPLEMENTED) |
| Escrow wallet | Payment held by platform until delivery confirmed (NOT YET IMPLEMENTED) |
| OCR upload | Screenshot of McDonald's app receipt → auto-extract order details |
| Reputation score | Cumulative rating (1-5 stars) visible on profiles (NOT YET IMPLEMENTED) |

---

## ANTI-PATTERNS (THIS PROJECT)

**Python:**
- ❌ `from typing import List, Dict` — use `list`, `dict` instead
- ❌ Missing type annotations
- ❌ Hardcoded constants — extract to module-level variables (e.g., `MAX_FILE_SIZE`)
- ❌ Bare `except:` — always specify exception types

**TypeScript:**
- ❌ Using `any` — prefer proper types or `unknown`
- ❌ Missing prop types for components
- ❌ Inline styles — use `StyleSheet.create()`
- ❌ Mutating state directly — always use `setState`

**General:**
- ❌ No direct payments — always use escrow (when payments implemented)
- ❌ No role blending — keep orderer/deliverer/admin cleanly separated (when auth implemented)
- ❌ No unverified deliveries — photo + GPS proof mandatory (when delivery tracking implemented)

---

## WORKFLOW (CURRENT - OCR ONLY)

```
User takes screenshot of McDonald's app order
  → Upload image via DashboardScreen (React Native)
    → LoadingScreen shows while processing
      → POST /api/ocr with image file
        → Backend: RapidOCR extracts text
          → Backend: receipt_parser.py parses order details
            → Response: order_number, restaurant, items, subtotal, total, is_valid, errors
              → Frontend: FormCorrectionScreen displays parsed data
                → User corrects any OCR mistakes
                  → User confirms order (if is_valid == true)
                    → [PENDING: Order enters queue for delivery]
```

---

## NOTES FOR AGENTS

- **Testing infrastructure**: NOT YET SET UP. No pytest/jest configs. When adding tests, create `tests/` directory and config files first.
- **Linting**: NO LINTERS CONFIGURED. Ruff (Python) and ESLint (TypeScript) need to be added to dependencies and configured.
- **Database**: PostgreSQL planned but NOT YET CONNECTED. Models in `backend/app/models/schemas.py` are Pydantic only (API schemas, not DB models).
- **Auth**: JWT + Firebase Auth planned but NOT YET IMPLEMENTED. No protected routes.
- **Deployment**: No Docker/CI/CD configs yet. GitHub Actions pipeline NOT configured.
- **OCR Gotchas**:
  - RapidOCR (ONNX version of PaddlePaddle) is used instead of original PaddlePaddle
  - Chinese/English mixed receipts require careful regex patterns
  - OCR often mangles section markers (e.g., "訂單詳情" → "訂罩内容")
  - Parser uses fuzzy matching and fallback heuristics
