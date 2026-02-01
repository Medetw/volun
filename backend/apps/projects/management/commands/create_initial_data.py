from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.projects.models import Category, Region
from apps.users.models import UserRole

User = get_user_model()


class Command(BaseCommand):
    help = 'Create initial data for the application'

    def handle(self, *args, **options):
        self.stdout.write('Creating initial data...')
        
        # Create categories
        categories = [
            {'name': 'Образование', 'description': 'Образовательные проекты и инициативы'},
            {'name': 'Экология', 'description': 'Экологические проекты и акции'},
            {'name': 'Здравоохранение', 'description': 'Медицинская помощь и здоровье'},
            {'name': 'Социальная помощь', 'description': 'Помощь нуждающимся и уязвимым группам'},
            {'name': 'Культура и искусство', 'description': 'Культурные мероприятия и проекты'},
            {'name': 'Спорт', 'description': 'Спортивные мероприятия и тренировки'},
        ]
        
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create regions
        regions = [
            {'name': 'Алматы', 'code': 'ALA'},
            {'name': 'Астана', 'code': 'AST'},
            {'name': 'Шымкент', 'code': 'SHY'},
            {'name': 'Актобе', 'code': 'AKT'},
            {'name': 'Караганда', 'code': 'KAR'},
            {'name': 'Тараз', 'code': 'TAR'},
            {'name': 'Павлодар', 'code': 'PAV'},
            {'name': 'Усть-Каменогорск', 'code': 'UST'},
            {'name': 'Семей', 'code': 'SEM'},
            {'name': 'Атырау', 'code': 'ATY'},
            {'name': 'Костанай', 'code': 'KOS'},
            {'name': 'Петропавловск', 'code': 'PET'},
            {'name': 'Кызылорда', 'code': 'KYZ'},
            {'name': 'Уральск', 'code': 'URA'},
            {'name': 'Темиртау', 'code': 'TEM'},
            {'name': 'Кокшетау', 'code': 'KOK'},
            {'name': 'Талдыкорган', 'code': 'TAL'},
            {'name': 'Экибастуз', 'code': 'EKI'},
            {'name': 'Рудный', 'code': 'RUD'},
            {'name': 'Актау', 'code': 'AKM'},
            {'name': 'Жезказган', 'code': 'ZHE'},
        ]
        
        for reg_data in regions:
            region, created = Region.objects.get_or_create(
                name=reg_data['name'],
                defaults={'code': reg_data['code']}
            )
            if created:
                self.stdout.write(f'Created region: {region.name}')
        
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'username': 'admin',
                'role': UserRole.ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('Created admin user: admin@example.com / admin123')
        
        # Create test organization
        org_user, created = User.objects.get_or_create(
            email='org@test.com',
            defaults={
                'username': 'org@test.com',
                'role': UserRole.ORGANIZATION,
            }
        )
        if created:
            org_user.set_password('testpass123')
            org_user.save()
            # Create organization profile
            from apps.users.models import OrganizationProfile
            OrganizationProfile.objects.get_or_create(
                user=org_user,
                defaults={
                    'name': 'Тестовая организация',
                    'organization_type': 'ngo',
                    'description': 'Тестовая организация для проверки функциональности',
                    'region': Region.objects.get(name='Алматы'),
                }
            )
            self.stdout.write('Created organization user: org@test.com / testpass123')
        
        # Create test volunteer
        volunteer_user, created = User.objects.get_or_create(
            email='volunteer@test.com',
            defaults={
                'username': 'volunteer@test.com',
                'role': UserRole.VOLUNTEER,
            }
        )
        if created:
            volunteer_user.set_password('testpass123')
            volunteer_user.save()
            # Create volunteer profile
            from apps.users.models import VolunteerProfile
            VolunteerProfile.objects.get_or_create(
                user=volunteer_user,
                defaults={
                    'first_name': 'Иван',
                    'last_name': 'Петров',
                    'city': 'Алматы',
                    'region': 'Алматинская область',
                    'gender': 'male',
                }
            )
            self.stdout.write('Created volunteer user: volunteer@test.com / testpass123')
        
        self.stdout.write(self.style.SUCCESS('Initial data created successfully!'))
