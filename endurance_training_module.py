"""
Advanced Endurance Training Module for Tyler's 300m Hurdles Training
Provides specialized endurance workouts, heart rate zones, and lactate threshold training
"""
import json
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Tuple
import math

class EnduranceTrainingSystem:
    """Comprehensive endurance training system for 300m hurdles"""
    
    def __init__(self):
        # Tyler's specific performance data
        self.athlete_data = {
            'current_300h_pr': 45.24,
            'recent_300h_avg': 48.00,
            'current_400m_pr': 58.76,
            'current_200m_pr': 26.45,
            'target_300h_goal': 42.08,  # School record
            'training_age': 2,  # Years of serious hurdles training
            'grade': 9
        }
        
        # Heart rate zones (estimated for 15-year-old athlete)
        self.heart_rate_zones = {
            'resting': 60,
            'max_estimated': 205,  # 220 - 15 years old
            'zone_1_recovery': (123, 143),    # 60-70% max HR
            'zone_2_aerobic': (143, 164),     # 70-80% max HR  
            'zone_3_threshold': (164, 184),   # 80-90% max HR
            'zone_4_vo2_max': (184, 195),     # 90-95% max HR
            'zone_5_neuromuscular': (195, 205) # 95-100% max HR
        }
        
        # Training phases based on competition schedule
        self.training_phases = {
            'base_building': {
                'duration_weeks': 8,
                'focus': 'Aerobic capacity and general endurance',
                'volume_high': True,
                'intensity_moderate': True
            },
            'build_phase': {
                'duration_weeks': 6,
                'focus': 'Lactate threshold and speed endurance',
                'volume_moderate': True,
                'intensity_high': True
            },
            'peak_phase': {
                'duration_weeks': 4,
                'focus': 'Race pace and neuromuscular power',
                'volume_low': True,
                'intensity_very_high': True
            },
            'taper_competition': {
                'duration_weeks': 2,
                'focus': 'Maintenance and recovery',
                'volume_very_low': True,
                'intensity_moderate': True
            }
        }
    
    def get_daily_endurance_workout(self, training_day: int, phase: str = 'build_phase') -> Dict[str, Any]:
        """Generate specific endurance workout for training day"""
        try:
            phase_config = self.training_phases.get(phase, self.training_phases['build_phase'])
            
            # 7-day microcycle pattern
            day_in_cycle = training_day % 7
            
            workouts = {
                0: self._generate_tempo_run_workout(),      # Monday
                1: self._generate_lactate_threshold_workout(), # Tuesday  
                2: self._generate_recovery_workout(),       # Wednesday
                3: self._generate_speed_endurance_workout(), # Thursday
                4: self._generate_aerobic_capacity_workout(), # Friday
                5: self._generate_long_run_workout(),       # Saturday
                6: self._generate_active_recovery_workout()  # Sunday
            }
            
            base_workout = workouts[day_in_cycle]
            
            # Modify based on training phase
            adjusted_workout = self._adjust_workout_for_phase(base_workout, phase_config)
            
            return adjusted_workout
            
        except Exception as e:
            logging.error(f"Error generating endurance workout: {e}")
            return self._generate_default_workout()
    
    def _generate_tempo_run_workout(self) -> Dict[str, Any]:
        """Tempo run for lactate threshold development"""
        return {
            'workout_type': 'Tempo Run',
            'focus': 'Lactate Threshold Development',
            'target_heart_rate_zone': 'zone_3_threshold',
            'estimated_hr_range': self.heart_rate_zones['zone_3_threshold'],
            'warm_up': [
                '10 min easy jog (Zone 1)',
                '5 min dynamic warm-up',
                '4 x 100m progressive accelerations'
            ],
            'main_workout': [
                '20 min continuous tempo run at 300m hurdle race pace + 10-15 seconds',
                'Maintain steady effort - should feel "comfortably hard"',
                'Target pace: ~85-90% of current 400m race pace',
                'Focus on relaxed rhythm and consistent breathing'
            ],
            'cool_down': [
                '10 min easy jog',
                '10 min stretching routine',
                'Focus on hip flexors and hamstrings'
            ],
            'coaching_notes': [
                'This pace develops the lactate threshold critical for 300m hurdles',
                'Should be sustainable for the full 20 minutes',
                'If unable to maintain pace, reduce intensity slightly'
            ],
            'target_energy_system': 'Lactate Threshold',
            'intensity_level': 7,  # 1-10 scale
            'estimated_duration': 45,  # minutes
            'equipment_needed': ['Running watch', 'Heart rate monitor'],
            'weather_adaptations': {
                'hot': 'Reduce pace by 5-10 seconds, increase hydration',
                'cold': 'Extend warm-up by 5 minutes',
                'windy': 'Find sheltered route or adjust for headwind'
            }
        }
    
    def _generate_lactate_threshold_workout(self) -> Dict[str, Any]:
        """Interval workout targeting lactate threshold"""
        return {
            'workout_type': 'Lactate Threshold Intervals',
            'focus': 'Lactate Clearance and Buffering',
            'target_heart_rate_zone': 'zone_3_threshold',
            'estimated_hr_range': self.heart_rate_zones['zone_3_threshold'],
            'warm_up': [
                '15 min easy jog with 5 x 100m strides',
                'Dynamic stretching routine (10 min)',
                '3 x 200m at progressive pace (easy, moderate, fast)'
            ],
            'main_workout': [
                '5 x 600m at lactate threshold pace',
                'Rest: 90 seconds active recovery (walk/jog)',
                'Target pace: Current 400m race pace + 5-8 seconds',
                'Focus: Smooth rhythm, controlled breathing',
                'Each rep should feel consistently challenging'
            ],
            'cool_down': [
                '12 min easy jog',
                '15 min comprehensive stretching',
                'Ice bath or cold therapy if available'
            ],
            'coaching_notes': [
                'Critical workout for 300m hurdle endurance',
                'Pace should allow completion of all 5 reps',
                'Last rep should feel similar to first rep',
                'This develops ability to clear lactate during race'
            ],
            'target_energy_system': 'Lactate Threshold + Aerobic Power',
            'intensity_level': 8,
            'estimated_duration': 65,
            'equipment_needed': ['Track access', 'Stopwatch', 'Water bottle'],
            'progression_notes': [
                'Week 1-2: 4 x 600m',
                'Week 3-4: 5 x 600m', 
                'Week 5-6: 5 x 600m with reduced rest (75 sec)',
                'Week 7-8: 6 x 600m or 4 x 800m'
            ]
        }
    
    def _generate_speed_endurance_workout(self) -> Dict[str, Any]:
        """Speed endurance specific to 300m hurdles demands"""
        return {
            'workout_type': 'Speed Endurance',
            'focus': 'Lactate Tolerance and Race Simulation',
            'target_heart_rate_zone': 'zone_4_vo2_max',
            'estimated_hr_range': self.heart_rate_zones['zone_4_vo2_max'],
            'warm_up': [
                '12 min easy jog',
                '10 min dynamic warm-up with hurdle mobility',
                '6 x 100m accelerations with 3 over hurdles'
            ],
            'main_workout': [
                'Set 1: 3 x 250m at race pace (300m hurdle pace)',
                'Rest: 3 minutes complete rest',
                'Set 2: 2 x 350m at race pace + 2-3 seconds', 
                'Rest: 4 minutes between reps',
                'Focus: Maintaining form under fatigue',
                'Simulate race conditions and pacing strategy'
            ],
            'cool_down': [
                '15 min easy jog',
                '20 min stretching with emphasis on recovery',
                'Foam rolling session'
            ],
            'coaching_notes': [
                'Most race-specific endurance workout',
                'Develops ability to maintain speed when fatigued',
                'Critical for final 100m of 300m hurdles',
                'Monitor form carefully - stop if technique breaks down'
            ],
            'target_energy_system': 'Lactate Tolerance + Neuromuscular Power',
            'intensity_level': 9,
            'estimated_duration': 70,
            'equipment_needed': ['Hurdles', 'Track', 'Timing device'],
            'race_simulation_notes': [
                'Practice race strategy during 350m reps',
                'Work on maintaining hurdle rhythm when tired',
                'Focus on strong finish and form maintenance'
            ]
        }
    
    def _generate_aerobic_capacity_workout(self) -> Dict[str, Any]:
        """VO2 max development for enhanced oxygen delivery"""
        return {
            'workout_type': 'Aerobic Capacity Development',
            'focus': 'VO2 Max and Oxygen Delivery',
            'target_heart_rate_zone': 'zone_4_vo2_max',
            'estimated_hr_range': self.heart_rate_zones['zone_4_vo2_max'],
            'warm_up': [
                '10 min easy jog',
                '8 min dynamic warm-up',
                '4 x 150m progressive runs'
            ],
            'main_workout': [
                '6 x 400m at VO2 max pace (current mile pace)',
                'Rest: 90 seconds active recovery',
                'Target: Hard but sustainable effort',
                'Focus: Efficient running mechanics',
                'Should reach near-maximal heart rate by rep 3-4'
            ],
            'cool_down': [
                '12 min easy jog',
                '12 min static stretching',
                'Breathing exercises for recovery'
            ],
            'coaching_notes': [
                'Develops maximal oxygen uptake capacity',
                'Improves cardiac output and stroke volume',
                'Enhances aerobic contribution to 300m hurdles',
                'Critical base for lactate threshold training'
            ],
            'target_energy_system': 'VO2 Max / Aerobic Power',
            'intensity_level': 8,
            'estimated_duration': 55,
            'equipment_needed': ['Track', 'Heart rate monitor'],
            'adaptations': [
                'Increased mitochondrial density',
                'Enhanced oxygen transport',
                'Improved lactate buffering capacity',
                'Greater aerobic power output'
            ]
        }
    
    def _generate_recovery_workout(self) -> Dict[str, Any]:
        """Active recovery for adaptation and regeneration"""
        return {
            'workout_type': 'Active Recovery',
            'focus': 'Recovery and Adaptation',
            'target_heart_rate_zone': 'zone_1_recovery',
            'estimated_hr_range': self.heart_rate_zones['zone_1_recovery'],
            'warm_up': [
                '5 min walking',
                '5 min easy jogging'
            ],
            'main_workout': [
                '25-30 min easy continuous run',
                'Effort: Conversational pace',
                'Focus: Relaxed form and breathing',
                'Include 4 x 100m strides at end if feeling good'
            ],
            'cool_down': [
                '10 min walking and light stretching',
                '15 min foam rolling and mobility work',
                'Hydration and nutrition focus'
            ],
            'coaching_notes': [
                'Promotes blood flow and recovery',
                'Maintains aerobic base while recovering',
                'Should feel refreshed, not fatigued',
                'Critical for adaptation from hard training'
            ],
            'target_energy_system': 'Aerobic Base / Recovery',
            'intensity_level': 3,
            'estimated_duration': 50,
            'equipment_needed': ['Foam roller', 'Stretching mat'],
            'recovery_indicators': [
                'Improved sleep quality',
                'Stable or decreasing resting heart rate',
                'Positive mood and energy',
                'Reduced muscle tension'
            ]
        }
    
    def _generate_long_run_workout(self) -> Dict[str, Any]:
        """Aerobic base development through longer duration"""
        return {
            'workout_type': 'Aerobic Base Run',
            'focus': 'Aerobic Endurance and Mental Toughness',
            'target_heart_rate_zone': 'zone_2_aerobic',
            'estimated_hr_range': self.heart_rate_zones['zone_2_aerobic'],
            'warm_up': [
                '8 min easy walking and jogging',
                '5 min dynamic stretching'
            ],
            'main_workout': [
                '40-50 min continuous run at aerobic pace',
                'Effort: Comfortable but purposeful',
                'Heart rate: 70-80% max HR',
                'Include 6 x 30-second pickups every 8 minutes',
                'Focus: Consistent effort and form'
            ],
            'cool_down': [
                '8 min easy walking',
                '15 min full-body stretching routine',
                'Hydration and electrolyte replacement'
            ],
            'coaching_notes': [
                'Builds aerobic base for all training',
                'Develops fat oxidation capacity',
                'Improves cardiac efficiency',
                'Mental preparation for sustained effort'
            ],
            'target_energy_system': 'Aerobic Base',
            'intensity_level': 5,
            'estimated_duration': 65,
            'equipment_needed': ['Heart rate monitor', 'Hydration'],
            'terrain_options': [
                'Track: Consistent pace monitoring',
                'Trails: Varied stimulus and mental break',
                'Roads: Race-specific surface adaptation'
            ]
        }
    
    def _generate_active_recovery_workout(self) -> Dict[str, Any]:
        """Complete active recovery day"""
        return {
            'workout_type': 'Active Recovery Day',
            'focus': 'Regeneration and Preparation',
            'target_heart_rate_zone': 'zone_1_recovery',
            'estimated_hr_range': self.heart_rate_zones['zone_1_recovery'],
            'warm_up': [
                '10 min easy walking',
                'Joint mobility routine'
            ],
            'main_workout': [
                'Option A: 20 min easy bike ride or swimming',
                'Option B: 25 min yoga or pilates session',
                'Option C: 30 min walking with light calisthenics',
                'Focus: Movement without stress'
            ],
            'cool_down': [
                '20 min comprehensive stretching',
                'Massage or self-massage with tools',
                'Meditation or relaxation practice'
            ],
            'coaching_notes': [
                'Essential for weekly recovery',
                'Prepares body for next training cycle',
                'Focus on sleep and nutrition',
                'Mental reset and goal reinforcement'
            ],
            'target_energy_system': 'Recovery and Regeneration',
            'intensity_level': 2,
            'estimated_duration': 45,
            'equipment_needed': ['Yoga mat', 'Massage tools'],
            'additional_activities': [
                'Sauna or hot/cold therapy',
                'Nutrition planning for upcoming week',
                'Video analysis of recent training',
                'Goal setting and visualization'
            ]
        }
    
    def _adjust_workout_for_phase(self, workout: Dict[str, Any], phase_config: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust workout intensity/volume based on training phase"""
        if phase_config.get('volume_high'):
            workout['estimated_duration'] = int(workout['estimated_duration'] * 1.15)
        elif phase_config.get('volume_low'):
            workout['estimated_duration'] = int(workout['estimated_duration'] * 0.85)
        
        if phase_config.get('intensity_very_high'):
            workout['intensity_level'] = min(10, workout['intensity_level'] + 1)
        elif phase_config.get('intensity_moderate'):
            workout['intensity_level'] = max(1, workout['intensity_level'] - 1)
        
        return workout
    
    def get_heart_rate_training_zones(self) -> Dict[str, Any]:
        """Return detailed heart rate zone information"""
        return {
            'athlete_max_hr': self.heart_rate_zones['max_estimated'],
            'zones': {
                'Zone 1 - Recovery': {
                    'range': self.heart_rate_zones['zone_1_recovery'],
                    'percentage': '60-70%',
                    'purpose': 'Active recovery, base building',
                    'feel': 'Very easy, conversational'
                },
                'Zone 2 - Aerobic': {
                    'range': self.heart_rate_zones['zone_2_aerobic'],
                    'percentage': '70-80%',
                    'purpose': 'Aerobic base, fat oxidation',
                    'feel': 'Comfortable, sustainable'
                },
                'Zone 3 - Threshold': {
                    'range': self.heart_rate_zones['zone_3_threshold'],
                    'percentage': '80-90%',
                    'purpose': 'Lactate threshold, tempo',
                    'feel': 'Comfortably hard'
                },
                'Zone 4 - VO2 Max': {
                    'range': self.heart_rate_zones['zone_4_vo2_max'],
                    'percentage': '90-95%',
                    'purpose': 'Maximal oxygen uptake',
                    'feel': 'Hard, near maximal'
                },
                'Zone 5 - Neuromuscular': {
                    'range': self.heart_rate_zones['zone_5_neuromuscular'],
                    'percentage': '95-100%',
                    'purpose': 'Speed, power, race pace',
                    'feel': 'Maximal effort'
                }
            }
        }
    
    def _generate_default_workout(self) -> Dict[str, Any]:
        """Fallback workout when system fails"""
        return {
            'workout_type': 'General Endurance',
            'focus': 'Aerobic Development',
            'main_workout': ['30 min easy run at conversational pace'],
            'intensity_level': 4,
            'estimated_duration': 45
        }
    
    def calculate_predicted_improvements(self, weeks_of_training: int) -> Dict[str, Any]:
        """Calculate predicted performance improvements from endurance training"""
        current_300h = self.athlete_data['current_300h_pr']
        target_300h = self.athlete_data['target_300h_goal']
        
        # Realistic improvement rates for 9th grader
        weekly_improvement_rate = 0.15  # seconds per week with proper training
        max_seasonal_improvement = 2.5   # seconds max improvement per season
        
        predicted_improvement = min(
            weeks_of_training * weekly_improvement_rate,
            max_seasonal_improvement
        )
        
        predicted_time = current_300h - predicted_improvement
        
        return {
            'current_pr': current_300h,
            'predicted_time': predicted_time,
            'improvement_needed_for_record': target_300h,
            'weeks_to_record_pace': max(0, (current_300h - target_300h) / weekly_improvement_rate),
            'probability_of_record': min(0.95, predicted_improvement / (current_300h - target_300h)),
            'training_phase_recommendations': self._get_phase_recommendations(predicted_time, target_300h)
        }
    
    def _get_phase_recommendations(self, predicted_time: float, target_time: float) -> List[str]:
        """Get training phase recommendations based on predicted vs target"""
        gap = predicted_time - target_time
        
        if gap <= 0.5:
            return ['Peak phase training', 'Race simulation', 'Taper for competition']
        elif gap <= 1.5:
            return ['Build phase training', 'Lactate threshold focus', 'Speed endurance']
        else:
            return ['Base building phase', 'Aerobic capacity development', 'General endurance']

# Global endurance training system
endurance_system = EnduranceTrainingSystem()