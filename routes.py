import json
import logging
from datetime import datetime, timedelta
from flask import render_template, jsonify
from app import app
from weather_service import get_weather_condition

# Load training plan
with open('training_plan.json', 'r') as f:
    training_data = json.load(f)

def get_daily_workout():
    """Get today's workout based on the date and training plan cycle"""
    try:
        # Calculate day of training cycle (2-year plan = 730 days)
        start_date = datetime(2024, 9, 1)  # Training plan start date
        today = datetime.now()
        days_since_start = (today - start_date).days
        
        # Cycle through the training plan
        cycle_day = days_since_start % len(training_data['daily_workouts'])
        
        return training_data['daily_workouts'][cycle_day]
    except Exception as e:
        logging.error(f"Error getting daily workout: {e}")
        return {
            "day": 1,
            "focus": "Recovery",
            "outdoor_workout": "Light jog and stretching",
            "indoor_workout": "Mobility and flexibility routine"
        }

@app.route('/')
def index():
    """Main page route"""
    try:
        # Get today's workout
        daily_workout = get_daily_workout()
        
        # Get weather condition
        weather_condition = get_weather_condition()
        
        # Determine which workout to show based on weather
        if weather_condition in ['clear', 'partly_cloudy']:
            recommended_workout = daily_workout.get('outdoor_workout', daily_workout.get('indoor_workout', 'Rest day'))
            workout_type = 'outdoor'
        else:
            recommended_workout = daily_workout.get('indoor_workout', daily_workout.get('outdoor_workout', 'Rest day'))
            workout_type = 'indoor'
        
        # Get additional data
        form_drills = training_data.get('form_drills', [])
        step_patterns = training_data.get('step_patterns', [])
        goals = training_data.get('progression_goals', [])
        
        return render_template('index.html',
                             daily_workout=daily_workout,
                             recommended_workout=recommended_workout,
                             workout_type=workout_type,
                             weather_condition=weather_condition,
                             form_drills=form_drills,
                             step_patterns=step_patterns,
                             goals=goals)
    
    except Exception as e:
        logging.error(f"Error in index route: {e}")
        return render_template('index.html',
                             daily_workout={"focus": "Error", "outdoor_workout": "Unable to load workout"},
                             recommended_workout="Please check back later",
                             workout_type="error",
                             weather_condition="unknown",
                             form_drills=[],
                             step_patterns=[],
                             goals=[])

@app.route('/api/weather')
def api_weather():
    """API endpoint for weather data"""
    try:
        condition = get_weather_condition()
        return jsonify({"condition": condition})
    except Exception as e:
        logging.error(f"Error in weather API: {e}")
        return jsonify({"condition": "unknown", "error": str(e)})
