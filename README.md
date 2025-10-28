## Dynamic Fleet Manager

A Streamlit application for interactive fleet operations: vehicle–order matching, dashboards, performance analytics, and cost insights. Built with `pandas`, `numpy`, `plotly`, and `scikit-learn`.

### Key features
- **Dashboard**: Fleet status, order volumes, on‑time rate, cost KPIs with interactive charts.
- **Order–Vehicle matching**: Scored recommendations based on constraints (priority, capacity, special handling, proximity).
- **Fleet overview**: Filterable vehicle table with efficiency and emissions analytics.
- **Performance analytics**: Delivery delays, carrier performance, customer feedback, and cost breakdowns.

---

## Project structure
```
OFI/
├─ fleet_manager.py            # Streamlit app entrypoint
├─ fleet_analysis.py           # Offline analysis to build model artifacts (optional)
├─ fleet_model_artifacts.pkl   # Saved artifacts used by the app (optional)
├─ requirements.txt            # Python dependencies
├─ how_to_run.txt              # Quick run notes
├─ orders.csv                  # Orders dataset
├─ routes_distance.csv         # Route info (per order)
├─ vehicle_fleet.csv           # Fleet inventory
├─ delivery_performance.csv    # Historical delivery performance
├─ cost_breakdown.csv          # Cost components per order
├─ customer_feedback.csv       # Customer feedback dataset
└─ warehouse_inventory.csv     # (optional) Inventory data
```

---

## Quick start (local)

### 1) Prerequisites
- Python 3.11+ recommended (3.13 supported)
- pip 23+

### 2) Create and activate a virtual environment
- Windows PowerShell
```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
```
- macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Run the app
```bash
streamlit run fleet_manager.py
```
Streamlit will open in your browser (default: `http://localhost:8501`).

---

## Using the app
- Open the app, navigate through tabs:
  - **📊 Dashboard**: High‑level KPIs and distributions.
  - **🔍 Order Matching**: Choose an order, set a minimum score, and compute the best vehicle matches.
  - **🚛 Fleet Overview**: Filter vehicles by type, status, and efficiency; explore plots.
  - **📈 Performance**: Analyze delays, carrier performance, ratings, and cost composition.

If `fleet_model_artifacts.pkl` is missing, the app still runs with heuristic matching but will show a warning. Generate it via `fleet_analysis.py` if needed.

---

## Data inputs
The app expects the CSV files at the project root:
- `orders.csv`: Includes `Order_ID`, `Priority`, `Product_Category`, `Origin`, `Destination`, `Special_Handling`, `Order_Value_INR`, ...
- `routes_distance.csv`: Includes `Order_ID` and route details per order.
- `vehicle_fleet.csv`: Includes `Vehicle_ID`, `Vehicle_Type`, `Status`, `Capacity_KG`, `Fuel_Efficiency_KM_per_L`, `CO2_Emissions_Kg_per_KM`, `Age_Years`, `Current_Location`, ...
- `delivery_performance.csv`: Includes `Carrier`, `Promised_Delivery_Days`, `Actual_Delivery_Days`, `Customer_Rating`, `Delivery_Cost_INR`, `Delivery_Status`, ...
- `cost_breakdown.csv`: Numeric columns of cost components; app adds `Total_Cost` at runtime.
- `customer_feedback.csv`: `Rating`, `Issue_Category`, ...

Column names should match those referenced in `fleet_manager.py`.

---

## Deployment

### Streamlit Community Cloud
1. Push this project to a public GitHub repository.
2. In Streamlit Cloud, create a new app and select your repo.
3. Set the app file to `fleet_manager.py`.
4. Ensure the default Python runtime supports your pins (3.13 currently supported). No extra config is required.

If your deployment environment is older than Python 3.12 and you must pin, use compatible versions in `requirements.txt` (already set with flexible ranges). The app relies on packages with wheels available for modern Python.

### Docker (optional)
Example `Dockerfile` concept:
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "fleet_manager.py", "--server.port=8501", "--server.address=0.0.0.0"]
```
Build and run:
```bash
docker build -t dynamic-fleet-manager .
docker run -p 8501:8501 dynamic-fleet-manager
```

---

## Configuration
- No secret keys are required.
- All datasets load from relative paths in the project root.
- Session state stores the latest matching results during a session.

---

## Troubleshooting
- **ModuleNotFoundError: plotly**
  - Ensure `plotly` is installed via `pip install -r requirements.txt`.
- **Build fails with numpy/distutils on Python ≥3.12**
  - The provided `requirements.txt` pins `numpy>=2.1` to avoid legacy `distutils` builds.
- **Data file not found**
  - Confirm CSVs are present at project root and named exactly as referenced.
- **Model artifacts missing**
  - The app will warn and continue; optionally run `fleet_analysis.py` to generate `fleet_model_artifacts.pkl`.

---

## Contributing
1. Create a feature branch from `main`.
2. Make changes with clear, small commits.
3. Run the app locally and verify no errors.
4. Submit a pull request describing the change and testing steps.

---

## License
This project is provided for demonstration and educational purposes. Insert your organization’s license of choice here (e.g., MIT, Apache-2.0).
