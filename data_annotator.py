import pandas as pd
import re
import random
from collections import Counter

class RecruitmentDataAnnotator:
    def __init__(self, input_file='cleaned_recruitment_data.csv'):
        self.input_file = input_file
        self.df = None
        
        self.skill_keywords = {
            'programming_languages': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'kotlin', 'swift', 'typescript', 'scala', 'rust'],
            'web_technologies': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring', 'laravel', 'jquery'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sql server', 'sqlite', 'cassandra', 'elasticsearch'],
            'cloud_platforms': ['aws', 'azure', 'google cloud', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform'],
            'mobile_development': ['android', 'ios', 'react native', 'flutter', 'xamarin', 'cordova'],
            'data_science': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'r'],
            'tools': ['git', 'jira', 'confluence', 'postman', 'selenium', 'junit', 'maven', 'gradle']
        }
        
        self.experience_patterns = {
            'junior': [r'\b(0-2|1-2)\s*year', r'\bfresh', r'\bentry', r'\bbeginner', r'\bjunior'],
            'mid': [r'\b(2-5|3-6|3-5)\s*year', r'\bmid', r'\bintermediate'],
            'senior': [r'\b(5\+|6\+|7\+|8\+)\s*year', r'\bsenior', r'\blead', r'\bprincipal', r'\barchitect']
        }
        
        self.question_types = {
            'technical': ['algorithm', 'data structure', 'coding', 'programming', 'sql', 'database', 'system design'],
            'behavioral': ['tell me about', 'describe a time', 'how do you handle', 'what would you do'],
            'conceptual': ['what is', 'explain', 'difference between', 'how does', 'define']
        }
        
    def load_data(self):
        try:
            self.df = pd.read_csv(self.input_file)
            print(f"Loaded {len(self.df)} records from {self.input_file}")
            return True
        except FileNotFoundError:
            print(f"Error: {self.input_file} not found. Please run the cleaner first.")
            return False
            
    def extract_skills(self, text):
        if pd.isna(text):
            return []
            
        text = str(text).lower()
        found_skills = []
        
        for category, skills in self.skill_keywords.items():
            for skill in skills:
                if skill in text:
                    found_skills.append(skill)
                    
        return list(set(found_skills))
        
    def determine_experience_level(self, text, existing_level=None):
        if existing_level and existing_level in ['junior', 'mid', 'senior']:
            return existing_level
            
        if pd.isna(text):
            return 'unknown'
            
        text = str(text).lower()
        
        for level, patterns in self.experience_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return level
                    
        skill_count = len(self.extract_skills(text))
        if skill_count >= 8:
            return 'senior'
        elif skill_count >= 4:
            return 'mid'
        else:
            return 'junior'
            
    def classify_question_type(self, text):
        if pd.isna(text):
            return 'unknown'
            
        text = str(text).lower()
        
        scores = {}
        for qtype, keywords in self.question_types.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[qtype] = score
            
        if max(scores.values()) > 0:
            return max(scores.keys(), key=scores.get)
        else:
            return 'general'
            
    def annotate_job_descriptions(self):
        job_mask = self.df['content_type'] == 'job_description'
        job_data = self.df[job_mask].copy()
        
        job_data['extracted_skills'] = job_data['content'].apply(self.extract_skills)
        job_data['skill_count'] = job_data['extracted_skills'].apply(len)
        job_data['primary_skills'] = job_data['extracted_skills'].apply(lambda x: ', '.join(x[:5]) if x else 'None')
        
        job_data['experience_level_annotated'] = job_data.apply(
            lambda row: self.determine_experience_level(row['content'], row.get('experience_level')), axis=1
        )
        
        job_data['content_complexity'] = job_data['skill_count'].apply(
            lambda x: 'high' if x >= 8 else 'medium' if x >= 4 else 'low'
        )
        
        return job_data
        
    def annotate_interview_questions(self):
        interview_mask = self.df['content_type'] == 'interview_question'
        interview_data = self.df[interview_mask].copy()
        
        interview_data['question_type_annotated'] = interview_data['content'].apply(self.classify_question_type)
        
        interview_data['difficulty_level'] = interview_data.apply(
            lambda row: row.get('difficulty', 'medium') if pd.notna(row.get('difficulty')) 
            else self.infer_difficulty(row['content']), axis=1
        )
        
        interview_data['related_skills'] = interview_data['content'].apply(self.extract_skills)
        interview_data['skill_focus'] = interview_data['related_skills'].apply(
            lambda x: ', '.join(x[:3]) if x else 'General'
        )
        
        return interview_data
        
    def annotate_resumes(self):
        resume_mask = self.df['content_type'] == 'resume_summary'
        resume_data = self.df[resume_mask].copy()
        
        resume_data['extracted_skills'] = resume_data['content'].apply(self.extract_skills)
        resume_data['skill_diversity'] = resume_data['extracted_skills'].apply(
            lambda x: len(set([self.categorize_skill(skill) for skill in x])) if x else 0
        )
        
        resume_data['experience_level_annotated'] = resume_data.apply(
            lambda row: self.determine_experience_level(row['content'], row.get('experience_level')), axis=1
        )
        
        resume_data['profile_strength'] = resume_data.apply(
            lambda row: 'strong' if len(row['extracted_skills']) >= 6 and row['skill_diversity'] >= 3
            else 'moderate' if len(row['extracted_skills']) >= 3
            else 'basic', axis=1
        )
        
        return resume_data
        
    def categorize_skill(self, skill):
        for category, skills in self.skill_keywords.items():
            if skill in skills:
                return category
        return 'other'
        
    def infer_difficulty(self, question):
        question = str(question).lower()
        
        if any(word in question for word in ['algorithm', 'complexity', 'optimize', 'design', 'architecture']):
            return 'advanced'
        elif any(word in question for word in ['implement', 'code', 'write', 'solve']):
            return 'intermediate'
        else:
            return 'beginner'
            
    def create_sample_annotations(self, n_samples=20):
        annotated_samples = []
        
        job_annotations = self.annotate_job_descriptions()
        interview_annotations = self.annotate_interview_questions()
        resume_annotations = self.annotate_resumes()
        
        all_annotations = [
            (job_annotations, 'job_description'),
            (interview_annotations, 'interview_question'),
            (resume_annotations, 'resume_summary')
        ]
        
        samples_per_type = n_samples // 3
        
        for annotated_data, content_type in all_annotations:
            if len(annotated_data) > 0:
                sample_size = min(samples_per_type, len(annotated_data))
                sampled_data = annotated_data.sample(n=sample_size, random_state=42)
                annotated_samples.append(sampled_data)
                
        if annotated_samples:
            final_sample = pd.concat(annotated_samples, ignore_index=True)
        else:
            final_sample = pd.DataFrame()
            
        return final_sample
        
    def save_annotated_data(self, annotated_df, output_file='annotated_recruitment_data.csv'):
        columns_to_save = [
            'source', 'content', 'content_type', 'job_title', 'company', 'location',
            'extracted_skills', 'primary_skills', 'skill_focus', 'experience_level_annotated',
            'question_type_annotated', 'difficulty_level', 'content_complexity',
            'skill_diversity', 'profile_strength', 'skill_count'
        ]
        
        available_columns = [col for col in columns_to_save if col in annotated_df.columns]
        annotated_df[available_columns].to_csv(output_file, index=False)
        
        print(f"Annotated data saved to {output_file}. Total records: {len(annotated_df)}")
        
    def generate_annotation_summary(self, annotated_df):
        summary = {
            'total_records': len(annotated_df),
            'content_types': annotated_df['content_type'].value_counts().to_dict(),
        }
        
        if 'experience_level_annotated' in annotated_df.columns:
            summary['experience_levels'] = annotated_df['experience_level_annotated'].value_counts().to_dict()
            
        if 'question_type_annotated' in annotated_df.columns:
            summary['question_types'] = annotated_df['question_type_annotated'].value_counts().to_dict()
            
        if 'extracted_skills' in annotated_df.columns:
            all_skills = []
            for skills in annotated_df['extracted_skills'].dropna():
                if isinstance(skills, list):
                    all_skills.extend(skills)
                elif isinstance(skills, str):
                    all_skills.extend(eval(skills) if skills.startswith('[') else [skills])
            
            skill_counter = Counter(all_skills)
            summary['top_skills'] = dict(skill_counter.most_common(10))
            
        return summary
        
    def annotate_data(self):
        print("Starting data annotation process...")
        
        if not self.load_data():
            return False
            
        print("Creating annotated samples...")
        annotated_df = self.create_sample_annotations(n_samples=25)
        
        if len(annotated_df) == 0:
            print("No data available for annotation")
            return False
            
        print("Generating annotation summary...")
        summary = self.generate_annotation_summary(annotated_df)
        
        print("\nAnnotation Summary:")
        print(f"Total annotated records: {summary['total_records']}")
        print(f"Content types: {summary['content_types']}")
        
        if 'experience_levels' in summary:
            print(f"Experience levels: {summary['experience_levels']}")
            
        if 'question_types' in summary:
            print(f"Question types: {summary['question_types']}")
            
        if 'top_skills' in summary:
            print(f"Top skills: {dict(list(summary['top_skills'].items())[:5])}")
            
        self.save_annotated_data(annotated_df)
        print("Data annotation completed!")
        
        return True

if __name__ == "__main__":
    annotator = RecruitmentDataAnnotator()
    annotator.annotate_data()