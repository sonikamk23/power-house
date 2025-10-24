from flask import Flask, render_template, Response, request, jsonify
import json
import random
from datetime import datetime
import time

app = Flask(__name__)

buildings = ["Admin Block", "Engineering Block", "Science Block", "Library", "Hostel Zone"]
alerts_log = []
historical_data = []
COST_PER_KWH = 0.12

def generate_data():
    global alerts_log, historical_data
    while True:
        timestamp = datetime.now()
        readings = []
        total_power = 0
        
        for b in buildings:
            power = round(random.uniform(10, 150), 2)
            total_power += power
            status = "high" if power > 120 else "normal"
            
            hourly_cost = power * COST_PER_KWH
            daily_cost = hourly_cost * 24
            monthly_cost = daily_cost * 30
            
            readings.append({
                "building": b,
                "power": power,
                "status": status,
                "hourly_cost": round(hourly_cost, 2),
                "daily_cost": round(daily_cost, 2),
                "monthly_cost": round(monthly_cost, 2)
            })
            
            if power > 130:
                alert = {
                    "building": b,
                    "power": power,
                    "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "severity": "critical" if power > 140 else "warning",
                    "estimated_cost": round(hourly_cost, 2)
                }
                alerts_log.append(alert)
                if len(alerts_log) > 50:
                    alerts_log.pop(0)
        
        total_hourly_cost = round(total_power * COST_PER_KWH, 2)
        total_daily_cost = round(total_hourly_cost * 24, 2)
        total_monthly_cost = round(total_daily_cost * 30, 2)
        total_annual_cost = round(total_daily_cost * 365, 2)
        
        data = {
            "time": timestamp.strftime("%H:%M:%S"),
            "date": timestamp.strftime("%B %d, %Y"),
            "readings": readings,
            "total": round(total_power, 2),
            "alerts": len([a for a in alerts_log if a.get('severity') == 'critical']),
            "cost_rate": COST_PER_KWH,
            "hourly_cost": total_hourly_cost,
            "daily_cost": total_daily_cost,
            "monthly_cost": total_monthly_cost,
            "annual_cost": total_annual_cost
        }
        
        historical_data.append({
            "timestamp": timestamp.isoformat(),
            "data": readings,
            "total": round(total_power, 2),
            "total_cost": total_hourly_cost
        })
        if len(historical_data) > 100:
            historical_data.pop(0)
        
        yield f"data: {json.dumps(data)}\n\n"
        time.sleep(3)

