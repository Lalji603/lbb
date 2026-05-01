from django.db import models



from django.contrib.auth.models import AbstractUser



from django.utils import timezone







class User(AbstractUser):



    ROLE_CHOICES = [



        ('admin', 'Admin'),



        ('patient', 'Patient'),



        ('donor', 'Donor'),



    ]



    BLOOD_GROUP_CHOICES = [



        ('A+', 'A+'),



        ('A-', 'A-'),



        ('B+', 'B+'),



        ('B-', 'B-'),



        ('AB+', 'AB+'),



        ('AB-', 'AB-'),



        ('O+', 'O+'),



        ('O-', 'O-'),



    ]



    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')



    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)



    phone = models.CharField(max_length=15, blank=True, null=True)



    address = models.TextField(blank=True, null=True)



    date_of_birth = models.DateField(blank=True, null=True)



    is_verified = models.BooleanField(default=False)



    created_at = models.DateTimeField(auto_now_add=True)



    updated_at = models.DateTimeField(auto_now=True)







    def __str__(self):



        return f"{self.username} ({self.role})"







class BloodStock(models.Model):



    BLOOD_GROUP_CHOICES = [



        ('A+', 'A+'),



        ('A-', 'A-'),



        ('B+', 'B+'),



        ('B-', 'B-'),



        ('AB+', 'AB+'),



        ('AB-', 'AB-'),



        ('O+', 'O+'),



        ('O-', 'O-'),



    ]



    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, unique=True)



    units = models.PositiveIntegerField(default=0)



    last_updated = models.DateTimeField(auto_now=True)







    def __str__(self):



        return f"{self.blood_group}: {self.units} units"







class BloodRequest(models.Model):



    STATUS_CHOICES = [



        ('pending', 'Pending'),



        ('approved', 'Approved'),



        ('fulfilled', 'Fulfilled'),



        ('cancelled', 'Cancelled'),



    ]



    URGENCY_CHOICES = [



        ('low', 'Low'),



        ('medium', 'Medium'),



        ('high', 'High'),



        ('critical', 'Critical'),



    ]



    BLOOD_GROUP_CHOICES = [



        ('A+', 'A+'),



        ('A-', 'A-'),



        ('B+', 'B+'),



        ('B-', 'B-'),



        ('AB+', 'AB+'),



        ('AB-', 'AB-'),



        ('O+', 'O+'),



        ('O-', 'O-'),



    ]



    



    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blood_requests', 



                              null=True, blank=True)



    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)



    units_required = models.PositiveIntegerField()



    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default='medium')



    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')



    hospital_name = models.CharField(max_length=200)



    hospital_address = models.TextField()



    doctor_name = models.CharField(max_length=100)



    reason = models.TextField()



    requested_date = models.DateTimeField(auto_now_add=True)



    required_date = models.DateField()



    approved_date = models.DateTimeField(blank=True, null=True)



    fulfilled_date = models.DateTimeField(blank=True, null=True)



    assigned_donor = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, 



                                       related_name='donations', limit_choices_to={'role': 'donor'})



    



    def __str__(self):



        patient_name = self.patient.username if self.patient else "Unassigned"



        return f"Request #{self.id} - {patient_name} - {self.blood_group}"







class Donation(models.Model):



    STATUS_CHOICES = [



        ('scheduled', 'Scheduled'),



        ('completed', 'Completed'),



        ('cancelled', 'Cancelled'),



    ]



    



    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations_made')



    blood_request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE, related_name='donations')



    donation_date = models.DateTimeField()



    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')



    units_donated = models.PositiveIntegerField(default=1)



    notes = models.TextField(blank=True, null=True)



    created_at = models.DateTimeField(auto_now_add=True)



    



    def __str__(self):



        return f"Donation by {self.donor.username} for Request #{self.blood_request.id}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, default='general') # e.g., 'request_created', 'request_approved', etc.
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"



