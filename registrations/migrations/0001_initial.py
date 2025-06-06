# Generated by Django 5.2 on 2025-04-19 21:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
        ('participants', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bib_number', models.PositiveIntegerField(blank=True, null=True)),
                ('registration_status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('payment_status', models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('refunded', 'Refunded'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('payment_method', models.CharField(blank=True, max_length=50)),
                ('payment_reference', models.CharField(blank=True, max_length=100)),
                ('ai_vaccine_status', models.CharField(choices=[('pending', 'Pending'), ('ok', 'OK'), ('issue', 'Issue'), ('error', 'Error/Needs Review')], default='pending', max_length=20)),
                ('vet_check_status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('vet_check_time', models.DateTimeField(blank=True, null=True)),
                ('vet_checker_details', models.TextField(blank=True)),
                ('kit_delivered', models.BooleanField(default=False)),
                ('kit_delivery_time', models.DateTimeField(blank=True, null=True)),
                ('checked_in', models.BooleanField(default=False)),
                ('checkin_time', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('waiver_accepted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('dog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='participants.dog')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='participants.participant')),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='events.race')),
                ('race_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='events.racecategory')),
            ],
            options={
                'ordering': ['race', 'bib_number'],
                'unique_together': {('race', 'bib_number')},
            },
        ),
        migrations.CreateModel(
            name='ParticipantAnnotation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('recorded', 'Recorded'), ('confirmed', 'Confirmed'), ('dismissed', 'Dismissed')], default='recorded', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('location', models.CharField(blank=True, help_text='Location on the course where the infraction occurred', max_length=100)),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('confirmed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='confirmed_annotations', to=settings.AUTH_USER_MODEL)),
                ('penalty_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='annotations', to='events.penaltytype')),
                ('recorded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recorded_annotations', to=settings.AUTH_USER_MODEL)),
                ('registration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='annotations', to='registrations.registration')),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_type', models.CharField(choices=[('identity', 'Identity Document'), ('veterinary_certificate', 'Veterinary Certificate'), ('vaccination_record', 'Vaccination Record'), ('insurance', 'Insurance Certificate'), ('other', 'Other')], max_length=50)),
                ('file', models.FileField(upload_to='documents/%Y/%m/%d/')),
                ('description', models.CharField(blank=True, max_length=255)),
                ('ocr_raw_text', models.TextField(blank=True)),
                ('ocr_status', models.CharField(default='pending', max_length=20)),
                ('ocr_analysis_result', models.JSONField(blank=True, default=dict)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('registration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='registrations.registration')),
            ],
        ),
    ]
