---
name: quefazeres
description: Work on the Quefazeres Django family task app while preserving its visual language and child and guardian flows.
---

# Quefazeres

Apply this skill when inspecting, implementing, or refining the Quefazeres project.

## Project context

- Quefazeres is a Django app for family chores, child-submitted proof, guardian review, points, and rewards.
- Keep the guardian and child experiences distinct while sharing the same visual language.
- The child interface uses a fixed bottom navigation bar, card-based panels, a blue and green palette, and friendly rounded styling from `static/familia/app.css`.
- Use the existing SVG or image icons; do not use emoji as navigation icons.

## Interface conventions

- For multiple views within a dashboard, follow the child dashboard pattern: one rendered page with a persistent bottom menu that switches visible panels immediately without a page load or opening another browser tab.
- Keep the visible panel synchronized with the URL fragment and browser back/forward history. Choose the appropriate default panel for each role.
- Reuse existing Django routes, forms, models, and family scoping where possible. After form submissions, return to the dashboard and restore the relevant panel.
- Preserve existing role permissions and the other role's flows when changing shared templates or styles.
- Match the existing color palette, spacing, cards, rounded corners, and responsive mobile layout; avoid unrelated redesigns.

## Data and access

- Scope guardian reads and writes to the authenticated guardian's family.
- Deactivate child accounts instead of deleting them when history must remain available; a deactivated account must not be able to sign in.
- Preserve task, proof, redemption, and point history when managing family participants.
- In the guardian dashboard, place pending proof reviews at the top of Análises and the task history beneath them. Keep task history out of the Tarefas panel.

## Validation

- Run `python manage.py check` after Django changes.
- Validate dashboard navigation by selecting each menu and checking fragment synchronization and back/forward behavior.
- Check that child and guardian flows still work after shared navigation or style changes.
