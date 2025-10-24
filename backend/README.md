# RentRate Backend

Flask-based REST API for the RentRate platform.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python app.py
```

**Alternative: Use the clean start script (recommended if you encounter issues):**
```bash
# On Linux/Mac:
./start_clean.sh

# On Windows:
start_clean.bat
```

The API will be available at `http://localhost:5000`

## Database Migrations

The RentRate backend uses **Flask-Migrate** (built on Alembic) for database schema management. This ensures consistent database schema across all environments and makes schema changes safe and reproducible.

### Why Migrations?

- ✅ **Version Control**: Database schema is versioned alongside code
- ✅ **Consistency**: Same schema across development, Docker, and production
- ✅ **Safety**: No more manual `ALTER TABLE` scripts
- ✅ **Rollback**: Easy to revert schema changes if needed
- ✅ **Team Collaboration**: Everyone gets the same database structure

### Initial Setup

The migrations are already initialized in the `migrations/` directory. When you start the application for the first time, migrations will be applied automatically.

### Running Migrations

#### Automatic (Recommended)

Migrations run automatically when using the startup scripts:

```bash
# The clean start script runs migrations automatically
./start_clean.sh        # Linux/Mac
start_clean.bat         # Windows
```

#### Manual Migration Commands

For more control, you can run migrations manually:

```bash
# Set the Flask app
export FLASK_APP=app.py  # Linux/Mac
set FLASK_APP=app.py     # Windows

# Apply pending migrations
flask db upgrade

# Check current database version
flask db current

# View migration history
flask db history
```

**Using the helper script (Linux/Mac only):**
```bash
./migrate.sh upgrade    # Apply migrations
./migrate.sh current    # Check current version
./migrate.sh history    # View history
```

### Creating New Migrations

When you modify database models in `app.py`:

1. **Generate migration automatically:**
   ```bash
   export FLASK_APP=app.py
   flask db migrate -m "Description of changes"
   ```
   
   Or use the helper script:
   ```bash
   ./migrate.sh migrate "Description of changes"
   ```

2. **Review the generated migration file** in `migrations/versions/`
   - Check that the changes are correct
   - Verify both `upgrade()` and `downgrade()` functions

3. **Apply the migration:**
   ```bash
   flask db upgrade
   ```

4. **Commit the migration file** to version control:
   ```bash
   git add migrations/versions/
   git commit -m "Add migration: Description of changes"
   ```

### Migration Best Practices

- **Always review** generated migrations before applying them
- **Test migrations** in development before production
- **One migration per feature** - keep migrations focused
- **Write descriptive messages** - help your team understand changes
- **Never modify** applied migrations - create new ones instead
- **Backup your database** before running migrations in production

### Common Migration Tasks

**Add a new column:**
```python
# In app.py, add to your model:
new_field = db.Column(db.String(100), nullable=True)

# Then generate and apply migration:
flask db migrate -m "Add new_field to Model"
flask db upgrade
```

**Modify a column:**
```python
# Change the model definition, then:
flask db migrate -m "Modify column_name in Model"
flask db upgrade
```

**Add an index:**
```python
# Add to your model:
__table_args__ = (
    db.Index('idx_field_name', 'field_name'),
)

# Then generate and apply:
flask db migrate -m "Add index on field_name"
flask db upgrade
```

### Troubleshooting

**Issue: "Can't locate revision identified by 'xxxxx'"**
- Your database is out of sync with migrations
- Solution: Back up data, drop database, and run `flask db upgrade`

**Issue: Migration fails with data integrity error**
- The migration conflicts with existing data
- Solution: Modify migration to handle existing data, or clean the database

**Issue: "Target database is not up to date"**
- You have pending migrations
- Solution: Run `flask db upgrade`

### Docker Usage

In Docker, migrations run automatically on container startup via the `startup.sh` script. No manual intervention needed.

```bash
# Docker Compose handles everything:
docker compose up --build
```

The API will be available at `http://localhost:5000`

## Testing the Server

After starting the server, you can verify it's running correctly:

