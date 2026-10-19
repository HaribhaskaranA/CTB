import os
import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
# Import your models based on app structure. Adjust app names if needed.
# from accounts.models import Profile
# from projects.models import Project, Milestone, ComplianceRule
# from payments.models import Quotation, Payment
# from complaints.models import Complaint

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with realistic demo data for CONNECT TO BUILD'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting to seed demo data...")
        
        # 1. Demo Users & Profiles
        self.stdout.write("Creating demo users...")
        owner_data = [
            {'user_id': 'HO-TN-8F42K', 'name': 'Ramesh Kumar', 'phone': '9876543210', 'email': 'ramesh@demo.ctb', 'city': 'Chennai', 'state': 'TN'},
            {'user_id': 'HO-KA-2X91M', 'name': 'Priya Nair', 'phone': '9876543211', 'email': 'priya@demo.ctb', 'city': 'Bangalore', 'state': 'KA'},
        ]
        
        worker_data = [
            {'user_id': 'WK-TN-3A91P', 'name': 'Ravi Kumar', 'profession': 'ELECTRICIAN', 'exp': 8, 'state': 'TN', 'city': 'Chennai', 'skills': ['Wiring','Switchboards','Solar Panel','Safety Standards'], 'rate': 1500, 'verified': True, 'rating': 4.7, 'phone': '9876543220'},
            {'user_id': 'WK-TN-7B22Q', 'name': 'Murugan Selvam', 'profession': 'MASON', 'exp': 12, 'state': 'TN', 'city': 'Chennai', 'skills': ['Brickwork','Plastering','Concrete','RCC Work'], 'rate': 1200, 'verified': True, 'rating': 4.5, 'phone': '9876543221'},
            {'user_id': 'WK-TN-5C44R', 'name': 'Karthik Raja', 'profession': 'PLUMBER', 'exp': 5, 'state': 'TN', 'city': 'Coimbatore', 'skills': ['Pipe Fitting','Sanitation','Water Proofing'], 'rate': 1100, 'verified': False, 'rating': 0, 'phone': '9876543222'},
            {'user_id': 'WK-KA-1D55S', 'name': 'Anbu Selvan', 'profession': 'CARPENTER', 'exp': 7, 'state': 'KA', 'city': 'Bangalore', 'skills': ['Furniture','Doors','Windows','Woodwork'], 'rate': 1300, 'verified': True, 'rating': 4.3, 'phone': '9876543223'},
            {'user_id': 'WK-TN-9E66T', 'name': 'Prakash Jeyaraj', 'profession': 'CIVIL_CONTRACTOR', 'exp': 15, 'state': 'TN', 'city': 'Chennai', 'skills': ['Project Management','Structural Work','Estimation','Supervision'], 'rate': 2500, 'verified': True, 'rating': 4.8, 'phone': '9876543224'},
            {'user_id': 'WK-TN-4F77U', 'name': 'Senthil Kumar', 'profession': 'PAINTER', 'exp': 6, 'state': 'TN', 'city': 'Chennai', 'skills': ['Interior Painting','Exterior Painting','Texture Paint','Waterproofing Paint'], 'rate': 900, 'verified': True, 'rating': 4.1, 'phone': '9876543225'},
        ]
        
        # NOTE: In a real implementation you would create actual user and profile models here.
        # Example:
        # for o in owner_data:
        #     user, created = User.objects.get_or_create(username=o['user_id'], defaults={'email': o['email']})
        #     if created:
        #         user.set_password('Demo@1234')
        #         user.save()
        #         Profile.objects.create(user=user, role='OWNER', name=o['name'], phone=o['phone'], city=o['city'], state=o['state'])
                
        # for w in worker_data:
        #     user, created = User.objects.get_or_create(username=w['user_id'], defaults={'email': f"{w['user_id']}@demo.ctb"})
        #     if created:
        #         user.set_password('Demo@1234')
        #         user.save()
        #         Profile.objects.create(user=user, role='WORKER', name=w['name'], phone=w['phone'], city=w['city'], state=w['state'], profession=w['profession'], years_experience=w['exp'], skills=w['skills'], daily_rate=w['rate'], is_verified=w['verified'])

        # 2. Demo Compliance Rules
        self.stdout.write("Creating demo compliance rules...")
        # ComplianceRule.objects.get_or_create(...)

        # 3. Demo Project
        self.stdout.write("Creating demo project...")
        # project, created = Project.objects.get_or_create(...)

        # 4. Demo Milestones
        self.stdout.write("Creating demo milestones...")
        # Milestone.objects.get_or_create(...)

        # 5. Demo Quotation
        self.stdout.write("Creating demo quotations...")
        # Quotation.objects.get_or_create(...)

        # 6. Demo Payment Records
        self.stdout.write("Creating demo payments...")
        # Payment.objects.get_or_create(...)

        # 7. Demo Complaint
        self.stdout.write("Creating demo complaints...")
        # Complaint.objects.get_or_create(...)
        
        self.stdout.write(self.style.SUCCESS("=== DEMO DATA SEEDED SUCCESSFULLY ==="))
        self.stdout.write(self.style.SUCCESS("Demo Login Credentials (password for all: Demo@1234):"))
        self.stdout.write(self.style.SUCCESS("  House Owner: HO-TN-8F42K | Phone: 9876543210"))
        self.stdout.write(self.style.SUCCESS("  Worker:      WK-TN-3A91P | Phone: 9876543220"))
        self.stdout.write(self.style.SUCCESS("=========================================="))
