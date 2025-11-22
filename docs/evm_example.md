# Earned Value Management (EVM) Example

This document provides an example of how Earned Value Management (EVM) can be applied to track project progress for the SCEMS Multi-Agent System.

## EVM Metrics

### Planned Value (PV)
The budgeted cost of work scheduled to be completed by a given date.

**Example:**
- Total project budget: $50,000
- Week 4 planned completion: 40% of work
- PV = $50,000 × 0.40 = $20,000

### Earned Value (EV)
The budgeted cost of work actually completed by a given date.

**Example:**
- Week 4 actual completion: 35% of work
- EV = $50,000 × 0.35 = $17,500

### Actual Cost (AC)
The actual cost incurred for work completed by a given date.

**Example:**
- Week 4 actual spending: $22,000
- AC = $22,000

## Performance Indices

### Cost Performance Index (CPI)
CPI = EV / AC

**Example:**
- CPI = $17,500 / $22,000 = 0.795
- Interpretation: Project is over budget (CPI < 1.0)

### Schedule Performance Index (SPI)
SPI = EV / PV

**Example:**
- SPI = $17,500 / $20,000 = 0.875
- Interpretation: Project is behind schedule (SPI < 1.0)

## Variance Analysis

### Cost Variance (CV)
CV = EV - AC

**Example:**
- CV = $17,500 - $22,000 = -$4,500
- Interpretation: $4,500 over budget

### Schedule Variance (SV)
SV = EV - PV

**Example:**
- SV = $17,500 - $20,000 = -$2,500
- Interpretation: $2,500 worth of work behind schedule

## Forecasts

### Estimate at Completion (EAC)
EAC = AC + (BAC - EV) / CPI

Where BAC = Budget at Completion

**Example:**
- BAC = $50,000
- EAC = $22,000 + ($50,000 - $17,500) / 0.795 = $62,830
- Interpretation: Project expected to cost $62,830 (over budget)

### Estimate to Complete (ETC)
ETC = EAC - AC

**Example:**
- ETC = $62,830 - $22,000 = $40,830
- Interpretation: $40,830 remaining to complete project

## Application to SCEMS Project

### Phase Breakdown

1. **Phase 1: Design & Planning** (Weeks 1-2)
   - PV: $10,000
   - EV: $10,000 (completed)
   - AC: $9,500
   - Status: On schedule, under budget

2. **Phase 2: Core Development** (Weeks 3-6)
   - PV: $20,000
   - EV: $17,500 (35% complete)
   - AC: $22,000
   - Status: Behind schedule, over budget

3. **Phase 3: Testing & Integration** (Weeks 7-8)
   - PV: $10,000
   - EV: $0 (not started)
   - AC: $0
   - Status: Not started

4. **Phase 4: Deployment & Documentation** (Weeks 9-10)
   - PV: $10,000
   - EV: $0 (not started)
   - AC: $0
   - Status: Not started

### Weekly Tracking

| Week | PV | EV | AC | CPI | SPI | CV | SV |
|------|----|----|----|-----|-----|----|----|
| 1 | $5,000 | $5,000 | $4,800 | 1.04 | 1.00 | $200 | $0 |
| 2 | $10,000 | $10,000 | $9,500 | 1.05 | 1.00 | $500 | $0 |
| 3 | $15,000 | $12,500 | $15,000 | 0.83 | 0.83 | -$2,500 | -$2,500 |
| 4 | $20,000 | $17,500 | $22,000 | 0.80 | 0.88 | -$4,500 | -$2,500 |

## Recommendations

Based on EVM analysis:
1. **Cost Overrun**: Implement cost controls and review resource allocation
2. **Schedule Delay**: Consider adding resources or adjusting scope
3. **CPI < 1.0**: Review development processes for efficiency improvements
4. **SPI < 1.0**: Prioritize critical path activities to recover schedule

## Tools for EVM Tracking

- Microsoft Project with EVM add-ins
- Jira with EVM plugins
- Custom spreadsheets with EVM formulas
- Project management dashboards

## References

- PMI PMBOK Guide - Earned Value Management
- Project Management Institute standards
- Course materials on project cost management

