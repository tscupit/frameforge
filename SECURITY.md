# Security policy

## Reporting a vulnerability

Please do not open a public issue for security problems. For this fork, contact the repository maintainer privately through an agreed secure channel. Do not post vulnerability details in a public issue. The upstream project's contact address is not the security contact for FrameForge.

## Keeping your keys safe

- API keys live in `.env`, and the YouTube tokens in `credentials.json` and `token.json`. All three are in `.gitignore`; never commit or share them.
- The Studio dashboard listens on `127.0.0.1` and every action needs a per-session token. Do not expose it on a public network with `--host 0.0.0.0`.
- If a key has leaked, revoke it with the provider and create a new one.
