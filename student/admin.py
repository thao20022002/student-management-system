from django.contrib import admin
from .models import Parent, Student, Class, Subject, Grade, Attendance, Teacher, AdmissionCandidate, Schedule

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('father_name', 'mother_name', 'father_mobile', 'mother_mobile')
    search_fields = ('father_name', 'mother_name', 'father_mobile', 'mother_mobile')
    list_filter = ('father_name', 'mother_name')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'student_id', 'student_code', 'gender', 'student_class', 'get_has_account', 'get_username', 'is_active')
    search_fields = ('first_name', 'last_name', 'student_id', 'student_code', 'admission_number', 'user__username')
    list_filter = ('gender', 'student_class', 'is_active', 'section')
    readonly_fields = ('slug', 'created_at', 'student_code')
    actions = ['create_student_accounts', 'reset_student_passwords']
    
    def get_has_account(self, obj):
        return "Có" if obj.user else "Không"
    get_has_account.short_description = 'Có tài khoản'
    get_has_account.boolean = True
    
    def get_username(self, obj):
        return obj.user.username if obj.user else "-"
    get_username.short_description = 'Username'
    
    def create_student_accounts(self, request, queryset):
        """Action để tạo tài khoản cho học sinh đã chọn"""
        # Lọc học sinh chưa có tài khoản
        students_without_accounts = queryset.filter(user__isnull=True)
        
        if not students_without_accounts:
            self.message_user(request, "Tất cả học sinh đã chọn đã có tài khoản.")
            return
        
        # Tạo tài khoản
        created_count = 0
        for student in students_without_accounts:
            login_code = (student.student_id or "").strip()
            if login_code:
                try:
                    from home_auth.models import CustomUser
                    email = self._build_unique_student_email(CustomUser, login_code)
                    # Lưu ý: Student.first_name là "Tên", Student.last_name là "Họ"
                    # Nhưng User.first_name cần là tên riêng, User.last_name là họ
                    # Nên swap lại: User.first_name = Student.last_name, User.last_name = Student.first_name
                    user = CustomUser.objects.create_user(
                        username=login_code,
                        password=login_code,
                        email=email,
                        first_name=student.last_name,
                        last_name=student.first_name,
                        is_student=True,
                        is_active=True
                    )

                    user.is_authorized = True
                    user.save()

                    student.user = user
                    student.save()
                    created_count += 1
                except Exception as e:
                    self.message_user(request, f"Lỗi tạo tài khoản cho {student}: {e}", level='error')
        
        if created_count > 0:
            self.message_user(request, f"Đã tạo tài khoản cho {created_count} học sinh.")
        else:
            self.message_user(request, "Không tạo được tài khoản nào.", level='warning')
    
    create_student_accounts.short_description = "Tạo tài khoản cho học sinh đã chọn"

    def _build_unique_student_email(self, user_model, login_code):
        base_email = f"{login_code}@student.edu.vn"
        if not user_model.objects.filter(email=base_email).exists():
            return base_email

        counter = 1
        while True:
            candidate = f"{login_code}.{counter}@student.edu.vn"
            if not user_model.objects.filter(email=candidate).exists():
                return candidate
            counter += 1
    
    def reset_student_passwords(self, request, queryset):
        """Action để reset mật khẩu về student_code"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Lọc học sinh có tài khoản
        students_with_accounts = queryset.filter(user__isnull=False)
        
        if not students_with_accounts:
            self.message_user(request, "Không có học sinh nào có tài khoản để reset.")
            return
        
        reset_count = 0
        for student in students_with_accounts:
            login_code = (student.student_id or "").strip()
            if login_code and student.user:
                student.user.set_password(login_code)
                student.user.save()
                reset_count += 1
        
        if reset_count > 0:
            self.message_user(request, f"Đã reset mật khẩu cho {reset_count} học sinh.")
    
    reset_student_passwords.short_description = "Reset mật khẩu về mã học sinh"

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'class_code', 'grade_level', 'capacity', 'class_teacher', 'get_student_count')
    search_fields = ('class_name', 'class_code', 'grade_level')
    list_filter = ('grade_level', 'class_teacher')
    
    def get_student_count(self, obj):
        return obj.get_student_count()
    get_student_count.short_description = 'Số học sinh'

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_name', 'subject_code', 'teacher')
    search_fields = ('subject_name', 'subject_code')
    list_filter = ('teacher',)

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'exam_type', 'score', 'max_score', 'grade_letter', 'exam_date')
    search_fields = ('student__first_name', 'student__last_name', 'subject__subject_name')
    list_filter = ('exam_type', 'grade_letter', 'exam_date', 'subject')
    date_hierarchy = 'exam_date'

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'remarks')
    search_fields = ('student__first_name', 'student__last_name')
    list_filter = ('status', 'date')
    date_hierarchy = 'date'

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('teacher_id', 'user', 'get_full_name', 'phone_number', 'specialization', 'is_active', 'joining_date')
    search_fields = ('teacher_id', 'user__username', 'user__first_name', 'user__last_name', 'user__email')
    list_filter = ('is_active', 'specialization', 'joining_date')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Họ và tên'


@admin.register(AdmissionCandidate)
class AdmissionCandidateAdmin(admin.ModelAdmin):
    list_display = ('exam_number', 'full_name', 'date_of_birth', 'previous_school', 'math_score', 'literature_score', 'english_score', 'total_score', 'assigned_class')
    search_fields = ('exam_number', 'full_name', 'previous_school')
    list_filter = ('date_of_birth', 'assigned_class')
    readonly_fields = ('total_score',)

    def total_score(self, obj):
        return obj.total_score
    total_score.short_description = 'Tổng điểm'


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('class_obj', 'subject', 'teacher', 'day_of_week', 'period', 'room', 'academic_year', 'semester', 'is_active')
    search_fields = ('class_obj__class_name', 'subject__subject_name', 'teacher__user__first_name', 'teacher__user__last_name', 'room')
    list_filter = ('day_of_week', 'period', 'academic_year', 'semester', 'is_active', 'class_obj__grade_level')
    list_editable = ('is_active',)
    ordering = ('day_of_week', 'period')
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('class_obj', 'subject', 'teacher', 'room')
        }),
        ('Thời gian', {
            'fields': ('day_of_week', 'period', 'academic_year', 'semester')
        }),
        ('Trạng thái', {
            'fields': ('is_active',)
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Lọc teacher chỉ hiển thị những user có teacher_profile
        form.base_fields['teacher'].queryset = form.base_fields['teacher'].queryset.filter(
            teacher_profile__isnull=False
        )
        return form
