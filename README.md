# YIASCM Pantry - Competitive Team Purchasing Game

A Flask-based web application designed as a competitive team-based purchasing game platform. Teams participate in two strategic rounds with different objectives while their performance is tracked on leaderboards.

## Features

### Team Management
- **Team Registration**: Secure registration with password hashing
- **Team Authentication**: Session-based login/logout system
- **Team Dashboard**: Overview of progress and round status

### Game Rounds
- **Round 1**: "Spend Less, Buy More" - Maximize quantity within budget constraints
- **Round 2**: "Spend More, Buy Less" - Maximize spending while minimizing quantity
- **Dynamic Scoring**: Different scoring systems for each round
- **Real-time Calculations**: Live price and score calculations during gameplay

### Admin Panel
- **Team Management**: View all registered teams with detailed information on hover
- **Team Deletion**: Remove teams and their submissions
- **Product Management**: Add, edit, and delete products
- **Budget Control**: Set and modify Round 1 budget limits
- **Submission Tracking**: Monitor all round submissions in real-time

### Leaderboards
- **Round-based Rankings**: Separate leaderboards for each round
- **Score Display**: Clear scoring information and team performance
- **Medal System**: Visual recognition for top 3 performers

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Data Storage**: JSON files (teams.json, products.json, submissions.json, settings.json)
- **Security**: Werkzeug password hashing, Flask sessions
- **UI Framework**: Bootstrap 5 with dark theme

## Installation & Setup

### Prerequisites
- Python 3.7+
- Flask
- Werkzeug

### Installation Steps

1. **Clone or download the project files**
2. **Install dependencies**:
   ```bash
   pip install flask werkzeug
   ```

3. **Set environment variables**:
   ```bash
   export SESSION_SECRET="your-secret-key-here"
   ```

4. **Run the application**:
   ```bash
   python main.py
   