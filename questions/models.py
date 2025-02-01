from django.db import models

from django.utils import timezone


class SubmissionTracker(models.Model):
    user_id = models.CharField(
        max_length=100
    )  # Store the user ID sent from the frontend
    date = models.DateField(default=timezone.now)  # Stores the date of submission
    submission_count = models.PositiveIntegerField(
        default=0
    )  # Tracks the number of submissions for the day

    def __str__(self):
        return f"{self.user_id} - {self.date} - {self.submission_count} submissions"

    class Meta:
        verbose_name = "Submission Tracker"
        verbose_name_plural = "Submission Trackers"
        unique_together = ("user_id", "date")  # Ensure only one entry per user per day


class Questions(models.Model):
    question = models.CharField(max_length=2000)
    domain = models.CharField(max_length=200)
    subdomain = models.CharField(max_length=200, default="")
    answer = models.TextField()


# class UserSubmission(models.Model):
#     user_id = models.CharField(max_length=2000)
#     date = models.DateField()
#     question = models.ForeignKey(
#         Questions, on_delete=models.CASCADE
#     )  # Link to the Questions model
#     answer = models.TextField()
#     problem_count = models.IntegerField(
#         default=0
#     )  # Count of problems submitted per day
#     submission_time = models.DateTimeField(auto_now_add=True)  # Track submission time

#     class Meta:
#         # No unique constraint, multiple submissions per day are allowed
#         pass
