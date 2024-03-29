# Generated by Django 3.2.8 on 2023-09-09 19:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='planPrice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='backend.planprice'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='userCard',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='backend.usercard'),
        ),
    ]
