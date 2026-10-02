# User Activity Analysis Report - Santander (One Week)

## Executive Summary
This report analyzes user activity data for the client "Santander" over a one-week period in January 2026. The goal is to identify high-usage areas, repetitive manual tasks, and opportunities for AI-driven automation.

---

## 1. Where Users Spend the Most Time
The "time spent" was calculated by measuring the interval between consecutive actions within a session (capping gaps at 30 minutes to exclude idle time).

| category | count | hours_spent |
| --- | --- | --- |
| Trade Details | 13426 | 201.57638888888889 |
| Folders | 1182 | 38.87388888888889 |
| Blotter | 1394 | 33.05388888888889 |
| Actions (Pickup/Affirm/etc) | 1973 | 28.68027777777778 |
| Token/Session | 575 | 27.145 |
| Search | 2399 | 25.09027777777778 |
| Other | 1294 | 9.458333333333334 |
| Trade View | 3351 | 8.438055555555556 |
| Compose | 2395 | 7.401111111111111 |
| Dropdown/Form Entry | 1790 | 2.805277777777778 |
| Find Trade | 879 | 2.293888888888889 |

**Insight:** Users spend a disproportionate amount of time interacting with **Trade Details**. This indicates that the core workflow involves extensive inspection, modification, or verification of individual trades.

---

## 2. Heat Charts (Peak Activity)
Two heat maps were generated to visualize the data:
- **heatmap_area_time.png**: Shows total hours spent per UI area across different hours of the day.
- **heatmap_activity_day_hour.png**: Visualizes overall system load (action count) by day of the week and hour.

---

## 3. Repetitive UI Patterns
There is a high volume of repetitive actions, which are prime candidates for AI-driven efficiency gains:

### Top Repetitive Categories:
| category | repeat_count |
| --- | --- |
| Trade Details | 8346 |
| Search | 1622 |
| Trade View | 1114 |
| Folders | 785 |
| Blotter | 671 |

---

## 4. AI Opportunities to "Make Life Easier"

### A. AI Trade Summarization (High Impact)
Since users spend most of their time in **Trade Details**, the assistant could provide a proactive "TL;DR" when a trade is opened, flagging discrepancies or missing mandatory fields.

### B. Predictive Search & Filtering
AI can learn the most common search patterns for specific users or roles and suggest "Smart Filters" to reduce manual searching friction.

### C. Automated Form Filling in 'Compose'
With significant 'Compose' actions, the assistant could predict field values (like Book ID or Counterparty) based on historical preferences or current session context.

### D. Bulk Action Recommendations
Detect patterns in manual 'Pickup' or 'Affirm' actions. If a user is manually processing a series of similar trades, offer a one-click "Batch Process" option.

---

## 5. Supporting Files
- `analyze_users.py`: Python/DuckDB analysis script.
- `heatmap_area_time.png`: UI Area vs. Hour heatmap.
- `heatmap_activity_day_hour.png`: Day vs. Hour activity heatmap.
- `Santanda_20260119-0123.xlsx - Export Worksheet.csv`: Raw data source.
