# Concrete Compressive Strength Assessment Platform

A modern, full-stack machine learning web application for civil engineers, materials scientists, and structural testing laboratories to evaluate concrete mixture proportions, predict compressive resistance ($f'_c$ in MPa), and classify quality into **STRONG** or **WEAK**.

---

## 1. Architecture Overview

- **Backend:** **FastAPI** Python service serving the pre-trained `concrete_model.pkl` pipeline with Pydantic validation, CORS middleware, and Vercel Serverless Function compatibility.
- **Frontend:** **Next.js** (App Router) + **TypeScript** + **Tailwind CSS** responsive dashboard with synchronized sliders, one-click preset mixture loading, visual cutoff benchmark gauges, and zero AI clichés.
- **Machine Learning Engine:** `GradientBoostingRegressor` model trained on 12 features (8 raw mix components + 4 engineered interaction variables) with a median cutoff threshold of **`33.72 MPa`**.

---

## 2. Directory Structure

```
concrete-web/
├── backend/
│   ├── api/
│   │   └── index.py            # Vercel Serverless Function entrypoint
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration & CORS settings
│   │   ├── main.py             # FastAPI routes, middleware, lifespan
│   │   ├── model.py            # ConcreteModelManager & add_features()
│   │   └── schemas.py          # Pydantic input/output validation models
│   ├── concrete_model.pkl      # Pre-trained ML model bundle
│   ├── requirements.txt        # Python dependencies (scikit-learn==1.6.1)
│   ├── vercel.json             # Vercel configuration for Python runtime
│   ├── .env.example
│   └── run.py                  # Local runner script (uvicorn)
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── globals.css     # Tailwind styling
│   │   │   ├── layout.tsx      # Root layout & metadata
│   │   │   └── page.tsx        # Main application dashboard
│   │   ├── components/
│   │   │   ├── Header.tsx      # Clean engineering header & API status
│   │   │   ├── MixForm.tsx     # 4-group categorized input form
│   │   │   ├── SliderInput.tsx # Synchronized slider + numeric input
│   │   │   ├── Presets.tsx     # Pre-configured mix designs
│   │   │   ├── ResultCard.tsx  # Hero strength display & cutoff gauge
│   │   │   └── StatusAlert.tsx # Error banner & retry action
│   │   ├── lib/
│   │   │   ├── api.ts          # API client with error handling
│   │   │   └── constants.ts    # Default ranges & preset definitions
│   │   └── types/
│   │       └── index.ts        # TypeScript data contracts
│   ├── package.json
│   ├── tsconfig.json
│   ├── vercel.json             # Vercel Next.js framework configuration
│   ├── .env.example
│   └── .env.local
└── README.md                   # Operational & deployment manual
```

---

## 3. Local Development Guide

### Step 1: Start the Backend (FastAPI)
1. Navigate into the backend folder:
   ```bash
   cd concrete-web/backend
   ```
2. Install Python dependencies (ensure `scikit-learn==1.6.1` is used):
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   python run.py
   ```
   The backend will start at **`http://127.0.0.1:8000`**.
   - Interactive Swagger API docs: `http://127.0.0.1:8000/docs`
   - Health check: `http://127.0.0.1:8000/health`

### Step 2: Start the Frontend (Next.js)
1. Open a new terminal and navigate into the frontend folder:
   ```bash
   cd concrete-web/frontend
   ```
2. Verify that `.env.local` contains:
   ```env
   NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
   Open **`http://localhost:3000`** in your browser.

---

## 4. Vercel Deployment Instructions

Deploying **Frontend** and **Backend** as **two separate Vercel projects** ensures clean separation of concerns and independent scaling.

### Part A: Deploying the Backend on Vercel
1. Push your repository to GitHub, GitLab, or Bitbucket.
2. In the [Vercel Dashboard](https://vercel.com/new), click **Add New Project** and select your repository.
3. **Configure Project Settings:**
   - **Project Name:** `concrete-strength-backend` (or your preferred name).
   - **Root Directory:** Click **Edit** and select **`concrete-web/backend`**.
   - **Framework Preset:** Select **Other**.
4. **Environment Variables:**
   - Add `CORS_ORIGINS`: Set to `*` or your frontend domain (e.g. `https://concrete-strength-frontend.vercel.app`).
5. Click **Deploy**.
6. Once deployed, copy your backend URL (e.g., `https://concrete-strength-backend.vercel.app`). Verify by opening `https://concrete-strength-backend.vercel.app/health`.

### Part B: Deploying the Frontend on Vercel
1. In the Vercel Dashboard, click **Add New Project** again and select the same repository.
2. **Configure Project Settings:**
   - **Project Name:** `concrete-strength-frontend`.
   - **Root Directory:** Click **Edit** and select **`concrete-web/frontend`**.
   - **Framework Preset:** Select **Next.js**.
3. **Environment Variables:**
   - Add `NEXT_PUBLIC_API_URL`: Paste the backend URL from Part A (e.g., `https://concrete-strength-backend.vercel.app` without trailing slash).
4. Click **Deploy**.
5. Your production frontend is now live and communicating with the serverless FastAPI backend!

---

## 5. Machine Learning Specification

### A. Raw Mixture Inputs (8 Parameters)
| Ingredient | Unit | Minimum | Maximum | Default | Role |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Cement** | $\text{kg/m}^3$ | $100$ | $540$ | $280$ | Hydraulic binder |
| **Blast Furnace Slag** | $\text{kg/m}^3$ | $0$ | $360$ | $0$ | Supplementary cementitious material |
| **Fly Ash** | $\text{kg/m}^3$ | $0$ | $200$ | $0$ | Pozzolanic admixture |
| **Water** | $\text{kg/m}^3$ | $120$ | $250$ | $180$ | Hydration liquid |
| **Superplasticizer** | $\text{kg/m}^3$ | $0.0$ | $33.0$ | $0.0$ | High-range water reducer |
| **Coarse Aggregate** | $\text{kg/m}^3$ | $800$ | $1150$ | $970$ | Gravel / crushed stone |
| **Fine Aggregate** | $\text{kg/m}^3$ | $590$ | $995$ | $780$ | Sand filler |
| **Age** | Days | $1$ | $365$ | $28$ | Moist curing time |

### B. Derived Features (`add_features`)
$$\text{Water\_Cement\_Ratio} = \frac{\text{Water}}{\text{Cement}}$$
$$\text{Binder} = \text{Cement} + \text{Blast\_Furnace\_Slag} + \text{Fly\_Ash}$$
$$\text{Water\_Binder\_Ratio} = \frac{\text{Water}}{\text{Binder}}$$
$$\text{Log\_Age} = \ln(1 + \text{Age})$$

### C. Decision Benchmark (Cutoff = 33.72 MPa)
- $\text{Predicted Strength} \ge 33.72\text{ MPa} \longrightarrow \mathbf{STRONG\ MIX}$ (Soft emerald badge `#15803d`)
- $\text{Predicted Strength} < 33.72\text{ MPa} \longrightarrow \mathbf{WEAK\ MIX}$ (Soft amber badge `#c2410c`)
