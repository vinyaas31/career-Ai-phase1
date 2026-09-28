# CareerAI — Database ER Design

## Status

Implemented so far (Phase 2): `users`, `user_profiles`.
Everything else below is the **planned** schema — each table gets built and
migrated in the phase that actually needs it, so we never have empty,
untested tables sitting in the database.

Building the full design now (rather than table-by-table with no plan)
means later phases won't require reshaping earlier ones.

## Entity List and Relationships

```
users (1)───(1) user_profiles
users (1)───(M) resumes
resumes (1)───(M) resume_versions
resumes (1)───(M) user_skills ───(M:1) skills
job_roles (1)───(M) job_requirements ───(M:1) skills
users (1)───(M) job_matches ───(M:1) job_roles
job_matches (1)───(M) skill_gaps
users (1)───(M) roadmaps ───(M:1) job_roles
roadmaps (1)───(M) roadmap_items
roadmap_items (1)───(1) roadmap_progress
users (1)───(M) interviews ───(M:1) job_roles
interviews (1)───(M) interview_questions
interview_questions (1)───(1) interview_answers
interviews (1)───(1) interview_reports
resumes (1)───(M) ats_reports
job_roles (1)───(0..1) career_trends
career_trends (1)───(M) career_resources
```

## Table-by-Table Design

### `users` — IMPLEMENTED
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| email | varchar(255) UNIQUE, indexed | login identifier |
| hashed_password | varchar(255) | bcrypt hash, never plaintext |
| is_active | bool | soft-disable without deleting |
| is_admin | bool | gates admin routes (Phase 19) |
| created_at / updated_at | timestamp | |

### `user_profiles` — IMPLEMENTED
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| user_id | UUID FK → users.id, UNIQUE, CASCADE delete | 1:1 with users |
| full_name, phone, education_level | varchar | expanded as needed |
| created_at / updated_at | timestamp | |

### `resumes` — Phase: Resume Upload
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| user_id | UUID FK → users.id | |
| file_path | varchar | storage-abstracted path, not raw bytes in DB |
| original_filename | varchar | |
| parsed_data | JSONB | extracted name/education/skills/etc — flexible schema |
| status | varchar | `uploaded` / `parsed` / `failed` |
| created_at | timestamp | |

### `resume_versions` — Phase: Resume Version Tracker
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| resume_id | UUID FK → resumes.id | |
| version_number | int | |
| target_role_id | UUID FK → job_roles.id, nullable | |
| ats_score | float | snapshot at this version |
| created_at | timestamp | |

### `skills` — Phase: Job Dataset
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| name | varchar UNIQUE | e.g. "Python", "Power BI" |
| category | varchar | "language" / "tool" / "soft-skill" / etc |

### `user_skills` — Phase: Skill Extraction
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| resume_id | UUID FK → resumes.id | |
| skill_id | UUID FK → skills.id | |
| proficiency_source | varchar | "extracted" / "user-confirmed" |

### `job_roles` — Phase: Job Dataset
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| title | varchar | e.g. "Data Analyst" |
| description | text | |
| education_requirement | varchar | |
| experience_level | varchar | |
| is_sample_data | bool | **required** — distinguishes seed data from real data per Rule 16 |

### `job_requirements` — Phase: Job Dataset
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| job_role_id | UUID FK → job_roles.id | |
| skill_id | UUID FK → skills.id | |
| is_required | bool | required vs. optional skill |
| weight | float | used by the scoring engine |

### `job_matches` — Phase: Job Matching / Readiness Engine
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| user_id | UUID FK → users.id | |
| job_role_id | UUID FK → job_roles.id | |
| method | varchar | "keyword" / "tfidf" / "semantic" — supports the research comparison |
| overall_score | float | |
| score_breakdown | JSONB | {technical, projects, experience, education, certifications} — auditable |
| created_at | timestamp | |

### `skill_gaps` — Phase: Skill Gap Engine
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| job_match_id | UUID FK → job_matches.id | |
| skill_id | UUID FK → skills.id | |
| gap_type | varchar | "missing" / "partial" | |

### `roadmaps` / `roadmap_items` / `roadmap_progress` — Phase: Roadmap
| Table | Key columns |
|---|---|
| roadmaps | id, user_id FK, job_role_id FK, created_at |
| roadmap_items | id, roadmap_id FK, phase_order, skill_id FK, description, estimated_hours, difficulty |
| roadmap_progress | id, roadmap_item_id FK, status ("not_started"/"in_progress"/"completed"), updated_at |

### `interviews` / `interview_questions` / `interview_answers` / `interview_reports` — Phase: Interview System
| Table | Key columns |
|---|---|
| interviews | id, user_id FK, job_role_id FK, mode ("text"/"voice"), started_at, finished_at |
| interview_questions | id, interview_id FK, category, difficulty, question_text, order_index |
| interview_answers | id, question_id FK, answer_text, response_time_seconds, filler_word_count |
| interview_reports | id, interview_id FK (unique), overall_score, breakdown JSONB, strengths, weaknesses |

### `ats_reports` — Phase: ATS Analyzer
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| resume_id | UUID FK → resumes.id | |
| job_description_text | text | pasted by user |
| overall_score | float | labelled "ATS Compatibility Score", never "guaranteed ATS score" |
| breakdown | JSONB | keywords/skills/experience/formatting/education |
| created_at | timestamp | |

### `career_trends` / `career_resources` — Phase: Career Intelligence
| Table | Key columns |
|---|---|
| career_trends | id, job_role_id FK, demand_signal_summary, data_source, is_sample_data, last_updated |
| career_resources | id, career_trend_id FK (or roadmap_item_id FK), resource_type, title, url |

## Design Principles Applied Throughout

1. **UUID primary keys everywhere** — avoids sequential-ID enumeration issues and makes merging seed data with real data safe later.
2. **JSONB for AI-output breakdowns** (`score_breakdown`, ATS `breakdown`, interview `breakdown`) — keeps the scoring methodology auditable and inspectable without needing a dozen extra narrow columns.
3. **`is_sample_data` flags** on `job_roles` and `career_trends` — enforces Rule 16 (never silently mix sample data with real data) at the database level, not just in UI copy.
4. **Every FK from a child to `users` cascades on delete** — supports the account-deletion privacy requirement (Section 27) without orphaned rows.
5. **No resume file bytes in the database** — `resumes.file_path` points to the storage abstraction (local disk now, S3-compatible later).
