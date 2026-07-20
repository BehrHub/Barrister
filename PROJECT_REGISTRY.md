# Canonical Project Registry

Verified from the Mac mini project and running-port audit on 2026-07-19.

| Port | Project folder | Canonical role | Git |
|---:|---|---|---|
| 8088 | `~/Documents/BarristerCloud` | Production Barrister dashboard | `https://github.com/BehrHub/Barrister.git` |
| 8501 | `~/Documents/CareerDashboard` | Development/test clone of the Barrister dashboard | No repository |
| 8020 | `~/Documents/Bronx-3D-Transition` | Transition laboratory and animation experiences | No repository |
| 8011 | `~/Documents/Heroes-Muses-Library` | Heroes & Muses static site | No repository |
| 9000 | `~/Documents/Family-Legacy-Archive` | Family Showcase static site | No repository |
| 8000 | Folder not yet verified | Bronx Daily active server | Unknown |

## Unassigned or legacy folders

These folders exist but are not assigned verified active dashboard ports:

- `~/Documents/BarristerEngine`
- `~/Documents/ticket_processor_test`
- `~/Documents/bronx`
- `~/Documents/Codex`

Inspect them before use. Never infer their purpose or port from the folder name.

## Operating rules

- Verify a listening process's working directory before modifying a port.
- 8088 production changes belong in `BarristerCloud`.
- 8501 experiments and tests belong in `CareerDashboard`.
- Do not modify production while testing on 8501.
- Search project roots directly; prune backups, caches, environments, and Git metadata.
