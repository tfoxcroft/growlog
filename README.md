# GrowLog - Plant Growth Tracking Application

## Overview
GrowLog is a web application for tracking plant growth and related facts. It provides CRUD functionality for plant entries and includes user authentication features.

## Technology Stack
- Python (Flask/Django-like framework)
- HTML/CSS
- Docker (optional)

## File Structure
```
.
├── app.py                # Main application entry point
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker compose configuration
├── requirements.txt      # Python dependencies
├── design_rules.md       # Design guidelines
├── static/               # Static assets
│   ├── css/styles.css    # Main stylesheet
│   └── images/           # Plant images
└── templates/            # HTML templates
    ├── base.html         # Base template
    ├── auth_layout.html  # Authentication layout
    ├── login.html        # Login page
    ├── list.html         # Plant listing
    ├── view.html         # Plant detail view
    ├── add.html          # Add new plant
    ├── edit.html         # Edit plant
    ├── add_fact.html     # Add plant facts
    ├── 403.html          # Forbidden page
    └── admin/            # Admin templates
        ├── users.html    # User management
        └── edit_user.html # Edit user
```

## Setup Instructions

### Prerequisites
- Python 3.x
- pip
- Docker (optional)

### Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
#### Development
```bash
python app.py
```

#### Using Docker
Build and run:
```bash
docker-compose up --build
```

## Configuration
Environment variables may be required - check `app.py` for specific requirements.

## Design Guidelines
Refer to [design_rules.md](design_rules.md) for UI/UX design principles and implementation details.

## Contributing
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License
[Specify license here if applicable]