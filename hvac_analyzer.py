import pandas as pd
import numpy as np
from typing import Dict

class HVACFaultAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.faults = []
        self.recommendations = {}

    def analyze(self) -> Dict:
        self.detect_supply_temp_out_of_range()
        self.detect_short_cycling()
        self.detect_simultaneous_heating_cooling()
        self.detect_schedule_mismatch()
        self.detect_high_humidity()
        self.detect_zone_sensor_failure()
        self.score_faults()
        
        faults = []
        for fault in sorted(self.faults, key=lambda x: x['severity_score'], reverse=True):
            converted_fault = {}
            for key, value in fault.items():
                if isinstance(value, (np.integer, np.floating)):
                    converted_fault[key] = int(value) if isinstance(value, np.integer) else float(value)
                else:
                    converted_fault[key] = value
            faults.append(converted_fault)

        return {'faults': faults, 'recommendations': self.recommendations, 'summary': self._generate_summary()}

    def detect_supply_temp_out_of_range(self):
        if 'supply_air_temp_C' in self.df.columns and 'supply_air_temp_setpoint_C' in self.df.columns:
            diff = abs(self.df['supply_air_temp_C'] - self.df['supply_air_temp_setpoint_C'])
            out_of_range = (diff > 2.0)
            if out_of_range.sum() > 0:
                pct = (out_of_range.sum() / len(self.df)) * 100
                if pct > 5:
                    self.faults.append({
                        'name': 'Supply Temperature out-of-range',
                        'type': 'supply_temp_out_of_range',
                        'severity': 'Critical',
                        'severity_score': 90,
                        'percentage': round(pct, 2),
                        'impact': 'COMFORT & ENERGY - Supply air not meeting setpoint requirements'
                    })
                    self.recommendations['supply_temp_out_of_range'] = {'actions': ['Check chiller/boiler output', 'Inspect coil for freezing']}

    def detect_short_cycling(self):
        if 'fan_status' in self.df.columns:
            transitions = self.df['fan_status'].diff().abs().sum()
            cycles = transitions / 2
            if cycles > (len(self.df) / 4 / 2): # more than 1 cycle every 2 hours roughly
                self.faults.append({
                    'name': 'Short cycling',
                    'type': 'short_cycling',
                    'severity': 'Alert',
                    'severity_score': 85,
                    'percentage': 100,
                    'impact': 'WEAR & TEAR - Frequent start/stops reduce equipment lifespan'
                })
                self.recommendations['short_cycling'] = {'actions': ['Check thermostat deadbands and compressor staging']}

    def detect_simultaneous_heating_cooling(self):
        simultaneous = (self.df['heating_valve_cmd_pct'] > 5) & (self.df['cooling_valve_cmd_pct'] > 5)
        if simultaneous.sum() > 0:
            pct = (simultaneous.sum() / len(self.df)) * 100
            if pct > 2:
                self.faults.append({
                    'name': 'Simultaneous Heating & cooling', 'type': 'simultaneous_heating_cooling',
                    'severity': 'Critical', 'severity_score': 95, 'percentage': round(pct, 2),
                    'impact': 'ENERGY WASTE - Systems fighting each other'
                })
                self.recommendations['simultaneous_heating_cooling'] = {'actions': ['Inspect VAV box dampers and reheat valves']}

    def detect_schedule_mismatch(self):
        unoccupied_running = (self.df['occupancy_mode'] == 'UNOCCUPIED') & (self.df['fan_status'] == 1)
        if unoccupied_running.sum() > 0:
            pct = (unoccupied_running.sum() / len(self.df)) * 100
            if pct > 5:
                self.faults.append({
                    'name': 'Schedule mismatch', 'type': 'schedule_mismatch',
                    'severity': 'Warning', 'severity_score': 70, 'percentage': round(pct, 2),
                    'impact': 'ENERGY WASTE - System running unoccupied'
                })
                self.recommendations['schedule_mismatch'] = {'actions': ['Review occupancy settings']}

    def detect_high_humidity(self):
        if 'return_air_relative_humidity_pct' in self.df.columns:
            high_hum = self.df['return_air_relative_humidity_pct'] > 60
            if high_hum.sum() > 0:
                pct = (high_hum.sum() / len(self.df)) * 100
                if pct > 10:
                    self.faults.append({
                        'name': 'High Humidity Levels', 'type': 'high_humidity_levels',
                        'severity': 'Warning', 'severity_score': 75, 'percentage': round(pct, 2),
                        'impact': 'IAQ - Risk of mold and occupant discomfort'
                    })
                    self.recommendations['high_humidity_levels'] = {'actions': ['Verify cooling coil discharge temperatures']}

    def detect_zone_sensor_failure(self):
        zones = ['zone_office1_temp_C', 'zone_office2_temp_C', 'zone_office3_temp_C']
        for zone in zones:
            if zone in self.df.columns:
                rolling_std = self.df[zone].rolling(window=12).std()
                if (rolling_std < 0.05).sum() > 5:
                    self.faults.append({
                        'name': 'Zone Sensor failure', 'type': 'zone_sensor_failure',
                        'severity': 'Alert', 'severity_score': 80, 'percentage': 100,
                        'impact': 'OPERATION - Unreliable control decisions'
                    })
                    self.recommendations['zone_sensor_failure'] = {'actions': ['Check wiring or replace sensor head']}
                    break

    def score_faults(self):
        pass

    def _generate_summary(self):
        return {"total_faults": len(self.faults), "critical_count": sum(1 for f in self.faults if f['severity'] == 'Critical')}
