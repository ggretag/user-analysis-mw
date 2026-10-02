import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from google import genai

# --- Configuration ---
CSV_FILE = 'Santanda_20260119-0123.xlsx - Export Worksheet.csv'
REPORT_FILE = 'user_analysis_report.md'
PROJECT_ID = "prj-s-ai-4kdn"
LOCATION = "global"
MODEL_NAME = "gemini-2.0-flash-lite"

class UserActivityAnalyser:
    def __init__(self):
        self.client = genai.Client(
            vertexai=True, 
            project=PROJECT_ID, 
            location=LOCATION
        )
        self.db = duckdb.connect(database=':memory:')

    def prepare_data(self):
        # Load and clean data
        self.db.execute(f"""
            CREATE TABLE raw_data AS 
            SELECT *,
                   strptime(
                       regexp_replace(ACTION_TS, ' (\\d{{2}})\\.(\\d{{2}})\\.(\\d{{2}})\\.(\\d{{6}})\\d{{3}} ', ' \\1:\\2:\\3.\\4 '),
                       '%Y-%m-%d %I:%M:%S.%f %p'
                   ) as ts,
                   USERNAME as user_id,
                   ULH as session_id
            FROM read_csv_auto('{CSV_FILE}')
        """)

        # Categorize
        self.db.execute("""
            CREATE TABLE categorized_actions AS
            SELECT *,
                   CASE 
                       WHEN ACTION LIKE '/rest/blotter%' THEN 'Blotter'
                       WHEN ACTION LIKE '/rest/trade/%/details%' THEN 'Trade Details'
                       WHEN ACTION LIKE '/rest/trade/%/view%' THEN 'Trade View'
                       WHEN ACTION LIKE '/rest/search%' THEN 'Search'
                       WHEN ACTION LIKE '/rest/findtrade%' THEN 'Find Trade'
                       WHEN ACTION LIKE '/rest/compose%' THEN 'Compose'
                       WHEN ACTION LIKE '/rest/actions/%' THEN 'Actions (Pickup/Affirm/etc)'
                       WHEN ACTION LIKE '/rest/dropdown%' THEN 'Dropdown/Form Entry'
                       WHEN ACTION LIKE '/rest/folders%' THEN 'Folders'
                       WHEN ACTION LIKE '/oauth2%' THEN 'Authentication'
                       WHEN ACTION LIKE '/rest/token%' THEN 'Token/Session'
                       ELSE 'Other'
                   END as category
            FROM raw_data
        """)

        # Calculate time (10m cutoff)
        self.db.execute("""
            CREATE TABLE time_spent AS
            WITH ranked AS (
                SELECT *,
                       LEAD(ts) OVER (PARTITION BY session_id ORDER BY ts) as next_ts
                FROM categorized_actions
            )
            SELECT *,
                   date_diff('second', ts, next_ts) as seconds_spent
            FROM ranked
            WHERE next_ts IS NOT NULL AND date_diff('second', ts, next_ts) < 600
        """)

    def get_summary_stats(self):
        stats = {}
        
        # Category Breakdown
        stats['categories'] = self.db.execute("""
            SELECT category, count(*) as action_count, round(sum(seconds_spent)/3600, 2) as hours_spent 
            FROM time_spent GROUP BY 1 ORDER BY hours_spent DESC
        """).df().to_string(index=False)

        # Top Users
        stats['top_users'] = self.db.execute("""
            SELECT user_id, count(*) as actions, round(sum(seconds_spent)/3600, 2) as active_hours
            FROM time_spent GROUP BY 1 ORDER BY actions DESC LIMIT 5
        """).df().to_string(index=False)

        # Repetitive Actions
        stats['repetitive'] = self.db.execute("""
            SELECT category, count(*) as repeat_count
            FROM (
                SELECT category, ts, lag(category) OVER (PARTITION BY session_id ORDER BY ts) as prev_cat
                FROM categorized_actions
            ) WHERE category = prev_cat
            GROUP BY 1 ORDER BY 2 DESC LIMIT 5
        """).df().to_string(index=False)

        return stats

    def generate_plots(self):
        print("Generating labeled heatmaps...")
        # 1. UI Area Heatmap (Time Spent)
        df_heatmap = self.db.execute("""
            SELECT hour(ts) as hour, category, sum(seconds_spent)/3600.0 as hrs 
            FROM time_spent GROUP BY 1, 2
        """).df()
        
        # Ensure all 24 hours are represented
        pivot = df_heatmap.pivot(index='category', columns='hour', values='hrs').fillna(0)
        all_hours = list(range(24))
        pivot = pivot.reindex(columns=all_hours, fill_value=0)

        plt.figure(figsize=(14, 8))
        im = plt.imshow(pivot, cmap='YlOrRd', aspect='auto')
        plt.colorbar(im, label='Active Hours Spent')
        
        # Add labels
        plt.yticks(range(len(pivot.index)), pivot.index)
        plt.xticks(range(24))
        plt.xlabel('Hour of Day (24h)')
        plt.ylabel('UI Area (Category)')
        plt.title('Heatmap: Active Time Spent per UI Area (10m Cutoff)')
        plt.tight_layout()
        plt.savefig('heatmap_area_time.png')
        plt.close()
        
        # 2. Activity Heatmap (Action Count)
        df_act = self.db.execute("""
            SELECT dayofweek(ts) as dw, hour(ts) as hr, count(*) as c 
            FROM raw_data GROUP BY 1, 2
        """).df()
        
        day_map = {0: 'Sun', 1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat'}
        df_act['day_name'] = df_act['dw'].map(day_map)
        
        pivot_act = df_act.pivot(index='day_name', columns='hr', values='c').fillna(0)
        days_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        pivot_act = pivot_act.reindex(index=days_order, columns=all_hours, fill_value=0)

        plt.figure(figsize=(14, 5))
        im_act = plt.imshow(pivot_act, cmap='Blues', aspect='auto')
        plt.colorbar(im_act, label='Action Count (Clicks)')
        
        # Add labels
        plt.yticks(range(len(pivot_act.index)), pivot_act.index)
        plt.xticks(range(24))
        plt.xlabel('Hour of Day (24h)')
        plt.ylabel('Day of Week')
        plt.title('Heatmap: Overall User Activity (Action Volume)')
        plt.tight_layout()
        plt.savefig('heatmap_activity_day_hour.png')
        plt.close()

    def run_analysis(self):
        print("Processing data...")
        self.prepare_data()
        self.generate_plots()
        stats = self.get_summary_stats()

        prompt = f"""
        You are a Senior Product Analyst. Analyze the following user activity data for our client 'Santander' (one week of data).
        The data was processed using a 10-minute inactivity cutoff to ensure we only measure 'Active Work' and exclude idle sessions.

        --- DATA: CATEGORY BREAKDOWN ---
        {stats['categories']}

        --- DATA: TOP USERS ---
        {stats['top_users']}

        --- DATA: REPETITIVE ACTIONS (Candidates for AI Automation) ---
        {stats['repetitive']}

        --- INSTRUCTIONS ---
        1. Generate a professional Markdown report.
        2. REPORT TITLE: 'Santander MW Platform: User Activity & AI Opportunity Report'
        3. Start with an 'Executive Summary' highlighting that 10-minute capping was used for data integrity.
        4. Analyze where time is spent. Note that 'Trade Details' usually dominates.
        5. Identify 'Power Users' vs 'Passive Monitors'.
        6. Propose 3-4 specific AI enhancements for our 'Integrated Digital Assistant' based on the repetitive actions and time sinks.
        7. Use a scientific but actionable tone.
        8. Refer to the existing heatmaps (heatmap_area_time.png and heatmap_activity_day_hour.png) as available evidence.
        9. Include a 'Data Summary Table' at the end.
        """

        print(f"Calling {MODEL_NAME} for dynamic report generation...")
        try:
            response = self.client.models.generate_content(model=MODEL_NAME, contents=prompt)
            with open(REPORT_FILE, 'w') as f:
                f.write(response.text)
            print(f"Analysis complete. Report saved to: {REPORT_FILE}")
        except Exception as e:
            print(f"Error calling Gemini: {e}")

if __name__ == "__main__":
    analyser = UserActivityAnalyser()
    analyser.run_analysis()
