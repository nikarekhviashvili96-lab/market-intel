---
id: plan
type: roadmap
title: სამოქმედო გეგმა — ეტაპები, მიმდინარე ეტაპი, backlog
status: living
updated: 2026-10-11
related:
  - "[[intent]]"
  - "[[progress]]"
---

# სამოქმედო გეგმა (roadmap)

ეს არის პროექტის დიდი რუკა: რა ეტაპებად მივდივართ და სად ვართ ახლა. ეტაპები ძრავის სამუშაო ციკლია ([[ADR-0001-foundation-and-sdlc-loop]]); სად ხარ, ყოველი სესიის დასაწყისში და სტატუსის ზოლში ჩანს (🧭, [[ADR-0011-idea-first-stage-conductor]]). კონკრეტული ფუნქციის დეტალური გეგმა ცალკე ფაილია — `docs/plans/PLAN-NNNN-…` ([[docs/plans/README]]) — და მხოლოდ დამტკიცებულ სპეციფიკაციაზე დგება; აგენტის კონკრეტული დავალებები — [[todo]]. ქვემოთ, `auto` მარკერებს შორის ბლოკი ყოველ სესიის დაწყებაზე და ყოველი compact-ის შემდეგ ავტომატურად ეწოდება აგენტს, როგორც სამუშაო მეხსიერება — ამიტომ მოკლე და ზუსტი უნდა იყოს. აახლებს `/session-close`.

<!-- auto: current-phase:start -->
## Current stage: F4 — plan and build (SPEC-0001)

Goal: [[PLAN-0001-foundation-walking-skeleton]] done — every task ticked, every gate green, verifier pass, owner saw the live chart.

- [ ] T1 Python foundation and gates · T2 fixture chart page · T3 live pooler proof
- [ ] T4 schema and access rules · T5 ingest · T6 schedule and staleness
- [ ] T7 site through RLS · T8 browser checks · T9 deploy and live proof
<!-- auto: current-phase:end -->

### F3 — done

- [x] [[ADR-0100-stack-and-hosting]] and [[ADR-0101-data-and-access-model]] accepted (2026-11-15)
- [x] [[PLAN-0001-foundation-walking-skeleton]] approved (2026-11-15)

### F2 — done

- [x] [[intent]] §5 items: SPEC-0001's handled in the spec and `docs/domain/`; the rest go to SPEC-0002 (2026-11-15)
- [x] SPEC-0001 → spec-reviewer (2 rounds) → `/approve spec 0001` (2026-11-15)

### F1 — დასრულებული

- [x] ძრავა დაყენებულია: git, commit-ის შემოწმებები და ხელსაწყოები პირველ სესიაზე თავისით ეწყობა ([[ADR-0011-idea-first-stage-conductor]])
- [x] შენი იდეა — ჩაიწერა [[intent]]-ის §1-ში (2026-11-14)
- [x] `/intent`-ის ინტერვიუ, მერე `/approve intent` (2026-11-14, `bfb67d7`)

## ეტაპები

| ეტაპი | შინაარსი | დასრულების ნიშანი | სტატუსი |
|---|---|---|---|
| F1 | განზრახვა — შენი იდეა და `/intent`-ის ინტერვიუ ([[intent]]) | `/approve intent` | დასრულდა 2026-11-14 |
| F2 | სპეციფიკაცია — SPEC-0001: რა უნდა შეეძლოს პირველ ვერსიას, შემოწმებადი კრიტერიუმებით | spec-reviewer გავლილი → `/approve spec 0001` | done 2026-11-15 |
| F3 | არქიტექტურა — რით აშენდეს: სტეკი, მონაცემები, ჰოსტინგი (პროექტის ADR-ები, ADR-0100-დან) | პროექტის ADR accepted | done 2026-11-15 (ADR-0100, ADR-0101) |
| F4 | გეგმა და აშენება — PLAN-0001, კოდი, კარიბჭეები | ყველა gate მწვანე; verifier: pass; შედეგი ნანახია | current — PLAN-0001 |
| F5 | ჩვენება და პილოტი — ცოცხალი ტესტი, მეტრიკები, შემდეგი ფუნქცია | მეტრიკები მიღწეულია პილოტზე; შენი `/approve live N` | — |
| F6 | გაშვება და დაკვირვება — ცოცხალი შედეგი, საზომები (სპეციფიკაციის §6), ხარჯი, drift, უკუკავშირი → ახალი სპეციფიკაცია ([[ADR-0013-sdlc-loop-2026-upgrade]]) | დაკვირვების რიტმი დგას; ცოცხალი შეცდომა ტესტად ბრუნდება | — |

## Backlog

- ორკესტრაციის ჩართვა პირველ სპეციფიკაციაზე — P-001, [[PROPOSALS]]; II ეტაპი (Fable, GPT და სხვა მოდელები) — მფლობელის გადაწყვეტილებით, ახალი ADR-ით — [[ADR-0005-maker-checker-orchestration]]
- დონე 1 კარიბჭეები სტეკის ADR-თან ერთად — P-002
- GitHub remote + CI, რომ კარიბჭეები ღრუბელშიც გაეშვას — P-003 (remote და CI-ის ჩართვა გაკეთდა 2026-11-14; პირველი მწვანე PR ჯერ მოსალოდნელია)
- Georgia news ფილტრის სიზუსტე (ყოფილი G5) — roadmap v2, [[intent]] §4
- Stop hook-ის გაფართოება პროექტის ტესტებზე — ეტაპ 3–4-ზე, მფლობელის თანხმობით ([[intent]] §5)
- დისპეჩერის ჩართვა კალიბრაციის შემდეგ — P-004, [[ADR-0009-decision-model-dispatcher]]
- პირველი eval-ნაკრები — პირველი სპეციფიკაციის მიღების კრიტერიუმებიდან ([[evals/README]])
- SPEC-0002 — the remaining v1 pages (Overview, Economy US/Georgia, News), owner MFA, an email service only if viewers need self-service reset, page-speed target, old-dashboard replacement rule; remaining [[intent]] §5 items (GDP definition, series IDs, units, Yahoo/Alpha Vantage/NBG/Geostat/news-source terms)
- Stage 6: monthly check that the scheduled job is still enabled (GitHub disables it after 60 days without activity — [[github]])

## მფლობელის გადაწყვეტილებების მოლოდინში

- PLAN-0001 T1: yes to switch on the `lint` and `unit` gates; later owner steps in T3, T5, T7, T9
- წინადადებები → [[PROPOSALS]]
- ძრავის ADR-ები (`scope: engine`) შენგან დამტკიცებას არ ელოდება — [[docs/adr/README]]
