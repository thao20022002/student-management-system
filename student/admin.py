from django.contrib import admin
from .models import Parent, Student, Class, Subject, Grade, Attendance, Teacher

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('father_name', 'mother_name', 'father_mobile', 'mother_mobile')
    search_fields = ('father_name', 'mother_name', 'father_mobile', 'mother_mobile')
    list_filter = ('father_name', 'mother_name')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'student_id', 'gender', 'date_of_birth', 'student_class', 'joining_date', 'mobile_number', 'admission_number', 'is_active')
    search_fields = ('first_name', 'last_name', 'student_id', 'admission_number')
    list_filter = ('gender', 'student_class', 'is_active', 'section')
    readonly_fields = ('slug', 'created_at')

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
