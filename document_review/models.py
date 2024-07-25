from django.db import models
from django.contrib.auth.models import User
from tinymce.models import HTMLField
from django.db.models import Case, When, IntegerField


class Custom_User(models.Model):
    class Role(models.TextChoices):
        ASSISTANT="ASSISTANT",'Assistant'
        AUDITOR="AUDITOR",'Auditor'
        SUPERVISOR='SUPERVISOR','Supervisor'
        MANAGER='MANAGER','Manager'
    role = models.CharField(max_length=50,choices=Role.choices)
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    def __str__(self):
        return str(self.user)
class FileType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
class File(models.Model):
    file = models.FileField(upload_to='uploaded_files',null=False)
    file_type = models.ForeignKey(FileType, on_delete=models.CASCADE)
    description = HTMLField()
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    upload_date = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False) 
    def __str__(self):
        return str(self.file)
    class Meta:
        ordering = ['-upload_date']

class ReviewOperation(models.Model):
    OPERATION_TYPE_CHOICES = [
        ('confirm', 'Confirm'),
        ('request_modification', 'Request Modification'),
        ('reject', 'Reject'),
        ('pending','Pending')
    ]
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='review_operations')
    forward_by=models.ForeignKey(User, on_delete=models.CASCADE, null=True,blank=True)

    reviewed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_operations',null=True,blank=True)
    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPE_CHOICES)
    comments = models.TextField()
    operation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file} - {self.operation_type}"
    class Meta:
            ordering = [
                Case(
                    When(operation_type='reject', then=0),
                    When(operation_type='request_modification', then=1),
                    When(operation_type='pending', then=2),
                    When(operation_type='confirm', then=3),
                    output_field=IntegerField(),
                ),
                '-operation_date',
            ]

class FileRequest(models.Model):
    requested_by = models.ForeignKey(Custom_User, on_delete=models.CASCADE, related_name='requested_files')
    requested_from = models.ForeignKey(Custom_User, on_delete=models.CASCADE, related_name='requests_received')
    file_type = models.ForeignKey(FileType, on_delete=models.CASCADE)
    description = HTMLField()
    request_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.requested_by} requesting {self.file_type} from {self.requested_from}"

class FileResponse(models.Model):
    file_request = models.OneToOneField(FileRequest, on_delete=models.CASCADE, related_name='response')
    response_file = models.FileField(upload_to='response_files/')
    comments = HTMLField()
    response_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to {self.file_request}"