# What Are Gen Z Up To?
### Where are young people in Ireland actually meeting each other now?

> A data analysis of pub closures, the cost of drinking, dating-app trends and the search for alternatives in Ireland, built in Python and designed to be deployed as a containerised dashboard on IBM Cloud.

![Status](https://img.shields.io/badge/status-in%20progress-orange) ![Python](https://img.shields.io/badge/python-3.11+-blue) ![pandas](https://img.shields.io/badge/pandas-2.x-150458) ![Docker](https://img.shields.io/badge/docker-planned-2496ED) ![IBM Cloud](https://img.shields.io/badge/IBM%20Cloud-Code%20Engine-0f62fe)

**Live dashboard:** 

---

## Contents
1. [The question](#1-the-question)
2. [Why it matters](#2-why-it-matters)
3. [Design thinking framing](#3-design-thinking-framing)
4. [Key findings](#4-key-findings)
5. [Data sources](#5-data-sources)
6. [Data quality and corrections](#6-data-quality-and-corrections)
7. [Method](#7-method)
8. [Project structure](#8-project-structure)
9. [Getting started](#9-getting-started)
10. [Limitations and responsible use of data](#11-limitations-and-responsible-use-of-data)
11. [Tech stack](#12-tech-stack)
12. [What I learned](#13-what-i-learned)
13. [Author](#14-author)

---

## 1. The question

Two of the traditional ways young people in Ireland meet each other appear to be changing at the same time:

- **The pub.** Ireland has far fewer pubs than it did twenty years ago, and closures are concentrated outside Dublin.
- **Dating apps.** The industry's flagship apps are reporting falling paying users, while newer apps are growing.

So this project asks:

> **If the pub and the old dating apps are fading, where are young people in Ireland meeting each other now, and what's driving the change?**

It breaks down into four sub-questions:

| # | Sub-question | Evidence used |
|---|---|---|
| **Q1** | How fast are pubs disappearing, and where? | Pub licence counts, nationally (2005–2025) and by county |
| **Q2** | Has drinking become less affordable? | CSO Consumer Price Index for alcohol vs national minimum wage |
| **Q3** | Are dating apps declining, or just changing? | Irish search interest in Tinder, Hinge and Bumble; global paying-user figures |
| **Q4** | What are people turning to instead? | Irish search interest in going-out terms and alternative activities |

---

## 2. Why it matters

- **Communities:** in many rural towns the pub is the only social venue. When it closes, a meeting place goes with it.
- **Young people:** loneliness is a growing public-health concern. Knowing *where* connection is moving helps clubs, councils and venues respond.
- **Business:** hospitality, events and app companies all need to know where demand is going.

---

## 3. Design thinking framing

The project was scoped using **IBM Enterprise Design Thinking**.

**Persona: Aoife, 22, final-year student in Waterford**
> Wants to meet people outside her course. Finds nights out expensive and the apps draining. Isn't sure what else is out there.

**Hill (the outcome the project aims for):**
> *A young person in Ireland can see, in under two minutes, how the ways people meet have changed over the last decade and what's growing instead, backed by public data.*

**Sponsor-user questions that guide the analysis:**
1. "Is my county losing its pubs faster than everywhere else?"
2. "Is it just me, or has going out got way more expensive?"
3. "If not the pub or Tinder, then where?"

---

## 4. Key findings

> Each finding links to the notebook and chart that supports it.

### Q1: Pub decline
| | Finding | Evidence |
|---|---|---|
| National | | [`01_explore_pubs.ipynb`](notebooks/01_explore_pubs.ipynb) · `01_national_trend.png` |
| Timing | | `01_closures_by_period.png` |
| Geography | | `01_county_ranking.png` |
| Dublin vs rest | | `01_dublin_vs_rest.png` |
| Since COVID | | `01_since_covid.png` |

### Q2: Cost of drinking
| | Finding | Evidence |
|---|---|---|
| Alcohol prices | | `02_cost_of_going_out.ipynb` |
| Prices vs wages | | |

### Q3: Dating apps
| | Finding | Evidence |
|---|---|---|
| Search interest | | `03_apps_and_alternatives.ipynb` |
| Paying users | | |

### Q4: Alternatives
| | Finding | Evidence |
|---|---|---|
| Going-out searches | | `03_apps_and_alternatives.ipynb` |
| Alternative activities | | |

### Forecast
| | Finding | Evidence |
|---|---|---|
| Pubs in 2030 | | `04_forecast.ipynb` |

**Headline (one sentence):**

---

## 5. Data sources

All data is public and aggregated. Raw files are stored unedited in `data/raw/`, and each one is documented column by column in [`data/DATA_DICTIONARY.md`](data/DATA_DICTIONARY.md).

| Raw file | What it contains | Source | Period |
|---|---|---|---|
| `pubs_national_by_year.csv` | Number of pubs each year | Drinks Industry Group of Ireland (DIGI) / A. Foley, *The Decline in the Number of Public Houses* (2024 and 2026 editions), based on the Revenue Commissioners licence register | 2005–2025, yearly |
| `pubs_by_county.csv` | Pubs per county | DIGI / A. Foley (2026), county pages | 2005 and 2019–2025 |
| `cpi-alcohol_tobacco.csv` | Consumer Price Index, *Alcoholic beverages and tobacco* (base Dec 2023 = 100) | CSO PxStat, table CPM01 | Nov 2019 – Dec 2025, monthly |
| `min_wage.csv` | National minimum wage rate changes | gov.ie, with later rates confirmed from official and professional sources (cited per row) | 2011–2026 |
| `dating_app_payers.csv` | Global paying users for Tinder, Hinge and Bumble App | Match Group and Bumble Inc. investor filings | 2022–2025, yearly |
| `trends_going_pub.csv` | Search interest: "pub" | Google Trends, Ireland | Nov 2015 – Nov 2025, monthly |
| `trends_nightclub.csv` | Search interest: "nightclub" | Google Trends, Ireland | Nov 2015 – Nov 2025, monthly |
| `app_tinder_trends.csv` | Search interest: "Tinder" | Google Trends, Ireland | Nov 2015 – Nov 2025, monthly |
| `app_trends_hinge.csv` | Search interest: "Hinge" | Google Trends, Ireland | Nov 2015 – Nov 2025, monthly |
| `app_trends_bumble.csv` | Search interest: "Bumble" | Google Trends, Ireland | Nov 2015 – Nov 2025, monthly |

> **On proxies:** no dataset directly measures how often young people meet each other. This project uses **proxies** (venue counts, prices, app users and search interest) and is upfront about what each one can and can't show. See [Section 11](#11-limitations-and-responsible-use-of-data).

---

## 6. Data quality and corrections

Every source was checked before it was used. All corrections are made in code (`src/clean.py`), never by editing raw files, so each change is visible and reproducible.

**County totals vs national totals.** County figures should add up to the national figure for each year. They don't always:

| Year | Sum of counties | National total | Difference |
|---|---|---|---|
| 2005 | 8,617 | 8,617 | ✅ 0 |
| 2019 | 7,137 | 7,137 | ✅ 0 |
| 2020 | 6,900 | 6,890 | ❌ +10 |
| 2021 | 6,788 | 6,788 | ✅ 0 |
| 2022 | 6,693 | 6,680 | ❌ +13 |
| 2023 | 6,480 → **6,563** after correction | 6,563 | ✅ fixed |
| 2024 | 6,498 | 6,498 | ✅ 0 |
| 2025 | 6,412 | 6,412 | ✅ 0 |

**Errors found in the source report:**
- **Clare 2023 is printed as 176**, between 277 (2022) and 265 (2024). The national total implies **259**, so it's corrected in `clean.py` with the reason logged.
- **Offaly 2025:** the headline figure (109) disagrees with the report's own yearly table (108). 108 is used because it balances the national total.
- **Westmeath:** the text says "64 fewer pubs," but the figures give **62**.
- The small 2020 and 2022 mismatches can't be traced to one county, so analysis that needs exact county figures uses only 2019 and 2025, which both balance.

**Other data handling:**
- The Google Trends and CSO downloads are **Excel workbooks saved with a `.csv` extension**. `clean.py` detects this automatically and reads them correctly.
- **Each Google Trends term was exported separately**, so each is scaled 0–100 within itself, and raw values can't be compared across terms. Each term is therefore **indexed to its own 2016 average (= 100)**. This compares how much each term *changed*, not how popular they are relative to each other.
- **The minimum wage** is stored as rate changes and converted to a monthly series so it can be joined with monthly price data. The February 2020 increase is applied from February, not January.

---

## 7. Method

```
Collect ──► Validate & clean ──► Explore ──► Combine ──► Forecast ──► Present ──► Deploy
 raw files     clean.py           notebooks    new metrics   scikit-learn   Streamlit   Docker + IBM Cloud
```

1. **Collect** public data into `data/raw/`, unedited.
2. **Validate and clean** with `src/clean.py`: check totals, correct documented errors, standardise dates and reshape into tidy tables in `data/processed/`.
3. **Explore** each question in its own notebook, with charts saved to `reports/figures/`.
4. **Combine** sources into metrics no single dataset provides:
   - **Pub loss rate by county** (% change, 2005 → 2025)
   - **Dublin vs rest-of-Ireland index** (2005 = 100)
   - **Alcohol prices vs wages:** growth in alcohol CPI compared with growth in the minimum wage
   - **Search-interest index** (2016 = 100) for going-out terms and dating apps
5. **Forecast** national pub numbers to 2030 with a simple, explainable model (linear and polynomial regression), shown with an error range.
6. **Present** the results in an interactive Streamlit dashboard, one page per question.
7. **Deploy** with Docker to **IBM Cloud Code Engine**.

---

## 8. Project structure

```
What-are-Gen-Z-up-to/
├── data/
│   ├── raw/                     # Original downloads, never edited
│   ├── processed/               # Clean, analysis-ready tables (made by clean.py)
│   └── DATA_DICTIONARY.md       # Every file and column explained
├── notebooks/
│   ├── 01_explore_pubs.ipynb            # Q1
│   ├── 02_cost_of_going_out.ipynb       # Q2
│   ├── 03_apps_and_alternatives.ipynb   # Q3 and Q4
│   └── 04_forecast.ipynb                # Forecast
├── reports/
│   └── figures/                 # Charts saved by the notebooks
├── src/
│   └── clean.py                 # Raw → processed, with documented corrections
├── app/
│   └── dashboard.py             # Streamlit dashboard
├── tests/                       # Unit tests for cleaning and metrics
├── Dockerfile
├── requirements.txt
└── README.md
```

**Processed outputs from `clean.py`:**

| File | Description |
|---|---|
| `pubs_national.csv` | Yearly pub count, change, % change and % of 2005 |
| `pubs_county_long.csv` | One row per county per year, with region and a correction flag |
| `pubs_county_summary.csv` | One row per county: 2005 vs 2025, pubs lost, % lost |
| `min_wage_monthly.csv` | Minimum wage for every month from 2015 |
| `cpi.csv` | Alcohol and tobacco CPI by month, with year-on-year inflation |
| `dating_apps.csv` | Paying users by app and year, with % change within each app |
| `trends.csv` | All search terms in one long table: raw interest and 2016 index |

---

## 9. Getting started

**Prerequisites:** Python 3.11+, Git, and Docker (deployment only).

```bash
# 1. Clone
git clone https://github.com/<your-username>/What-are-Gen-Z-up-to.git
cd What-are-Gen-Z-up-to

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Build the processed data (prints a county-total check)
python src/clean.py

# 5. Explore the analysis
jupyter notebook notebooks/
```

**Dashboard (after Chunk 7):**
```bash
streamlit run app/dashboard.py
```

**Docker (after Chunk 8):**
```bash
docker build -t what-are-gen-z-up-to .
docker run -p 8501:8501 what-are-gen-z-up-to
# open http://localhost:8501
```

---

## 11. Limitations and responsible use of data

Being clear about what the data *can't* show matters as much as the findings.

- **Correlation, not causation.** Rising prices and falling pub numbers happening at the same time doesn't prove one caused the other. Rural depopulation, the 2004 smoking ban, drink-driving laws, COVID-19 and drinking at home are all possible factors this data can't separate.
- **Proxies, not direct measurement.** Pub licences count venues, not visitors. Google Trends measures *search interest*, not attendance or sign-ups.
- **Not age-specific.** The pub, price and search data cover everyone, not just young people. Conclusions about Gen Z are framed carefully.
- **Search terms are ambiguous.** "Hinge" and "Bumble" are also ordinary English words, and "pub" includes searches for food, sport and directions.
- **Indexed trends compare change, not size.** A term at 400 (2016 = 100) has grown fourfold, but it may still be searched less than a term at 50.
- **Broad price category.** The CPI series combines alcohol *and* tobacco, and doesn't separate pub prices from off-licence prices.
- **Geography mismatch.** Dating-app paying users are **global** figures, used only to show the industry trend alongside Irish search data.
- **Source interest.** The pub-closure reports were commissioned by the drinks industry, which has a stake in the policy debate (e.g. excise duty). The counts come from the Revenue licence register, but the reports' interpretation is treated with care.
- **Forecast uncertainty.** A trend model can't anticipate shocks such as a pandemic or policy change. Forecasts are illustrative and shown with an error range.
- **No personal data.** Every dataset is public and aggregated, so no individual can be identified.

---

## 12. Tech stack

| Area | Tools |
|---|---|
| Language | Python 3.11 |
| Data | pandas, NumPy, openpyxl |
| Charts | matplotlib (notebooks), Plotly (dashboard) |
| Modelling | scikit-learn |
| Dashboard | Streamlit |
| Testing | pytest |
| Containers | Docker |
| Cloud | IBM Cloud Code Engine, IBM Cloud Container Registry |
| Process | IBM Enterprise Design Thinking, Git and GitHub |

---

## 13. What I learned

-
-
-

---

## 14. Author

**Joseph (Joey) Ronan**, BSc (Hons) Computer Science, South East Technological University (SETU)

[LinkedIn](#) · [GitHub](#) · [Credly](#)

_Data sources are credited in Section 5. This project is for educational and portfolio purposes._
