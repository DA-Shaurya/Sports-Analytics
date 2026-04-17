# ⚽ Footlysis AI: Next-Gen Football Analytics Dashboard

Footlysis AI is a premium, interactive sports analytics dashboard built to provide real-time insights, performance trends, and player comparisons for the top European football leagues.

Combining a stunning custom **Glassmorphism UI** with the power of the **HoloViz ecosystem**, Footlysis AI delivers a seamless, highly responsive, and beautiful data exploration experience.

---

## ✨ Key Features

### 1. 🎨 Premium Glassmorphism UI
- Fully custom HTML/CSS Grid architecture featuring a translucent, sleek dark-mode aesthetic.
- Fully responsive design that seamlessly adapts from widescreen desktop displays to single-column mobile views.
- **HoloViz Integration**: Utilizes native Panel layout components (like `pn.Accordion`) to elegantly organize UI elements without sacrificing the custom design.

### 2. 📊 Interactive Visualizations (Powered by HoloViz hvplot)
- **Vibrant Charting:** Replaces default dark lines with vibrant, color-coded metric visuals (Emerald Green, Sky Blue, Pink/Purple gradients).
- **Deep Interactivity:** Features advanced interactive toolbars (Pan, Zoom, Reset) and custom hover tooltips (`hover_cols`) allowing users to deep-dive into the exact metrics that make up a player's performance.
- Built on top of Bokeh to guarantee buttery-smooth rendering, even with massive datasets.

### 3. 🤖 "Ask AI" Natural Language Query Engine
- **Chat-to-Chart:** Type natural language queries like *"Compare Bukayo Saka and Phil Foden"* or *"Who are the top scorers?"*.
- **Fuzzy Matching & NLP:** Powered by Pandas and `thefuzz`, the engine extracts player entities from typos or partial names and automatically synchronizes the dashboard's dropdown menus and charts to match your query.

### 4. ⚡ The "Hybrid" Database Architecture
- **API-Football Integration:** Pulls live, real-time data from the `API-Football V3` API for the top performing players across Europe.
- **Smart Local Caching:** Bypasses harsh API pagination limits by instantly loading a massive static dataset of over 2,600+ players, then strategically fetching and overwriting just the live stats of the top stars.
- **Cost-Effective:** Ensures blazing fast load times and protects the user's daily API limits.

---

## 🛠️ Technology Stack

- **Frontend & UI:** [Panel](https://panel.holoviz.org/) (HoloViz), Jinja2 HTML Templates, Vanilla CSS (Glassmorphism CSS Grid)
- **Data Visualization:** [hvPlot](https://hvplot.holoviz.org/) & Bokeh
- **Data Processing:** Pandas
- **Natural Language Processing:** `thefuzz` (Token Set Ratio string matching)
- **Data Source:** [API-Football](https://www.api-football.com/) (RapidAPI)

---

## 🚀 Installation & Setup

1. **Clone the repository and install dependencies:**
   Make sure you have Python installed, then install the required libraries:
   ```bash
   pip install panel pandas hvplot requests thefuzz
   ```

2. **API Key Setup:**
   The project uses API-Football. If you want to use your own key, update the `API_KEY` variable inside `data_loader.py`.

3. **Run the Dashboard:**
   Launch the application using Panel's built-in server:
   ```bash
   python main.py
   ```
   *(Or run `panel serve dashboard.py --show`)*

4. **Explore!**
   The application will automatically build the Hybrid Database on its first run and cache it locally (`cached_api_data.csv`). Open the generated `localhost` link in your browser to start exploring!
