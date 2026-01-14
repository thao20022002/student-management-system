from django.core.management.base import BaseCommand
from home_auth.models import CustomUser
from student.models import Teacher
import uuid


class Command(BaseCommand):
    help = 'Migrate existing teachers to Teacher model'

    def handle(self, *args, **options):
        teachers = CustomUser.objects.filter(is_teacher=True)
        created_count = 0
        skipped_count = 0
        
        for user in teachers:
            # Kiểm tra xem đã có Teacher profile chưa
            if hasattr(user, 'teacher_profile'):
                self.stdout.write(self.style.WARNING(f'Teacher profile already exists for {user.username}'))
                skipped_count += 1
                continue
            
            # Tạo teacher_id tự động nếu chưa có
            teacher_id = f"GV{user.id:04d}"  # Format: GV0001, GV0002, etc.
            
            # Đảm bảo teacher_id là unique
            counter = 1
            while Teacher.objects.filter(teacher_id=teacher_id).exists():
                teacher_id = f"GV{user.id:04d}-{counter}"
                counter += 1
            
            # Tạo Teacher profile
            Teacher.objects.create(
                teacher_id=teacher_id,
                user=user,
                phone_number='',
                address='',
                specialization='',
                qualification='',
                joining_date=user.date_joined.date() if user.date_joined else None,
                is_active=True
            )
            
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'Created Teacher profile for {user.username} with ID: {teacher_id}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nMigration completed!'))
        self.stdout.write(self.style.SUCCESS(f'Created: {created_count}'))
        self.stdout.write(self.style.WARNING(f'Skipped: {skipped_count}'))



