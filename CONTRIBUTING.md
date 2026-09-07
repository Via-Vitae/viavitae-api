# Contributing to `viavitae-api`

Thank you for improving ViaVitae. This repository follows the organisation-wide
contribution rules.

## Ground rules

- The default branch is protected: no direct pushes, review required, CI green.
- Every change that touches personal data needs a DPIA note
  (`docs/DPIA-template.md`) referenced in the pull request.
- No secrets in the repository. `.github/workflows/compliance-check.yml` runs
  Gitleaks on every push and will fail the build.
- EU data residency is a hard constraint: do not introduce third-party services
  that store or process EU personal data outside the EEA without an ADR.

## Workflow

1. Pick or open an issue; ask for assignment to avoid duplicated work.
2. Branch from `main`: `feat/<issue>-<short-description>`, `fix/<issue>-...`,
   `chore/<issue>-...`, `docs/...`.
3. Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/):
   `feat(assessment): add multilingual funnel step validation`.
4. Keep pull requests small and reversible; prefer expand-contract migrations.
5. Fill in the pull request template. Draft PRs are welcome.

## Definition of done

- [ ] Lint, type check and unit tests pass locally and in CI.
- [ ] New behaviour is covered by tests (unit + at least one e2e path if
      user-visible).
- [ ] Accessibility verified for UI work (WCAG 2.2 AA, `axe` clean).
- [ ] i18n: user-visible strings live in `messages/`, all supported locales
      updated or explicitly marked for translation.
- [ ] Documentation updated (README, `docs/architecture.md`, CHANGELOG).
- [ ] ADR added when the change alters an architectural decision.

## Review

Code owners are defined in `.github/CODEOWNERS`. Reviewers check correctness,
security, data minimisation and maintainability — not style (that is automated).

## Licence of contributions

By submitting a contribution you agree it is provided under the repository
licence (see `LICENSE`) and that you have the right to submit it.
