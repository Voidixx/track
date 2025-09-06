"""
Enhanced AI-Powered Routes for Tyler's Elite Training Platform
Integrates video analysis, competitor tracking, predictive modeling, and endurance training
"""
import os
import json
import logging
from datetime import datetime, date, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from app import app, db
from models import TrainingLog, PersonalRecord, VideoAnalysis, CoachMessage
from ai_video_analysis import hurdle_analyzer
from competitor_scraper import competitor_analyzer
from performance_predictor import PerformancePredictor
from endurance_training_module import endurance_system

# Initialize AI systems
predictor = PerformancePredictor()

@app.route('/api/ai-video-analysis', methods=['POST'])
def api_ai_video_analysis():
    """AI-powered video analysis endpoint"""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'No video selected'}), 400
        
        if file:
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            
            # Create upload directory
            upload_dir = 'uploads/ai_analysis'
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            # Run AI analysis
            analysis_result = hurdle_analyzer.analyze_video(file_path, analysis_type='comprehensive')
            
            # Save to database
            video_analysis = VideoAnalysis(
                filename=filename,
                original_filename=file.filename,
                file_path=file_path,
                video_type=request.form.get('video_type', 'hurdle_technique'),
                analysis_notes=json.dumps(analysis_result),
                technique_focus=request.form.get('technique_focus', '300m_hurdles')
            )
            db.session.add(video_analysis)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'analysis': analysis_result,
                'video_id': video_analysis.id,
                'message': 'AI analysis completed successfully'
            })
    
    except Exception as e:
        logging.error(f"AI video analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/competitor-analysis')
def api_competitor_analysis():
    """Get comprehensive competitor analysis"""
    try:
        # Get real competitor data
        competitors = competitor_analyzer.scrape_athletic_net_competitors(grade_level=9)
        milesplit_news = competitor_analyzer.scrape_milesplit_news()
        meet_schedule = competitor_analyzer.get_regional_meet_schedule()
        
        # Analyze competitive positioning
        tyler_position = None
        for i, competitor in enumerate(competitors):
            if competitor.get('highlight'):  # Tyler's data
                tyler_position = {
                    'rank': i + 1,
                    'total_competitors': len(competitors),
                    'percentile': ((len(competitors) - i) / len(competitors)) * 100
                }
                break
        
        return jsonify({
            'competitors': competitors,
            'tyler_position': tyler_position,
            'news_articles': milesplit_news,
            'upcoming_meets': meet_schedule,
            'last_updated': datetime.now().isoformat(),
            'competitive_analysis': {
                'threats': [c for c in competitors if c.get('competitive_threat_level') == 'high_threat'],
                'close_competition': [c for c in competitors if c.get('competitive_threat_level') == 'close_competitor'],
                'improvement_targets': [c for c in competitors if c['events'].get('300m_hurdles', {}).get('pr', 999) < 45.24]
            }
        })
        
    except Exception as e:
        logging.error(f"Competitor analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance-predictions')
def api_performance_predictions():
    """Get AI-powered performance predictions"""
    try:
        consistency_level = request.args.get('consistency', 'high_consistency')
        
        # Get predictions for different timeframes
        predictions = {
            'current_season': predictor.predict_seasonal_progression('300m_hurdles', consistency_level),
            'sophomore_year': predictor.predict_future_performance('300m_hurdles', grade=10),
            'junior_year': predictor.predict_future_performance('300m_hurdles', grade=11),
            'senior_year': predictor.predict_future_performance('300m_hurdles', grade=12),
            'school_record_probability': predictor.calculate_record_probability(42.08),
            'improvement_recommendations': predictor.get_improvement_recommendations()
        }
        
        # Add training impact analysis
        training_impact = predictor.analyze_training_impact()
        predictions['training_impact'] = training_impact
        
        return jsonify(predictions)
        
    except Exception as e:
        logging.error(f"Performance prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/endurance-workout')
def api_endurance_workout():
    """Get AI-powered endurance workout recommendation"""
    try:
        training_day = int(request.args.get('day', 1))
        phase = request.args.get('phase', 'build_phase')
        
        # Get personalized endurance workout
        workout = endurance_system.get_daily_endurance_workout(training_day, phase)
        
        # Add heart rate zone information
        hr_zones = endurance_system.get_heart_rate_training_zones()
        
        # Get predicted improvements from endurance training
        weeks_training = int(request.args.get('weeks', 12))
        improvement_predictions = endurance_system.calculate_predicted_improvements(weeks_training)
        
        return jsonify({
            'workout': workout,
            'heart_rate_zones': hr_zones,
            'predicted_improvements': improvement_predictions,
            'training_phase': phase,
            'day_in_cycle': training_day % 7
        })
        
    except Exception as e:
        logging.error(f"Endurance workout error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/advanced-analytics')
def advanced_analytics():
    """Advanced analytics dashboard with all AI insights"""
    try:
        # Get comprehensive analytics data
        competitors = competitor_analyzer.scrape_athletic_net_competitors(grade_level=9)[:10]
        predictions = predictor.predict_seasonal_progression('300m_hurdles', 'high_consistency')
        
        # Get recent training data
        recent_logs = TrainingLog.query.filter_by(completed=True).order_by(TrainingLog.date.desc()).limit(30).all()
        
        # Calculate training consistency
        total_days = 30
        completed_days = len(recent_logs)
        consistency_percentage = (completed_days / total_days) * 100
        
        # Get performance progression
        pr_records = PersonalRecord.query.filter_by(event='300m Hurdles').order_by(PersonalRecord.date_achieved.asc()).all()
        
        return render_template('advanced_analytics.html',
                             competitors=competitors,
                             predictions=predictions,
                             consistency_percentage=consistency_percentage,
                             pr_records=pr_records,
                             recent_logs=recent_logs)
        
    except Exception as e:
        logging.error(f"Advanced analytics error: {e}")
        return render_template('advanced_analytics.html',
                             competitors=[],
                             predictions={},
                             consistency_percentage=0,
                             pr_records=[],
                             recent_logs=[])

@app.route('/ai-form-analysis')
def ai_form_analysis():
    """AI-powered form analysis page"""
    try:
        # Get recent video analyses
        recent_analyses = VideoAnalysis.query.order_by(VideoAnalysis.upload_date.desc()).limit(10).all()
        
        # Parse analysis results
        analyses_with_results = []
        for analysis in recent_analyses:
            if analysis.analysis_notes:
                try:
                    parsed_results = json.loads(analysis.analysis_notes)
                    analysis.parsed_results = parsed_results
                except:
                    analysis.parsed_results = None
            analyses_with_results.append(analysis)
        
        return render_template('ai_form_analysis.html', 
                             video_analyses=analyses_with_results)
        
    except Exception as e:
        logging.error(f"AI form analysis page error: {e}")
        return render_template('ai_form_analysis.html', video_analyses=[])

@app.route('/competitor-intelligence')
def competitor_intelligence():
    """Competitor intelligence dashboard"""
    try:
        # Get comprehensive competitor data
        competitors = competitor_analyzer.scrape_athletic_net_competitors(grade_level=9)
        milesplit_articles = competitor_analyzer.scrape_milesplit_news()
        meet_schedule = competitor_analyzer.get_regional_meet_schedule()
        
        # Sort competitors by threat level
        high_threats = [c for c in competitors if c.get('competitive_threat_level') == 'high_threat']
        moderate_threats = [c for c in competitors if c.get('competitive_threat_level') == 'moderate_threat']
        close_competitors = [c for c in competitors if c.get('competitive_threat_level') == 'close_competitor']
        
        return render_template('competitor_intelligence.html',
                             high_threats=high_threats,
                             moderate_threats=moderate_threats,
                             close_competitors=close_competitors,
                             all_competitors=competitors,
                             milesplit_articles=milesplit_articles,
                             upcoming_meets=meet_schedule)
        
    except Exception as e:
        logging.error(f"Competitor intelligence error: {e}")
        return render_template('competitor_intelligence.html',
                             high_threats=[],
                             moderate_threats=[],
                             close_competitors=[],
                             all_competitors=[],
                             milesplit_articles=[],
                             upcoming_meets=[])

@app.route('/performance-projection')
def performance_projection():
    """Performance projection and goal tracking"""
    try:
        # Get comprehensive predictions
        current_predictions = predictor.predict_seasonal_progression('300m_hurdles', 'high_consistency')
        future_predictions = {}
        
        for grade in [10, 11, 12]:
            future_predictions[f'grade_{grade}'] = predictor.predict_future_performance('300m_hurdles', grade=grade)
        
        # Calculate school record probability
        record_probability = predictor.calculate_record_probability(42.08)
        
        # Get improvement recommendations
        recommendations = predictor.get_improvement_recommendations()
        
        return render_template('performance_projection.html',
                             current_predictions=current_predictions,
                             future_predictions=future_predictions,
                             record_probability=record_probability,
                             recommendations=recommendations,
                             school_record_target=42.08,
                             current_pr=45.24)
        
    except Exception as e:
        logging.error(f"Performance projection error: {e}")
        return render_template('performance_projection.html',
                             current_predictions={},
                             future_predictions={},
                             record_probability={},
                             recommendations=[],
                             school_record_target=42.08,
                             current_pr=45.24)

@app.route('/endurance-training')
def endurance_training():
    """Advanced endurance training module"""
    try:
        # Get current workout recommendation
        today_workout = endurance_system.get_daily_endurance_workout(1, 'build_phase')
        
        # Get heart rate zones
        hr_zones = endurance_system.get_heart_rate_training_zones()
        
        # Get predicted improvements
        improvement_predictions = endurance_system.calculate_predicted_improvements(16)
        
        return render_template('endurance_training.html',
                             today_workout=today_workout,
                             hr_zones=hr_zones,
                             predictions=improvement_predictions)
        
    except Exception as e:
        logging.error(f"Endurance training error: {e}")
        return render_template('endurance_training.html',
                             today_workout={},
                             hr_zones={},
                             predictions={})

@app.route('/api/real-time-stats')
def api_real_time_stats():
    """Real-time statistics API for dashboard widgets"""
    try:
        # Calculate real-time statistics
        total_workouts = TrainingLog.query.filter_by(completed=True).count()
        this_week_workouts = TrainingLog.query.filter(
            TrainingLog.date >= date.today() - timedelta(days=7),
            TrainingLog.completed == True
        ).count()
        
        # Get latest PR
        latest_pr = PersonalRecord.query.filter_by(event='300m Hurdles').order_by(PersonalRecord.date_achieved.desc()).first()
        
        # Days until next major meet
        next_meet_date = date(2025, 5, 22)  # District Championship
        days_to_meet = (next_meet_date - date.today()).days
        
        # Calculate improvement needed for school record
        improvement_needed = 45.24 - 42.08  # Current PR vs school record
        
        return jsonify({
            'total_workouts_completed': total_workouts,
            'this_week_workouts': this_week_workouts,
            'current_pr': 45.24,
            'recent_time_average': 48.00,
            'school_record_target': 42.08,
            'improvement_needed': round(improvement_needed, 2),
            'days_to_next_meet': days_to_meet,
            'next_meet': 'District 10 Championship',
            'training_consistency': round((this_week_workouts / 7) * 100, 1),
            'latest_pr_date': latest_pr.date_achieved.isoformat() if latest_pr else None
        })
        
    except Exception as e:
        logging.error(f"Real-time stats error: {e}")
        return jsonify({'error': str(e)}), 500