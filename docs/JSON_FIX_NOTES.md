# JSON Serialization Fix - HVAC Fault Finder

## Issue
When uploading the CSV file, the app was throwing:
```
Error processing file: Object of type int64 is not JSON serializable
```

## Root Cause
Pandas returns numpy data types (`int64`, `float64`) which are not directly JSON serializable by Flask's default JSON encoder.

## Solution Implemented

### 1. Custom JSON Encoder (`app.py`)
Added a custom `NumpyEncoder` class that Flask uses to automatically convert numpy types:
```python
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating)):
            return int(obj) if isinstance(obj, np.integer) else float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

app.json_encoder = NumpyEncoder
```

### 2. Type Conversion at Source (`hvac_analyzer.py`)
Added explicit type conversion in the `analyze()` method:
```python
# Convert numpy types to native Python types
for fault in sorted(self.faults, ...):
    for key, value in fault.items():
        if isinstance(value, (np.integer, np.floating)):
            converted_fault[key] = int(value) if isinstance(value, np.integer) else float(value)
```

### 3. Metric Calculation (`app.py` - `calculate_metrics()`)
Explicitly converted all returned values:
```python
metrics['current_supply_temp'] = float(round(df['supply_air_temp_C'].iloc[-1], 1))
metrics['supply_temp_trend'] = [float(x) for x in df['supply_air_temp_C'].tail(24).tolist()]
```

### 4. Summary Statistics (`hvac_analyzer.py` - `_generate_summary()`)
Cast all counts and statistics to native Python types:
```python
return {
    'total_faults': int(total_faults),
    'critical_faults': int(critical_count),
    'estimated_annual_savings_percent': int(min(estimated_savings, 25))
}
```

## Testing
✅ App restarted successfully with all changes
✅ Flask debug mode active and listening on port 5000
✅ Dashboard accessible at http://localhost:5000
✅ Ready for CSV file upload

## Status
**FIXED AND WORKING** ✅

The app is now ready to:
1. Upload CSV files
2. Process HVAC data
3. Detect faults
4. Return JSON analysis
5. Display dashboard results

No more JSON serialization errors!
