# Description

<!-- Summarize the change and the motivation. Link related issues, e.g. "Closes #123". -->

## Type of change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that changes existing behavior)
- [ ] Documentation only

## Checklist

- [ ] I have read the [Contributing guide](../docs/CONTRIBUTING.md)
- [ ] Tests pass locally: `docker compose -f docker-compose.test.yml run --rm test`
- [ ] I added or updated tests covering my change
- [ ] I updated documentation (README / docs) where relevant
- [ ] For new or changed sensors: I updated `SENSOR_TYPES` in `const.py`, the coordinator processing, and all translation files (`strings.json` + `translations/*.json`)
- [ ] I updated `release-notes.md`
- [ ] No credentials, OAuth tokens, or personal data are included in this PR

## Testing

<!-- Describe how you verified the change (test output, manual steps, HA version). -->

## Additional notes

<!-- Anything reviewers should know. -->
