# Generated by Django 3.2.9 on 2022-01-17 11:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20220104_1838'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_category', models.CharField(choices=[('ELECTRONICS', 'electronics'), ('MEDICAL/HEALTH', 'medical/health'), ('APPLIANCES ', 'appliances'), ('BEAUTY & PERSONAL CARE', 'beauty & personal Care'), ('GROCERY', 'grocery'), ('HOME & KITCHEN', 'home & kitchen'), ('CLOTHING', 'clothing')], default='', max_length=256)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product', to='users.products')),
            ],
        ),
        migrations.CreateModel(
            name='CompanyCatgeory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_category', models.CharField(choices=[('RETAILER', 'Retailer'), ('HEALTH PRACTITIONER', 'Health Practitioner'), ('FOOD SERVICE', 'Food Service'), ('SUPPLIER/RAW INGREDIENT DISTRIBUTOR', 'Supplier/Raw Ingredient Distributor'), ('MANUFACTURER', 'Manufacturer'), ('BUSINESS SERVICES', 'Business Services'), ('INVESTOR', 'Investor')], default='', max_length=256)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company', to='users.company')),
            ],
        ),
    ]