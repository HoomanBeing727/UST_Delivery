# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-27
**Stack:** React Native (Expo) + FastAPI (Python)
**Status:** Early dev (OCR implemented; Auth/Queue pending)

---

## BUILD & RUN COMMANDS

### Backend (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Win: venv\Scripts\activate
pip install -r requirements.txt

# Run Dev Server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testing (Manual Scripts - No pytest yet)
python backend/test_vlm.py    # Test VLM service
python test_ocr.py            # Test OCR (Note: currently broken/needs update)
```

### Frontend (React Native)
```bash
cd frontend
npm install

# Run Dev
npm start                     # Expo Go
npm run android               # Android Emulator
npm run ios                   # iOS Simulator
npm run web                   # Web Browser

# Type Check
npx tsc --noEmit
```

---

## CODE STYLE & CONVENTIONS

### Python (Backend)
- **Imports**: Stdlib → Third-party → Local (`from app.services import ...`)
- **Types**: Python 3.10+ syntax. `list[str]`, `dict[str, Any]`, `float | None`.
  - ❌ NO `from typing import List, Optional`.
- **Naming**: `snake_case` (vars/funcs), `PascalCase` (classes), `UPPER_CASE` (constants).
- **Error Handling**: Raise `HTTPException` in routes. Return `{"errors": []}` in services.
- **Formatting**: 4 spaces indent. No trailing whitespace.

### TypeScript (Frontend)
- **Imports**: React → RN → 3rd-party → Local types → Local components.
- **Types**: Strict mode. Use `interface` for shapes.
  - ❌ Avoid `any` (use `unknown` if needed).
  - ✅ Always type component props: `Props = NativeStackScreenProps<...>`
- **Components**: Functional only. Destructure props.
- **Styles**: `StyleSheet.create()` at bottom of file. ❌ No inline styles.
- **Naming**: `PascalCase` (Components), `camelCase` (funcs/vars).

---

## PROJECT STRUCTURE
```
UST_Delivery/
├── frontend/src/
│   ├── screens/        # Dashboard, FormCorrection
│   ├── types/          # Shared interfaces
│   ├── services/       # API clients
│   └── context/        # React Context
├── backend/app/
│   ├── api/            # Routes (ocr.py)
│   ├── services/       # Logic (ocr_service.py, receipt_parser.py)
│   └── models/         # Pydantic schemas (schemas.py)
├── AGENTS.md           # This file
└── detailed_plan.md    # Architecture docs
```

---

## CRITICAL RULES FOR AGENTS

1. **NO BROKEN CODE**: Do not leave the repo in a broken state. Fix syntax errors immediately.
2. **NO HALLUCINATED DEPENDENCIES**: Do not use `pytest`, `ruff`, or `jest` commands unless you have installed and configured them. They are currently missing.
3. **OCR FLOW**:
   - Frontend sends image → Backend `RapidOCR` → `receipt_parser.py` → JSON response.
   - **Validation**: Check `is_valid` flag. Only HKUST McDonald's receipts allowed.
4. **FILE PATHS**:
   - Backend tests are scripts, not standard pytest suites.
   - `test_ocr.py` is in ROOT, not `backend/`.
5. **ANTI-PATTERNS**:
   - Python: Hardcoded paths/constants (extract them). Bare `except:`.
   - TS: Mutating state directly. Missing prop types.

## DOMAIN CONCEPTS
- **Orderer**: User ordering food.
- **Deliverer**: User picking up food.
- **Escrow**: Holds funds (Not implemented).
- **OCR**: Automated receipt parsing (Implemented).

## WORKFLOW
1. User uploads receipt screenshot.
2. Backend parses items, price, restaurant name.
3. Frontend shows `FormCorrectionScreen`.
4. User verifies/corrects data.
5. Order submitted to queue (Pending).
