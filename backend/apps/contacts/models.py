from django.db import models
from django.conf import settings

class Contact(models.Model):
    # user = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE,
    #     related_name='contacts'
    # )
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    aadhar = models.CharField(max_length=20, null=True, blank=True)
    father_name = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    email_id = models.EmailField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    nationality = models.CharField(max_length=50, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    other_mobile = models.CharField(max_length=20, null=True, blank=True)
    permanent = models.TextField(null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    source_file = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"

    class Meta:
        app_label = 'contacts'  # ✅ YEH LINE ADD KARO