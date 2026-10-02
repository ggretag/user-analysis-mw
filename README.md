# MW User Activity Analysis Tool

## Overview
This tool performs a deep-dive analysis of user activity logs on the MW platform. It identifies where users spend their most productive time, detects repetitive manual workflows, and uses **Gemini 2.0 Flash Lite** to propose specific AI-driven automation opportunities.

## How It Works
The analysis follows a "Clean Data" pipeline to ensure results reflect actual work rather than idle time:

1.  **Data Ingestion:** Loads logs via **DuckDB** for high-performance SQL processing.
2.  **UI Categorization:** Automatically groups raw URLs (e.g., `/rest/trade/.../details`) into logical functional areas like "Trade Details," "Blotter," or "Compose."
3.  **Active Work Calculation:** Instead of simple session duration, it measures the time gap between every consecutive click.
4.  **Idle Filtering (The 10-Minute Rule):** Discards any gap larger than 10 minutes to filter out "Screen-Left-Open" noise.
5.  **Dynamic AI Reporting:** Sends aggregated statistics to Gemini, which writes a professional, narrative-driven business report.

---

## Why the 10-Minute Cutoff?
Traditional analytics often use a 30-minute session timeout. For building an **AI Digital Assistant**, we use a strict **10-minute threshold** for three critical reasons:

### 1. Accuracy vs. Inflation
A 30-minute threshold is "forgiving"—it captures lunch breaks, phone calls, and background tabs. This inflates the time spent in the UI (e.g., showing 200 hours instead of 90). The 10-minute rule provides the **Clean Truth**: it only measures time when a user is actively "wrestling" with the interface.

### 2. High-Density ROI
AI assistants are most effective when they intervene in high-intensity tasks (e.g., auto-filling a form or summarizing a trade). By using a 10-minute cutoff, we identify the **"Work Bench"** areas where users are clicking rapidly. These are the areas where an AI "Co-pilot" will provide the highest Return on Investment (ROI).

### 3. Actionability
If a user is inactive for 25 minutes, they are likely doing work *outside* the platform (reading physical mail, using Excel, etc.). Since our AI assistant lives *inside* the UI, we should ignore that time. We focus exclusively on the 5-8 minute bursts of intense platform interaction where our AI can actually help.

---

## Outputs
Running `analyze_users.py` generates the following files:

*   **`user_analysis_report.md`**: A professional report written by Gemini identifying power users and AI automation targets.
*   **`heatmap_area_time.png`**: Visualizes which UI areas are "hottest" at specific times of the day.
*   **`heatmap_activity_day_hour.png`**: Visualizes total system load by day of the week.

## Getting Started
### Prerequisites
- Python 3.x
- Libraries: `duckdb`, `pandas`, `matplotlib`, `google-genai`
- Access to Vertex AI (Project: `prj-s-ai-4kdn`)

### Running the Analysis
```bash
python3 analyze_users.py
```
