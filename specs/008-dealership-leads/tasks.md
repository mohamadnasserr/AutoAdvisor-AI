> Renumbered from Spec 009 after inserting Spec 007 Safety Guardrails.

# Tasks - Dealer Inquiry / Lead Capture

- [x] Define dealership and dealer-lead SQLAlchemy models.
- [x] Define dealer inquiry request/response schemas.
- [x] Add dealer lead request schema.
- [x] Add dealer lead response schema.
- [x] Add dealer lead service.
- [x] Generate safe dealership inquiry draft.
- [x] Create `DealerLead` database record.
- [x] Return dealership contact details when available.
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
- [x] Verify full test suite passes.
- [ ] Add real user-confirmation and sending workflow.
- [ ] Add privacy and no-auto-send tests.

## Important Note

- The workflow creates a draft/demo lead only.
- It does not send emails, WhatsApp messages, or contact dealers automatically.
- User confirmation and real sending can be added later as a production
  upgrade.

## Verification

- `python -m pytest tests\test_dealer_leads.py` -> 2 passed.
- `python -m pytest tests\test_recommendation_chat.py tests\test_dealer_leads.py`
  -> 12 passed.
- `python -m pytest tests` -> 60 passed.
