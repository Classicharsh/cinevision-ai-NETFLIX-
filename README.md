# 🎬 CineVision AI — Intelligent Streaming Analytics Platform

CineVision AI is a premium, cyber-themed Netflix Intelligence Dashboard built with **Streamlit**, **Pandas**, **Plotly**, and **Scikit-Learn**. It offers high-level platform insights, detailed content exploration, geographic analytics, talent relationship mapping, and an NLP content recommendation engine.

---

## ✨ Features

1. **📊 Executive Overview**: Real-time KPI counters (Total Titles, Movies, TV Shows, Countries) using glassmorphic design and Plotly analytics on catalog composition and runtime distributions.
2. **🔍 Interactive Content Explorer**: Dynamic search across metadata (title, cast, director, plot description) with paginated results and custom detail drawer cards.
3. **🎨 Genre & Geographic Insights**: A global choropleth production map, catalog genre distribution charts, and a co-occurrence heatmap of genres vs. age ratings.
4. **🤝 Talent & Network Explorer**: Analytics on top directors and actors, plus an interactive collaboration explorer that computes co-stars and catalog listings for any selected actor.
5. **🤖 AI-Powered Content Recommender**: Content-based filtering using **TF-IDF Vectorization** and **Cosine Similarity** on combined text features (plot, title, cast, genres, director), featuring adjustable output counts and fuzzy-match title search.

---

## 🎨 Design System

- **Theme**: Premium cyber-dark mode (deep charcoal base `#0d0d0e` and sidebar `#111113`).
- **Accents**: Neon red/crimson gradient (`#FF2E3B` / `#E50914`) for branding and metrics; neon violet (`#7A22E8`) for TV/ML indicators.
- **Glassmorphism**: KPIs and cards use semi-transparent dark borders, backdrop blurs, and glowing hover states with translation animations.
- **Typography**: Inter for readability; Outfit for bold headers.

---

## 📂 Project Structure

```text
CineVision-AI/
│
├── assets/
│   └── style.css            # Custom glassmorphic styling
├── data/
│   └── datanetflix_titles.csv # Netflix raw titles dataset
├── src/
│   ├── data_loader.py       # Data loading, cleaning & caching
│   ├── overview.py          # Executive overview view component
│   ├── explorer.py          # Tabular explorer view component
│   ├── insights.py          # Geography & genre charts
│   ├── talent.py            # Actor & director network dashboards
│   ├── recommender.py       # Core similarity recommendation ML math
│   └── recommender_ui.py    # Recommender page layout component
├── app.py                   # Main entry point & layout routing
├── requirements.txt         # Package dependencies
└── README.md                # Project documentation
```

---

## 🚀 Getting Started

### 1. Set Up Environment
Create and activate a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate  # macOS/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Dashboard
```bash
streamlit run app.py
```
Streamlit will launch a server and open the browser automatically (typically at `http://localhost:8501`).
