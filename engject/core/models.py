from django.db import models
from datetime import date


# =====================================
# TECHNOLOGY TRENDS
# =====================================

class TechnologyTrend(models.Model):

    DOMAIN_CHOICES = [

        # CORE TECH
        ("AI", "Artificial Intelligence"),
        ("ML", "Machine Learning"),
        ("DS", "Data Science"),
        ("CV", "Computer Vision"),
        ("NLP", "Natural Language Processing"),

        # SOFTWARE & DEV
        ("WebDev", "Web Development"),
        ("AppDev", "Mobile App Development"),
        ("DevOps", "DevOps"),
        ("Cloud", "Cloud Computing"),
        ("Backend", "Backend Engineering"),
        ("Frontend", "Frontend Engineering"),

        # SECURITY
        ("Cybersecurity", "Cybersecurity"),
        ("EthicalHacking", "Ethical Hacking"),

        # HARDWARE / CORE ENGINEERING
        ("IoT", "Internet of Things"),
        ("Robotics", "Robotics"),
        ("Embedded", "Embedded Systems"),
        ("VLSI", "VLSI Design"),

        # EMERGING TECH
        ("Blockchain", "Blockchain"),
        ("ARVR", "AR/VR"),
        ("Quantum", "Quantum Computing"),

        # INDUSTRY DOMAINS (VERY IMPORTANT 🔥)
        ("Healthcare", "Healthcare Technology"),
        ("FinTech", "FinTech"),
        ("EdTech", "EdTech"),
        ("AgriTech", "AgriTech"),
        ("SmartCity", "Smart City Solutions"),
        ("Sustainability", "Sustainability / Green Tech"),

        # MISC
        ("Other", "Other"),

    ]

    title = models.CharField(max_length=200)

    description = models.TextField()

    domain = models.CharField(
        max_length=100,
        choices=DOMAIN_CHOICES,
        default="Other",
        db_index=True   # faster filtering
    )

    image = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["domain"]),
        ]


    def __str__(self):
        return f"{self.title} ({self.domain})"


# =====================================
# API USAGE TRACKER
# =====================================

class ApiUsage(models.Model):

    date = models.DateField(default=date.today, unique=True)

    # EXISTING
    google_count = models.IntegerField(default=0)
    brave_count = models.IntegerField(default=0)
    tavily_count = models.IntegerField(default=0)

    # 🔥 NEW (for your project scaling)
    github_count = models.IntegerField(default=0)
    kscst_count = models.IntegerField(default=0)
    sih_count = models.IntegerField(default=0)

    total_requests = models.IntegerField(default=0)  # overall tracking


    def save(self, *args, **kwargs):
        self.total_requests = (
            self.google_count +
            self.brave_count +
            self.tavily_count +
            self.github_count +
            self.kscst_count +
            self.sih_count
        )
        super().save(*args, **kwargs)


    def __str__(self):
        return f"API usage for {self.date}"