```bash
# Test the root endpoint
curl http://localhost:5000/

# Or visit in your browser:
# http://localhost:5000/
```

You should see a JSON response:
```json
{
  "status": "ok",
  "message": "RentRate API is running"
}
```

## API Endpoints

### Root
- `GET /` - API status check (returns 200 OK with status message)

### Health Check
- `GET /api/health` - Check if API is running

### Reviews
- `GET /api/reviews` - Get all reviews (optional query param: `property_id`)
- `POST /api/reviews` - Create a new review (supports JSON and multipart/form-data with photos)
- `GET /api/reviews/<id>` - Get a specific review

### Properties
- `GET /api/properties` - Get all properties with review stats
- `GET /api/properties/<id>` - Get a specific property with all reviews

### Photos
- `GET /api/photos/<id>` - Get a photo by ID (returns image file)

## Request Examples

### Create a Review (JSON)
```bash
curl -X POST http://localhost:5000/api/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "address": "123 Main St, Apt 4B",
    "city": "New York",
    "property_type": "apartment",
    "reviewer_name": "John Doe",
    "rating": 4,
    "review_text": "Great apartment, spacious and clean!",
    "landlord_name": "Jane Smith",
    "landlord_rating": 5
  }'
```

### Create a Review with Photos (Multipart Form)
```bash
curl -X POST http://localhost:5000/api/reviews \
  -F "address=123 Main St, Apt 4B" \
  -F "city=New York" \
  -F "property_type=apartment" \
  -F "reviewer_name=John Doe" \
  -F "rating=4" \
  -F "review_text=Great apartment, spacious and clean!" \
  -F "photos=@photo1.jpg" \
  -F "photos=@photo2.jpg"
```

**Photo Upload Limits:**
- Maximum 5 photos per review
- Supported formats: JPG, JPEG, PNG
- Maximum file size: 5MB per photo

### Get All Reviews
```bash
curl http://localhost:5000/api/reviews
```

## Troubleshooting

### Getting 404 errors when accessing endpoints

If you're seeing 404 errors even though the server is running, try these steps:

1. **Clear Python cache and restart:**
   ```bash
   # On Windows PowerShell:
   Remove-Item -Recurse -Force __pycache__
   Remove-Item *.pyc
   python app.py

   # On Linux/Mac:
   rm -rf __pycache__
   find . -name "*.pyc" -delete
   python app.py
   ```

2. **Make sure you're accessing the correct port:**
   - Check the server logs to see which port Flask is using
   - The server should show: `Running on http://127.0.0.1:5000`
   - If it shows a different port (like 5001), use that port instead

3. **Verify the server is running correctly:**
   ```bash
   curl http://localhost:5000/
   ```
   You should see: `{"message": "RentRate API is running", "status": "ok"}`

4. **Check for multiple instances:**
   - Make sure you don't have multiple instances of the server running
   - On Windows: Check Task Manager for python.exe processes
   - On Linux/Mac: `ps aux | grep python`
   - Kill any extra processes and restart

5. **Try accessing via IP address:**
   - Instead of `localhost`, try `127.0.0.1`
   - Example: `http://127.0.0.1:5000/`

### Port 5000 already in use

If you see an error that port 5000 is already in use:

1. **Find and kill the process using port 5000:**
   ```bash
   # On Windows PowerShell:
   netstat -ano | findstr :5000
   taskkill /PID <process_id> /F

   # On Linux/Mac:
   lsof -ti:5000 | xargs kill -9
   ```

2. **Or use a different port:**
   Edit `app.py` and change the last line:
   ```python
   app.run(debug=True, host='0.0.0.0', port=5001)  # Use port 5001 instead
   ```

### Virtual environment issues

Make sure your virtual environment is activated:
- On Windows: Look for `(venv)` at the beginning of your command prompt
- On Linux/Mac: Look for `(venv)` in your terminal prompt

If not activated:
```bash
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### Dependencies not installed

If you get import errors, reinstall dependencies:
```bash
pip install -r requirements.txt
```
