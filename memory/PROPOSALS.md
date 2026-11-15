---
id: proposals
type: memory
title: წინადადებები — რას სჭირდება მფლობელის გადაწყვეტილება
status: living
---

# წინადადებები (prospective memory)

აგენტი აქ წერს იდეებს, რომლებსაც მფლობელის გადაწყვეტილება სჭირდება: ახალი skill, gate, ADR, ინსტრუმენტის დაყენება, პროცესის ცვლილება. **არაფერი სრულდება თანხმობამდე.** პასუხი ჩვეულებრივად: „P-001 — კი" ან „არა".

ქვემოთ მოცემული წინადადებები ძრავასთან ერთად მოვიდა: ეს ის შესაძლებლობებია, რომლებიც ძრავში ჩადებულია, მაგრამ ჩართვამდე შენს გადაწყვეტილებას ელოდება.

## ღია

- [ ] **P-001** ორკესტრაციის ჩართვა პირველი სპეციფიკაციის დამტკიცებისას (`orchestration/config.toml` → `enabled = true`). წინაპირობა: I ეტაპის კოდი (მხოლოდ Claude-ის მოდელები) ჯერ დასაწერია — დღეს `config.toml`-ში წინა ვერსიაა (Fable ↔ ChatGPT Astra, Opus ↔ ChatGPT Sol), რომელსაც Codex CLI და ChatGPT-ის ანგარიში სჭირდება — [[ADR-0005-maker-checker-orchestration]]
- [ ] **P-002** დონე 1 კარიბჭეები (`ruff` + `pytest`) სტეკის ADR-თან ერთად — საჭიროა `ruff`-ის დაყენება — [[ADR-0006-deterministic-gates-and-evals]]
- [ ] **P-003** GitHub remote + CI: კარიბჭეები ღრუბელშიც, ყოველ push-სა და PR-ზე (GitHub Actions) — [[ADR-0006-deterministic-gates-and-evals]]
- [ ] **P-004** დისპეჩერის ჩართვა (`[decision] enabled = true`): წინაპირობა — `orchestration/decide.py` ჯერ დასაწერია, მერე კალიბრაცია (~30 ნიმუში დავალება) და `OPENROUTER_API_KEY` `.env`-ში — [[ADR-0009-decision-model-dispatcher]]
- [ ] **P-005** Haiku 5.5-ის ქართულის და კითხვა-შეჯამების ხარისხის გაზომვა, სანამ ის ასეთ საქმეს აიღებს: 10–20 დავალება ცნობილი პასუხით, Haiku vs Sonnet, სიზუსტე და ფასი — [[evals/README]], [[LESSONS]] L-006
- [ ] **P-006** შეტყობინება, როცა ნებართვის მოთხოვნა გელოდება: Claude Code-ის `Notification` hook-ი (ეშვება, როცა აგენტს შენი ნებართვა სჭირდება) გამოგიგზავნის Windows-ის შეტყობინებას ან Telegram-ს — საათზე გრძელი მოლოდინი ქეშს აცივებს — [[ADR-0010-prompt-cache-and-cost]]
- [ ] **P-007** gate.py-მ drill-ის დაწყებისას ერთი პროგრესის ხაზი დაბეჭდოს, რადგან ~5 წუთი ჩუმად მუშაობა გაჭედვას ჰგავს _(ავტო, [[EP-2026-11-14-d9d82856]] — მფლობელის გადასაწყვეტი)_
- [x] **P-008** main-ის დაცვა GitHub ruleset-ით (restrict deletions, block force pushes, require PR, require status check `gates`) _(ავტო, [[EP-2026-11-14-d9d82856]] — მფლობელის გადასაწყვეტი)_ — გაკეთდა 2026-11-14: მფლობელმა შექმნა ruleset `main-protection` ([[EP-2026-11-14-97f500f5]])
- [ ] **P-009** guard-ის 20 წამიანი timeout დატვირთულ მანქანაზე (ფონზე მიმდინარე drill) ყოველ Edit/Bash-ს ბლოკავს (`onFailure: block`) — 2026-11-14-ს ზედიზედ 4-ჯერ; ვარიანტი: commit-ის gate ფონზე არ გავუშვათ სხვა სამუშაოსთან ერთად, ან guard-ის timeout გაიზარდოს (harness — მხოლოდ მფლობელის „კი"-თ) — [[ADR-0004-harness-permissions-hooks-guard]], [[EP-2026-11-14-97f500f5]]
- [ ] **P-010** Log in the GitHub CLI once (`! gh auth login`, the owner's own step) so the agent can open PRs instead of handing over compare links — four PRs on 2026-11-15 needed the manual step ([[EP-2026-11-15-519db0a3]]) — owner, 2026-11-15: later; then yes the same day — the owner logs in, the agent opens PRs and reads CI, `gh pr merge` asks (`.claude/settings.json`), only the owner merges
- [x] **P-011** The engine's skills (`/spec`, `/approve`, `/session-close`, builder check) still tell the agent to speak and write Georgian; align them with the owner's language rule in `CLAUDE.md` (2026-11-15) — harness change, only with the owner's yes ([[EP-2026-11-15-519db0a3]]) — done 2026-11-15 on the owner's yes: skills, `spec-reviewer` and two rules now point at `CLAUDE.md` → Language; hooks (`episodic.py`, `sentinel.py`, `firstrun.py`) still write Georgian — not in scope (session EP-2026-11-15-876bc843)
<!-- auto: proposals:end -->

## გადაწყვეტილი
