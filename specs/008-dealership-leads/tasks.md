> Renumbered from Spec 009 after inserting Spec 007 Safety Guardrails.

# Tasks - Dealer Inquiry / Save Interest

## Completed

- [x] Define dealership and dealer-lead SQLAlchemy models.
- [x] Define dealer inquiry request/response schemas.
- [x] Add dealer lead request schema.
- [x] Add dealer lead response schema.
- [x] Add optional `customer_name`, `customer_phone`, `customer_email`, and
  `notes` fields.
- [x] Add safe additive migration/startup support for new customer contact
  columns.
- [x] Add dealer lead service.
- [x] Generate safe dealership inquiry draft.
- [x] Create `DealerLead` database record.
- [x] Store customer contact fields when provided.
- [x] Return dealership contact details when available.
- [x] Return lead ID, selected car ID, customer fields, status, and message
  draft.
- [x] Add `/dealer/leads` endpoint.
- [x] Return 404 when selected car does not exist.
- [x] Add focused dealer lead tests.
- [x] Add dealer matching helper for chat requests.
- [x] Match dealer-contact messages to inventory cars.
- [x] Connect `/chat` `dealer_contact` intent to dealer lead creation.
- [x] Create a draft `DealerLead` from chat.
- [x] Return matched dealer information when available.
- [x] Return safe dealership inquiry draft.
- [x] Clearly state that the message was not sent automatically.
- [x] Add chat dealer-contact test.
- [x] Add React Save Interest integration from car cards.
- [x] Add React `S - Save` / dealer draft form.
- [x] Verify full test suite passes.

## Future Work

- [ ] Add authenticated user accounts and saved lead history.
- [ ] Add explicit production sending workflow after user confirmation.
- [ ] Add privacy and redaction audit tests for logs.

## Important Note

- The workflow creates a draft/demo lead only.
- It does not send emails, WhatsApp messages, SMS messages, or contact dealers
  automatically.
- Real sending can be added later as a production upgrade with explicit user
  confirmation.

## Verification

- `python -m pytest tests\test_dealer_leads.py` -> passed.
- `python -m pytest tests\test_recommendation_chat.py tests\test_dealer_leads.py`
  -> passed.
- `python -m pytest tests` -> latest full suite passes.
- `cd web-frontend && npm run build` -> passes.
- Manual React demo verified Save Interest from car cards and the `S - Save`
  section.
