"""Your portfolio content. Edit ONLY this file to change text on the website.

main.py (the design/code) never needs to touch this file, so you can replace main.py
anytime without losing your details.
"""

# Your GitHub profile. Each project below links to GITHUB + "/" + repo name.
GITHUB = "https://github.com/aditya-ds-py"

PROFILE = {
    "name": "Aditya Sharma",
    "initials": "ADDY",
    "role": "Full-Stack Developer"
    "&" "AI-Engineer",
    "tagline": "I design and build fast, clean and thoughtful web products, from first sketch to production.",
    "about": [
        "I am a developer who likes turning messy ideas into simple, reliable products. "
        "I work across the stack, with a strong focus on performance and details people actually notice.",
        "When I am not coding, I am learning something new, writing about what I build, "
        "or helping other people get started in tech.",
    ],
    # "Projects" number on the homepage. Remove this line to count the projects below automatically.
    "stats": [("4", "Projects")],
    "skills": [
        ("Python", 92),
        ("JavaScript", 85),
        ("React", 80),
        ("SQL", 78),
        ("UI Design", 74),
        ("DevOps", 66),
    ],
    "projects": [
        {
            "icon": "storefront",
            "url": "https://github.com/aditya-ds-py/Revision-RAG-.git",  # change to the real repo link
            "title": "Rev-RAG",
            "desc": "AI-powered RAG system answering DSA questions with context-aware responses and clickable YouTube lecture timestamps.",
            "tags": ["RAG", "Generative-AI", "LLM"],
        },
        {
            "icon": "insights",
            "url": "https://github.com/aditya-ds-py/My-AI-Portfolio-Website.git",
            "title": "AI-Portfolio",
            "desc": "AI-powered developer portfolio featuring an interactive recruiter assistant, resume analysis, PDF job-description matching, and real-time AI chat",
            "tags": ["AI", "Python", "FastAPI"],
        },
        {
            "icon": "school",
            "url": f"{GITHUB}/LearnLoop",
            "title": "LearnLoop",
            "desc": "A learning platform with progress tracking, quizzes and spaced-repetition reminders.",
            "tags": ["Django", "PostgreSQL"],
        },
    ],
    # (icon, text). Email, phone and GitHub become clickable links automatically.
    "contact": [
        ("mail", "aditya.sharma.dev.coder@gmail.com"),
        ("call", "+91 720-520-1552"),
        ("code", "github.com/aditya-ds-py"),
        ("location_on", "Jatni, Odisha, India"),
    ],
    "chat_suggestions": [
        "What do you do?",
        "Which skills are you best at?",
        "Show me your projects",
        "How can I contact you?",
    ],
}
