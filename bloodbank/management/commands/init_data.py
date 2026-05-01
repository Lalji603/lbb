from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from bloodbank.models import BloodStock

User = get_user_model()

class Command(BaseCommand):
    help = 'Initialize the database with sample data'

    def handle(self, *args, **options):
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@lifeserve.org',
                password='admin123',
                first_name='Admin',
                last_name='User',
                role='admin',
                is_verified=True,
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS('Admin user created successfully'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))

        # Create sample blood stocks
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        for blood_group in blood_groups:
            BloodStock.objects.get_or_create(
                blood_group=blood_group,
                defaults={'units': 100}
            )
        
        self.stdout.write(self.style.SUCCESS('Blood stocks initialized successfully'))
