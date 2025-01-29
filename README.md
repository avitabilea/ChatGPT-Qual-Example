# Teacher Feedback Analysis Script

This folder contains an example Python script analyzes written feedback provided to pre-service teachers (PSTs) using ChatGPT (GPT-4o-mini) to identify areas for improvement in teaching practices. It processes feedback stored in an Excel file and saves the results, identifying areas for improvement like classroom management, lesson planning, and more.

## Features
- Analyze feedback using GPT-4o-mini.
- Identify key areas for improvement (e.g., Classroom Management, Lesson Planning, Student Engagement).
- Process feedback stored in Excel files.
- Save the results to a new Excel file with an additional column identifying the area for improvement.

## Setup Instructions

Before running the script, ensure you have completed the following setup steps:

### 0. Confirm you have python installed on your computer and an IDE that can run python script (e.g., Positron)

### 1. Install Required Packages
Run these commands in your terminal to install the necessary dependencies:
```bash
pip install pandas openai python-dotenv
```

### 2. Setup an API key with OpenAI and save to an .env file
Replace `your-key-here` with your actual OpenAI API key obtained from the OpenAI platform.

### 3. Excel File Requirements
- Your input Excel file must include:
- A column named `text` containing the feedback data for analysis
- Any additional columns will be preserved in the output file

### 4. How to Use
- Update File Paths: Ensure that the file paths for your .env file and input Excel file are correct in the script.
- Run the Script: Execute the script to begin analyzing the feedback. The results will be saved to a new Excel file with an added column, area_for_improvement, indicating the identified area for improvement.