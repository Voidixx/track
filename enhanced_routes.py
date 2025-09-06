"""
Enhanced routes for Tyler's 300m Hurdles Training Hub
Includes training logs, video uploads, coach communication, and statistics
"""
import os
import json
import logging
from datetime import datetime, timedelta, date
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import TrainingLog, PersonalRecord, VideoAnalysis, CoachMessage, WeeklyStats, Goal
from weather_service import get_weather_condition

# Load training plan
with open('training_plan.json', 'r') as f:
    training_data = json.load(f)

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'wmv'}
UPLOAD_FOLDER = 'uploads/videos'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
def dashboard():
    """Main dashboard with today's workout and quick stats"""
    try:
        # Get today's workout
        daily_workout = get_daily_workout()
        weather_condition = get_weather_condition()
        
        # Determine which workout to show based on weather
        if weather_condition in ['clear', 'partly_cloudy']:
            recommended_workout = daily_workout.get('outdoor_workout', daily_workout.get('indoor_workout', 'Rest day'))
            workout_type = 'outdoor'
        else:
            recommended_workout = daily_workout.get('indoor_workout', daily_workout.get('outdoor_workout', 'Rest day'))
            workout_type = 'indoor'
        
        # Check if today's workout is already logged
        today_log = TrainingLog.query.filter_by(date=date.today()).first()
        
        # Get recent stats
        recent_logs = TrainingLog.query.filter_by(completed=True).order_by(TrainingLog.date.desc()).limit(7).all()
        completion_rate = len(recent_logs) / 7 * 100 if recent_logs else 0
        
        # Get latest personal record
        latest_pr = PersonalRecord.query.filter_by(event='300m Hurdles').order_by(PersonalRecord.date_achieved.desc()).first()
        
        # Get unread messages from coach
        unread_messages = CoachMessage.query.filter_by(sender='coach', is_read=False).count()
        
        # Get additional data
        form_drills = training_data.get('form_drills', [])
        step_patterns = training_data.get('step_patterns', [])
        goals = training_data.get('progression_goals', [])
        
        return render_template('dashboard.html',
                             daily_workout=daily_workout,
                             recommended_workout=recommended_workout,
                             workout_type=workout_type,
                             weather_condition=weather_condition,
                             today_log=today_log,
                             completion_rate=completion_rate,
                             latest_pr=latest_pr,
                             unread_messages=unread_messages,
                             form_drills=form_drills,
                             step_patterns=step_patterns,
                             goals=goals)
    
    except Exception as e:
        logging.error(f"Error in dashboard route: {e}")
        return render_template('dashboard.html',
                             daily_workout={"focus": "Error", "outdoor_workout": "Unable to load workout"},
                             recommended_workout="Please check back later",
                             workout_type="error",
                             weather_condition="unknown",
                             today_log=None,
                             completion_rate=0,
                             latest_pr=None,
                             unread_messages=0,
                             form_drills=[],
                             step_patterns=[],
                             goals=[])

