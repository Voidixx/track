"""
Database models for Tyler's 300m Hurdles Training Hub
"""
from datetime import datetime
from app import db


class TrainingLog(db.Model):
    """Records of daily workout completions"""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    workout_type = db.Column(db.String(50), nullable=False)  # outdoor/indoor
    workout_focus = db.Column(db.String(100), nullable=False)  # Speed Endurance, etc.
    workout_description = db.Column(db.Text, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completion_time = db.Column(db.DateTime)
    notes = db.Column(db.Text)  # User notes about the workout
    difficulty_rating = db.Column(db.Integer)  # 1-5 scale
    energy_level = db.Column(db.Integer)  # 1-5 scale before workout
    weather_condition = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PersonalRecord(db.Model):
    """Track personal bests and race times"""
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(50), nullable=False)  # 300m Hurdles, 200m, etc.
    time_seconds = db.Column(db.Float, nullable=False)  # Time in seconds
    date_achieved = db.Column(db.Date, nullable=False)
    meet_name = db.Column(db.String(100))  # Name of the meet/competition
    conditions = db.Column(db.String(100))  # Weather, track conditions, etc.
    notes = db.Column(db.Text)  # Additional notes about the performance
    is_official = db.Column(db.Boolean, default=True)  # Official meet vs practice
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class VideoAnalysis(db.Model):
    """Store uploaded videos for form analysis"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    original_filename = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    video_type = db.Column(db.String(50))  # hurdle technique, sprint form, etc.
    analysis_notes = db.Column(db.Text)  # Coach or self analysis notes
    technique_focus = db.Column(db.String(100))  # lead leg, trail leg, rhythm, etc.
    training_log_id = db.Column(db.Integer, db.ForeignKey('training_log.id'))  # Link to workout
    
    # Relationship
    training_log = db.relationship('TrainingLog', backref='videos')


class CoachMessage(db.Model):
    """Communication between Tyler and coach"""
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(50), nullable=False)  # 'tyler' or 'coach'
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    category = db.Column(db.String(50))  # technique, training, race strategy, injury, etc.
    training_log_id = db.Column(db.Integer, db.ForeignKey('training_log.id'))  # Optional link to workout
    
    # Relationship
    training_log = db.relationship('TrainingLog', backref='messages')


class WeeklyStats(db.Model):
    """Weekly training statistics and summaries"""
    id = db.Column(db.Integer, primary_key=True)
    week_start = db.Column(db.Date, nullable=False)
    week_end = db.Column(db.Date, nullable=False)
    workouts_completed = db.Column(db.Integer, default=0)
    workouts_planned = db.Column(db.Integer, default=7)
    total_training_time = db.Column(db.Integer, default=0)  # minutes
    avg_difficulty_rating = db.Column(db.Float)
    avg_energy_level = db.Column(db.Float)
    outdoor_workouts = db.Column(db.Integer, default=0)
    indoor_workouts = db.Column(db.Integer, default=0)
    best_time_this_week = db.Column(db.Float)  # Best time recorded this week
    notes = db.Column(db.Text)  # Weekly summary notes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Goal(db.Model):
    """Training goals and milestones"""
    id = db.Column(db.Integer, primary_key=True)
    goal_type = db.Column(db.String(50), nullable=False)  # time, technique, strength, etc.
    description = db.Column(db.String(200), nullable=False)
    target_value = db.Column(db.String(50))  # target time, reps, etc.
    target_date = db.Column(db.Date)
    current_value = db.Column(db.String(50))  # current progress
    is_achieved = db.Column(db.Boolean, default=False)
    date_achieved = db.Column(db.Date)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    category = db.Column(db.String(50))  # short-term, season, annual, career
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)