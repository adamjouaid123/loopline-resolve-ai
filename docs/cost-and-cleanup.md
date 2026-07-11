# Cost and cleanup

## Subscription
- Type: Azure Free Trial (single subscription, "Azure subscription 1")
- Personal spending ceiling for this entire capstone: **$100 USD**, tracked
  manually against the Azure Cost Management view.

## Active resources
- Resource group: `rg-adam.jouaid123-8353` (Sweden Central) — the only
  resource group this project should ever create resources in.
- Foundry project: `adamjouaid123-2390`
- Deployed/planned models: gpt-5-mini (chat/multimodal), text-embedding-3-large
  (embeddings) — see ADR 001 for rationale.

A prior resource group (`rg-adam.jouaid123-4865`, containing an older Foundry
project and two unrelated Bot Service resources) was deleted before this
project began, so it's no longer a cost concern.

## Highest-risk components to watch
- gpt-5-mini / embedding token usage (shared TPM quota, not unlimited)
- Image generation (Dalle/GPT-image-2) — kept off by default, one controlled
  call only
- Sora 2 video generation — preview, optional, off by default
- Free-trial credit expiry (time-limited, not just dollar-limited)

## Cleanup plan
- Delete `rg-adam.jouaid123-8353` (or the whole subscription's resources) when
  the capstone is complete or before the trial credit/window expires.
- Before/after cost screenshots recorded per the guide's hard cost rules.
