# HVAC Fault Finder - Intelligent Diagnostics Platform

A lightweight, web-based platform that analyzes HVAC Building Automation System (BAS) data in CSV format to detect common faults early, calculate severity scores, and provide actionable recommendations to save energy and money.

## Features

✨ **Core Capabilities:**
- 📁 **CSV File Upload** - Support for any BAS trend data export
- 🔍 **Automated Fault Detection** - Identifies 5 major HVAC fault categories:
  - Simultaneous Heating & Cooling (energy waste)
  - Schedule Mismatch (runtime outside occupied hours)
  - Sensor Flatline (temperature sensor stuck)
  - High Filter Pressure Drop (dirty filter alert)
  - Short Cycling (excessive on/off cycles)
- 📊 **Severity Scoring** - AI-driven scoring (0-100) for fault prioritization
- 💡 **Smart Recommendations** - Plain-language explanations and "what to check next"
- 📈 **Interactive Dashboard** - Real-time metrics visualization
- 📥 **Report Export** - Generate detailed fault analysis reports
- 💰 **Savings Estimation** - Calculate potential energy savings by fault category

## Prerequisites

- **Python 3.8 or higher**
- **pip** (Python package manager)

## Installation & Setup

### 1. Install Dependencies

```bash
cd HVAC-Fault-finder
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

You should see output like:
```
Starting HVAC Fault Finder Web App
Open your browser at: http://localhost:5000
```

### 3. Open in Browser

Navigate to: **http://localhost:5000**

## How to Use

### Step 1: Upload CSV Data
1. Click **"Select CSV File"** button
2. Choose your HVAC BAS export CSV file
3. Click **"Analyze Data"** button

### Step 2: Review Analysis
The dashboard will display:
- **Overall Status** - Total faults, potential savings percentage
- **Active Metrics** - Current supply temperature, humidity, system status
- **Temperature Trends** - Multi-line chart of historical temperatures
- **Faults List** - Ranked by severity with descriptions and impact
- **Recommendations** - Prioritized actions with next steps
- **Equipment Summary** - Breakdown by equipment type

### Step 3: Download Report
Click **"Download Full Report"** to export detailed findings as a text file.

## Sample Data

A sample HVAC CSV file is included:
- `CSV sample_medium_office_15min_1day_FAULTY.csv` - Contains sample HVAC data with intentional faults

Test with this file to see the system in action:
1. Click "Select CSV File"
2. Choose `CSV sample_medium_office_15min_1day_FAULTY.csv`
3. Click "Analyze Data"
4. Review the faults detected and recommendations

## Required CSV Columns

The system expects the following columns (exact names required):

```
timestamp                   - Date/time of reading (any format, will be parsed)
occupancy_mode             - "OCCUPIED" or "UNOCCUPIED"
outdoor_air_temp_C         - Outside air temperature
return_air_temp_C          - Return air temperature
mixed_air_temp_C           - Mixed air temperature
supply_air_temp_C          - Supply air temperature
supply_air_temp_setpoint_C - Supply temp setpoint
outside_air_damper_pct     - Damper position (0-100%)
fan_status                 - 0 (off) or 1 (on)
fan_speed_pct              - Fan speed percentage
duct_static_pressure_inwg  - Static pressure in inches of water
duct_static_pressure_setpoint_inwg - Static pressure setpoint
heating_valve_cmd_pct      - Heating valve command (0-100%)
cooling_valve_cmd_pct      - Cooling valve command (0-100%)
zone_reception_temp_C      - Reception area temperature
zone_office1_temp_C        - Office 1 temperature
zone_office2_temp_C        - Office 2 temperature
zone_office3_temp_C        - Office 3 temperature
zone_temp_setpoint_C       - Zone temperature setpoint
filter_dP_inwg             - Filter pressure drop
alarm_status               - Status indicator
```

## Fault Detection Details

### 1. Simultaneous Heating & Cooling
**What:** Both heating and cooling valves open at the same time
**Why Bad:** Wastes significant energy as systems fight each other
**Detection:** Monitors when both heating_valve_cmd_pct > 5% AND cooling_valve_cmd_pct > 5%
**Savings Potential:** 10-15% energy reduction

### 2. Schedule Mismatch
**What:** System running when building is unoccupied
**Why Bad:** Heats/cools empty spaces unnecessarily
**Detection:** Checks for fan_status=1 when occupancy_mode="UNOCCUPIED"
**Savings Potential:** 5-10% energy reduction

### 3. Sensor Flatline
**What:** Temperature sensor readings stuck at same value
**Why Bad:** Indicates faulty sensor, unreliable feedback to controls
**Detection:** Rolling standard deviation < 0.1°C over 3-hour windows
**Action Required:** Physical sensor inspection and possible replacement

### 4. High Filter Pressure Drop
**What:** Dirty or clogged air filter
**Why Bad:** Reduces airflow, increases fan energy, poor air quality
**Detection:** filter_dP_inwg > 0.6 inwg (should change at ~0.8 inwg)
**Action Required:** Immediate filter replacement
**Savings Potential:** 3-5% energy reduction

### 5. Short Cycling
**What:** Excessive on/off cycles (>3 per hour)
**Why Bad:** Reduces equipment lifespan, wasted startup energy
**Detection:** Counts fan state transitions per hour
**Action Required:** Adjust control tuning parameters

## Application Structure

```
HVAC-Fault-finder/
├── app.py                          # Flask web application
├── hvac_analyzer.py                # Fault detection engine
├── requirements.txt                # Python dependencies
├── templates/
│   └── index.html                  # Web dashboard UI
├── uploads/                        # CSV uploads (auto-created)
├── CSV sample_medium_office_15min_1day_FAULTY.csv
├── MVP Prototype Plan.docx         # Project requirements
└── README.md                       # This file
```

## API Endpoints

- `GET /` - Main dashboard page
- `POST /api/upload` - Upload CSV and run analysis
- `GET /api/stats` - Get current analysis statistics
- `GET /api/chart-data` - Get trend chart data
- `GET /api/report` - Download report as text file

## Technical Stack

- **Backend:** Python 3, Flask
- **Frontend:** HTML5, CSS3, JavaScript (Chart.js for visualizations)
- **Data Processing:** Pandas, NumPy
- **Hosting:** Local Flask development server

## Performance

- Analyzes datasets with 100,000+ entries in seconds
- Supports up to 50MB CSV files
- Memory-efficient streaming for large datasets

## Troubleshooting

**Issue: "Module not found" errors**
- Solution: Run `pip install -r requirements.txt` again

**Issue: Port 5000 already in use**
- Solution: Modify `app.py` port number, or close the application using that port

**Issue: CSV upload fails**
- Check that all required columns are present
- Verify CSV encoding is UTF-8
- Ensure timestamp format is parseable

**Issue: Dashboard shows "No data"**
- Refresh the page
- Check browser console for JavaScript errors (F12 key)

## Future Enhancements

- Multi-file batch analysis
- Historical trend analysis and anomaly detection
- Machine learning-based fault prediction
- Integration with BAS systems (direct data pulls)
- Mobile app version
- Real-time monitoring and alerts
- Custom fault rule engine
- Cost-benefit analysis calculator

## MVP Development Timeline

- [x] Core fault detection engine (5 major faults)
- [x] Severity scoring algorithm
- [x] Web dashboard with visualizations
- [x] CSV upload and processing
- [x] Report generation
- [x] Local hosting capability
- [ ] Enterprise cloud deployment
- [ ] Advanced analytics and ML model

## License

Internal MVP - For evaluation and demo purposes only

## Support

For questions or issues, please refer to the MVP Prototype Plan documentation.

---

**Version:** 1.0 MVP
**Last Updated:** 2026-02-10
**Status:** Ready for Demo
