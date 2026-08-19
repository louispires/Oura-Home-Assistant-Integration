# Security Policy

## Supported Versions

This is a Home Assistant custom integration distributed via HACS. Security
fixes are applied to the latest released version only. Please make sure you are
running the most recent release before reporting a vulnerability.

| Version        | Supported          |
| -------------- | ------------------ |
| Latest release | :white_check_mark: |
| Older releases | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, report them privately using GitHub's built-in private vulnerability
reporting:

1. Go to the repository's **Security** tab.
2. Click **Report a vulnerability**.
3. Provide a description of the issue, steps to reproduce, and any relevant
   logs (with credentials and tokens redacted).

If private reporting is unavailable to you, open a minimal public issue asking a
maintainer to contact you, without disclosing vulnerability details.

### What to include

- A clear description of the vulnerability and its potential impact.
- Steps to reproduce or a proof of concept.
- The integration version, Home Assistant version, and installation method.
- Any relevant logs — **redact OAuth tokens, client secrets, and personal data**.

### What to expect

- Acknowledgement of your report as soon as reasonably possible.
- An assessment of the report and a plan for a fix if the issue is confirmed.
- Coordinated disclosure once a fix is released.

## Scope

This policy covers the integration code in this repository. Vulnerabilities in
Home Assistant core, HACS, or the Oura API itself should be reported to their
respective projects.

## Handling of Credentials and Personal Data

This integration stores OAuth tokens and Oura health data locally in your Home
Assistant instance. Never share tokens, client secrets, or unredacted logs in
public issues or pull requests.
