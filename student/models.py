from django.db import models
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.conf import settings
from datetime import datetime
from django.db import transaction
# Create your models here.

def generate_student_code():
    """
    Tự động tạo mã học sinh theo định dạng HS{last_two_digits_of_year}XXXX
    Ví dụ: HS260001, HS260002, ...
    """
    current_year = datetime.now().year
    year_suffix = current_year % 100  # Lấy 2 chữ số cuối
    prefix = f"HS{year_suffix:02d}"

    with transaction.atomic():
        # Tìm mã lớn nhất cho năm hiện tại
        latest_student = Student.objects.filter(
            student_code__startswith=prefix
        ).order_by('-student_code').first()

        if latest_student and latest_student.student_code:
            try:
                # Trích xuất số cuối (4 chữ số)
                last_number_str = latest_student.student_code[-4:]
                last_number = int(last_number_str)
                next_number = last_number + 1
            except (ValueError, IndexError):
                # Nếu mã không hợp lệ, bắt đầu từ 1
                next_number = 1
        else:
            # Nếu chưa có mã nào cho năm này, bắt đầu từ 1
            next_number = 1

        # Định dạng số thành 4 chữ số
        formatted_number = f"{next_number:04d}"
        student_code = f"{prefix}{formatted_number}"

        # Đảm bảo mã chưa tồn tại (thêm kiểm tra cuối cùng)
        while Student.objects.filter(student_code=student_code).exists():
            next_number += 1
            formatted_number = f"{next_number:04d}"
            student_code = f"{prefix}{formatted_number}"

        return student_code

class Parent(models.Model):
    father_name = models.CharField(max_length=100)
    father_occupation = models.CharField(max_length=100, blank=True)
    father_mobile = models.CharField(max_length=15)
    father_email = models.EmailField(max_length=100)
    mother_name = models.CharField(max_length=100)
    mother_occupation = models.CharField(max_length=100, blank=True)
    mother_mobile = models.CharField(max_length=15)
    mother_email = models.EmailField(max_length=100)
    present_address = models.TextField()
    permanent_address = models.TextField()

    def __str__(self):
        return f"{self.father_name} & {self.mother_name}"

class Student(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Tên")
    last_name = models.CharField(max_length=100, verbose_name="Họ")
    student_id = models.CharField(max_length=20, unique=True, verbose_name="Mã học sinh")
    student_code = models.CharField(max_length=12, unique=True, blank=True, verbose_name="Mã tự động")
    gender = models.CharField(max_length=10, choices=[('Male', 'Nam'), ('Female', 'Nữ'), ('Others', 'Khác')], verbose_name="Giới tính")
    date_of_birth = models.DateField(verbose_name="Ngày sinh")
    student_class = models.ForeignKey('Class', on_delete=models.SET_NULL, null=True, blank=True, related_name='students', verbose_name="Lớp học")
    religion = models.CharField(max_length=50, blank=True, verbose_name="Tôn giáo")
    joining_date = models.DateField(verbose_name="Ngày nhập học")
    mobile_number = models.CharField(max_length=15, verbose_name="Số điện thoại")
    admission_number = models.CharField(max_length=20, unique=True, verbose_name="Số nhập học")
    section = models.CharField(max_length=10, blank=True, verbose_name="Khối")
    student_image = models.ImageField(upload_to='students/', blank=True, verbose_name="Ảnh học sinh")
    parent = models.OneToOneField(Parent, on_delete=models.CASCADE, verbose_name="Phụ huynh")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='student_profile', verbose_name="Tài khoản")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Đang học")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Học sinh"
        verbose_name_plural = "Học sinh"
        ordering = ['student_class', 'first_name', 'last_name']

    def save(self, *args, **kwargs):
        if not self.student_code:
            self.student_code = generate_student_code()
        if not self.slug:
            self.slug = slugify(f"{self.first_name}-{self.last_name}-{self.student_id}")
        super(Student, self).save(*args, **kwargs)
    
    def get_full_name(self):
        """Trả về tên đầy đủ theo định dạng: last_name first_name"""
        first_name = self.first_name or ''
        last_name = self.last_name or ''
        full_name = f"{last_name} {first_name}".strip()
        return full_name if full_name else self.student_id
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"

