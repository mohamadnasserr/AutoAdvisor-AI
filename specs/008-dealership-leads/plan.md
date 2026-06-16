> Renumbered from Spec 009 after inserting Spec 007 Safety Guardrails.

# Plan - Dealer Inquiry / Save Interest

## Implementation Approach

1. Keep dealer matching and draft generation in the backend service layer.
2. Accept optional buyer contact fields on `DealerLeadCreateRequest`.
3. Store `customer_name`, `customer_phone`, `customer_email`, and `notes` when
   provided.
4. Preserve the existing generated inquiry draft and `draft_created` style
   status.
5. Add additive migration/startup safety for existing local databases using
   `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`.
6. Keep `/dealer/leads` as the single draft creation API.
7. Keep chat dealer-contact intent connected to draft creation.
8. Add React Save Interest forms on car cards and in the `S - Save` section.
9. Display success results with lead ID, car ID, buyer contact fields, dealer
   details, and inquiry draft.

## Non-Goals

- No authentication or user registration in this MVP.
- No real email, WhatsApp, SMS, CRM, or dealer integration.
- No automatic dealer contact.

## Validation

- Dealer lead API tests cover basic draft creation and missing car ID.
- Save Interest tests cover customer name, phone, email, and notes.
- Recommendation chat tests cover dealer-contact draft behavior.
- Manual React demo verifies Save Interest from car cards and the Save section.
