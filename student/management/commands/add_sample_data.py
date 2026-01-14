from django.core.management.base import BaseCommand
from student.models import Student, Class, Subject, Grade, Attendance, Parent, Teacher
from home_auth.models import CustomUser
from django.utils import timezone
from datetime import date, timedelta
import random
import string

class Command(BaseCommand):
    help = 'Thêm dữ liệu mẫu vào cơ sở dữ liệu: lớp học, học sinh, môn học, điểm số và điểm danh'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Bắt đầu thêm dữ liệu mẫu...'))
        
        # Danh sách tên Việt Nam
        first_names_male = ['Anh', 'Bảo', 'Cường', 'Đức', 'Hùng', 'Khoa', 'Long', 'Minh', 'Nam', 'Phong', 
                           'Quang', 'Sơn', 'Thành', 'Tuấn', 'Vinh', 'Duy', 'Hải', 'Hoàng', 'Kiên', 'Lâm',
                           'Mạnh', 'Nghĩa', 'Phúc', 'Quân', 'Tài', 'Thắng', 'Trung', 'Việt', 'Xuân', 'Yên']
        
        first_names_female = ['An', 'Bình', 'Chi', 'Dung', 'Hà', 'Hương', 'Lan', 'Linh', 'Mai', 'Nga',
                             'Oanh', 'Phương', 'Quỳnh', 'Thảo', 'Uyên', 'Vy', 'Yến', 'Ánh', 'Bích', 'Cúc',
                             'Diệu', 'Giang', 'Hạnh', 'Hoa', 'Khanh', 'Lệ', 'My', 'Nhung', 'Phượng', 'Thúy']
        
        last_names = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng',
                     'Bùi', 'Đỗ', 'Hồ', 'Ngô', 'Dương', 'Lý', 'Đinh', 'Đào', 'Tạ', 'Tôn',
                     'Lương', 'Trương', 'Vương', 'Đoàn', 'Bạch', 'Cao', 'Chu', 'Đồng', 'Hà', 'Lưu']
        
        # Tên môn học
        subjects_list = [
            'Toán', 'Vật lý', 'Hóa học', 'Sinh học', 
            'Ngữ văn', 'Lịch sử', 'Địa lý', 'Tiếng Anh'
        ]
        
        # Tạo các lớp học
        self.stdout.write(self.style.NOTICE('Đang tạo các lớp học...'))
        classes = {}
        grade_levels = ['10', '11', '12']
        class_types = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C']
        
        for grade in grade_levels:
            for class_type in class_types:
                class_name = f"{grade}{class_type}"
                class_code = f"{grade}{class_type.lower()}"
                
                # Kiểm tra xem lớp đã tồn tại chưa
                class_obj, created = Class.objects.get_or_create(
                    class_name=class_name,
                    defaults={
                        'class_code': class_code,
                        'grade_level': grade,
                        'capacity': 35
                    }
                )
                classes[class_name] = class_obj
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Đã tạo lớp: {class_name}'))
        
        # Tạo các môn học
        self.stdout.write(self.style.NOTICE('Đang tạo các môn học...'))
        subjects = {}
        for subject_name in subjects_list:
            subject_code = ''.join([c for c in subject_name if c.isupper() or c.isdigit()])
            if not subject_code:
                subject_code = subject_name[:3].upper()
            
            # Tạo mã môn học duy nhất
            counter = 1
            original_code = subject_code
            while Subject.objects.filter(subject_code=subject_code).exists():
                subject_code = f"{original_code}{counter}"
                counter += 1
            
            subject, created = Subject.objects.get_or_create(
                subject_name=subject_name,
                defaults={
                    'subject_code': subject_code,
                    'description': f'Môn học {subject_name}'
                }
            )
            subjects[subject_name] = subject
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Đã tạo môn học: {subject_name}'))
        
        # Tạo học sinh cho mỗi lớp
        self.stdout.write(self.style.NOTICE('Đang tạo học sinh...'))
        students_per_class = 30
        total_students = 0
        
        for class_name, class_obj in classes.items():
            # Đếm số học sinh hiện có trong lớp
            existing_count = class_obj.students.filter(is_active=True).count()
            needed = students_per_class - existing_count
            
            if needed <= 0:
                self.stdout.write(self.style.WARNING(f'  - Lớp {class_name} đã có đủ học sinh ({existing_count})'))
                continue
            
            self.stdout.write(self.style.NOTICE(f'  Đang thêm {needed} học sinh cho lớp {class_name}...'))
            
            for i in range(needed):
                # Tạo mã học sinh duy nhất
                student_counter = existing_count + i + 1
                student_id = f"HS{class_obj.grade_level}{class_obj.class_code.upper()}{student_counter:03d}"
                
                # Kiểm tra mã học sinh đã tồn tại chưa
                while Student.objects.filter(student_id=student_id).exists():
                    student_counter += 1
                    student_id = f"HS{class_obj.grade_level}{class_obj.class_code.upper()}{student_counter:03d}"
                
                # Chọn giới tính ngẫu nhiên (50% nam, 50% nữ)
                is_male = random.choice([True, False])
                gender = 'Male' if is_male else 'Female'
                
                # Chọn tên
                if is_male:
                    first_name = random.choice(first_names_male)
                else:
                    first_name = random.choice(first_names_female)
                last_name = random.choice(last_names)
                
                # Tạo số nhập học
                admission_number = f"ADM{class_obj.grade_level}{class_obj.class_code.upper()}{student_counter:03d}"
                while Student.objects.filter(admission_number=admission_number).exists():
                    student_counter += 1
                    admission_number = f"ADM{class_obj.grade_level}{class_obj.class_code.upper()}{student_counter:03d}"
                
                # Ngày sinh (từ 15-18 tuổi)
                age = random.randint(15, 18)
                birth_year = timezone.now().year - age
                birth_month = random.randint(1, 12)
                birth_day = random.randint(1, 28)
                date_of_birth = date(birth_year, birth_month, birth_day)
                
                # Ngày nhập học (từ 2020-2024)
                join_year = random.randint(2020, 2024)
                join_month = random.randint(8, 9)  # Tháng 8-9
                join_day = random.randint(1, 30)
                joining_date = date(join_year, join_month, join_day)
                
                # Số điện thoại
                mobile_number = f"0{random.randint(100000000, 999999999)}"
                
                # Tạo Parent
                father_name = f"Ông {last_name} {random.choice(['Văn', 'Đức', 'Minh', 'Hùng', 'Tuấn'])}"
                mother_name = f"Bà {last_name} {random.choice(['Thị', 'Ngọc', 'Thu', 'Hương', 'Lan'])}"
                
                parent = Parent.objects.create(
                    father_name=father_name,
                    father_occupation=random.choice(['Công nhân', 'Nông dân', 'Giáo viên', 'Bác sĩ', 'Kỹ sư', 'Kinh doanh']),
                    father_mobile=mobile_number,
                    father_email=f"father_{student_id.lower()}@example.com",
                    mother_name=mother_name,
                    mother_occupation=random.choice(['Nội trợ', 'Giáo viên', 'Y tá', 'Kế toán', 'Nhân viên văn phòng']),
                    mother_mobile=f"0{random.randint(100000000, 999999999)}",
                    mother_email=f"mother_{student_id.lower()}@example.com",
                    present_address=f"{random.randint(1, 999)} Đường {random.choice(['Lê Lợi', 'Nguyễn Huệ', 'Trần Hưng Đạo', 'Lý Thường Kiệt'])}",
                    permanent_address=f"{random.randint(1, 999)} Đường {random.choice(['Lê Lợi', 'Nguyễn Huệ', 'Trần Hưng Đạo', 'Lý Thường Kiệt'])}"
                )
                
                # Tạo Student
                student = Student.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    student_id=student_id,
                    gender=gender,
                    date_of_birth=date_of_birth,
                    student_class=class_obj,
                    religion=random.choice(['Không', 'Phật giáo', 'Thiên chúa giáo', '']),
                    joining_date=joining_date,
                    mobile_number=mobile_number,
                    admission_number=admission_number,
                    section=class_obj.grade_level,
                    parent=parent,
                    is_active=True
                )
                
                total_students += 1
                
                # Thêm điểm số cho học sinh (mỗi môn 2-3 điểm)
                for subject_name, subject_obj in subjects.items():
                    num_grades = random.randint(2, 3)
                    used_dates = set()  # Để tránh trùng ngày thi
                    
                    for j in range(num_grades):
                        # Điểm từ 3.0 đến 10.0
                        score = round(random.uniform(3.0, 10.0), 1)
                        max_score = 10.0
                        
                        # Xác định grade_letter
                        if score >= 9.0:
                            grade_letter = 'A+'
                        elif score >= 8.0:
                            grade_letter = 'A'
                        elif score >= 7.0:
                            grade_letter = 'B+'
                        elif score >= 6.0:
                            grade_letter = 'B'
                        elif score >= 5.0:
                            grade_letter = 'C+'
                        elif score >= 4.0:
                            grade_letter = 'C'
                        elif score >= 3.0:
                            grade_letter = 'D'
                        else:
                            grade_letter = 'F'
                        
                        # Ngày thi (trong 6 tháng gần đây) - đảm bảo không trùng
                        attempts = 0
                        while attempts < 100:
                            exam_date = timezone.now().date() - timedelta(days=random.randint(1, 180))
                            exam_type = random.choice(['Quiz', 'Midterm', 'Final', 'Assignment'])
                            
                            # Kiểm tra xem đã có điểm với cùng student, subject, exam_type, exam_date chưa
                            key = (exam_date, exam_type)
                            if key not in used_dates and not Grade.objects.filter(
                                student=student,
                                subject=subject_obj,
                                exam_type=exam_type,
                                exam_date=exam_date
                            ).exists():
                                used_dates.add(key)
                                break
                            attempts += 1
                        else:
                            # Nếu không tìm được ngày hợp lệ, bỏ qua
                            continue
                        
                        Grade.objects.create(
                            student=student,
                            subject=subject_obj,
                            score=score,
                            max_score=max_score,
                            grade_letter=grade_letter,
                            exam_type=exam_type,
                            exam_date=exam_date
                        )
                
                # Thêm điểm danh (30 ngày gần nhất)
                for day_offset in range(30):
                    attendance_date = timezone.now().date() - timedelta(days=day_offset)
                    # Bỏ qua cuối tuần (thứ 7 và chủ nhật)
                    if attendance_date.weekday() >= 5:
                        continue
                    
                    # 85% có mặt, 10% vắng, 3% muộn, 2% có phép
                    rand = random.random()
                    if rand < 0.85:
                        status = 'Present'
                    elif rand < 0.95:
                        status = 'Absent'
                    elif rand < 0.98:
                        status = 'Late'
                    else:
                        status = 'Excused'
                    
                    Attendance.objects.get_or_create(
                        student=student,
                        date=attendance_date,
                        defaults={
                            'status': status,
                            'remarks': '' if status == 'Present' else random.choice(['Ốm', 'Có việc gia đình', ''])
                        }
                    )
            
            self.stdout.write(self.style.SUCCESS(f'  ✓ Đã thêm {needed} học sinh cho lớp {class_name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Hoàn thành! Đã thêm tổng cộng {total_students} học sinh mới'))
        self.stdout.write(self.style.SUCCESS(f'✓ Tổng số lớp: {len(classes)}'))
        self.stdout.write(self.style.SUCCESS(f'✓ Tổng số môn học: {len(subjects)}'))

