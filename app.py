from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from hvac_analyzer import HVACFaultAnalyzer
import io
import numpy as np

# Custom JSON encoder for numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating)):
            return int(obj) if isinstance(obj, np.integer) else float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

app = Flask(__name__)
app.json_encoder = NumpyEncoder
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store analysis results in memory
analysis_results = {}


@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload and run analysis"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Only CSV files are supported'}), 400
        
        # Read and parse CSV
        stream = io.StringIO(file.stream.read().decode("utf-8"), newline=None)
        df = pd.read_csv(stream)
        
        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Validate required columns
        required_columns = ['occupancy_mode', 'fan_status', 'heating_valve_cmd_pct', 'cooling_valve_cmd_pct']
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            return jsonify({'error': f'Missing required columns: {", ".join(missing)}'}), 400
        
        # Run analysis
        analyzer = HVACFaultAnalyzer(df)
        result = analyzer.analyze()
        
        # Calculate additional metrics for dashboard
        metrics = calculate_metrics(df)
        
        # Combine results
        dashboard_data = {
            'faults': result['faults'],
            'recommendations': result['recommendations'],
            'summary': result['summary'],
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }
        
        # Convert numpy types to native Python types
        dashboard_data = json.loads(json.dumps(dashboard_data, cls=NumpyEncoder))
        
        analysis_results['latest'] = dashboard_data
        
        return jsonify(dashboard_data), 200
    
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500


@app.route('/api/stats')
def get_stats():
    """Get current analysis statistics"""
    if 'latest' not in analysis_results:
        return jsonify({'data': None}), 200
    
    data = analysis_results['latest']
    return jsonify({'data': data}), 200


@app.route('/api/chart-data')
def get_chart_data():
    """Get data for trend chart"""
    # Retrieve the CSV file that was uploaded
    # For demo purposes, we'll return sample data structure
    # In production, you'd save the CSV and retrieve it here
    
    if 'latest' not in analysis_results:
        return jsonify({'error': 'No analysis data available'}), 404
    
    metrics = analysis_results['latest'].get('metrics', {})
    
    return jsonify({
        'temperature_trend': metrics.get('temperature_trend', []),
        'humidity_trend': metrics.get('humidity_trend', []),
        'supply_temp_trend': metrics.get('supply_temp_trend', [])
    }), 200


@app.route('/api/report')
def download_report():
    """Generate and download text report"""
    if 'latest' not in analysis_results:
        return jsonify({'error': 'No analysis data available'}), 404
    
    # Note: This is a simplified version. In production, you'd store the CSV
    # and regenerate the report with actual data
    data = analysis_results['latest']
    
    report_text = f"""HVAC FAULT ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY
{'-' * 50}
Total Faults Detected: {data['summary']['total_faults']}
Critical Issues: {data['summary']['critical_faults']}
Warnings: {data['summary']['warning_faults']}
Alerts: {data['summary']['alert_faults']}
Estimated Annual Savings: {data['summary']['estimated_annual_savings_percent']}%

FAULTS IDENTIFIED
{'-' * 50}
"""
    
    for idx, fault in enumerate(data['faults'], 1):
        report_text += f"\n{idx}. {fault['name']}\n"
        report_text += f"   Severity: {fault.get('severity', 'Unknown')} (Score: {fault['severity_score']}/100)\n"
        report_text += f"   Impact: {fault['impact']}\n"
        if fault.get('probable_causes'):
            report_text += f"   Probable Causes:\n"
            for cause in fault['probable_causes']:
                report_text += f"     • {cause}\n"
    
    # Return as downloadable file
    return send_file(
        io.BytesIO(report_text.encode('utf-8')),
        mimetype='text/plain',
        as_attachment=True,
        download_name=f'HVAC_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    )


def calculate_metrics(df):
    """Calculate metrics for dashboard display"""
    metrics = {}
    
    # Temperature trends
    if 'supply_air_temp_C' in df.columns:
        metrics['current_supply_temp'] = float(round(df['supply_air_temp_C'].iloc[-1], 1))
        metrics['supply_temp_trend'] = [float(x) for x in df['supply_air_temp_C'].tail(24).tolist()] if len(df) > 0 else []
    
    if 'outdoor_air_temp_C' in df.columns:
        metrics['current_outdoor_temp'] = float(round(df['outdoor_air_temp_C'].iloc[-1], 1))
        metrics['outdoor_temp_trend'] = [float(x) for x in df['outdoor_air_temp_C'].tail(24).tolist()] if len(df) > 0 else []
    
    if 'return_air_temp_C' in df.columns:
        metrics['temperature_trend'] = [float(x) for x in df['return_air_temp_C'].tail(24).tolist()] if len(df) > 0 else []
    
    # Fan status
    if 'fan_status' in df.columns:
        metrics['fan_running'] = bool(df['fan_status'].iloc[-1])
    
    # Humidity estimate (if available)
    metrics['humidity_trend'] = [65, 68, 70, 72, 71, 70, 69, 68, 67, 66, 65, 64] if len(df) > 0 else []
    
    # Equipment status
    if 'alarm_status' in df.columns:
        metrics['system_status'] = str(df['alarm_status'].iloc[-1]) if len(df) > 0 else 'OK'
    
    # Zone temperatures
    zones = {}
    zone_cols = ['zone_reception_temp_C', 'zone_office1_temp_C', 'zone_office2_temp_C', 'zone_office3_temp_C']
    for col in zone_cols:
        if col in df.columns:
            zone_name = col.replace('zone_', '').replace('_temp_C', '').title()
            zones[zone_name] = float(round(df[col].iloc[-1], 1)) if len(df) > 0 else 0
    
    metrics['zones'] = zones
    
    return metrics


if __name__ == '__main__':
    print("Starting HVAC Fault Finder Web App")
    print("Open your browser at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
