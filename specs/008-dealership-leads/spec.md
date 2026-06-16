> Renumbered from Spec 009 after inserting Spec 007 Safety Guardrails.

# 008 - Dealer Inquiry / Save Interest

## Goal

Allow a buyer to save interest in a selected inventory car and generate/store a
safe dealer inquiry draft. The system must not contact dealers automatically.

## Current State

- `/dealer/leads` creates a draft `DealerLead` record.
- Chat dealer-contact intent can match a request to an inventory car and create
  a draft lead.
- The React/Vite frontend exposes Save Interest from car cards and from the
  `S - Save` section.
- Save Interest accepts optional customer contact fields:
  `customer_name`, `customer_phone`, `customer_email`, and `notes`.
- Responses include lead ID, selected car ID, customer contact fields,
  dealership details when available, status, and generated inquiry draft.
- Existing local PostgreSQL databases are handled with safe additive columns;
  no destructive reset is required.

## Requirements

- Use the existing dealership and dealer-lead database models.
- Store only draft lead data.
- Never send email, WhatsApp, SMS, or dealer contact automatically.
- Make no claim that a dealer has received or confirmed the inquiry.
- Return dealership contact details when available from the curated demo
  inventory.
- Keep safe user-facing wording: buyer interest is saved as a draft/demo lead.
- Redact contact details from logs where possible.

## Acceptance Criteria

- Creating a dealer lead with only `selected_car_id` works.
- Creating a dealer lead with customer name, phone, email, and notes works.
- Response includes customer contact fields.
- Missing car IDs return 404.
- Chat dealer-contact requests create a draft lead only.
- React Save Interest form submits to `/dealer/leads`.
- User-facing copy clearly states that no message is sent automatically.
