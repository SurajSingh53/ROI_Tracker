# 🎯 Influencer ROI Tracker (Streamlit Dashboard)

A sleek, data-driven web dashboard built using **Streamlit** to help marketers, analysts, and brands **track ROI**, **optimize influencer performance**, and decode what truly works in influencer campaigns.

No fluff. Just real insights.

---
### Check it out - https://roitracker.streamlit.app/
## 🔍 Features

- 📈 ROI & Incremental ROAS Calculation  
- 👑 Top Influencer & Persona Identification  
- 🚫 Poor ROI Flagging  
- 🎛️ Filters by Brand, Product, Influencer Type, Platform  
- 📊 Interactive Charts (Bar, Pie, Line)  
- 💡 Smart Data Visuals with Campaign-Level Metrics  

---

## 🗂️ Data Structure

Make sure you have these CSV files ready:

| File              | Description                                           |
|-------------------|-------------------------------------------------------|
| `influencers.csv` | Influencer metadata (Name, Platform, Gender, etc.)   |
| `posts.csv`       | Post-level performance (Reach, Likes, Comments, etc.)|
| `tracking.csv`    | Campaign data (Clicks, Revenue, Orders, etc.)        |
| `payouts.csv`     | Payout data per influencer                           |

> Place all files in a `data/` folder or update the path in `app.py`.

---

## 🚀 Getting Started

### Clone the Repository
```bash
git clone https://github.com/<your-username>/influencer-roi-tracker.git
cd influencer-roi-tracker