@app.route('/log_workout', methods=['GET', 'POST'])
def log_workout():
    """Log today's workout completion"""
    if request.method == 'POST':
        try:
            # Get form data
            completed = request.form.get('completed') == 'on'
            notes = request.form.get('notes', '')
            difficulty_rating = int(request.form.get('difficulty_rating', 3))
            energy_level = int(request.form.get('energy_level', 3))
            
            # Check if log already exists for today
            today_log = TrainingLog.query.filter_by(date=date.today()).first()
            
            if today_log:
                # Update existing log
                today_log.completed = completed
                today_log.completion_time = datetime.now() if completed else None
                today_log.notes = notes
                today_log.difficulty_rating = difficulty_rating
                today_log.energy_level = energy_level
            else:
                # Create new log
                daily_workout = get_daily_workout()
                weather_condition = get_weather_condition()
                
                if weather_condition in ['clear', 'partly_cloudy']:
                    workout_description = daily_workout.get('outdoor_workout', 'Rest day')
                    workout_type = 'outdoor'
                else:
                    workout_description = daily_workout.get('indoor_workout', 'Rest day')
                    workout_type = 'indoor'
                
                today_log = TrainingLog(
                    date=date.today(),
                    workout_type=workout_type,
                    workout_focus=daily_workout.get('focus', 'Training'),
                    workout_description=workout_description,
                    completed=completed,
                    completion_time=datetime.now() if completed else None,
                    notes=notes,
                    difficulty_rating=difficulty_rating,
                    energy_level=energy_level,
                    weather_condition=weather_condition
                )
                db.session.add(today_log)
            
            db.session.commit()
            flash('Workout logged successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            logging.error(f"Error logging workout: {e}")
            flash('Error logging workout. Please try again.', 'error')
    
    # GET request - show the form
    daily_workout = get_daily_workout()
    today_log = TrainingLog.query.filter_by(date=date.today()).first()
    
    return render_template('log_workout.html', daily_workout=daily_workout, today_log=today_log)

@app.route('/training_log')
def training_log():
    """View training log history"""
    page = request.args.get('page', 1, type=int)
    logs = TrainingLog.query.order_by(TrainingLog.date.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    # Calculate stats
    total_workouts = TrainingLog.query.filter_by(completed=True).count()
    total_planned = TrainingLog.query.count()
    avg_difficulty = db.session.query(db.func.avg(TrainingLog.difficulty_rating)).filter_by(completed=True).scalar() or 0
    
    return render_template('training_log.html', 
                         logs=logs, 
                         total_workouts=total_workouts,
                         total_planned=total_planned,
                         avg_difficulty=round(avg_difficulty, 1))

@app.route('/personal_records', methods=['GET', 'POST'])
def personal_records():
    """Manage personal records and race times"""
    if request.method == 'POST':
        try:
            # Add new personal record
            event = request.form.get('event')
            time_str = request.form.get('time')
            date_str = request.form.get('date', '')
            date_achieved = datetime.strptime(date_str, '%Y-%m-%d').date()
            meet_name = request.form.get('meet_name', '')
            conditions = request.form.get('conditions', '')
            notes = request.form.get('notes', '')
            is_official = request.form.get('is_official') == 'on'
            
            # Convert time string to seconds (assume format MM:SS.ss)
            if time_str and ':' in time_str:
                parts = time_str.split(':')
                minutes = float(parts[0])
                seconds = float(parts[1])
                time_seconds = minutes * 60 + seconds
            else:
                time_seconds = float(time_str) if time_str else 0.0
            
            pr = PersonalRecord(
                event=event,
                time_seconds=time_seconds,
                date_achieved=date_achieved,
                meet_name=meet_name,
                conditions=conditions,
                notes=notes,
                is_official=is_official
            )
            
            db.session.add(pr)
            db.session.commit()
            flash('Personal record added successfully!', 'success')
            return redirect(url_for('personal_records'))
            
        except Exception as e:
            logging.error(f"Error adding personal record: {e}")
            flash('Error adding personal record. Please try again.', 'error')
    
    # Get personal records grouped by event
    records = PersonalRecord.query.order_by(PersonalRecord.date_achieved.desc()).all()
    
    # Get best times for each event
    best_times = {}
    for record in records:
        if record.event not in best_times or record.time_seconds < best_times[record.event].time_seconds:
            best_times[record.event] = record
    
    return render_template('personal_records.html', records=records, best_times=best_times)

@app.route('/video_analysis', methods=['GET', 'POST'])
def video_analysis():
    """Upload and manage training videos"""
    if request.method == 'POST':
        try:
            if 'video' not in request.files:
                flash('No video file selected', 'error')
                return redirect(request.url)
            
            file = request.files['video']
            if file.filename == '':
                flash('No video file selected', 'error')
                return redirect(request.url)
            
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                
                # Ensure directory exists
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(file_path)
                
                # Save to database
                video = VideoAnalysis(
                    filename=filename,
                    original_filename=file.filename,
                    file_path=file_path,
                    video_type=request.form.get('video_type', ''),
                    analysis_notes=request.form.get('analysis_notes', ''),
                    technique_focus=request.form.get('technique_focus', '')
                )
                
                db.session.add(video)
                db.session.commit()
                flash('Video uploaded successfully!', 'success')
                return redirect(url_for('video_analysis'))
            else:
                flash('Invalid file type. Please upload MP4, MOV, AVI, or WMV files.', 'error')
                
        except Exception as e:
            logging.error(f"Error uploading video: {e}")
            flash('Error uploading video. Please try again.', 'error')
    
    # Get uploaded videos
    videos = VideoAnalysis.query.order_by(VideoAnalysis.upload_date.desc()).all()
    
    return render_template('video_analysis.html', videos=videos)

@app.route('/coach_communication', methods=['GET', 'POST'])
def coach_communication():
    """Coach messaging system"""
    if request.method == 'POST':
        try:
            message = request.form.get('message')
            category = request.form.get('category', 'general')
            priority = request.form.get('priority', 'normal')
            
            coach_message = CoachMessage(
                sender='tyler',
                message=message,
                category=category,
                priority=priority
            )
            
            db.session.add(coach_message)
            db.session.commit()
            flash('Message sent to coach!', 'success')
            return redirect(url_for('coach_communication'))
            
        except Exception as e:
            logging.error(f"Error sending message: {e}")
            flash('Error sending message. Please try again.', 'error')
    
    # Get messages
    messages = CoachMessage.query.order_by(CoachMessage.timestamp.desc()).limit(50).all()
    
    # Mark messages as read when viewing
    unread_coach_messages = CoachMessage.query.filter_by(sender='coach', is_read=False).all()
    for msg in unread_coach_messages:
        msg.is_read = True
    db.session.commit()
    
    return render_template('coach_communication.html', messages=messages)

@app.route('/statistics')
def statistics():
    """Training statistics and analytics"""
    try:
        # Get various statistics
        total_workouts = TrainingLog.query.filter_by(completed=True).count()
        total_days_trained = TrainingLog.query.count()
        completion_rate = (total_workouts / total_days_trained * 100) if total_days_trained > 0 else 0
        
        # Weekly completion rates
        weekly_stats = []
        for i in range(8):  # Last 8 weeks
            week_start = date.today() - timedelta(weeks=i+1)
            week_end = week_start + timedelta(days=6)
            
            week_workouts = TrainingLog.query.filter(
                TrainingLog.date >= week_start,
                TrainingLog.date <= week_end,
                TrainingLog.completed == True
            ).count()
            
            weekly_stats.append({
                'week': f"Week of {week_start.strftime('%b %d')}",
                'completed': week_workouts,
                'percentage': min(100, week_workouts / 7 * 100)
            })
        
        weekly_stats.reverse()  # Show oldest to newest
        
        # Recent personal records
        recent_prs = PersonalRecord.query.order_by(PersonalRecord.date_achieved.desc()).limit(5).all()
        
        # Workout focus breakdown
        focus_stats = db.session.query(
            TrainingLog.workout_focus,
            db.func.count(TrainingLog.id)
        ).filter_by(completed=True).group_by(TrainingLog.workout_focus).all()
        
        return render_template('statistics.html',
                             total_workouts=total_workouts,
                             completion_rate=round(completion_rate, 1),
                             weekly_stats=weekly_stats,
                             recent_prs=recent_prs,
                             focus_stats=focus_stats)
        
    except Exception as e:
        logging.error(f"Error loading statistics: {e}")
        return render_template('statistics.html',
                             total_workouts=0,
                             completion_rate=0,
                             weekly_stats=[],
                             recent_prs=[],
                             focus_stats=[])

@app.route('/api/weather')
def api_weather():
    """API endpoint for weather data"""
    try:
        condition = get_weather_condition()
        return jsonify({"condition": condition})
    except Exception as e:
        logging.error(f"Error in weather API: {e}")
        return jsonify({"condition": "unknown", "error": str(e)})