# AutoAdvisor AI Workflow

This document describes the user-facing demo flows for AutoAdvisor AI.

## Buyer Journey

1. Open the React website at `http://localhost:5173`.
2. Start in **D - Drive** and ask the AI assistant for car recommendations.
3. Browse **P - Park** to explore the curated demo inventory.
4. Select cars for **N - Neutral** comparison.
5. Use **R - Rate** to check a used-car fair-price estimate.
6. Use image-assisted evaluation to upload a car photo, confirm details, estimate price, and find similar inventory cars.
7. Use **S - Save** to save buyer interest and generate a dealer inquiry draft.

## Save Interest Journey

1. Choose or enter a car ID.
2. Enter buyer name, phone, email, preferred contact method, location, budget, and notes.
3. Submit the Save Interest form.
4. The backend creates a `DealerLead` draft.
5. No email, WhatsApp message, or dealer contact is sent automatically.

## Dealer Login Journey

1. Open `http://localhost:5173/dealer-dashboard`.
2. Log in with a demo dealer account.
3. The backend authenticates the dealer and issues a JWT token.
4. The dealer dashboard calls `/dealer/me/leads`.
5. The backend derives the dealership ID from the authenticated dealer user and returns only that dealership's leads.

## Recommended Chatbot Prompts

- `I need a reliable used SUV under $15,000 in Beirut`
- `Compare Toyota Corolla and Kia Picanto`
- `Can you show me good used cars between 5000 and 15000?`
- `Show me some used cars more than 10000 price`
- `I want a fast car`
- `Show me a Ferrari`
- `Is a 2018 Hyundai Tucson with 90,000 km for $14,000 fair?`
- `What should I inspect before buying a used car in Lebanon?`
- `Connect me with the dealer for Toyota Corolla`

## Demo Scenario For Presentation

1. Start with the homepage and explain the PRNDS product idea.
2. Ask the chatbot for a used car recommendation.
3. Add a recommended car to compare.
4. Open inventory, filter by make or budget, and add another car to compare.
5. Run a side-by-side comparison.
6. Run a used-car price check.
7. Upload a vehicle image, show safety/quality feedback, confirm details, and find similar cars.
8. Save interest in a car.
9. Open the dealer portal manually and show that the authenticated dealer sees only its own leads.

## Demo-Safe Notes

- Inventory is curated demo data, not live marketplace scraping.
- Images are representative demo visuals, not verified listing photos.
- Dealer messages are drafts only.
- The dealer portal is lightweight demo isolation, not production SaaS tenancy.
