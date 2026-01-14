from django.core.management.base import BaseCommand
from student.models import Class, Teacher
from home_auth.models import CustomUser
from django.utils import timezone
from datetime import date
import random
import string

class Command(BaseCommand):
    help = 'Tạo giáo viên và gán giáo viên chủ nhiệm cho từng lớp'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Bắt đầu gán giáo viên chủ nhiệm...'))
        
        # Danh sách tên giáo viên Việt Nam
        first_names_male = ['Anh', 'Bảo', 'Cường', 'Đức', 'Hùng', 'Khoa', 'Long', 'Minh', 'Nam', 'Phong', 
                           'Quang', 'Sơn', 'Thành', 'Tuấn', 'Vinh', 'Duy', 'Hải', 'Hoàng', 'Kiên', 'Lâm']
        
        first_names_female = ['An', 'Bình', 'Chi', 'Dung', 'Hà', 'Hương', 'Lan', 'Linh', 'Mai', 'Nga',
                             'Oanh', 'Phương', 'Quỳnh', 'Thảo', 'Uyên', 'Vy', 'Yến', 'Ánh', 'Bích', 'Cúc']
        
        last_names = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng',
                     'Bùi', 'Đỗ', 'Hồ', 'Ngô', 'Dương', 'Lý', 'Đinh', 'Đào', 'Tạ', 'Tôn']
        
        # Lấy tất cả các lớp
        all_classes = Class.objects.all().order_by('grade_level', 'class_name')
        self.stdout.write(self.style.NOTICE(f'Tìm thấy {all_classes.count()} lớp học'))
        
        # Lấy tất cả giáo viên hiện có
        existing_teachers = Teacher.objects.filter(is_active=True)
        self.stdout.write(self.style.NOTICE(f'Có {existing_teachers.count()} giáo viên hiện có'))
        
        # Tạo thêm giáo viên nếu cần
        needed_teachers = all_classes.count() - existing_teachers.count()
        if needed_teachers > 0:
            self.stdout.write(self.style.NOTICE(f'Cần tạo thêm {needed_teachers} giáo viên...'))
            
            for i in range(needed_teachers):
                # Chọn giới tính ngẫu nhiên
                is_male = random.choice([True, False])
                gender = 'Male' if is_male else 'Female'
                
                # Chọn tên
                if is_male:
                    first_name = random.choice(first_names_male)
                else:
                    first_name = random.choice(first_names_female)
                last_name = random.choice(last_names)
                
                # Tạo username
                username = f"gv{first_name.lower()}{last_name.lower()}{i+1}"
                counter = 1
                while CustomUser.objects.filter(username=username).exists():
                    username = f"gv{first_name.lower()}{last_name.lower()}{i+1}{counter}"
                    counter += 1
                
                # Tạo mã giáo viên
                teacher_id = f"GV{random.randint(1000, 9999)}"
                while Teacher.objects.filter(teacher_id=teacher_id).exists():
                    teacher_id = f"GV{random.randint(1000, 9999)}"
                
                # Tạo user
                user = CustomUser.objects.create_user(
                    username=username,
                    email=f"{username}@school.edu.vn",
                    password='123456',  # Mật khẩu mặc định
                    first_name=first_name,
                    last_name=last_name,
                    is_teacher=True
                )
                
                # Tạo Teacher profile
                teacher = Teacher.objects.create(
                    teacher_id=teacher_id,
                    user=user,
                    phone_number=f"0{random.randint(100000000, 999999999)}",
                    address=f"{random.randint(1, 999)} Đường {random.choice(['Lê Lợi', 'Nguyễn Huệ', 'Trần Hưng Đạo'])}",
                    specialization=random.choice(['Toán', 'Vật lý', 'Hóa học', 'Sinh học', 'Ngữ văn', 'Lịch sử', 'Địa lý', 'Tiếng Anh']),
                    qualification=random.choice(['Đại học', 'Thạc sĩ', 'Tiến sĩ']),
                    joining_date=date(2020, 1, 1),
                    is_active=True
                )
                
                self.stdout.write(self.style.SUCCESS(f'  ✓ Đã tạo giáo viên: {first_name} {last_name} ({teacher_id})'))
        
        # Gán giáo viên chủ nhiệm cho từng lớp
        all_teachers = list(Teacher.objects.filter(is_active=True))
        self.stdout.write(self.style.NOTICE(f'\nĐang gán giáo viên chủ nhiệm cho {all_classes.count()} lớp...'))
        
        assigned_count = 0
        for class_obj in all_classes:
            if class_obj.class_teacher:
                self.stdout.write(self.style.WARNING(f'  - Lớp {class_obj.class_name} đã có giáo viên chủ nhiệm: {class_obj.class_teacher.get_full_name()}'))
                continue
            
            # Chọn giáo viên chưa được gán hoặc ít lớp nhất
            available_teachers = [t for t in all_teachers if t.user.classes.count() < 2]
            if not available_teachers:
                available_teachers = all_teachers
            
            teacher = random.choice(available_teachers)
            
            # Gán giáo viên chủ nhiệm
            class_obj.class_teacher = teacher.user
            class_obj.save()
            
            assigned_count += 1
            self.stdout.write(self.style.SUCCESS(f'  ✓ Đã gán {teacher.get_full_name()} ({teacher.teacher_id}) làm giáo viên chủ nhiệm lớp {class_obj.class_name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Hoàn thành! Đã gán giáo viên chủ nhiệm cho {assigned_count} lớp'))
        self.stdout.write(self.style.SUCCESS(f'✓ Tổng số giáo viên: {Teacher.objects.filter(is_active=True).count()}'))



