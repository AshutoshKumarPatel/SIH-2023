from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator

class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
        ('IN_PROGRESS', 'In Progress'),
    ]

    ticket_no = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField(validators=[MinLengthValidator(10)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket No: {self.ticket_no}, Status: {self.status}"

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.ticket_no:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(SupportTicket, self).save(*args, **kwargs)
