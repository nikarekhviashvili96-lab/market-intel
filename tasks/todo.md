---
id: todo
type: memory
title: დავალებები — რას ვაკეთებ ახლა, რა მოდის შემდეგ, რა გელოდება შენ
status: living
related:
  - "[[plan]]"
  - "[[progress]]"
  - "[[PROPOSALS]]"
---

# დავალებები (tasks/todo.md)

ეს არის აგენტის კონკრეტული სამუშაო სია — ის, რასაც ახლა ვაკეთებ და რასაც შემდეგ გავაკეთებ, ნაბიჯ-ნაბიჯ. [[plan]] დიდი რუკაა (ეტაპები), [[progress]] — სად ვართ, `docs/plans/PLAN-NNNN` — ერთი ფუნქციის დამტკიცებული გეგმა, [[PROPOSALS]] — იდეები, რომლებიც შენს „კის" ელოდება. აქ კი წერია ყოველი დავალება, რომელიც უკვე გადაწყვეტილია და შესასრულებელია. `<!-- auto -->` ბლოკი ყოველ სესიის დაწყებაზე და ყოველი compact-ის შემდეგ ავტომატურად ეწოდება აგენტს, რომ მეხსიერების შეკუმშვის შემდეგაც იცოდეს, რას აკეთებდა.

წესები (`tasks` gate — მანქანური შემოწმება — ამოწმებს 1-ს და 3-ს):

1. ყოველ დავალებას აქვს ნომერი `D-NNN`, რომელიც არასდროს მეორდება; ახალი ნომერი = ამ ფაილში ყველაზე დიდი + 1 (L-011).
2. ფორმა: `- [ ] D-NNN — რა (წყარო) — verify: როგორ გავიგებთ, რომ შესრულდა`. წყარო: შენი მოთხოვნა თარიღით, `PLAN-NNNN T3` ან `P-NNN`. ფუნქციის ამოცანის ტექსტი თავის PLAN-შია — აქ მხოლოდ ბმული და მდგომარეობა.
3. მონიშვნა `[x]` მხოლოდ ქვითრით: ხაზი მთავრდება `✓ YYYY-MM-DD · <commit | მფლობელი | ფაილი>`; commit-ის ნომერი ნამდვილად უნდა არსებობდეს.
4. სამზე მეტი ნაბიჯის სამუშაო ჯერ აქ იწერება; თუ დიდია ან ორაზროვანი — ჯერ შენ გაჩვენებ.
5. რასაც მხოლოდ შენ აკეთებ ან წყვეტ, დგას „შენ გელოდება"-ში, ზუსტი ბრძანებით ან კითხვით.
6. `/session-close` ამ ფაილს ასწორებს: დასრულებულს ქვემოთ გადაიტანს, 14 დღეზე ძველს წაშლის (ისტორია git-სა და ეპიზოდებშია).

<!-- auto: todo-now:start -->
## ახლა

- Stage 4/6 — build PLAN-0001 in batches (B1, B2a, B2b, B3, B4 — PLAN-0001 deviations), one branch and PR per batch, each merged before the next.

## შემდეგი

- [ ] D-008 — B1 = PLAN-0001 T2 (PLAN-0001 deviations) — verify: T2's verify line; PR merged after green `gates`
- [ ] D-010 — B2a = PLAN-0001 T3 alone, after the owner's B2 checklist (D-015) (PLAN-0001 deviations) — verify: T3's verify line; PR merged
- [ ] D-011 — B2b = PLAN-0001 T4 + T5 (PLAN-0001 deviations) — verify: T4's and T5's verify lines; PR merged
- [ ] D-012 — B3 = PLAN-0001 T6 + T7 + T8 (PLAN-0001 deviations) — verify: their verify lines; PR merged
- [ ] D-013 — B4 = PLAN-0001 T9 (PLAN-0001 deviations) — verify: T9's verify line; verifier `VERDICT: pass`
<!-- auto: todo-now:end -->

## შენ გელოდება

- [ ] D-015 — the B2 checklist: Supabase project, sign-up off and 12-character passwords, `ingest_writer` login, access token, new FRED key and the old one revoked, four GitHub secrets, the project ref told to the agent (owner, 2026-11-15) — verify: the agent sees the four secret names in `gh secret list`

- [ ] D-006 — Claude Code-ის გადატვირთვა: ქვედა ზოლზე „auto mode on" აღარ უნდა ჩანდეს; თუ ჩანს — `Shift+Tab` ან `claude --permission-mode default` — verify: ზოლზე default რეჟიმი

## დასრულებული

- [x] D-009 — push `chore/session-close-2026-11-15` and merge its PR (owner, 2026-11-15) — PR #6 merged ✓ 2026-11-15 · 0817545
- [x] D-014 — `gh auth login` in the browser (P-010, the owner's step) ✓ 2026-11-15 · owner

- [x] D-007 — PLAN-0001 T1 on `feat/t1-python-foundation` (PLAN-0001 T1) — PR #8 merged ✓ 2026-11-15 · 86d0e36

- [x] D-003 — intent §5 items for SPEC-0001 decided or verified in the spec and `docs/domain/`; the rest moved to SPEC-0002 ✓ 2026-11-15 · 705f148
- [x] D-004 — `/spec` → SPEC-0001, spec-reviewer two rounds, `/approve spec 0001` ✓ 2026-11-15 · 7700717
- [x] D-005 — PR `feat/intent` merged after green `gates` (PR #3) ✓ 2026-11-15 · c83e57f
- [x] D-001 — `/intent`: იდეა [[intent]]-ის §1-ში, ინტერვიუ, მშენებლის შემოწმება ✓ 2026-11-14 · 4856f3a
- [x] D-002 — მფლობელის იდეა და `/approve intent` ✓ 2026-11-14 · მფლობელი
