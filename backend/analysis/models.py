from django.db import models
from django.contrib.auth.models import User
from resumes.models import Resume
from jobs.models import JobDescription

class Analysis(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='analyses'
    )
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='analyses'
    )
    job_description = models.ForeignKey(
        JobDescription,
        on_delete=models.CASCADE,
        related_name='analyses'
    )
    match_score = models.IntegerField(null=True, blank=True, default=None)
    result = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        score_str = f"{self.match_score}%" if self.match_score is not None else "N/A"
        return f"Analysis #{self.id} - {self.job_description.title} ({score_str})"
