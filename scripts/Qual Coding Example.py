# Author: Andrew Avitabile
# Purpose: This script analyzes teacher feedback using ChatGPT (GPT-4o-mini) to identify areas for improvementin teaching practice. 
# It processes feedback stored in an Excel file and saves the results.

# ============== SETUP INSTRUCTIONS ==============
# Before running this script, you need to:
# 1. Install required packages by running these commands in your terminal:
#    pip install pandas openai python-dotenv
#
# 2. Create a .env file containing your OpenAI API key like this:
#    OPENAI_API_KEY=your-key-here
#
# 3. Prepare your Excel file with at least these columns:
#    - text: contains the feedback to be analyzed
#    Note: Other columns will be preserved in the output

# Import required Python packages
import os                   # For working with file paths
import pandas as pd         # For handling Excel files and data processing
from openai import OpenAI   # For communicating with ChatGPT
from dotenv import load_dotenv  # For loading API key from .env file

# This class contains all the logic for analyzing feedback
class SimpleFeedbackAnalyzer:
    # This is a special method that runs when you create a new analyzer. It's like setting up your workspace before you start working.
    # self refers to the specific instance of the analyzer you're creating. It's like saying "this particular analyzer"
    # The other methods (create_prompt and get_area_for_improvement) are tools or functions that belong to this analyzer
    def __init__(self, env_path): 
        # This is information for future people who use the analyzer.
        """
        Sets up the feedback analyzer by:
        1. Loading the OpenAI API key
        2. Setting up the connection to OpenAI
        3. Defining the possible teaching skills to look for
        
        Args:
            env_path (str): Path to your .env file containing the OpenAI API key
        """
        # Load the API key from a specified .env file (env_path)
        load_dotenv(env_path)
        
        # Set up the connection to OpenAI's API
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")  # Get API key from environment variables (i.e., you need OPENAI_API_KEY in your .env file)
        )
        
        # List of teaching skills that ChatGPT will look for in the feedback
        # You can modify this list to look for different skills or change what you're looking for in the text
        self.teaching_skills = [
            "Classroom Management",
            "Lesson Planning",
            "Differentiation",
            "Assessment and Feedback",
            "Student Engagement",
            "Student Comprehension",
            "Communication"
        ]

    # Now we're defining a prompt to use for each row of text. 
    # Note that it requires a string of text (e.g., the feedback) 
    # Also note that it returns a string with the feedback surrounded by the prmopt
    def create_prompt(self, feedback_text):
        """
        Creates the instruction text (prompt) that will be sent to ChatGPT.
        
        Args:
            feedback_text (str): The feedback text to analyze
            
        Returns:
            str: The complete prompt for ChatGPT
        """
        # Convert the list of skills into a comma-separated string
        skills_list = ", ".join(self.teaching_skills)
        
        # Create the prompt that tells ChatGPT exactly what to do. This is where you may need to beg a bit.
        return f"""Analyze this feedback given to a pre-service teacher and identify the main area that needs improvement.
        
Feedback text:
{feedback_text}

Respond with ONLY ONE of these options: {skills_list}, "other", "none", or "multiple".

Rules:
- Choose "multiple" if there are several equally emphasized areas for improvement
- Choose "none" if no specific area for improvement is mentioned
- Choose "other" if the area for improvement doesn't match any of the listed skills
- Otherwise, choose the most prominent teaching skill that needs improvement"""

    def get_area_for_improvement(self, feedback_text):
        """
        Sends the feedback text to ChatGPT and gets back the area for improvement.
        
        Args:
            feedback_text (str): The feedback text to analyze
            
        Returns:
            str: The identified area for improvement
        """
        # Skip empty text to avoid errors
        if not feedback_text or len(feedback_text.strip()) < 0:
            return "none"

        try:
            # Send the request to ChatGPT
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # The GPT model to use
                messages=[
                    # Tell ChatGPT its role
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing teacher feedback. Respond with only the area that needs improvement."
                    },
                    # Provide the actual task and feedback
                    {
                        "role": "user",
                        "content": self.create_prompt(feedback_text)
                    }
                ],
                temperature=1  # Lower temperature means more consistent responses. If temperature is 0 you should get the same responses every time, but ChatGPT may be more risk-averse.
            )

            # Extract the response text from ChatGPT
            area = response.choices[0].message.content.strip()

            # Make sure the response is one of our expected values
            if area not in self.teaching_skills + ["other", "none", "multiple"]:
                area = "other"

            return area

        except Exception as e:
            # If anything goes wrong, print the error and return "none"
            print(f"Error analyzing feedback: {e}")
            return "none"

# Now we setup another function that will import our data from Excel and read our .env file
def process_excel_file(input_file, output_file, env_path):
    """
    Main function that:
    1. Reads the Excel file
    2. Processes each piece of feedback
    3. Saves the results to a new Excel file
    
    Args:
        input_file (str): Path to your input Excel file
        env_path (str): Path to your .env file with API key
    """
    try:
        # Load the Excel file into a pandas DataFrame
        print(f"Reading data from {input_file}...")
        df = pd.read_excel(input_file)
        
        # Create an instance of our feedback analyzer (i.e., we can run the SimpleFeedbackAnalyzer defined above using the word "analyzer")
        analyzer = SimpleFeedbackAnalyzer(env_path)
        
        # Add a new column to store our results
        df['area_for_improvement'] = 'none'
        
        # Process each row in the Excel file
        print("Analyzing feedback texts...")
        for index, row in df.iterrows():
            # Get the feedback text from the current row (note the importance of the text variable being present in the data)
            feedback_text = row['text']
            
            # Get the area for improvement from ChatGPT
            result = analyzer.get_area_for_improvement(feedback_text)
            
            # Save the result in our DataFrame. This is saved in our dataframe (df) at rownumber index and in column 'area_for_improvement'
            df.at[index, 'area_for_improvement'] = result
            
            # Show progress update every 10 rows. This is nice if you're running a lot of code.
            if (index + 1) % 10 == 0:
                print(f"Processed {index + 1} of {len(df)} rows")
        
        # Save the results to a new Excel file
        df.to_excel(output_file, index=False)
        print(f"\nAnalysis complete! Results saved to: {output_file}")
        
    except Exception as e:
        print(f"Error processing file: {e}")

def main():
    """
    Entry point of the script. Sets up file paths and starts the analysis.
    """
    # Specify where your files are located
    # IMPORTANT: Update these paths to match your computer!
    env_path = r"C:\Users\Andre\Dropbox\ChatGPT Qual Example\scripts\.env"
    input_file = r"C:\Users\Andre\Dropbox\ChatGPT Qual Example\data\Example Data.xlsx"
    output_file = r"C:\Users\Andre\Dropbox\ChatGPT Qual Example\output\Example Data - Coded.xlsx"
    
    # Start processing the Excel file
    process_excel_file(input_file, output_file, env_path)

# This is the standard way to run a Python script
if __name__ == "__main__":
    main()