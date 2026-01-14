from django.core.management.base import BaseCommand
from student.models import Class, Teacher
from home_auth.models import CustomUser

class Command(BaseCommand):
    help = 'Sửa lại tên giáo viên chủ nhiệm cho các lớp'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Bắt đầu sửa tên giáo viên chủ nhiệm...'))
        
        # Mapping các lớp và tên giáo viên mới
        # Trong Django: first_name là tên, last_name là họ
        # Nhưng Teacher.get_full_name() trả về f"{first_name} {last_name}"
        # Để hiển thị "Phan Thùy Linh", cần: first_name="Phan", last_name="Thùy Linh"
        class_teacher_mapping = {
            '10A1': {'first_name': 'Phan', 'last_name': 'Thùy Linh'},
            '10A2': {'first_name': 'Nguyễn', 'last_name': 'Thị A'},
            '11B2': {'first_name': 'Nguyễn', 'last_name': 'Thị A'},
            '11A1': {'first_name': 'Lê', 'last_name': 'Văn B'},
            '10B2': {'first_name': 'Lê', 'last_name': 'Văn B'},
            '11A2': {'first_name': 'Trần', 'last_name': 'Đức C'},
            '12A1': {'first_name': 'Phạm', 'last_name': 'Văn D'},
        }
        
        updated_count = 0
        
        for class_name, teacher_info in class_teacher_mapping.items():
            try:
                class_obj = Class.objects.get(class_name=class_name)
                
                if not class_obj.class_teacher:
                    self.stdout.write(self.style.WARNING(f'  - Lớp {class_name}: Chưa có giáo viên chủ nhiệm'))
                    continue
                
                user = class_obj.class_teacher
                old_first_name = user.first_name
                old_last_name = user.last_name
                
                # Cập nhật tên
                user.first_name = teacher_info['first_name']
                user.last_name = teacher_info['last_name']
                user.save()
                
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Đã sửa tên giáo viên lớp {class_name}: {old_first_name} {old_last_name} -> {teacher_info["first_name"]} {teacher_info["last_name"]}'))
                
            except Class.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'  ✗ Không tìm thấy lớp: {class_name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Hoàn thành! Đã sửa tên {updated_count} giáo viên'))