class AdmissionCandidate(models.Model):
    exam_number = models.CharField(max_length=50, unique=True, verbose_name="Số báo danh")
    full_name = models.CharField(max_length=200, verbose_name="Họ và tên")
    date_of_birth = models.DateField(verbose_name="Ngày sinh")
    previous_school = models.CharField(max_length=255, verbose_name="Trường THCS")
    math_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Điểm Toán")
    literature_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Điểm Văn")
    english_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Điểm Anh")
    assigned_class = models.ForeignKey('Class', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_candidates', verbose_name='Lớp phân chia')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Thí sinh tuyển sinh"
        verbose_name_plural = "Thí sinh tuyển sinh"
        ordering = ['exam_number']

    @property
    def total_score(self):
        if self.math_score is None or self.literature_score is None or self.english_score is None:
            return None
        return self.math_score + self.literature_score + self.english_score

    def __str__(self):
        return f"{self.exam_number} - {self.full_name}"

class Class(models.Model):
    class_name = models.CharField(max_length=50, unique=True, verbose_name="Tên lớp")
    class_code = models.CharField(max_length=10, unique=True, verbose_name="Mã lớp")
    grade_level = models.CharField(max_length=20, verbose_name="Khối")
    capacity = models.IntegerField(default=30, verbose_name="Sĩ số tối đa")
    class_teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='classes', verbose_name="Giáo viên chủ nhiệm")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Lớp học"
        verbose_name_plural = "Lớp học"
        ordering = ['grade_level', 'class_name']
    
    def __str__(self):
        return f"{self.class_name} - {self.grade_level}"
    
    def get_student_count(self):
        return self.students.count()

class Subject(models.Model):
    subject_name = models.CharField(max_length=100, unique=True, verbose_name="Tên môn học")
    subject_code = models.CharField(max_length=10, unique=True, verbose_name="Mã môn học")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='subjects', verbose_name="Giáo viên")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Môn học"
        verbose_name_plural = "Môn học"
        ordering = ['subject_name']
    
    def __str__(self):
        return self.subject_name

class Grade(models.Model):
    GRADE_CHOICES = [
        ('A+', 'A+ (9.0-10.0)'),
        ('A', 'A (8.0-8.9)'),
        ('B+', 'B+ (7.0-7.9)'),
        ('B', 'B (6.0-6.9)'),
        ('C+', 'C+ (5.0-5.9)'),
        ('C', 'C (4.0-4.9)'),
        ('D', 'D (3.0-3.9)'),
        ('F', 'F (0.0-2.9)'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades', verbose_name="Học sinh")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grades', verbose_name="Môn học")
    exam_type = models.CharField(max_length=50, choices=[
        ('Quiz', 'Kiểm tra 15 phút'),
        ('Midterm', 'Giữa kỳ'),
        ('Final', 'Cuối kỳ'),
        ('Assignment', 'Bài tập'),
    ], verbose_name="Loại kiểm tra")
    score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Điểm số")
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100, verbose_name="Điểm tối đa")
    grade_letter = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True, verbose_name="Xếp loại")
    exam_date = models.DateField(verbose_name="Ngày thi")
    remarks = models.TextField(blank=True, verbose_name="Nhận xét")
    is_approved = models.BooleanField(default=False, verbose_name="Đã được duyệt")
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_grades', verbose_name="Người duyệt")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian duyệt")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Điểm số"
        verbose_name_plural = "Điểm số"
        ordering = ['-exam_date']
        unique_together = ['student', 'subject', 'exam_type', 'exam_date']
    
    def save(self, *args, **kwargs):
       
        try:
            from decimal import Decimal
            score = Decimal(str(self.score)) if self.score else Decimal('0')
            max_score = Decimal(str(self.max_score)) if self.max_score else Decimal('100')
          
            if max_score > 0:
                percentage = float((score / max_score) * 100)
            else:
                percentage = 0
                
            if percentage >= 90:
                self.grade_letter = 'A+'
            elif percentage >= 80:
                self.grade_letter = 'A'
            elif percentage >= 70:
                self.grade_letter = 'B+'
            elif percentage >= 60:
                self.grade_letter = 'B'
            elif percentage >= 50:
                self.grade_letter = 'C+'
            elif percentage >= 40:
                self.grade_letter = 'C'
            elif percentage >= 30:
                self.grade_letter = 'D'
            else:
                self.grade_letter = 'F'
        except (ValueError, TypeError, ZeroDivisionError) as e:
         
            self.grade_letter = 'F'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.first_name} - {self.subject.subject_name} - {self.score}"

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Có mặt'),
        ('Absent', 'Vắng mặt'),
        ('Late', 'Đi muộn'),
        ('Excused', 'Có phép'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances', verbose_name="Học sinh")
    date = models.DateField(verbose_name="Ngày")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Present', verbose_name="Trạng thái")
    remarks = models.TextField(blank=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Điểm danh"
        verbose_name_plural = "Điểm danh"
        ordering = ['-date']
        unique_together = ['student', 'date']
    
    def __str__(self):
        return f"{self.student.first_name} - {self.date} - {self.status}"

class Teacher(models.Model):
    teacher_id = models.CharField(max_length=20, unique=True, verbose_name="Mã giáo viên")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_profile', verbose_name="Tài khoản")
    phone_number = models.CharField(max_length=15, blank=True, verbose_name="Số điện thoại")
    address = models.TextField(blank=True, verbose_name="Địa chỉ")
    specialization = models.CharField(max_length=100, blank=True, verbose_name="Chuyên môn")
    qualification = models.CharField(max_length=100, blank=True, verbose_name="Trình độ")
    joining_date = models.DateField(null=True, blank=True, verbose_name="Ngày vào làm")
    teacher_image = models.ImageField(upload_to='teachers/', blank=True, verbose_name="Ảnh giáo viên")
    is_active = models.BooleanField(default=True, verbose_name="Đang làm việc")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Giáo viên"
        verbose_name_plural = "Giáo viên"
        ordering = ['teacher_id', 'user__first_name', 'user__last_name']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.teacher_id})"
    
    def get_full_name(self):
        
        first_name = self.user.first_name or ''
        last_name = self.user.last_name or ''
        
     
        if last_name and '(' in last_name and ')' in last_name:
            # Tìm và loại bỏ phần trong ngoặc cuối cùng
            last_name = last_name.rsplit('(', 1)[0].strip()
        
        full_name = f"{last_name} {first_name}".strip()
        return full_name if full_name else self.user.username
    
    def get_email(self):
        return self.user.email
    
    def get_username(self):
        return self.user.username

