# AutoAdvisor AI Evaluation

This document summarizes how to validate the MVP.

## Automated Backend Tests

Run:

```cmd
cd C:\Users\user\Desktop\AutoAdvisor-AI
.venv\Scripts\activate
set PYTHONPATH=%CD%
python -m pytest tests
```

The suite covers inventory, search, recommendations, comparison, chat memory, intent classification, price estimation, RAG, guardrails, image analysis, similar-car matching, dealer leads, and dealer authentication/isolation.

## React Build

Run:

```cmd
cd C:\Users\user\Desktop\AutoAdvisor-AI\web-frontend
npm run build
```

A successful build confirms the React/Vite frontend compiles.

## Intent Classifier Evaluation

The intent classifier uses labeled examples for:

- `car_recommendation`
- `car_comparison`
- `price_check`
- `image_analysis`
- `dealer_contact`
- `general_advice`

Manual smoke prompts should include recommendation requests, range budgets, minimum budgets, price checks for specific cars, dealer contact requests, and general advice questions.

## RAG Manual Prompts

Use:

- `What should I inspect before buying a used car in Lebanon?`
- `Should I buy new or used?`
- `What documents should I check before buying a car?`

Expected result: advice should be grounded in local sources or state when knowledge is insufficient.

## Price Estimator Limitations

- Used cars only.
- ML model is a baseline and can be calibrated with similar curated inventory.
- Estimates are not guaranteed real market value.
- Production should use verified local transaction data and dealer feeds.

## Dealer Isolation Tests

Validate:

- Dealer login succeeds for seeded demo users.
- Invalid login fails.
- `/dealer/auth/me` returns the authenticated dealer profile.
- `/dealer/me/leads` requires a token.
- A dealer only sees leads connected to its dealership inventory.

## Demo Acceptance Checklist

- Backend health endpoint responds.
- React homepage loads.
- Chatbot returns recommendations.
- Inventory search works.
- Add to Compare works from cards.
- Price check returns fair range and disclaimer.
- Image-assisted evaluation returns safety and quality feedback.
- Save Interest creates a draft lead.
- Dealer portal login works.
- Dealer portal shows only that dealer's leads.
- `python -m pytest tests` passes.
- `npm run build` passes.
