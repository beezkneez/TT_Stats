# Supabase Setup Guide

## 📋 Overview

This dashboard uses **Supabase** (PostgreSQL database) for real-time data updates instead of JSON files. This allows instant updates from your trading PC to the dashboard without pushing to GitHub.

---

## 🚀 Step 1: Create Supabase Account

1. Go to https://supabase.com
2. Click **"Start your project"**
3. Sign up with GitHub or email
4. Create a new project:
   - Organization: `Trading Stats`
   - Project name: `tt-stats`
   - Database password: **SAVE THIS!**
   - Region: Choose closest (US East/West)
   - Click **"Create new project"** (takes 1-2 minutes)

---

## 📊 Step 2: Create Database Tables

Once your project is ready:

1. Click **"SQL Editor"** in left sidebar
2. Paste this SQL code:

```sql
-- Table for NQ Alerts
CREATE TABLE alerts_nq (
  id BIGSERIAL PRIMARY KEY,
  data JSONB NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for ES Alerts
CREATE TABLE alerts_es (
  id BIGSERIAL PRIMARY KEY,
  data JSONB NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for Gap Details
CREATE TABLE gap_details (
  id BIGSERIAL PRIMARY KEY,
  data JSONB NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for IB Details
CREATE TABLE ib_details (
  id BIGSERIAL PRIMARY KEY,
  data JSONB NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for Single Prints
CREATE TABLE single_prints (
  id BIGSERIAL PRIMARY KEY,
  data JSONB NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for Market Environment
CREATE TABLE market_environment (
  id BIGSERIAL PRIMARY KEY,
  data JSONB NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for Risk Assessment
CREATE TABLE risk_assessment (
  id BIGSERIAL PRIMARY KEY,
  data JSONB NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert initial empty data
INSERT INTO alerts_nq (id, data) VALUES (1, '[]'::jsonb);
INSERT INTO alerts_es (id, data) VALUES (1, '[]'::jsonb);
INSERT INTO gap_details (id, data) VALUES (1, '[]'::jsonb);
INSERT INTO ib_details (id, data) VALUES (1, '[]'::jsonb);
INSERT INTO single_prints (id, data) VALUES (1, '[]'::jsonb);
INSERT INTO market_environment (id, data) VALUES (1, '{}'::jsonb);
INSERT INTO risk_assessment (id, data) VALUES (1, '{}'::jsonb);
```

3. Click **"Run"**
4. Verify: "Success. No rows returned"

---

## 🔑 Step 3: Get API Keys

1. Click **"Settings"** (gear icon)
2. Click **"API"**
3. Copy these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: Long string starting with `eyJ...`

---

## ⚙️ Step 4: Configure Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click on your app **"tt-stats"**
3. Click **"Settings"** (⚙️)
4. Click **"Secrets"**
5. Paste this (replace with your actual values):

```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "your-actual-anon-key-here"
```

6. Click **"Save"**
7. Your app will automatically restart

---

## 💻 Step 5: Configure Local Development (Optional)

If testing locally:

1. Create file: `.streamlit/secrets.toml`
2. Copy from `.streamlit/secrets.toml.example`
3. Fill in your actual Supabase URL and key
4. **DO NOT commit this file to GitHub!** (it's in `.gitignore`)

---

## 🐍 Step 6: Install Python Package on Trading PC

On your trading PC (where Sierra Chart runs):

```bash
pip install supabase
```

---

## 📝 Step 7: Write Data from Sierra Chart/Python

Use the example script: `python_scripts/supabase_writer_example.py`

### Quick Example:

```python
from supabase import create_client

# Initialize once
supabase = create_client("YOUR_URL", "YOUR_KEY")

# Update NQ alerts (call this every second/minute)
alerts = [
    {
        "timestamp": "2025-10-25T14:35:22",
        "symbol": "NQ",
        "type": "IB Extension",
        "priority": "critical",
        "message": "30% IB extension reached",
        "price": 20565.00
    }
]

supabase.table('alerts_nq').upsert({
    'id': 1,
    'data': alerts
}).execute()
```

---

## 🔄 How Real-Time Updates Work

1. **Sierra Chart** → Python script → **Supabase** (every second)
2. **Streamlit Dashboard** → Reads from **Supabase** (every 1-5 seconds via cache)
3. **Users** see updated data instantly!

### Update Frequency:
- **Alerts**: 1 second cache (near real-time)
- **Gap/IB/Single Prints**: 5 second cache

---

## ✅ Verify It's Working

1. Run the example script: `python supabase_writer_example.py`
2. Check your Streamlit dashboard
3. You should see the test alert appear!

---

## 🔍 Troubleshooting

### Dashboard shows "Using local JSON files"
- Check Streamlit Cloud secrets are configured correctly
- Verify SUPABASE_URL and SUPABASE_KEY are correct

### "Failed to connect to Supabase"
- Check your internet connection
- Verify API key is correct (should start with `eyJ`)
- Check Project URL format: `https://xxxxx.supabase.co`

### Data not updating
- Check your Python script is running
- Verify data is being written (check Supabase dashboard → Table Editor)
- Check cache TTL settings (might need to wait a few seconds)

---

## 📊 Viewing Data in Supabase Dashboard

1. Go to Supabase project
2. Click **"Table Editor"**
3. Select table (e.g., `alerts_nq`)
4. You'll see your data in the `data` column

---

## 🆓 Free Tier Limits

Supabase free tier:
- ✅ 500MB database
- ✅ Unlimited API requests
- ✅ 50MB file storage
- ✅ No credit card required

**Your data will use ~1-5MB max** - plenty of room!

---

## 🔐 Security Notes

- **Never commit `secrets.toml`** to GitHub
- **Keep your SUPABASE_KEY private**
- The "anon" key is safe to use in client apps
- For production, consider Row Level Security (RLS) policies

---

## 📧 Need Help?

Check Supabase docs: https://supabase.com/docs

---

**You're all set! Your dashboard is now real-time! 🎉**
