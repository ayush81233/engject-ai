from django.db import models
from datetime import date


# =====================================
# TECHNOLOGY TRENDS
# =====================================

class TechnologyTrend(models.Model):

    DOMAIN_CHOICES = [

        ("AI", "Artificial Intelligence"),
        ("Cybersecurity", "Cybersecurity"),
        ("Blockchain", "Blockchain"),
        ("IoT", "Internet of Things"),
        ("Robotics", "Robotics"),
        ("Cloud", "Cloud Computing"),
        ("Data Science", "Data Science"),
        ("Other", "Other"),

    ]

    title = models.CharField(max_length=200)

    description = models.TextField()

    domain = models.CharField(
        max_length=100,
        choices=DOMAIN_CHOICES,
        default="Other"
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
        return self.title



# =====================================
# API USAGE TRACKER
# =====================================

class ApiUsage(models.Model):

    date = models.DateField(default=date.today, unique=True)

    google_count = models.IntegerField(default=0)

    brave_count = models.IntegerField(default=0)

    tavily_count = models.IntegerField(default=0)


    def __str__(self):
        return f"API usage for {self.date}"