from django.db import models
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.conf import settings
# Create your models here.

from django.db import models

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
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Đang học")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Học sinh"
        verbose_name_plural = "Học sinh"
        ordering = ['student_class', 'first_name', 'last_name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.first_name}-{self.last_name}-{self.student_id}")
        super(Student, self).save(*args, **kwargs)
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"

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
        return f"{self.user.get_full_name() or self.user.username} ({self.teacher_id})"
    
    def get_full_name(self):
        
        first_name = self.user.first_name or ''
        last_name = self.user.last_name or ''
        
     
        if last_name and '(' in last_name and ')' in last_name:
            # Tìm và loại bỏ phần trong ngoặc cuối cùng
            last_name = last_name.rsplit('(', 1)[0].strip()
        
        full_name = f"{first_name} {last_name}".strip()
        return full_name if full_name else self.user.username
    
    def get_email(self):
        return self.user.email
    
    def get_username(self):
        return self.user.username