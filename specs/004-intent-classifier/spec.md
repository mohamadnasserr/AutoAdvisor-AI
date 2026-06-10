# 004 - Intent Classifier

## Goal

Replace or supplement the current keyword router with a small evaluated intent
classifier suitable for a solo junior AI engineering project.

## Planned Scope

- Preserve the current intent labels and rule-based router as a baseline.
- Train a lightweight classifier on manually labeled messages.
- Report accuracy, macro-F1, and common failure cases.
- Keep a deterministic fallback for low-confidence or failed inference.
