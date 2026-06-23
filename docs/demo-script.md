# AutoAdvisor AI Demo Script

This script is designed for a 5 to 7 minute presentation.

## 1. Opening Pitch

"AutoAdvisor AI is a working MVP for AI-powered car discovery, used-car fair-price estimation, image-assisted evaluation, and dealer lead management for Lebanon and the wider MENA market."

"The goal is to make car shopping feel more guided: a buyer can ask natural questions, compare options, check fair price, save interest, and a dealership can log in to see only its own leads."

## 2. Homepage And Product Concept

Open:

```text
http://localhost:5173
```

Point out the PRNDS-inspired navigation:

- P - Park: inventory.
- R - Rate: fair-price check.
- N - Neutral: comparison.
- D - Drive: AI assistant.
- S - Save: save buyer interest.

Mention that the inventory is curated demo data, not live scraping.

## 3. Chatbot Recommendation

Use:

```text
I need a reliable used SUV under $15,000 in Beirut
```

Show:

- Intent-aware chatbot answer.
- Recommended car cards.
- Representative images.
- Advisor overview.
- Add to Compare and Save Interest actions.

## 4. Inventory Search

Open **P - Park**.

Show:

- Optional filters.
- Make/body/fuel/transmission/region dropdowns from inventory.
- Availability filter.
- Six-car display with Show More controls.

Add one car to comparison.

## 5. Comparison

Open **N - Neutral**.

Show:

- Selected cars from recommendations/inventory.
- Compare selected cars.
- Manual car ID fallback.

Explain that comparison supports 2 to 5 cars.

## 6. Fair-Price Check

Open **R - Rate**.

Enter a used-car scenario such as a 2018 Hyundai Tucson.

Show:

- Estimated price.
- Fair range.
- Confidence label.
- Disclaimer.

Explain that the system uses a local ML baseline and inventory calibration when similar cars are available.

## 7. Image-Assisted Evaluation

Upload a car image.

Show:

- Safety and quality feedback.
- Vehicle visibility status.
- Dominant color and body-type hints.
- Technical details hidden by default.

Then confirm structured details and show:

- Fair-price estimate from confirmed details.
- Similar cars from inventory.
- Add uploaded profile to comparison.

Emphasize: AutoAdvisor does not estimate price from image alone.

## 8. Save Interest

Open **S - Save** or click Save Interest on a car card.

Enter buyer contact details:

- Name.
- Phone.
- Email.
- Preferred contact method.
- Location.
- Budget.
- Notes.

Submit and show the generated inquiry draft.

State clearly: no email, WhatsApp, or dealer contact is sent automatically.

## 9. Dealer Login And Isolated Leads

Open manually:

```text
http://localhost:5173/dealer-dashboard
```

Login:

```text
beirut@autoadvisor.demo / demo123
```

Show:

- Dealer profile.
- Leads for that dealership only.

Explain:

"The frontend does not choose the dealership ID. The backend derives it from the authenticated dealer token, then returns only matching leads."

## 10. Closing Architecture Summary

Close with:

"The project combines React, FastAPI, PostgreSQL, Redis, ML models, RAG with pgvector, image guardrails, optional OpenAI response polishing, and lightweight dealer isolation. It is demo-safe: curated inventory, representative images, draft-only dealer messages, and no live scraping claims."
