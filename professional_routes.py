"""
Professional Enhanced Routes for Tyler's Elite Training Hub
Integrates real Athletic.net/MileSplit data, rankings, and advanced features
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
from athletic_data_service import athletic_service

# Load training plan
with open('training_plan.json', 'r') as f:
    training_data = json.load(f)

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'wmv', 'jpg', 'jpeg', 'png', 'gif'}
UPLOAD_FOLDER = 'uploads/videos'
PHOTO_FOLDER = 'uploads/photos'

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

@app.route('/professional')
@app.route('/')
def professional_dashboard():
    """Main professional dashboard with comprehensive analytics"""
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
        
        # Get Tyler's real athletic data
        current_stats = athletic_service.get_tyler_current_stats()
        rankings = athletic_service.get_ranking_estimates()
        competitor_analysis = athletic_service.get_competitor_analysis()
        milesplit_articles = athletic_service.get_milesplit_mentions()
        
        # Check if today's workout is already logged
        today_log = TrainingLog.query.filter_by(date=date.today()).first()
        
        # Get recent stats for dashboard
        recent_logs = TrainingLog.query.filter_by(completed=True).order_by(TrainingLog.date.desc()).limit(7).all()
        completion_rate = len(recent_logs) / 7 * 100 if recent_logs else 0
        
        # Get latest personal record
        latest_pr = PersonalRecord.query.filter_by(event='300m Hurdles').order_by(PersonalRecord.date_achieved.desc()).first()
        
        # Get unread coach messages
        unread_messages = CoachMessage.query.filter_by(sender='coach', is_read=False).count()
        
        # Get form drills and step patterns
        form_drills = training_data.get('form_drills', [])
        step_patterns = training_data.get('step_patterns', [])
        goals = training_data.get('progression_goals', [])
        
        # Get recent videos
        recent_videos = VideoAnalysis.query.order_by(VideoAnalysis.upload_date.desc()).limit(3).all()
        
        # Weekly training summary
        week_start = date.today() - timedelta(days=date.today().weekday())
        weekly_workouts = TrainingLog.query.filter(
            TrainingLog.date >= week_start,
            TrainingLog.date <= week_start + timedelta(days=6)
        ).all()
        
        completed_this_week = len([w for w in weekly_workouts if w.completed])
        
        return render_template('professional_dashboard.html',
                             # Core data
                             daily_workout=daily_workout,
                             recommended_workout=recommended_workout,
                             workout_type=workout_type,
                             weather_condition=weather_condition,
                             
                             # Athletic performance data
                             current_stats=current_stats,
                             rankings=rankings,
                             competitor_analysis=competitor_analysis,
                             latest_pr=latest_pr,
                             
                             # Training data
                             today_log=today_log,
                             completion_rate=completion_rate,
                             completed_this_week=completed_this_week,
                             weekly_workouts_planned=7,
                             
                             # Media and analysis
                             recent_videos=recent_videos,
                             milesplit_articles=milesplit_articles,
                             
                             # Communication
                             unread_messages=unread_messages,
                             
                             # Training guides
                             form_drills=form_drills,
                             step_patterns=step_patterns,
                             goals=goals)
    
    except Exception as e:
        logging.error(f"Error in professional dashboard route: {e}")
        return render_template('professional_dashboard.html',
                             daily_workout={"focus": "Error", "outdoor_workout": "Unable to load workout"},
                             recommended_workout="Please check back later",
                             workout_type="error",
                             weather_condition="unknown",
                             current_stats={},
                             rankings={},
                             competitor_analysis={},
                             latest_pr=None,
                             today_log=None,
                             completion_rate=0,
                             completed_this_week=0,
                             weekly_workouts_planned=7,
                             recent_videos=[],
                             milesplit_articles=[],
                             unread_messages=0,
                             form_drills=[],
                             step_patterns=[],
                             goals=[])

@app.route('/api/rankings')
def api_rankings():
    """API endpoint to get current rankings and competitor data"""
    try:
        rankings = athletic_service.get_ranking_estimates()
        competitors = athletic_service.get_competitor_analysis()
        
        return jsonify({
            'rankings': rankings,
            'competitors': competitors,
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        logging.error(f"Error fetching rankings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync-athletic-data')
def api_sync_athletic_data():
    """Sync data from Athletic.net and MileSplit"""
    try:
        athletic_service.sync_to_database()
        return jsonify({'success': True, 'message': 'Data synced successfully'})
    except Exception as e:
        logging.error(f"Error syncing athletic data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/log_workout', methods=['GET', 'POST'])
def log_workout():
    """Enhanced workout logging with photo upload"""
    if request.method == 'POST':
        try:
            # Get form data
            completed = request.form.get('completed') == 'on'
            notes = request.form.get('notes', '')
            difficulty_rating = int(request.form.get('difficulty_rating', 3))
            energy_level = int(request.form.get('energy_level', 3))
            workout_duration = request.form.get('workout_duration', '')
            
            # Handle photo uploads
            uploaded_photos = []
            for file_key in request.files:
                if file_key.startswith('photo_'):
                    file = request.files[file_key]
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                        filename = timestamp + filename
                        
                        os.makedirs(PHOTO_FOLDER, exist_ok=True)
                        file_path = os.path.join(PHOTO_FOLDER, filename)
                        file.save(file_path)
                        uploaded_photos.append(file_path)
            
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
            
            # If photos were uploaded, redirect to form analysis
            if uploaded_photos:
                flash(f'Uploaded {len(uploaded_photos)} training photos!', 'success')
            
            return redirect(url_for('professional_dashboard'))
            
        except Exception as e:
            logging.error(f"Error logging workout: {e}")
            flash('Error logging workout. Please try again.', 'error')
    
    # GET request - show the form
    daily_workout = get_daily_workout()
    today_log = TrainingLog.query.filter_by(date=date.today()).first()
    
    return render_template('log_workout.html', daily_workout=daily_workout, today_log=today_log)

@app.route('/video_analysis', methods=['GET', 'POST'])
def video_analysis():
    """Enhanced video analysis with AI-powered insights"""
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
                
                flash('Video uploaded successfully! Analysis will be ready shortly.', 'success')
                return redirect(url_for('video_analysis'))
            else:
                flash('Invalid file type. Please upload MP4, MOV, AVI, or WMV files.', 'error')
                
        except Exception as e:
            logging.error(f"Error uploading video: {e}")
            flash('Error uploading video. Please try again.', 'error')
    
    # Get uploaded videos with enhanced analysis
    videos = VideoAnalysis.query.order_by(VideoAnalysis.upload_date.desc()).all()
    
    return render_template('video_analysis.html', videos=videos)

@app.route('/personal_records', methods=['GET', 'POST'])
def personal_records():
    """Enhanced personal records with Athletic.net integration"""
    if request.method == 'POST':
        try:
            # Add new personal record
            event = request.form.get('event')
            time_str = request.form.get('time', '')
            date_str = request.form.get('date', '')
            meet_name = request.form.get('meet_name', '')
            conditions = request.form.get('conditions', '')
            notes = request.form.get('notes', '')
            is_official = request.form.get('is_official') == 'on'
            
            if not date_str:
                flash('Date is required', 'error')
                return redirect(request.url)
            
            date_achieved = datetime.strptime(date_str, '%Y-%m-%d').date()
            
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
    
    # Get personal records with enhanced analytics
    records = PersonalRecord.query.order_by(PersonalRecord.date_achieved.desc()).all()
    
    # Get best times for each event
    best_times = {}
    for record in records:
        if record.event not in best_times or record.time_seconds < best_times[record.event].time_seconds:
            best_times[record.event] = record
    
    # Get Tyler's real stats for comparison
    current_stats = athletic_service.get_tyler_current_stats()
    rankings = athletic_service.get_ranking_estimates()
    
    return render_template('personal_records.html', 
                         records=records, 
                         best_times=best_times,
                         current_stats=current_stats,
                         rankings=rankings)

@app.route('/coach_communication', methods=['GET', 'POST'])
def coach_communication():
    """Enhanced coach messaging with priority and categories"""
    if request.method == 'POST':
        try:
            message = request.form.get('message', '')
            category = request.form.get('category', 'general')
            priority = request.form.get('priority', 'normal')
            
            if not message.strip():
                flash('Message cannot be empty', 'error')
                return redirect(request.url)
            
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
    
    # Get messages with enhanced filtering
    messages = CoachMessage.query.order_by(CoachMessage.timestamp.desc()).limit(50).all()
    
    # Mark coach messages as read when viewing
    unread_coach_messages = CoachMessage.query.filter_by(sender='coach', is_read=False).all()
    for msg in unread_coach_messages:
        msg.is_read = True
    db.session.commit()
    
    return render_template('coach_communication.html', messages=messages)

@app.route('/statistics')
def statistics():
    """Enhanced statistics dashboard with charts and analytics"""
    try:
        # Get comprehensive statistics
        total_workouts = TrainingLog.query.filter_by(completed=True).count()
        total_days_trained = TrainingLog.query.count()
        completion_rate = (total_workouts / total_days_trained * 100) if total_days_trained > 0 else 0
        
        # Weekly completion rates for last 12 weeks
        weekly_stats = []
        for i in range(12):
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
        
        # Performance progression
        hurdle_records = PersonalRecord.query.filter_by(event='300m Hurdles').order_by(PersonalRecord.date_achieved.asc()).all()
        
        # Training focus breakdown
        focus_stats = db.session.query(
            TrainingLog.workout_focus,
            db.func.count(TrainingLog.id)
        ).filter_by(completed=True).group_by(TrainingLog.workout_focus).all()
        
        # Get ranking and competitor data
        rankings = athletic_service.get_ranking_estimates()
        competitor_analysis = athletic_service.get_competitor_analysis()
        
        return render_template('statistics.html',
                             total_workouts=total_workouts,
                             completion_rate=round(completion_rate, 1),
                             weekly_stats=weekly_stats,
                             hurdle_records=hurdle_records,
                             focus_stats=focus_stats,
                             rankings=rankings,
                             competitor_analysis=competitor_analysis)
        
    except Exception as e:
        logging.error(f"Error loading statistics: {e}")
        return render_template('statistics.html',
                             total_workouts=0,
                             completion_rate=0,
                             weekly_stats=[],
                             hurdle_records=[],
                             focus_stats=[],
                             rankings={},
                             competitor_analysis={})

@app.route('/api/training-calendar')
def api_training_calendar():
    """API endpoint for training calendar events"""
    try:
        logs = TrainingLog.query.all()
        events = []
        
        for log in logs:
            color = '#28a745' if log.completed else '#dc3545'
            if log.workout_focus == 'Speed Endurance':
                color = '#007bff'
            elif log.workout_focus == 'Technique Work':
                color = '#17a2b8'
            elif log.workout_focus == 'Strength Training':
                color = '#fd7e14'
            
            events.append({
                'title': log.workout_focus,
                'start': log.date.isoformat(),
                'color': color,
                'completed': log.completed,
                'notes': log.notes or ''
            })
        
        return jsonify(events)
        
    except Exception as e:
        logging.error(f"Error loading calendar events: {e}")
        return jsonify([]), 500

@app.route('/api/weather')
def api_weather():
    """Enhanced weather API with detailed information"""
    try:
        condition = get_weather_condition()
        
        # Enhanced weather response
        weather_data = {
            'condition': condition,
            'temperature': 72,  # Mock data - integrate with real weather API
            'humidity': 45,
            'wind_speed': 8,
            'recommendation': 'Perfect for outdoor training!' if condition == 'clear' else 'Consider indoor alternatives'
        }
        
        return jsonify(weather_data)
    except Exception as e:
        logging.error(f"Error in weather API: {e}")
        return jsonify({"condition": "unknown", "error": str(e)})

# Additional API endpoints for the professional dashboard

@app.route('/api/progress-chart')
def api_progress_chart():
    """API endpoint for progress chart data"""
    try:
        records = PersonalRecord.query.filter_by(event='300m Hurdles').order_by(PersonalRecord.date_achieved.asc()).all()
        
        chart_data = {
            'labels': [],
            'times': [],
            'dates': []
        }
        
        for record in records:
            chart_data['labels'].append(record.date_achieved.strftime('%b %Y'))
            chart_data['times'].append(record.time_seconds)
            chart_data['dates'].append(record.date_achieved.isoformat())
        
        return jsonify(chart_data)
        
    except Exception as e:
        logging.error(f"Error loading progress chart: {e}")
        return jsonify({'labels': [], 'times': [], 'dates': []})

@app.route('/api/milesplit-news')
def api_milesplit_news():
    """API endpoint for MileSplit news and articles"""
    try:
        articles = athletic_service.get_milesplit_mentions()
        return jsonify(articles)
    except Exception as e:
        logging.error(f"Error loading MileSplit news: {e}")
        return jsonify([])

# Legacy route redirects
@app.route('/dashboard')
def dashboard_redirect():
    return redirect(url_for('professional_dashboard'))

@app.route('/training_log')
def training_log():
    """View training log history with enhanced filtering"""
    page = request.args.get('page', 1, type=int)
    logs = TrainingLog.query.order_by(TrainingLog.date.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    # Calculate enhanced stats
    total_workouts = TrainingLog.query.filter_by(completed=True).count()
    total_planned = TrainingLog.query.count()
    avg_difficulty = db.session.query(db.func.avg(TrainingLog.difficulty_rating)).filter_by(completed=True).scalar() or 0
    
    return render_template('training_log.html', 
                         logs=logs, 
                         total_workouts=total_workouts,
                         total_planned=total_planned,
                         avg_difficulty=round(avg_difficulty, 1))

# Auto-sync Tyler's Athletic.net data on startup (using app context)
with app.app_context():
    try:
        athletic_service.sync_to_database()
        logging.info("Successfully initialized athletic data from Athletic.net")
    except Exception as e:
        logging.error(f"Error initializing athletic data: {e}")