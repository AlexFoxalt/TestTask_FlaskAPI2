# Test Task Flask CSV
~


## Development flow
[1.01] 14.01:
- Installed packages, virtual env, dependencies
- Created row Flask-REST project
- Filled DB with data from csv file (fill_db.py)
- Created view for 'Info' rout (/api/info)
- Designed ORM queries for generating response
- Created view for 'Timeline' rout (/api/timeline...)
- Made simple Pydantic model for validation of incoming data from URL string (models.py)
- Developed function for separation timestamp by step (week, 2-week, month)
- Developed Queryset for parsing data from DB between timedelta
- Timestamp and separation depend on real life time flow, so every week is starting from monday
- Added days counter for better information displaying
- Made tests via Postman, all is working by now