class Schedule(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Thứ Hai'),
        ('Tuesday', 'Thứ Ba'),
        ('Wednesday', 'Thứ Tư'),
        ('Thursday', 'Thứ Năm'),
        ('Friday', 'Thứ Sáu'),
        ('Saturday', 'Thứ Bảy'),
        ('Sunday', 'Chủ Nhật'),
    ]
    
    PERIODS = [
        ('1', 'Tiết 1 (7:00-7:45)'),
        ('2', 'Tiết 2 (7:45-8:30)'),
        ('3', 'Tiết 3 (8:45-9:30)'),
        ('4', 'Tiết 4 (9:30-10:15)'),
        ('5', 'Tiết 5 (10:30-11:15)'),
        ('6', 'Tiết 6 (11:15-12:00)'),
        ('7', 'Tiết 7 (13:00-13:45)'),
        ('8', 'Tiết 8 (13:45-14:30)'),
        ('9', 'Tiết 9 (14:45-15:30)'),
        ('10', 'Tiết 10 (15:30-16:15)'),
    ]
    
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='schedules', verbose_name="Lớp học")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='schedules', verbose_name="Môn học")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedules', verbose_name="Giáo viên")
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK, verbose_name="Ngày trong tuần")
    period = models.CharField(max_length=2, choices=PERIODS, verbose_name="Tiết học")
    room = models.CharField(max_length=50, blank=True, verbose_name="Phòng học")
    academic_year = models.CharField(max_length=20, default='2026-2027', verbose_name="Năm học")
    semester = models.CharField(max_length=10, choices=[('1', 'Học kỳ I'), ('2', 'Học kỳ II')], default='1', verbose_name="Học kỳ")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Thời khóa biểu"
        verbose_name_plural = "Thời khóa biểu"
        ordering = ['day_of_week', 'period']
        unique_together = ['class_obj', 'day_of_week', 'period', 'academic_year', 'semester']
    
    def __str__(self):
        return f"{self.class_obj.class_name} - {self.day_of_week} - Tiết {self.period} - {self.subject.subject_name}"