from django.db import models
from django.contrib.auth.models import User

class Bounty(models.Model):
    STATUS_CHOICES = [
        ('wanted', 'Wanted'),
        ('captured', 'Captured'),
    ]

    DANGER_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('extreme', 'Extreme'),
    ]

    target_name = models.CharField(max_length=255, help_text="The outlaw / debtor / cargo description")
    reward = models.DecimalField(max_digits=10, decimal_places=2, help_text="The bounty / tab amount / declared value")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='wanted')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bounties')
    
    # Flavor/creative fields
    danger_level = models.CharField(max_length=10, choices=DANGER_CHOICES, default='medium')
    last_seen_at = models.CharField(max_length=255, blank=True, null=True, help_text="Last known location")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Bounties"

    def __str__(self):
        return f"{self.target_name} ({self.status.upper()}) - {self.reward} USD"