def get_ai_suggestion(building, problem):
    problem_lower = problem.lower()
    
    if "high" in problem_lower or "consumption" in problem_lower:
        return {
            "title": "High Energy Consumption",
            "solution": f"For {building}:\n\n• Install LED lighting (75% savings)\n• Optimize HVAC schedules\n• Add motion sensors in corridors\n• Conduct comprehensive energy audit\n• Implement smart power management systems\n• Set automated lighting timers\n• Upgrade to energy-efficient appliances",
            "priority": "high",
            "estimated_savings": "30-40% cost reduction",
            "implementation_time": "3-6 months",
            "implementation_cost": "$15,000 - $25,000",
            "roi_period": "2-3 years",
            "cost_breakdown": "LED: $5,000 | Sensors: $3,000 | Smart Systems: $8,000 | Audit: $2,000"
        }
    elif "lighting" in problem_lower:
        return {
            "title": "Lighting Issues",
            "solution": f"For {building}:\n\n• Replace with LED bulbs (ROI: 1-2 years)\n• Install daylight harvesting sensors\n• Add occupancy-based automatic controls\n• Implement zone-based lighting control\n• Use timers for outdoor lighting\n• Clean fixtures and lenses regularly\n• Check and repair faulty wiring",
            "priority": "medium",
            "estimated_savings": "40-60% lighting cost reduction",
            "implementation_time": "1-2 months",
            "implementation_cost": "$8,000 - $12,000",
            "roi_period": "1.5-2 years",
            "cost_breakdown": "LED Bulbs: $4,000 | Sensors: $3,000 | Controls: $2,500 | Installation: $1,500"
        }
    elif "hvac" in problem_lower or "ac" in problem_lower:
        return {
            "title": "HVAC Optimization",
            "solution": f"For {building}:\n\n• Service HVAC units quarterly\n• Install programmable smart thermostats\n• Seal air leaks in ducts (saves 20-30%)\n• Replace dirty filters monthly\n• Set optimal temperature: 24°C (75°F)\n• Implement zone-based cooling\n• Add ceiling fans to improve circulation\n• Use night cooling when possible",
            "priority": "high",
            "estimated_savings": "25-35% HVAC cost reduction",
            "implementation_time": "2-4 months",
            "implementation_cost": "$18,000 - $30,000",
            "roi_period": "3-4 years",
            "cost_breakdown": "Thermostats: $2,000 | Duct Sealing: $5,000 | Service: $3,000 | Fans: $4,000 | Controls: $8,000"
        }
    elif "equipment" in problem_lower or "malfunction" in problem_lower:
        return {
            "title": "Equipment Malfunction",
            "solution": f"For {building}:\n\n• Schedule emergency maintenance inspection\n• Replace faulty equipment with Energy Star models\n• Inspect circuit breakers and connections\n• Check voltage levels and power quality\n• Implement preventive maintenance schedule\n• Install IoT sensors for monitoring\n• Document all issues for analysis\n• Train staff on early warning signs",
            "priority": "urgent",
            "estimated_savings": "Avoid 50-80% downtime costs",
            "implementation_time": "Immediate - 2 weeks",
            "implementation_cost": "$5,000 - $15,000",
            "roi_period": "Immediate",
            "cost_breakdown": "Inspection: $500 | Repair: $3,000 | Sensors: $2,000 | Maintenance: $1,500"
        }
    else:
        return {
            "title": "General Optimization",
            "solution": f"For {building}:\n\n• Conduct detailed energy audit\n• Analyze consumption patterns\n• Identify top 5 energy consumers\n• Train staff on conservation practices\n• Upgrade to energy-efficient appliances\n• Implement automated building management\n• Set energy reduction targets (10-20%)\n• Monitor and adjust continuously",
            "priority": "medium",
            "estimated_savings": "15-30% cost reduction",
            "implementation_time": "6-12 months",
            "implementation_cost": "$20,000 - $40,000",
            "roi_period": "3-5 years",
            "cost_breakdown": "Audit: $3,000 | Upgrades: $15,000 | Automation: $12,000 | Training: $2,000"
        }

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/alerts')
def alerts():
    return render_template('alerts.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/calculator')
def calculator():
    return render_template('calculator.html')

@app.route('/stream')
def stream():
    return Response(generate_data(), mimetype='text/event-stream')

@app.route('/report-problem', methods=['POST'])
def report_problem():
    data = request.get_json()
    building = data.get('building', '')
    problem = data.get('problem', '')
    
    if building and problem:
        suggestion = get_ai_suggestion(building, problem)
        return jsonify({'status': 'success', 'suggestion': suggestion})
    else:
        return jsonify({'status': 'error', 'message': 'Please fill all fields'}), 400

@app.route('/get-alerts')
def get_alerts():
    return jsonify({'alerts': alerts_log})

@app.route('/calculate-savings', methods=['POST'])
def calculate_savings():
    data = request.get_json()
    current_usage = data.get('current_usage', 0)
    target_reduction = data.get('target_reduction', 0)
    cost_per_kwh = data.get('cost_per_kwh', 0.12)
    
    try:
        current_usage = float(current_usage)
        target_reduction = float(target_reduction)
        cost_per_kwh = float(cost_per_kwh)
        
        reduced_usage = current_usage * (1 - target_reduction / 100)
        savings_kwh = current_usage - reduced_usage
        savings_cost = savings_kwh * cost_per_kwh * 30
        annual_savings = savings_cost * 12
        
        return jsonify({
            'status': 'success',
            'current_usage': current_usage,
            'reduced_usage': round(reduced_usage, 2),
            'savings_kwh': round(savings_kwh, 2),
            'monthly_savings': round(savings_cost, 2),
            'annual_savings': round(annual_savings, 2)
        })
    except:
        return jsonify({'status': 'error', 'message': 'Invalid input'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
