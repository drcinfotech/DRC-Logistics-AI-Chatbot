# Contributing to Routara

Thanks for your interest in contributing! This project is a demo of conversational AI for the logistics & transportation domain, so contributions are welcome — but **safety-critical code paths have extra rules** that apply on top of the usual code-review.

## Code of conduct

Be kind. Disagree on technical merits, not on people. Maintainers reserve the right to close issues and PRs that violate this.

## Quick start for contributors

```bash
git clone https://github.com/drcinfotech/Logistics-AI-Chatbot.git
cd Logistics-AI-Chatbot

# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pytest -v       # must be 60/60 green before you start

# Frontend
cd ../frontend
npm install
npm run dev
```

## What we accept

✅ **Good contributions:**

- New intents with corresponding tests
- New block renderers in `Blocks.jsx` with corresponding Pydantic models
- New screening patterns (prohibited goods, misdeclaration, privacy) — with both a positive test and a no-false-positive test
- Documentation, README improvements, screenshots
- Accessibility improvements (keyboard nav, ARIA, contrast)
- i18n / localization support
- Tighter test coverage

❌ **What we do NOT accept:**

- Real courier, carrier, or freight-brand trademarks anywhere in the codebase. The CI test `test_no_real_logistics_brands_in_data` will fail your PR.
- Removing or weakening the prohibited-goods / dangerous-goods screening
- Anything that helps conceal, mislabel, or misdeclare shipment contents
- Making the bot reveal another person's address or reroute a parcel that isn't the user's
- Removing or relaxing prompt-injection / social-engineering blocks
- Making pickups or claims actually dispatch/submit (this is a demo)
- Adding personal API keys or credentials
- Code that calls real carrier, customs, or fleet-tracking APIs without explicit opt-in and clear documentation of risks

## Screening-rule changes (require extra review)

Any PR that modifies the following files **must** include test coverage and a written rationale in the PR description:

- `backend/app/safety.py` — shipment screening and social-engineering detection
- `backend/app/chatbot.py` — disclaimer injection and demo-only guards
- `backend/data/*.json` — particularly anything that resembles a real brand

The maintainers will request changes to any screening-weakening PR unless the justification is strong. When in doubt about whether something is a prohibited good, the safe default is to **flag it** — false positives are cheap (we educate the user), false negatives can be dangerous and illegal.

## Style

- Python: PEP 8, type hints on public functions, docstrings on modules
- JS/JSX: 2-space indent, prefer functional components
- Commits: imperative present tense ("Add X", "Fix Y"), not past tense
- One logical change per PR

## Reporting a security issue

For anything that looks like a real security issue (not just a demo limitation), please email the maintainers privately rather than opening a public issue.
