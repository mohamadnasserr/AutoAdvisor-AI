# Tasks - React/Vite Frontend

## Completed

- [x] Create `web-frontend` Vite + React app.
- [x] Add API helper module with `VITE_API_BASE_URL`.
- [x] Integrate AutoAdvisor logo.
- [x] Add premium dark automotive/AI styling.
- [x] Add sticky navbar with backend status.
- [x] Add PRNDS gearbox-themed product navigation.
- [x] Add smooth active gear animation and scroll-aware active state.
- [x] Add Drive chatbot UI.
- [x] Add example prompt buttons.
- [x] Display recommended cars as cards with representative images.
- [x] Add Park inventory explorer.
- [x] Add optional filters from current inventory values.
- [x] Show inventory cards six at a time with Show more / Reset view.
- [x] Add Add to Compare from recommendation and inventory cards.
- [x] Add Neutral comparison workflow from selected cards.
- [x] Keep manual comma-separated comparison fallback.
- [x] Add Rate used-car fair-price form.
- [x] Add image-assisted evaluation flow aligned with the PRNDS product
  navigation.
- [x] Add fair-price estimation from confirmed image details.
- [x] Add similar-car matching from confirmed image details.
- [x] Add uploaded/confirmed profile support in comparison.
- [x] Add Save Interest forms from car cards.
- [x] Add `S - Save` / dealer inquiry draft section.
- [x] Show buyer contact fields and generated inquiry draft after save.
- [x] Keep Streamlit app available as backup.

## Future Work

- [ ] Add lightweight frontend smoke tests if the project adopts a React test
  runner.
- [ ] Add production deployment configuration for the React frontend.
- [ ] Add accessibility pass for keyboard navigation and focus states.

## Verification

- `cd web-frontend && npm run build` -> passes.
- `python -m pytest tests` -> latest full suite passes.
- Manual React demo verified where appropriate.
