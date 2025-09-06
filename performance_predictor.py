"""
AI-Powered Performance Prediction System
Predicts Tyler's future performance based on training consistency, progression patterns, and physiological development
"""
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
import logging
from app import db
from models import TrainingLog, PersonalRecord

class PerformancePredictor:
    """Predict Tyler's future performance using advanced modeling"""
    
    def __init__(self):
        # Tyler's current stats (updated with real data)
        self.current_stats = {
            '300m_hurdles': {
                'pr': 45.85,
                'recent_avg': 47.95,
                'progression': [48.30, 47.12, 46.45, 45.85],  # Season progression
                'consistency_variance': 2.1  # Standard deviation of recent times
            },
            '110m_hurdles': {
                'pr': 18.95,
                'recent_avg': 19.25,
                'progression': [19.67, 19.45, 19.12, 18.95]
            },
            '400m': {
                'pr': 58.76,
                'endurance_base': 'good'
            },
            '200m': {
                'pr': 26.45,
                'speed_base': 'excellent'
            }
        }
        
        # Physiological development factors for 9th grader
        self.development_factors = {
            'strength_gains_per_year': 0.12,      # 12% strength gain potential per year
            'speed_development': 0.08,            # 8% speed improvement potential
            'endurance_development': 0.15,        # 15% endurance improvement potential
            'technique_mastery': 0.20,            # 20% technique improvement potential
            'experience_factor': 0.10             # 10% race experience improvement
        }
        
        # Training consistency impact
        self.training_multipliers = {
            'high_consistency': 1.0,              # 90%+ workout completion
            'good_consistency': 0.85,             # 80-89% completion
            'moderate_consistency': 0.70,         # 70-79% completion
            'low_consistency': 0.50               # Below 70% completion
        }
    
    def predict_seasonal_progression(self, event='300m_hurdles', consistency_level='high_consistency'):
        """Predict Tyler's performance progression through seasons"""
        
        current_pr = self.current_stats[event]['pr']
        base_multiplier = self.training_multipliers[consistency_level]
        
        predictions = {
            'current_season_remaining': {},
            'sophomore_year': {},
            'junior_year': {},
            'senior_year': {},
            'improvement_timeline': {}
        }
        
        # Current season remaining (9th grade)
        current_season_potential = self.calculate_season_potential(
            current_pr, 
            'freshman',
            consistency_level,
            event
        )
        predictions['current_season_remaining'] = current_season_potential
        
        # Sophomore year projections
        sophomore_potential = self.calculate_season_potential(
            current_season_potential['season_best_projection'],
            'sophomore', 
            consistency_level,
            event
        )
        predictions['sophomore_year'] = sophomore_potential
        
        # Junior year projections
        junior_potential = self.calculate_season_potential(
            sophomore_potential['season_best_projection'],
            'junior',
            consistency_level, 
            event
        )
        predictions['junior_year'] = junior_potential
        
        # Senior year projections
        senior_potential = self.calculate_season_potential(
            junior_potential['season_best_projection'],
            'senior',
            consistency_level,
            event
        )
        predictions['senior_year'] = senior_potential
        
        # Key milestone timeline
        predictions['improvement_timeline'] = self.calculate_milestone_timeline(
            current_pr, 
            [current_season_potential, sophomore_potential, junior_potential, senior_potential],
            event
        )
        
        return predictions
    
    def calculate_season_potential(self, starting_pr, grade_level, consistency, event):
        """Calculate potential improvement for a single season"""
        
        # Base improvement factors by grade
        grade_factors = {
            'freshman': {'strength': 0.10, 'technique': 0.25, 'experience': 0.15},
            'sophomore': {'strength': 0.12, 'technique': 0.15, 'experience': 0.12},
            'junior': {'strength': 0.08, 'technique': 0.08, 'experience': 0.08},
            'senior': {'strength': 0.04, 'technique': 0.05, 'experience': 0.03}
        }
        
        factors = grade_factors.get(grade_level, grade_factors['sophomore'])
        consistency_multiplier = self.training_multipliers[consistency]
        
        # Event-specific improvement potential
        if event == '300m_hurdles':
            # 300m hurdles has high improvement potential due to endurance component
            base_improvement = starting_pr * 0.035  # 3.5% base improvement
            technique_bonus = starting_pr * factors['technique'] * 0.02
            endurance_bonus = starting_pr * 0.025  # Endurance is key for 300mH
            
        elif event == '110m_hurdles':
            # 110m hurdles more technique dependent
            base_improvement = starting_pr * 0.025  # 2.5% base improvement  
            technique_bonus = starting_pr * factors['technique'] * 0.03
            endurance_bonus = 0  # Less endurance dependent
            
        else:
            base_improvement = starting_pr * 0.03
            technique_bonus = 0
            endurance_bonus = 0
        
        # Calculate total improvement
        total_improvement = (
            base_improvement + 
            technique_bonus + 
            endurance_bonus
        ) * consistency_multiplier
        
        # Add realistic variance
        conservative_improvement = total_improvement * 0.7
        aggressive_improvement = total_improvement * 1.3
        
        season_best = starting_pr - total_improvement
        conservative_best = starting_pr - conservative_improvement
        aggressive_best = starting_pr - aggressive_improvement
        
        return {
            'grade': grade_level,
            'season_best_projection': round(season_best, 2),
            'conservative_projection': round(conservative_best, 2),
            'aggressive_projection': round(aggressive_best, 2),
            'improvement_range': f"{conservative_improvement:.2f}-{aggressive_improvement:.2f}s",
            'key_factors': self.get_improvement_factors(grade_level, event),
            'training_focus': self.get_training_recommendations(grade_level, event)
        }
    
    def calculate_milestone_timeline(self, current_pr, season_projections, event):
        """Calculate when Tyler will hit key milestones"""
        
        milestones = {
            '300m_hurdles': {
                'sub_45': 45.0,
                'sub_44': 44.0, 
                'sub_43': 43.0,
                'school_record': 42.08,
                'state_qualifying': 44.50,
                'elite_level': 41.50
            },
            '110m_hurdles': {
                'sub_19': 19.0,
                'sub_18': 18.0,
                'sub_17': 17.0,
                'state_qualifying': 18.50,
                'elite_level': 16.50
            }
        }
        
        event_milestones = milestones.get(event, milestones['300m_hurdles'])
        timeline = {}
        
        # Check current season
        current_season = season_projections[0]
        
        for milestone_name, milestone_time in event_milestones.items():
            if current_pr <= milestone_time:
                timeline[milestone_name] = "Already achieved!"
            elif current_season['aggressive_projection'] <= milestone_time:
                timeline[milestone_name] = "Possible this season (9th grade)"
            elif season_projections[1]['season_best_projection'] <= milestone_time:
                timeline[milestone_name] = "Likely sophomore year"
            elif season_projections[2]['season_best_projection'] <= milestone_time:
                timeline[milestone_name] = "Projected junior year"
            elif season_projections[3]['season_best_projection'] <= milestone_time:
                timeline[milestone_name] = "Senior year goal"
            else:
                timeline[milestone_name] = "Beyond high school projection"
        
        return timeline
    
    def get_improvement_factors(self, grade_level, event):
        """Get key improvement factors for each grade level"""
        
        factors_by_grade = {
            'freshman': [
                "Technique mastery (huge potential)",
                "Building endurance base", 
                "Learning race strategy",
                "Strength development beginning"
            ],
            'sophomore': [
                "Continued strength gains",
                "Refined technique",
                "Better race experience",
                "Improved consistency"
            ],
            'junior': [
                "Peak strength development",
                "Advanced race tactics", 
                "Mental toughness",
                "Specialization focus"
            ],
            'senior': [
                "Fine-tuning technique",
                "Peak experience level",
                "Mental preparation",
                "Consistency under pressure"
            ]
        }
        
        return factors_by_grade.get(grade_level, factors_by_grade['sophomore'])
    
    def get_training_recommendations(self, grade_level, event):
        """Get training focus recommendations by grade"""
        
        recommendations = {
            'freshman': {
                'primary_focus': 'Technique development and endurance base',
                'weekly_structure': '60% technique, 25% endurance, 15% speed',
                'key_workouts': ['Form drills', 'Tempo runs', 'Hurdle mobility']
            },
            'sophomore': {
                'primary_focus': 'Strength building and consistency',
                'weekly_structure': '40% technique, 35% strength, 25% race prep',
                'key_workouts': ['Weight training', 'Race pace work', 'Competition drills']
            },
            'junior': {
                'primary_focus': 'Race specialization and peak performance',
                'weekly_structure': '30% technique, 40% race specific, 30% strength maintenance',
                'key_workouts': ['Race simulation', 'Advanced hurdle patterns', 'Peak training']
            },
            'senior': {
                'primary_focus': 'Consistency and mental preparation',
                'weekly_structure': '25% technique, 50% race preparation, 25% maintenance',
                'key_workouts': ['Competition simulation', 'Pressure training', 'Recovery focus']
            }
        }
        
        return recommendations.get(grade_level, recommendations['sophomore'])
    
    def predict_with_different_scenarios(self, event='300m_hurdles'):
        """Predict outcomes under different training scenarios"""
        
        scenarios = {
            'elite_commitment': {
                'consistency': 'high_consistency',
                'description': '95%+ workout completion, summer training, camps',
                'multiplier': 1.2
            },
            'dedicated_training': {
                'consistency': 'high_consistency', 
                'description': '90%+ workout completion, consistent year-round',
                'multiplier': 1.0
            },
            'good_training': {
                'consistency': 'good_consistency',
                'description': '80-89% completion, some missed workouts',
                'multiplier': 0.85
            },
            'inconsistent_training': {
                'consistency': 'moderate_consistency',
                'description': '70-79% completion, frequent interruptions', 
                'multiplier': 0.70
            }
        }
        
        predictions = {}
        
        for scenario_name, scenario_data in scenarios.items():
            scenario_predictions = self.predict_seasonal_progression(
                event, 
                scenario_data['consistency']
            )
            
            # Apply scenario multiplier to improvements
            for year_key in ['current_season_remaining', 'sophomore_year', 'junior_year', 'senior_year']:
                if year_key in scenario_predictions:
                    year_data = scenario_predictions[year_key]
                    if 'season_best_projection' in year_data:
                        # Apply multiplier to improvement amount, not final time
                        current_pr = self.current_stats[event]['pr']
                        improvement = current_pr - year_data['season_best_projection']
                        adjusted_improvement = improvement * scenario_data['multiplier']
                        year_data['season_best_projection'] = round(current_pr - adjusted_improvement, 2)
            
            predictions[scenario_name] = {
                'description': scenario_data['description'],
                'predictions': scenario_predictions
            }
        
        return predictions
    
    def get_endurance_improvement_plan(self):
        """Specific endurance improvement plan for Tyler"""
        
        plan = {
            'current_assessment': {
                '300m_hurdles_endurance': 'Moderate - needs improvement for consistency',
                '400m_base': 'Good foundation with 58.76 PR',
                'issue': 'Significant drop-off from PR (45.85) to recent times (47-48s)',
                'primary_limiters': ['Lactate tolerance', 'Speed endurance', 'Late-race technique maintenance']
            },
            
            'improvement_phases': {
                'phase_1_aerobic_base': {
                    'duration': '4-6 weeks',
                    'focus': 'Build aerobic capacity',
                    'workouts': [
                        '25-30min easy runs 3x/week',
                        '400m repeats @ 75-80% effort',
                        'Long tempo runs (8-12 minutes)',
                        'Recovery between reps: 2-3 minutes'
                    ],
                    'expected_outcome': 'Better base for harder training'
                },
                
                'phase_2_lactate_threshold': {
                    'duration': '4-6 weeks', 
                    'focus': 'Improve lactate clearance',
                    'workouts': [
                        '300m repeats @ 85-90% effort',
                        '200m + 100m combinations',
                        'Broken 300s (150m + 150m)',
                        'Recovery: 3-4 minutes between reps'
                    ],
                    'expected_outcome': 'Handle race pace longer'
                },
                
                'phase_3_speed_endurance': {
                    'duration': '4-5 weeks',
                    'focus': 'Race-specific endurance', 
                    'workouts': [
                        '350m repeats @ 95% effort',
                        '300m hurdle race simulations',
                        '250m + 100m split runs',
                        'Recovery: 4-5 minutes complete rest'
                    ],
                    'expected_outcome': 'Maintain speed through full 300mH'
                }
            },
            
            'weekly_endurance_structure': {
                'monday': 'Aerobic base run (25-30 min)',
                'tuesday': 'Speed endurance work (main session)',
                'wednesday': 'Easy recovery run (15-20 min)',
                'thursday': 'Lactate threshold work',
                'friday': 'Rest or easy technique work',
                'saturday': 'Long run or race pace work',
                'sunday': 'Complete rest'
            },
            
            'endurance_testing_protocol': {
                'monthly_tests': [
                    '400m time trial (target: sub-57s by junior year)',
                    '300m flat sprint (target: sub-38s)', 
                    '600m time trial (endurance indicator)',
                    '5x200m @ race pace w/ 90s rest (consistency test)'
                ],
                'success_indicators': [
                    'Consistent times across multiple 300mH races',
                    'Less than 1.5s variance from PR in competitions',
                    'Strong finishing speed in races',
                    'Quick recovery between races at meets'
                ]
            },
            
            'projected_improvements': {
                'short_term_6_months': {
                    'consistency_improvement': '1.5-2.0 seconds',
                    'expected_range': '46.5-47.5s regularly',
                    'race_readiness': 'Much better'
                },
                'medium_term_1_year': {
                    'consistency_improvement': '2.0-2.5 seconds', 
                    'expected_range': '45.5-46.5s regularly',
                    'new_pr_potential': '44.5-45.0s'
                },
                'long_term_senior_year': {
                    'consistency_improvement': '3.0+ seconds',
                    'expected_range': '43.5-44.5s regularly',
                    'school_record_potential': 'Highly achievable (42.08s target)'
                }
            }
        }
        
        return plan

# Global predictor instance
performance_predictor = PerformancePredictor()