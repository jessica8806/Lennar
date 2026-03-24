# CivicSignal Product Requirements (PRD)

This document captures **user requirements** (what users need and why). Engineering implementation details live in `docs/02-architecture/functional-spec.md`.

## Product Objective
Provide a system that automatically monitors municipal meeting activity across cities and surfaces actionable signals related to development, zoning, infrastructure, procurement, and policy changes.

CivicSignal should reduce municipal monitoring effort from hours of manual research to minutes of review.

## Target Users
### Primary users
- Real estate developers: track development approvals and zoning changes
- Homebuilders: monitor land-use policy and competing development activity
- Investors: identify infrastructure investment and growth patterns
- Government affairs teams: track ordinances and regulatory changes
- Consulting firms: monitor public procurement and infrastructure projects

## User Problems
Current workflows require users to:
- manually search multiple city websites
- read long and inconsistent agenda packets
- monitor planning commission outcomes across cities
- discover relevant signals too late

Top pain points:
- too many cities to monitor
- signals buried in staff reports
- vague agenda titles
- difficult project tracking across meetings

## Core User Capabilities
### 1) Monitor government signals
Users can view newly detected signals and filter by:
- city
- category
- date
- confidence
- keyword

### 2) Identify development activity
Users can detect:
- new development proposals
- project approvals
- zoning amendments
- planning commission decisions

Each signal links to agenda item, staff report, and source documents.

### 3) Track projects over time
Users can access grouped project timelines combining related actions across Planning Commission and City Council meetings.

### 4) Search municipal documents
Users can search:
- agenda items
- staff reports
- meeting titles
- ingested documents

Search filters:
- city
- meeting body
- date range
- category

### 5) Access meeting records
Users can view:
- meeting date
- agenda
- agenda items
- documents
- detected signals

### 6) Monitor changes
Users are alerted when:
- agenda updated
- agenda item added/changed
- documents changed

### 7) Discover trends
Users can view trends such as:
- development activity by city
- category growth over time
- recent infrastructure projects

## Signal Taxonomy
Signals must be classified into exactly one primary category:
1. Housing / Development
2. Zoning / Land Use
3. Capital Projects
4. Infrastructure / Utilities
5. Procurement / Contracts
6. Finance / Bonds
7. Fees / Taxes
8. Policy / Ordinances
9. Public Safety
10. Parks / Recreation
11. Legal / Litigation
12. Personnel / HR

## Signal Confidence
Each signal includes one confidence value:
- High
- Medium
- Low

## Default User Experience
Default landing experience is the Signals Dashboard showing:
- new signals detected
- signals by city
- signals by category
- trending projects

## Data Freshness and Scope
- Refresh cadence: Daily
- Phase 1 geography: 10 Orange County cities
- Historical access: 12 months of meeting history

## Success Metrics
Product is successful when users:
- discover important municipal signals earlier
- monitor more cities with less effort
- rely on CivicSignal as a recurring intelligence workflow
