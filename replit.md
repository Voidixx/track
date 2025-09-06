# Tyler Messina - Elite 300m Hurdles Training Hub

## Overview

A professional-grade athletic training platform designed for Tyler Messina, a 9th-grade student at Union City Area High School in Pennsylvania, who is training to break the school 300m hurdles record of 42.08 seconds. Tyler currently holds a PR of 47.20s (as of May 2025) and needs to improve by 5.12 seconds to achieve his goal.

The application integrates real athletic performance data from Athletic.net and MileSplit, provides comprehensive rankings and competitor analysis, and features professional-grade training tools including form analysis, rival tracking, and advanced analytics.

## User Preferences

Preferred communication style: Simple, everyday language.
Location: Union City, Pennsylvania
Current Status: 9th Grade at Union City Area High School
Athletic Profiles: 
- Athletic.net High School: #27122466
- Athletic.net Middle School: #23393294  
- MileSplit: #13417195-tyler-messina

## System Architecture

### Professional Frontend Architecture
- **Template Engine**: Jinja2 with advanced templating for professional dashboard
- **UI Framework**: Bootstrap 5.3.3 with custom professional styling
- **Design System**: Modern professional sports-oriented design with:
  - Hamburger menu navigation with smooth animations
  - Real-time charts and analytics using Chart.js
  - Interactive calendar integration with FullCalendar
  - Video analysis and photo upload capabilities
  - Mobile-responsive design with professional gradients
- **Icons**: Font Awesome 6.5.1 for comprehensive iconography
- **Layout**: Multi-section professional dashboard with:
  - Hero section with athlete stats and progress tracking
  - Real-time rankings and competitor analysis
  - Interactive training calendar
  - Form analysis with video/photo upload
  - MileSplit news integration

### Enhanced Backend Architecture
- **Framework**: Flask with professional route organization
- **Application Structure**: 
  - `app.py`: Enhanced application factory with PostgreSQL integration
  - `professional_routes.py`: Advanced route handling with Athletic.net integration
  - `athletic_data_service.py`: Real-time data fetching from Athletic.net/MileSplit
  - `models.py`: Comprehensive database models for all features
  - `weather_service.py`: Weather integration for training recommendations
- **Database**: PostgreSQL with comprehensive models for:
  - Personal records with Athletic.net sync
  - Video analysis and form tracking
  - Coach communication system
  - Weekly statistics and progress tracking
  - Goal setting and achievement monitoring

### Advanced Data Integration
- **Athletic Performance Data**: Real-time integration with:
  - Athletic.net profile data (Middle School: #23393294, High School: #27122466)
  - MileSplit profile and article mentions (#13417195-tyler-messina)
  - Automatic performance record synchronization
  - Rankings estimation and competitor analysis
- **Training Data**: Enhanced JSON-based storage with:
  - 730-day comprehensive training cycle
  - Weather-adaptive workout selection
  - Form drills and technique analysis
  - Progressive goal tracking
- **Media Management**: Professional photo/video upload system for form analysis

### Professional Business Logic
- **Performance Analytics**: Advanced analytics including:
  - Real-time rankings (District, State, National levels)
  - Competitor analysis and rival tracking
  - Progress tracking toward school record goal
  - Performance trend analysis with charts
- **Form Analysis**: Video/photo analysis system with technique tracking
- **Communication**: Coach messaging system with priority levels
- **Weather Integration**: Union City, PA weather data for training adaptation

## External Dependencies

### Athletic Data Integration
- **Data Sources**: 
  - Athletic.net API integration for real performance data
  - MileSplit profile scraping for rankings and articles
  - Automated data synchronization for personal records
- **Web Scraping**: BeautifulSoup4 and Trafilatura for:
  - Performance data extraction from athletic websites
  - Rankings and competitor analysis
  - News article mentions and recognition tracking

### Weather Service Integration  
- **API Provider**: OpenWeatherMap API for real-time weather data
- **Location**: Union City, Pennsylvania (Tyler's actual location)
- **Condition Mapping**: Enhanced weather condition processing for training recommendations
- **Fallback Strategy**: Graceful degradation with mock data when API unavailable
- **Timeout Configuration**: 10-second request timeout for reliability

### Professional Libraries
- **Backend**: Flask, SQLAlchemy, PostgreSQL, Pandas for analytics
- **Media Processing**: Pillow for image handling, video upload support
- **Data Visualization**: Chart.js integration, Plotly for advanced analytics
- **UI/UX**: Bootstrap 5.3.3, Font Awesome 6.5.1, FullCalendar for scheduling
- **Scraping**: BeautifulSoup4, lxml, Trafilatura, Requests with session management

### Enhanced Configuration Management
- **Environment Variables**: 
  - `OPENWEATHER_API_KEY`: Weather service authentication
  - `DATABASE_URL`: PostgreSQL connection string
  - `SESSION_SECRET`: Flask session encryption key
- **Media Storage**: Professional file upload handling with:
  - Secure filename processing
  - Video/photo upload directories
  - File type validation and security

## Recent Major Updates (September 2025)

### Professional Dashboard Overhaul
- Complete UI redesign with professional sports-oriented styling
- Hamburger menu navigation with smooth animations
- Real-time athlete statistics and progress tracking
- Interactive charts showing performance progression

### Athletic Data Integration
- Real-time data sync from Athletic.net profiles
- MileSplit news and article integration
- Comprehensive rankings system (District, State, National)
- Competitor analysis and rival tracking

### Advanced Features Added
- Professional form analysis with video/photo upload
- Interactive training calendar with FullCalendar
- Enhanced coach communication system
- Advanced statistics dashboard with Chart.js
- Weather-adaptive training recommendations for Union City, PA

### Database Enhancement
- PostgreSQL integration with comprehensive models
- Video analysis tracking system
- Coach messaging with priority levels
- Weekly statistics and goal monitoring
- Personal records with Athletic.net synchronization