from django.db import migrations

CATEGORIES = [
    {'name': 'Образование', 'description': 'Образовательные проекты и инициативы'},
    {'name': 'Экология', 'description': 'Экологические проекты и акции'},
    {'name': 'Здравоохранение', 'description': 'Медицинская помощь и здоровье'},
    {'name': 'Социальная помощь', 'description': 'Помощь нуждающимся и уязвимым группам'},
    {'name': 'Культура и искусство', 'description': 'Культурные мероприятия и проекты'},
    {'name': 'Спорт', 'description': 'Спортивные мероприятия и тренировки'},
]

REGIONS = [
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


def populate_initial_data(apps, schema_editor):
    Category = apps.get_model('projects', 'Category')
    Region = apps.get_model('projects', 'Region')

    for cat in CATEGORIES:
        Category.objects.get_or_create(
            name=cat['name'],
            defaults={'description': cat['description']}
        )

    for reg in REGIONS:
        Region.objects.get_or_create(
            name=reg['name'],
            defaults={'code': reg['code']}
        )


def reverse_initial_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_initial_data, reverse_initial_data),
    ]
