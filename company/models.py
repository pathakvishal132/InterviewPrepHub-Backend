from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class CompanyQuestion(models.Model):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

    LEVEL_CHOICES = [
        (HIGH, "High"),
        (MEDIUM, "Medium"),
        (LOW, "Low"),
    ]
    companies = models.ManyToManyField(Company)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default=MEDIUM)
    question = models.TextField()
    answer = models.TextField()
    date_of_creation = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=255, null=True, blank=True)
    min_experience = models.IntegerField(default=0)
    max_experience = models.IntegerField(default=5)

    def __str__(self):
        return f"{self.question[:50]}..."


class CompanyReview(models.Model):
    company_id = models.CharField(max_length=100)  # Company identifier
    company_name = models.CharField(max_length=255)  # Company name
    job_role = models.CharField(max_length=255)
    interview_level = models.CharField(max_length=255, blank=True, null=True)
    questions_asked = models.TextField(blank=True, null=True)
    company_culture = models.TextField(blank=True, null=True)
    company_payroll = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company_name} - {self.job_role}"
