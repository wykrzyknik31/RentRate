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
