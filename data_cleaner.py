import pandas as pd
import re
import html
from bs4 import BeautifulSoup
import numpy as np

class RecruitmentDataCleaner:
    def __init__(self, input_file='raw_recruitment_data.csv'):
        self.input_file = input_file
        self.df = None
        
    def load_data(self):
        try:
            self.df = pd.read_csv(self.input_file)
            print(f"Loaded {len(self.df)} records from {self.input_file}")
        except FileNotFoundError:
            print(f"Error: {self.input_file} not found. Please run the scraper first.")
            return False
        return True
        
    def remove_duplicates(self):
        initial_count = len(self.df)
        
        # Interview questions and resumes
        mask_manual = self.df['source'].str.contains('manual_collection', na=False)
        manual = self.df[mask_manual].drop_duplicates(subset=['content', 'content_type'], keep='first')
        
        # Job postings
        mask_job = self.df['content_type'].str.contains('job_description', na=False)
        jobs = self.df[mask_job].drop_duplicates(subset=['job_title', 'company', 'description', 'location'], keep='first')
        
        # Others (if any)
        others = self.df[~(mask_manual | mask_job)].drop_duplicates(keep='first')
        
        # Combine all
        self.df = pd.concat([manual, jobs, others], ignore_index=True)
        self.df.reset_index(drop=True, inplace=True)
        
        final_count = len(self.df)
        print(f"Removed {initial_count - final_count} duplicate records")
        
    def remove_empty_rows(self):
        initial_count = len(self.df)
        
        important_columns = ['content', 'job_title', 'description']
        mask = pd.Series([False] * len(self.df))
        
        for col in important_columns:
            if col in self.df.columns:
                mask |= self.df[col].notna() & (self.df[col].str.strip() != '') & (self.df[col] != 'N/A')
        
        self.df = self.df[mask]
        final_count = len(self.df)
        print(f"Removed {initial_count - final_count} empty/invalid rows")
        
    def clean_html(self, text):
        if pd.isna(text) or text == '':
            return text
            
        text = html.unescape(text)
        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text()
        
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'&[a-zA-Z]+;', '', text)
        
        return text
        
    def normalize_text(self, text):
        if pd.isna(text) or text == '':
            return text
            
        text = str(text)
        
        text = self.clean_html(text)
        
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        text = re.sub(r'[^\w\s\.\,\!\?\-\(\)\:\;\'\"]', '', text)
        
        text = re.sub(r'\.{2,}', '.', text)
        text = re.sub(r'\,{2,}', ',', text)
        
        return text
        
    def standardize_experience_levels(self):
        if 'experience_level' not in self.df.columns:
            return
            
        experience_mapping = {
            'entry': 'junior',
            'entry level': 'junior',
            'entry-level': 'junior',
            'fresher': 'junior',
            'beginner': 'junior',
            '0-2 years': 'junior',
            'intermediate': 'mid',
            'mid level': 'mid',
            'mid-level': 'mid',
            '2-5 years': 'mid',
            '3-6 years': 'mid',
            'experienced': 'senior',
            'senior level': 'senior',
            'senior-level': 'senior',
            '5+ years': 'senior',
            '6+ years': 'senior',
            'expert': 'senior',
            'lead': 'senior'
        }
        
        self.df['experience_level'] = self.df['experience_level'].str.lower()
        self.df['experience_level'] = self.df['experience_level'].replace(experience_mapping)
        
    def standardize_content_types(self):
        if 'content_type' not in self.df.columns:
            return
            
        type_mapping = {
            'job posting': 'job_description',
            'job_posting': 'job_description',
            'job ad': 'job_description',
            'job_ad': 'job_description',
            'interview_questions': 'interview_question',
            'interview q&a': 'interview_question',
            'resume': 'resume_summary',
            'cv': 'resume_summary',
            'cv_summary': 'resume_summary'
        }
        
        self.df['content_type'] = self.df['content_type'].str.lower()
        self.df['content_type'] = self.df['content_type'].replace(type_mapping)
        
    def clean_salary_data(self):
        if 'salary' not in self.df.columns:
            return
            
        def clean_salary(salary):
            if pd.isna(salary) or salary == '' or salary == 'N/A':
                return 'Not disclosed'
                
            salary = str(salary).strip()
            
            salary = re.sub(r'[^\d\.\,\-\s\w]', '', salary)
            salary = re.sub(r'\s+', ' ', salary)
            
            return salary
            
        self.df['salary'] = self.df['salary'].apply(clean_salary)
        
    def clean_location_data(self):
        if 'location' not in self.df.columns:
            return
            
        def clean_location(location):
            if pd.isna(location) or location == '' or location == 'N/A':
                return 'Remote'
                
            location = str(location).strip()
            location = self.normalize_text(location)
            
            location = re.sub(r'\d+\s*km.*', '', location, flags=re.IGNORECASE)
            location = re.sub(r'(work from home|wfh|remote)', 'Remote', location, flags=re.IGNORECASE)
            
            return location
            
        self.df['location'] = self.df['location'].apply(clean_location)
        
    def merge_content_fields(self):
        def merge_content(row):
            content_parts = []
            # Add all non-empty fields
            for field in ['content', 'description', 'job_title']:
                val = row.get(field)
                if pd.notna(val) and str(val).strip() != '' and str(val).strip() != 'N/A':
                    content_parts.append(str(val).strip())
            return ' '.join(content_parts) if content_parts else ''
        self.df['content'] = self.df.apply(merge_content, axis=1)
        
    def apply_text_cleaning(self):
        text_columns = ['content', 'job_title', 'company', 'description']
        
        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].apply(self.normalize_text)
                
    def validate_and_filter(self):
        initial_count = len(self.df)
        
        if 'content' in self.df.columns:
            self.df = self.df[self.df['content'].astype(str).str.len() >= 5]
            # Only filter rows where content is entirely non-word characters
            self.df = self.df[~self.df['content'].astype(str).str.match(r'^[^\w]+$')]
        
        final_count = len(self.df)
        print(f"Filtered out {initial_count - final_count} records with insufficient content")
        
    def save_cleaned_data(self, output_file='cleaned_recruitment_data.csv'):
        self.df.to_csv(output_file, index=False)
        print(f"Cleaned data saved to {output_file}. Final record count: {len(self.df)}")
        
    def clean_data(self):
        print("Starting data cleaning process...")
        
        if not self.load_data():
            return False
            
        print("Removing duplicates...")
        self.remove_duplicates()
        
        print("Removing empty rows...")
        self.remove_empty_rows()
        
        print("Merging content fields...")
        self.merge_content_fields()
        
        print("Applying text cleaning...")
        self.apply_text_cleaning()
        
        print("Standardizing experience levels...")
        self.standardize_experience_levels()
        
        print("Standardizing content types...")
        self.standardize_content_types()
        
        print("Cleaning salary data...")
        self.clean_salary_data()
        
        print("Cleaning location data...")
        self.clean_location_data()
        
        print("Validating and filtering data...")
        self.validate_and_filter()
        
        self.save_cleaned_data()
        print("Data cleaning completed!")
        
        return True

if __name__ == "__main__":
    cleaner = RecruitmentDataCleaner()
    cleaner.clean_data()
