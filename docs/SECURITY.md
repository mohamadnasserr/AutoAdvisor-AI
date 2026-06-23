# AutoAdvisor AI Security Notes

AutoAdvisor AI includes lightweight security controls suitable for an MVP demo. These notes describe what is implemented and what would need hardening for production.

## Dealer Authentication

- Dealer users log in with email and password.
- Passwords are stored as hashed values using PBKDF2-HMAC-SHA256.
- Authenticated dealer sessions use signed JWT-style bearer tokens.
- `DEALER_JWT_SECRET` should be set to a strong stable value in `.env` for local demos.

## Demo Credentials

- Demo dealer accounts are fake local accounts created for seeded demo data.
- Public demo credentials should never be reused in production.
- Before production deployment, demo accounts should be changed, disabled, or removed.
- Production should require unique dealer onboarding, strong passwords, secure secret management, HTTPS, and proper account lifecycle management.

## Dealer Lead Isolation

- Authenticated dealers call `/dealer/me/leads`.
- The backend loads the dealer user from the token.
- The backend derives `dealership_id` server-side.
- The frontend cannot choose another dealership ID for authenticated dealer lead access.
- Internal/demo `/dealer/leads` remains available for admin-style local testing.

## Save Interest Safety

- Save Interest creates a dealer inquiry draft only.
- The system does not send email, WhatsApp messages, SMS, or dealer contact automatically.
- Buyer phone, email, and notes are stored for demo lead-management purposes.

## Chat Guardrails

- Text guardrails run before intent classification.
- Empty and too-long messages are blocked.
- Prompt-injection and secret/system-prompt requests receive safe refusal responses.
- The system must not reveal secrets, API keys, system prompts, hidden instructions, or internal configuration.

## Image Upload Safety

- Upload validation checks extension, MIME type, file size, readability, and resolution.
- Image safety checks run before permanent storage or deeper analysis.
- Image quality checks flag blur, brightness problems, and low-detail images.
- The current image flow does not identify people, read license plates, or estimate price from image alone.

## Data And Demo Boundaries

- Inventory is curated demo data, not live scraped marketplace data.
- Representative images are not verified listing photos.
- Price estimates are advisory and not guaranteed market valuations.

## Production Improvements

- Full account lifecycle and password reset flows.
- Stronger password hashing policy and rotation controls.
- HTTPS-only deployment.
- Rate limiting and abuse protection.
- Audit logs for dealer access.
- Real tenant administration and role management.
- Secrets management through a cloud secret store.
- Observability, alerting, backups, and disaster recovery.
- Privacy and retention policies for buyer contact details.
