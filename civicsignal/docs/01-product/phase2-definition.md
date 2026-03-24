# Phase 2 Product Definition

Phase 2 delivers the first end-user product surface on top of the ingestion and signal pipeline.

## Phase 2 Scope

Phase 1 delivered:
- connectors
- ingestion
- change detection
- signal extraction

Phase 2 delivers:
- user interface
- signal browsing
- search
- project tracking
- system health
- admin tools

## User Stories and Acceptance Criteria

### 1) Signals Dashboard

User story:
- As a user, I want to see all newly detected municipal signals so I can quickly understand what government activity has occurred.

Acceptance criteria:
- User can view signals from last 24h and last 7 days.
- User can sort by date and confidence.
- User can filter by city and signal category.
- Each signal card shows: city, meeting body, date, signal type, confidence, summary, source document link.

### 2) Signal Detail Page

User story:
- As a user, I want to see full context of a detected signal so I can verify its meaning.

Acceptance criteria:
- Signal page shows: signal title, signal type, category, confidence, generated summary, meeting date, meeting body, agenda item number, supporting documents.
- Signal page includes text excerpt used for classification.
- User can open agenda packet, staff report, and meeting page.

### 3) Project View

User story:
- As a user, I want related signals grouped into projects so I can track developments across multiple meetings.

Acceptance criteria:
- Project page shows: project name, city, first detected date, latest activity, timeline of signals.
- Timeline includes signal context by meeting body/type/date and allows opening each signal.

### 4) Meetings Browser

User story:
- As a user, I want to browse meetings so I can see agenda activity even if signals were not detected.

Acceptance criteria:
- Meeting page displays: meeting date, meeting body, agenda items, documents, signals detected.
- User can open agenda and staff reports.
- User can search agenda items.

### 5) Document Library

User story:
- As a user, I want to search municipal documents to find specific topics or projects.

Acceptance criteria:
- User can search agenda items, staff reports, documents, meeting titles.
- Filters: city, meeting body, date range, keyword.
- Results show: document title, meeting date, city, snippet preview, link to document.

### 6) Signal Search

User story:
- As a user, I want to search signals by topic so I can quickly find relevant government actions.

Acceptance criteria:
- User can search project name, developer, signal type, keywords.
- Filters: city, category, confidence, date.

## Admin and Internal Tools

### 7) Signal Discovery Mode

User story:
- As an admin, I want to see recurring agenda phrases so I can improve signal taxonomy.

Acceptance criteria:
- Admin page shows top phrases in agenda titles and staff reports.
- Admin page shows common bigrams, trigrams, and entities.
- Phrase list and frequency counts are exportable.

### 8) System Health Dashboard

User story:
- As an operator, I want to monitor scraper health so I can detect failures.

Acceptance criteria:
- Dashboard displays last successful scrape per city, documents downloaded, signals generated, connector errors.
- Status is visible per connector/city as Healthy, Warning, or Failed.

### 9) Connector Dry Run Tool

User story:
- As an engineer, I want to run connectors in dry-run mode so I can validate scraping without modifying production data.

Acceptance criteria:
- Admin UI allows selecting city/date range and running scraper tests.
- Output includes meetings discovered, documents downloaded, signals detected, and errors.

## UI Functional Specification

### Navigation

Main navigation:
- Dashboard
- Signals
- Projects
- Meetings
- Documents
- Search
- Admin

Admin submenu:
- System Health
- Connector Tests
- Signal Discovery
- Taxonomy

### Signals Table

Columns:
- Date
- City
- Body
- Signal Type
- Project
- Confidence
- Documents

Filters:
- City
- Category
- Confidence
- Date
- Keyword

### Dashboard Layout

Sections:
- New Signals (24h)
- Signals by Category
- Signals by City
- Trending Projects

Charts:
- Signals per city
- Signals per category
- Signals per week

### Project Timeline UI

Display fields:
- Timeline position
- Signal type
- Meeting
- Date
- Confidence

### Search UI

Behavior:
- Global search bar with filters.
- Result grouping includes signals, meetings, documents, and projects.

## Phase 2 API Endpoints

Signals:
- GET /signals
- GET /signals/{id}

Projects:
- GET /projects
- GET /projects/{id}

Meetings:
- GET /meetings
- GET /meetings/{id}

Documents:
- GET /documents
- GET /documents/{id}

Admin:
- GET /system-health
- POST /connector-test
- GET /signal-discovery

## Phase 2 Engineering Priorities

- Priority 6 — Signals API
- Priority 7 — Projects grouping service
- Priority 8 — Search index
- Priority 9 — Dashboard UI
- Priority 10 — Admin tools
- Priority 11 — System health UI

## Phase 2 Completion Criteria

Phase 2 is complete when:
- users can view signals
- users can search signals
- users can browse meetings
- users can open documents
- projects group signals correctly
- system health dashboard works
- dry-run harness is accessible via UI

## Strategic Recommendation

Add a signal ranking engine before broad UI rollout to reduce dashboard noise.

Recommended ranking factors:
- development size
- contract value
- signal category importance
- confidence score
- recency
