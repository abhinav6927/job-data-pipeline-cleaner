import requests
from bs4 import BeautifulSoup
import csv
import time
import json
from urllib.parse import urljoin, urlparse
import random

class JobDataScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.scraped_data = []
        
    def scrape_indeed_jobs(self, query="software engineer", location="india", pages=3):
        base_url = "https://in.indeed.com/jobs"
        
        for page in range(pages):
            params = {
                'q': query,
                'l': location,
                'start': page * 10
            }
            
            try:
                response = requests.get(base_url, params=params, headers=self.headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h2', class_='jobTitle')
                        title = title_elem.get_text().strip() if title_elem else "N/A"
                        
                        company_elem = card.find('span', class_='companyName')
                        company = company_elem.get_text().strip() if company_elem else "N/A"
                        
                        location_elem = card.find('div', class_='companyLocation')
                        location = location_elem.get_text().strip() if location_elem else "N/A"
                        
                        summary_elem = card.find('div', class_='summary')
                        description = summary_elem.get_text().strip() if summary_elem else "N/A"
                        
                        salary_elem = card.find('span', class_='salaryText')
                        salary = salary_elem.get_text().strip() if salary_elem else "N/A"
                        
                        self.scraped_data.append({
                            'source': 'indeed',
                            'job_title': title,
                            'company': company,
                            'location': location,
                            'description': description,
                            'salary': salary,
                            'content_type': 'job_description'
                        })
                        
                    except Exception as e:
                        continue
                        
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"Error scraping Indeed page {page}: {e}")
                
    def scrape_naukri_jobs(self, query="software-engineer", pages=2):
        base_url = "https://www.naukri.com"
        search_url = f"{base_url}/{query}-jobs"
        
        try:
            response = requests.get(search_url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_containers = soup.find_all('div', class_='srp-jobtuple-wrapper')
            
            for container in job_containers[:15]:
                try:
                    title_elem = container.find('a', class_='title')
                    title = title_elem.get_text().strip() if title_elem else "N/A"
                    
                    company_elem = container.find('a', class_='subTitle')
                    company = company_elem.get_text().strip() if company_elem else "N/A"
                    
                    exp_elem = container.find('span', class_='ellipsis experience')
                    experience = exp_elem.get_text().strip() if exp_elem else "N/A"
                    
                    location_elem = container.find('span', class_='ellipsis location')
                    location = location_elem.get_text().strip() if location_elem else "N/A"
                    
                    desc_elem = container.find('div', class_='job-description')
                    description = desc_elem.get_text().strip() if desc_elem else "N/A"
                    
                    self.scraped_data.append({
                        'source': 'naukri',
                        'job_title': title,
                        'company': company,
                        'location': location,
                        'description': description,
                        'experience': experience,
                        'content_type': 'job_description'
                    })
                    
                except Exception as e:
                    continue
                    
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            print(f"Error scraping Naukri: {e}")
            
    def scrape_interview_questions(self):
        interview_questions = [
            "What is the difference between abstract class and interface in Java?",
            "Explain the concept of polymorphism in object-oriented programming",
            "How do you handle exceptions in Python?",
            "What is the time complexity of quicksort algorithm?",
            "Describe the MVC architecture pattern",
            "What is the difference between SQL and NoSQL databases?",
            "Explain RESTful web services and HTTP methods",
            "What is the difference between stack and heap memory?",
            "How does garbage collection work in Java?",
            "Explain the concept of dependency injection",
            "What is the difference between synchronous and asynchronous programming?",
            "Describe the SOLID principles of software design",
            "What is the difference between unit testing and integration testing?",
            "Explain the concept of microservices architecture",
            "How do you optimize database queries for better performance?",
            "What is the difference between authentication and authorization?",
            "Explain the concept of version control and Git workflow",
            "What are design patterns and give examples?",
            "How do you handle security in web applications?",
            "Describe the software development lifecycle phases"
        ]
        
        for i, question in enumerate(interview_questions):
            self.scraped_data.append({
                'source': 'manual_collection',
                'content': question,
                'content_type': 'interview_question',
                'difficulty': 'intermediate' if i % 3 == 0 else 'beginner' if i % 3 == 1 else 'advanced',
                'category': 'technical'
            })
            
    def scrape_resume_samples(self):
        resume_samples = [
            "Software Engineer with 3+ years experience in Java, Spring Boot, and microservices. Developed scalable web applications serving 100K+ users.",
            "Full Stack Developer proficient in React, Node.js, and MongoDB. Built responsive web applications with modern UI/UX design principles.",
            "Python Developer with expertise in Django, Flask, and data analysis. Experience in machine learning and AI model development.",
            "DevOps Engineer skilled in AWS, Docker, Kubernetes, and CI/CD pipelines. Automated deployment processes reducing deployment time by 60%.",
            "Mobile App Developer with 4+ years in iOS and Android development. Published 5+ apps on App Store and Play Store with 50K+ downloads.",
            "Data Scientist with strong background in statistics, machine learning, and data visualization. Proficient in Python, R, and SQL.",
            "Frontend Developer specializing in Angular, Vue.js, and modern CSS frameworks. Created pixel-perfect responsive designs for enterprise clients.",
            "Backend Developer with expertise in .NET, C#, and SQL Server. Built robust APIs serving millions of requests per day.",
            "Cloud Architect with AWS and Azure certifications. Designed and implemented scalable cloud infrastructure for enterprise applications.",
            "Security Engineer focused on application security, penetration testing, and vulnerability assessment. Certified in CISSP and CEH.",
            "QA Engineer with 5+ years in manual and automated testing. Expertise in Selenium, TestNG, and continuous testing practices.",
            "Product Manager with technical background in software development. Led cross-functional teams to deliver products with 95% user satisfaction.",
            "Systems Administrator with Linux and Windows server management experience. Maintained 99.9% uptime for critical business applications.",
            "Database Administrator specialized in MySQL, PostgreSQL, and Oracle. Optimized database performance improving query speed by 40%.",
            "Software Architect with 8+ years designing enterprise-level applications. Expert in system design, scalability, and performance optimization."
        ]
        
        for i, resume in enumerate(resume_samples):
            experience_level = "senior" if i % 3 == 0 else "mid" if i % 3 == 1 else "junior"
            self.scraped_data.append({
                'source': 'manual_collection',
                'content': resume,
                'content_type': 'resume_summary',
                'experience_level': experience_level,
                'domain': 'software_engineering'
            })
            
    def save_raw_data(self, filename='raw_recruitment_data.csv'):
        fieldnames = ['source', 'content', 'content_type', 'job_title', 'company', 'location', 'description', 'salary', 'experience', 'difficulty', 'category', 'experience_level', 'domain']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in self.scraped_data:
                row = {}
                for field in fieldnames:
                    row[field] = item.get(field, '')
                writer.writerow(row)
                
        print(f"Raw data saved to {filename}. Total records: {len(self.scraped_data)}")
        
    def scrape_monster_jobs(self, query="software+engineer", location="india", pages=2):
        base_url = "https://www.monsterindia.com"
        
        for page in range(pages):
            search_url = f"{base_url}/search/{query}-jobs-in-{location}?page={page+1}"
            
            try:
                response = requests.get(search_url, headers=self.headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                job_cards = soup.find_all('div', {'data-testid': 'job-card'}) or soup.find_all('div', class_='card jobTuple')
                
                for card in job_cards:
                    try:
                        title_elem = card.find('a', class_='jobTitle') or card.find('h2') or card.find('h3')
                        title = title_elem.get_text().strip() if title_elem else "N/A"
                        
                        company_elem = card.find('span', class_='companyName') or card.find('div', class_='companyName')
                        company = company_elem.get_text().strip() if company_elem else "N/A"
                        
                        location_elem = card.find('span', class_='locationsContainer') or card.find('div', class_='jobLocation')
                        location = location_elem.get_text().strip() if location_elem else "N/A"
                        
                        desc_elem = card.find('div', class_='job-summary') or card.find('p')
                        description = desc_elem.get_text().strip() if desc_elem else "N/A"
                        
                        exp_elem = card.find('span', class_='experience')
                        experience = exp_elem.get_text().strip() if exp_elem else "N/A"
                        
                        self.scraped_data.append({
                            'source': 'monster',
                            'job_title': title,
                            'company': company,
                            'location': location,
                            'description': description,
                            'experience': experience,
                            'content_type': 'job_description'
                        })
                        
                    except Exception as e:
                        continue
                        
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"Error scraping Monster page {page}: {e}")
                
    def scrape_times_jobs(self, query="software engineer", pages=2):
        base_url = "https://www.timesjobs.com"
        
        for page in range(pages):
            search_url = f"{base_url}/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={query.replace(' ', '+')}&txtLocation=&cboWorkExp1=0&cboWorkExp2=37&pDate=I&sequence={page+1}&startPage=1"
            
            try:
                response = requests.get(search_url, headers=self.headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                job_items = soup.find_all('li', class_='clearfix job-bx wht-shd-bx') or soup.find_all('article', class_='jobTuple')
                
                for item in job_items[:8]:
                    try:
                        title_elem = item.find('h2') or item.find('h3', class_='jobTitle')
                        title = title_elem.get_text().strip() if title_elem else "N/A"
                        
                        company_elem = item.find('h3', class_='joblist-comp-name') or item.find('span', class_='comp-name')
                        company = company_elem.get_text().strip() if company_elem else "N/A"
                        
                        location_elem = item.find('ul', class_='top-jd-dtl clearfix') or item.find('span', class_='loc')
                        location = location_elem.get_text().strip() if location_elem else "N/A"
                        
                        desc_elem = item.find('ul', class_='list-job-dtl clearfix') or item.find('div', class_='job-description')
                        description = desc_elem.get_text().strip() if desc_elem else "N/A"
                        
                        exp_elem = item.find('li', string=lambda text: text and 'Exp' in text)
                        experience = exp_elem.get_text().strip() if exp_elem else "N/A"
                        
                        self.scraped_data.append({
                            'source': 'timesjobs',
                            'job_title': title,
                            'company': company,
                            'location': location,
                            'description': description,
                            'experience': experience,
                            'content_type': 'job_description'
                        })
                        
                    except Exception as e:
                        continue
                        
                time.sleep(random.uniform(3, 6))
                
            except Exception as e:
                print(f"Error scraping TimesJobs page {page}: {e}")
                
    def scrape_shine_jobs(self, query="software+engineer", pages=2):
        base_url = "https://www.shine.com"
        
        for page in range(pages):
            search_url = f"{base_url}/job-search/{query}?p={page+1}"
            
            try:
                response = requests.get(search_url, headers=self.headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                job_cards = soup.find_all('div', class_='jobCard_jobCard__') or soup.find_all('div', class_='job-card')
                
                for card in job_cards:
                    try:
                        title_elem = card.find('a', class_='jobCard_pRel__') or card.find('h2')
                        title = title_elem.get_text().strip() if title_elem else "N/A"
                        
                        company_elem = card.find('div', class_='jobCard_companyName__') or card.find('span', class_='company')
                        company = company_elem.get_text().strip() if company_elem else "N/A"
                        
                        location_elem = card.find('div', class_='jobCard_jobLocation_secondary__') or card.find('div', class_='location')
                        location = location_elem.get_text().strip() if location_elem else "N/A"
                        
                        desc_elem = card.find('div', class_='jobCard_jobDesc__') or card.find('p', class_='description')
                        description = desc_elem.get_text().strip() if desc_elem else "N/A"
                        
                        salary_elem = card.find('div', class_='jobCard_salary__')
                        salary = salary_elem.get_text().strip() if salary_elem else "N/A"
                        
                        self.scraped_data.append({
                            'source': 'shine',
                            'job_title': title,
                            'company': company,
                            'location': location,
                            'description': description,
                            'salary': salary,
                            'content_type': 'job_description'
                        })
                        
                    except Exception as e:
                        continue
                        
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                print(f"Error scraping Shine page {page}: {e}")
                
    def scrape_foundit_jobs(self, query="software engineer", pages=2):
        base_url = "https://www.foundit.in"
        
        for page in range(pages):
            search_url = f"{base_url}/srp/results?query={query.replace(' ', '%20')}&locations=All%20locations&experience=0%20to%2050"
            
            try:
                response = requests.get(search_url, headers=self.headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                job_articles = soup.find_all('article', class_='jobTuple') or soup.find_all('div', class_='srpResultCardContainer')
                
                for article in job_articles[:10]:
                    try:
                        title_elem = article.find('a', class_='title') or article.find('h3')
                        title = title_elem.get_text().strip() if title_elem else "N/A"
                        
                        company_elem = article.find('a', class_='subTitle') or article.find('span', class_='companyName')
                        company = company_elem.get_text().strip() if company_elem else "N/A"
                        
                        location_elem = article.find('span', class_='locationsContainer') or article.find('div', class_='location')
                        location = location_elem.get_text().strip() if location_elem else "N/A"
                        
                        desc_elem = article.find('div', class_='jobDescription') or article.find('p')
                        description = desc_elem.get_text().strip() if desc_elem else "N/A"
                        
                        exp_elem = article.find('span', class_='experience')
                        experience = exp_elem.get_text().strip() if exp_elem else "N/A"
                        
                        self.scraped_data.append({
                            'source': 'foundit',
                            'job_title': title,
                            'company': company,
                            'location': location,
                            'description': description,
                            'experience': experience,
                            'content_type': 'job_description'
                        })
                        
                    except Exception as e:
                        continue
                        
                time.sleep(random.uniform(3, 5))
                
            except Exception as e:
                print(f"Error scraping Foundit page {page}: {e}")
                
    def scrape_instahyre_jobs(self, query="software-engineer"):
        base_url = "https://www.instahyre.com"
        search_url = f"{base_url}/search-jobs/{query}/"
        
        try:
            response = requests.get(search_url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_cards = soup.find_all('div', class_='job-listing-container') or soup.find_all('div', class_='job-card')
            
            for card in job_cards[:12]:
                try:
                    title_elem = card.find('h3') or card.find('h2', class_='job-title')
                    title = title_elem.get_text().strip() if title_elem else "N/A"
                    
                    company_elem = card.find('h4') or card.find('span', class_='company-name')
                    company = company_elem.get_text().strip() if company_elem else "N/A"
                    
                    location_elem = card.find('div', class_='job-location') or card.find('span', class_='location')
                    location = location_elem.get_text().strip() if location_elem else "N/A"
                    
                    desc_elem = card.find('div', class_='job-description-text') or card.find('p')
                    description = desc_elem.get_text().strip() if desc_elem else "N/A"
                    
                    salary_elem = card.find('div', class_='salary-range')
                    salary = salary_elem.get_text().strip() if salary_elem else "N/A"
                    
                    self.scraped_data.append({
                        'source': 'instahyre',
                        'job_title': title,
                        'company': company,
                        'location': location,
                        'description': description,
                        'salary': salary,
                        'content_type': 'job_description'
                    })
                    
                except Exception as e:
                    continue
                    
            time.sleep(random.uniform(4, 7))
            
        except Exception as e:
            print(f"Error scraping Instahyre: {e}")

    def run_scraper(self):
        print("Starting data scraping process...")
        
        print("Scraping interview questions...")
        self.scrape_interview_questions()
        
        print("Scraping resume samples...")
        self.scrape_resume_samples()
        
        print("Scraping job postings from Indeed...")
        self.scrape_indeed_jobs()
        
        print("Scraping job postings from Naukri...")
        self.scrape_naukri_jobs()
        
        print("Scraping job postings from Monster...")
        self.scrape_monster_jobs()
        
        print("Scraping job postings from TimesJobs...")
        self.scrape_times_jobs()
        
        print("Scraping job postings from Shine...")
        self.scrape_shine_jobs()
        
        print("Scraping job postings from Foundit...")
        self.scrape_foundit_jobs()
        
        print("Scraping job postings from Instahyre...")
        self.scrape_instahyre_jobs()
        
        self.save_raw_data()
        print("Data scraping completed!")

if __name__ == "__main__":
    scraper = JobDataScraper()
    scraper.run_scraper()
