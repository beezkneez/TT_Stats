# TT Stats Dashboard - Documentation

## 📁 Repository Structure

```
TT_Stats/
├── streamlit_app.py          # Main dashboard application
├── requirements.txt           # Python dependencies
├── data/                      # JSON data files (local development)
│   ├── alerts_nq.json
│   ├── alerts_es.json
│   ├── gap_details.json
│   ├── ib_details.json
│   └── single_prints.json
├── scripts/                   # Python scripts for data collection
│   └── supabase_writer_example.py
├── docs/                      # Documentation
│   ├── SUPABASE_SETUP.md     # Supabase integration guide
│   └── README.md             # This file
├── sierra_studies/            # Sierra Chart ACSIL studies
└── .streamlit/                # Streamlit configuration
    └── secrets.toml.example

```

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Dashboard Locally**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Set Up Supabase** (for real-time updates)
   - Follow `docs/SUPABASE_SETUP.md`

## 📊 Dashboard Features

- **Real-Time Alerts** - NQ/ES alerts with sound notifications
- **RTH Gap Statistics** - Overnight gaps relative to ATR
- **Initial Balance** - 9:30-10:30 EST IB tracking with extensions
- **Single Prints** - Active and filled single print analysis
- **Custom Alert Sounds** - Upload your own sounds for each priority level

## 🔧 For Deaner (Data Collection)

Use `scripts/supabase_writer_example.py` to push data from Sierra Chart to Supabase.

See `docs/SUPABASE_SETUP.md` for integration details.
