# Tyler's 300m Hurdles Training Hub

## Overview

A personalized training web application designed for Tyler, a 10th-grade student at UCASD (University City Area School District), who is training for the 300m hurdles with a goal of breaking the school record of 42.08 seconds. The application provides daily workout recommendations that adapt based on weather conditions, cycling through a comprehensive 2-year training plan that includes speed endurance, strength training, technique work, and recovery sessions.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask for server-side rendering
- **UI Framework**: Bootstrap 5.3.0 for responsive design and components
- **Styling**: Custom CSS with CSS variables for theming, featuring a sports-oriented color scheme (orange, blue, yellow)
- **Icons**: Font Awesome 6.4.0 for consistent iconography
- **Layout**: Single-page application with card-based layout for workout information

### Backend Architecture
- **Framework**: Flask web framework with modular route organization
- **Application Structure**: 
  - `app.py`: Application factory and configuration
  - `routes.py`: Request handling and business logic
  - `main.py`: Application entry point
- **Session Management**: Flask sessions with configurable secret key
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxies
- **Logging**: Python logging module configured for debugging

### Data Storage Solutions
- **Training Data**: JSON file-based storage (`training_plan.json`) containing:
  - 7-day cycling workout plan with indoor/outdoor alternatives
  - Detailed form drills and techniques
  - Focus areas (Speed Endurance, Strength Training, Technique Work, etc.)
- **Date Calculation**: Dynamic workout selection based on training start date (September 1, 2024)
- **Cycle Logic**: 730-day training plan that automatically cycles through the program

### Core Business Logic
- **Workout Selection Algorithm**: Calculates current day in training cycle and selects appropriate workout
- **Weather-Based Adaptation**: Automatically switches between indoor and outdoor workouts based on weather conditions
- **Error Handling**: Graceful degradation with fallback workouts when data loading fails

## External Dependencies

### Weather Service Integration
- **API Provider**: OpenWeatherMap API for real-time weather data
- **Location**: Hardcoded to San Diego (Tyler's location)
- **Condition Mapping**: Translates detailed weather conditions to simplified categories (clear, partly_cloudy, cloudy, rain, snow)
- **Fallback Strategy**: Demo mode when API key is unavailable, graceful error handling for API failures
- **Timeout Configuration**: 10-second request timeout for reliability

### Third-Party Libraries
- **Flask**: Web framework and templating
- **Requests**: HTTP client for weather API integration
- **Werkzeug**: WSGI utilities and proxy handling
- **Bootstrap**: Frontend CSS framework (CDN-hosted)
- **Font Awesome**: Icon library (CDN-hosted)

### Configuration Management
- **Environment Variables**: 
  - `OPENWEATHER_API_KEY`: Weather service authentication
  - `SESSION_SECRET`: Flask session encryption key
- **Development Settings**: Debug mode enabled, host configured for 0.0.0.0:5000