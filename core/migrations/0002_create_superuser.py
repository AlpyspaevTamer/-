from django.db import migrations
from django.contrib.auth import get_user_model

def create_admin(apps, schema_editor):
    User = get_user_model()
    # Создаем админа, если его нет
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin')

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'), # Убедитесь, что имя предыдущей миграции совпадает
    ]
    operations = [
        migrations.RunPython(create_admin),
    ]