import pdfplumber
import re

class ResumeParserService:
    @staticmethod
    def extract_text(file_stream):
        """
        Extracts raw text from a PDF file stream using pdfplumber.
        file_stream should be a file-like object or a byte stream.
        """
        text = ""
        with pdfplumber.open(file_stream) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    @staticmethod
    def parse_resume(text):
        """
        Parses raw resume text to extract candidate name, email, phone, role, and skills.
        Uses robust, rule-based regex patterns and technical keyword matching.
        """
        if not text:
            return {
                "name": None,
                "email": None,
                "phone": None,
                "role": None,
                "skills": []
            }

        # 1. Extract Email
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        emails = re.findall(email_pattern, text)
        email = emails[0] if emails else None

        # 2. Extract Phone
        phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        phone = phones[0] if phones else None

        # 3. Extract Name
        # Heuristic: Find the first non-empty line that doesn't contain contact details or common structural headings.
        name = None
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines[:5]:
            if "@" in line or "http" in line or "/" in line or "\\" in line:
                continue
            if line.upper() in ["RESUME", "CURRICULUM VITAE", "CV", "CONTACT", "EXPERIENCE", "EDUCATION", "SUMMARY"]:
                continue
            cleaned = re.sub(r'[^a-zA-Z\s]', '', line).strip()
            if 2 < len(cleaned) < 50:
                name = line
                break

        # 4. Extract Target Role
        # Heuristic: Check the document for common software engineering designations.
        role = None
        role_keywords = [
            "Software Engineer", "Software Developer", "Backend Developer", "Backend Engineer",
            "Frontend Developer", "Frontend Engineer", "Full Stack Developer", "Full Stack Engineer",
            "Data Scientist", "Data Analyst", "Machine Learning Engineer", "DevOps Engineer",
            "Product Manager", "Project Manager", "QA Engineer", "Mobile Developer", "iOS Developer",
            "Android Developer", "SDE Intern", "SDE", "Full Stack SDE"
        ]
        
        text_lower = text.lower()
        for kw in role_keywords:
            if kw.lower() in text_lower:
                role = kw
                break

        # Fallback to lines near the top that describe a title/role
        if not role and len(lines) > 1:
            for line in lines[1:4]:
                if any(k in line.lower() for k in ["engineer", "developer", "designer", "manager", "analyst", "intern", "student"]):
                    if len(line) < 60:
                        role = line
                        break

        # 5. Extract Skills
        # Heuristic: Check against a list of common tech stack keywords.
        known_skills = [
            "Python", "JavaScript", "TypeScript", "HTML", "CSS", "SQL", "NoSQL",
            "React", "Angular", "Vue", "Node.js", "Node", "Express", "Django", "Flask", "FastAPI",
            "Spring Boot", "Java", "C++", "C#", "Go", "Golang", "Rust", "Ruby", "PHP",
            "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Oracle",
            "Docker", "Kubernetes", "AWS", "Google Cloud", "GCP", "Azure", "Git", "GitHub",
            "GitLab", "CI/CD", "Jenkins", "Terraform", "Ansible", "Linux",
            "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Scikit-Learn",
            "Data Structures", "Algorithms", "System Design", "Microservices", "REST API",
            "GraphQL", "WebSockets", "Firebase", "Supabase", "Tailwind CSS", "Bootstrap"
        ]
        
        extracted_skills = []
        for skill in known_skills:
            escaped_skill = re.escape(skill)
            if skill.lower() in ["go", "c"]:
                pattern = rf'\b{escaped_skill}\b'
            else:
                pattern = rf'\b{escaped_skill}\b|{escaped_skill}'
            
            if re.search(pattern, text, re.IGNORECASE):
                extracted_skills.append(skill)

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "role": role,
            "skills": extracted_skills
        }
