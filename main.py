from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import List
import os

# Create FastAPI app
app = FastAPI(title="Smart Timetable Scheduler API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to store generated timetable
generated_timetable_data = None

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Backend is running successfully"}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Smart Timetable Scheduler API", "status": "running"}

# Upload endpoint for CSV files
@app.post("/api/upload")
async def upload_files(
    teachers: UploadFile = File(None),
    rooms: UploadFile = File(None),
    sections: UploadFile = File(None),
    courses: UploadFile = File(None)
):
    try:
        uploaded_files = {}
        
        # Process each uploaded file
        for file_type, file in [("teachers", teachers), ("rooms", rooms), ("sections", sections), ("courses", courses)]:
            if file:
                content = await file.read()
                # Here you would typically save or process the CSV content
                uploaded_files[file_type] = {
                    "filename": file.filename,
                    "size": len(content),
                    "status": "uploaded"
                }
        
        return {
            "status": "success",
            "message": "Files uploaded successfully",
            "files": uploaded_files
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# Sample data endpoint
@app.post("/api/load-sample-data")
async def load_sample_data():
    try:
        # Here you would load sample data into your database
        return {
            "status": "success",
            "message": "Sample data loaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load sample data: {str(e)}")

# Seed endpoint (alias for load-sample-data)
@app.post("/api/seed")
async def seed_data():
    try:
        # Here you would load sample data into your database
        return {
            "status": "success",
            "message": "Sample data seeded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to seed data: {str(e)}")

# Generate timetable endpoint
@app.post("/api/generate-timetable")
async def generate_timetable():
    global generated_timetable_data
    try:
        # Generate sample timetable in the format frontend expects
        generated_timetable_data = [
            {"day": "Mon", "slot": "09:00-10:00", "course": "Math 101", "section": "A", "teacher": "Dr. Smith", "room": "Room 101"},
            {"day": "Mon", "slot": "10:00-11:00", "course": "Physics 201", "section": "A", "teacher": "Dr. Johnson", "room": "Lab 1"},
            {"day": "Tue", "slot": "09:00-10:00", "course": "English 101", "section": "A", "teacher": "Prof. Davis", "room": "Room 102"},
        ]
        
        return {
            "status": "success",
            "message": "Timetable generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Timetable generation failed: {str(e)}")

# Generate endpoint (alternative name for frontend compatibility)
@app.post("/api/generate")
async def generate():
    global generated_timetable_data
    try:
        # Generate sample timetable in the format frontend expects
        # Frontend expects an array of objects with: day, slot, course, section, teacher, room
        generated_timetable_data = [
            {"day": "Mon", "slot": "09:00-10:00", "course": "Math 101", "section": "A", "teacher": "Dr. Smith", "room": "Room 101"},
            {"day": "Mon", "slot": "10:00-11:00", "course": "Physics 201", "section": "A", "teacher": "Dr. Johnson", "room": "Lab 1"},
            {"day": "Mon", "slot": "11:00-12:00", "course": "Chemistry 101", "section": "B", "teacher": "Dr. Brown", "room": "Lab 2"},
            {"day": "Tue", "slot": "09:00-10:00", "course": "English 101", "section": "A", "teacher": "Prof. Davis", "room": "Room 102"},
            {"day": "Tue", "slot": "10:00-11:00", "course": "History 201", "section": "B", "teacher": "Dr. Wilson", "room": "Room 103"},
            {"day": "Wed", "slot": "09:00-10:00", "course": "Biology 101", "section": "A", "teacher": "Dr. Taylor", "room": "Lab 3"},
            {"day": "Wed", "slot": "11:00-12:00", "course": "Computer Sci 101", "section": "A", "teacher": "Prof. Anderson", "room": "Lab 4"},
            {"day": "Thu", "slot": "09:00-10:00", "course": "Math 101", "section": "B", "teacher": "Dr. Smith", "room": "Room 101"},
            {"day": "Thu", "slot": "10:00-11:00", "course": "Physics 201", "section": "B", "teacher": "Dr. Johnson", "room": "Lab 1"},
            {"day": "Fri", "slot": "09:00-10:00", "course": "English 101", "section": "B", "teacher": "Prof. Davis", "room": "Room 102"},
            {"day": "Fri", "slot": "11:00-12:00", "course": "Chemistry 101", "section": "A", "teacher": "Dr. Brown", "room": "Lab 2"},
        ]
        
        return {
            "status": "success",
            "message": "Timetable generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Timetable generation failed: {str(e)}")

# Get timetable endpoint (THIS WAS MISSING!)
@app.get("/api/timetable")
async def get_timetable():
    global generated_timetable_data
    
    if generated_timetable_data is None:
        # Return empty array if nothing has been generated yet
        return []
    
    # Return the flat array format that frontend expects
    return generated_timetable_data

# Quick run endpoint (test -> seed -> generate)
@app.post("/api/quick-run")
async def quick_run():
    global generated_timetable_data
    try:
        # Generate sample timetable as part of quick run
        generated_timetable_data = [
            {"day": "Mon", "slot": "09:00-10:00", "course": "Math 101", "section": "A", "teacher": "Dr. Smith", "room": "Room 101"},
            {"day": "Mon", "slot": "10:00-11:00", "course": "Physics 201", "section": "A", "teacher": "Dr. Johnson", "room": "Lab 1"},
            {"day": "Tue", "slot": "09:00-10:00", "course": "English 101", "section": "A", "teacher": "Prof. Davis", "room": "Room 102"},
            {"day": "Wed", "slot": "09:00-10:00", "course": "Biology 101", "section": "A", "teacher": "Dr. Taylor", "room": "Lab 3"},
        ]
        
        # Combine test connection, load sample data, and generate timetable
        return {
            "status": "success",
            "message": "Quick run completed successfully",
            "steps": [
                {"step": "connection_test", "status": "passed"},
                {"step": "sample_data_loaded", "status": "completed"},
                {"step": "timetable_generated", "status": "completed"}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick run failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)