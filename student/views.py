from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Parent, Student, Class, Subject, Grade, Attendance, Teacher
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .decorators import admin_required, teacher_required, admin_or_teacher_required
from django.contrib.auth.decorators import login_required
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
# Create your views here.

@admin_required
def add_student(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        student_id = request.POST.get('student_id')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        student_class = request.POST.get('student_class')
        religion = request.POST.get('religion')
        joining_date = request.POST.get('joining_date')
        mobile_number = request.POST.get('mobile_number')
        admission_number = request.POST.get('admission_number')
        section = request.POST.get('section')
        student_image = request.FILES.get('student_image')

        # Retrieve parent data from the form
        father_name = request.POST.get('father_name')
        father_occupation = request.POST.get('father_occupation')
        father_mobile = request.POST.get('father_mobile')
        father_email = request.POST.get('father_email')
        mother_name = request.POST.get('mother_name')
        mother_occupation = request.POST.get('mother_occupation')
        mother_mobile = request.POST.get('mother_mobile')
        mother_email = request.POST.get('mother_email')
        present_address = request.POST.get('present_address')
        permanent_address = request.POST.get('permanent_address')

        # save parent information
        parent = Parent.objects.create(
            father_name= father_name,
            father_occupation= father_occupation,
            father_mobile= father_mobile,
            father_email= father_email,
            mother_name= mother_name,
            mother_occupation= mother_occupation,
            mother_mobile= mother_mobile,
            mother_email= mother_email,
            present_address= present_address,
            permanent_address= permanent_address
        )

        # Get class object if provided
        class_obj = None
        if student_class:
            try:
                class_obj = Class.objects.get(pk=student_class)
            except Class.DoesNotExist:
                pass

        # Save student information
        student = Student.objects.create(
            first_name= first_name,
            last_name= last_name,
            student_id= student_id,
            gender= gender,
            date_of_birth= date_of_birth,
            student_class= class_obj,
            religion= religion,
            joining_date= joining_date,
            mobile_number = mobile_number,
            admission_number = admission_number,
            section = section,
            student_image = student_image,
            parent = parent
        )
        from school.models import Notification
        Notification.objects.create(user=request.user, message=f"Đã thêm học sinh: {student.first_name} {student.last_name}")
        messages.success(request, "Đã thêm học sinh thành công!")
        return redirect('student_list')

    classes = Class.objects.all()
    return render(request,"students/add-student.html", {'classes': classes})



@admin_or_teacher_required
def student_list(request):
    # Admin và giáo viên xem tất cả học sinh
    # Giáo viên chỉ xem học sinh trong lớp của mình
    if request.user.is_admin:
        all_classes = Class.objects.all().order_by('grade_level', 'class_name')
        student_list = Student.objects.select_related('parent', 'student_class').filter(is_active=True)
    else:
        # Giáo viên chỉ xem học sinh trong lớp mà họ là giáo viên chủ nhiệm
        all_classes = Class.objects.filter(class_teacher=request.user).order_by('grade_level', 'class_name')
        student_list = Student.objects.filter(student_class__in=all_classes, is_active=True).select_related('parent', 'student_class')
    
    # Filtering theo lớp
    selected_class = None
    class_id = request.GET.get('class')
    if class_id:
        try:
            selected_class = Class.objects.get(id=class_id)
            # Nếu là giáo viên, kiểm tra xem lớp có thuộc giáo viên không
            if request.user.is_teacher and selected_class.class_teacher != request.user:
                messages.error(request, "Bạn không có quyền xem học sinh của lớp này!")
                selected_class = None
            else:
                student_list = student_list.filter(student_class=selected_class)
        except Class.DoesNotExist:
            selected_class = None
    
    # Sắp xếp theo alphabet (tên, họ)
    student_list = student_list.order_by('first_name', 'last_name')
    
    unread_notification = request.user.notification_set.filter(is_read=False)
    context = {
        'student_list': student_list,
        'all_classes': all_classes,
        'selected_class': selected_class,
        'unread_notification': unread_notification
    }
    return render(request, "students/students.html", context)


@admin_or_teacher_required
def export_students_excel(request):
    """
    Export danh sách học sinh ra file Excel với đầy đủ thông tin
    """
    # Lấy danh sách học sinh theo quyền (giống student_list)
    if request.user.is_admin:
        students = Student.objects.select_related('parent', 'student_class').filter(is_active=True)
    else:
        # Giáo viên chỉ xem học sinh trong lớp mà họ là giáo viên chủ nhiệm
        classes = Class.objects.filter(class_teacher=request.user)
        students = Student.objects.filter(student_class__in=classes, is_active=True).select_related('parent', 'student_class')
    
    # Filtering theo lớp nếu có
    class_id = request.GET.get('class')
    if class_id:
        try:
            selected_class = Class.objects.get(id=class_id)
            # Nếu là giáo viên, kiểm tra xem lớp có thuộc giáo viên không
            if request.user.is_teacher and selected_class.class_teacher != request.user:
                messages.error(request, "Bạn không có quyền xuất danh sách học sinh của lớp này!")
                return redirect('student_list')
            students = students.filter(student_class=selected_class)
        except Class.DoesNotExist:
            pass
    
    # Sắp xếp theo alphabet (tên, họ)
    students = students.order_by('first_name', 'last_name')
    
    # Tạo workbook và worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Danh sách học sinh"
    
    # Định nghĩa header
    headers = [
        'STT',
        'Mã học sinh',
        'Họ',
        'Tên',
        'Giới tính',
        'Ngày sinh',
        'Lớp',
        'Số điện thoại',
        'Ngày nhập học',
        'Số nhập học',
        'Khối',
        'Tên cha',
        'Nghề nghiệp cha',
        'SĐT cha',
        'Email cha',
        'Tên mẹ',
        'Nghề nghiệp mẹ',
        'SĐT mẹ',
        'Email mẹ',
        'Địa chỉ hiện tại',
        'Địa chỉ thường trú',
        'Tôn giáo',
        'Trạng thái'
    ]
    
    # Tạo header row với style
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    
    # Điền dữ liệu
    for row_num, student in enumerate(students, 2):
        ws.cell(row=row_num, column=1, value=row_num - 1)  # STT
        ws.cell(row=row_num, column=2, value=student.student_id)
        ws.cell(row=row_num, column=3, value=student.last_name)  # Họ
        ws.cell(row=row_num, column=4, value=student.first_name)  # Tên
        ws.cell(row=row_num, column=5, value=student.get_gender_display())
        ws.cell(row=row_num, column=6, value=student.date_of_birth.strftime('%d/%m/%Y') if student.date_of_birth else '')
        ws.cell(row=row_num, column=7, value=student.student_class.class_name if student.student_class else '')
        ws.cell(row=row_num, column=8, value=student.mobile_number)
        ws.cell(row=row_num, column=9, value=student.joining_date.strftime('%d/%m/%Y') if student.joining_date else '')
        ws.cell(row=row_num, column=10, value=student.admission_number)
        ws.cell(row=row_num, column=11, value=student.section)
        
        # Thông tin phụ huynh
        if student.parent:
            ws.cell(row=row_num, column=12, value=student.parent.father_name)
            ws.cell(row=row_num, column=13, value=student.parent.father_occupation)
            ws.cell(row=row_num, column=14, value=student.parent.father_mobile)
            ws.cell(row=row_num, column=15, value=student.parent.father_email)
            ws.cell(row=row_num, column=16, value=student.parent.mother_name)
            ws.cell(row=row_num, column=17, value=student.parent.mother_occupation)
            ws.cell(row=row_num, column=18, value=student.parent.mother_mobile)
            ws.cell(row=row_num, column=19, value=student.parent.mother_email)
            ws.cell(row=row_num, column=20, value=student.parent.present_address)
            ws.cell(row=row_num, column=21, value=student.parent.permanent_address)
        
        ws.cell(row=row_num, column=22, value=student.religion)
        ws.cell(row=row_num, column=23, value='Đang học' if student.is_active else 'Đã nghỉ')
    
    # Điều chỉnh độ rộng cột
    column_widths = {
        'A': 6,   # STT
        'B': 12,  # Mã học sinh
        'C': 15,  # Họ
        'D': 15,  # Tên
        'E': 10,  # Giới tính
        'F': 12,  # Ngày sinh
        'G': 10,  # Lớp
        'H': 15,  # Số điện thoại
        'I': 12,  # Ngày nhập học
        'J': 12,  # Số nhập học
        'K': 8,   # Khối
        'L': 20,  # Tên cha
        'M': 20,  # Nghề nghiệp cha
        'N': 15,  # SĐT cha
        'O': 25,  # Email cha
        'P': 20,  # Tên mẹ
        'Q': 20,  # Nghề nghiệp mẹ
        'R': 15,  # SĐT mẹ
        'S': 25,  # Email mẹ
        'T': 30,  # Địa chỉ hiện tại
        'U': 30,  # Địa chỉ thường trú
        'V': 15,  # Tôn giáo
        'W': 12,  # Trạng thái
    }
    
    for col_letter, width in column_widths.items():
        ws.column_dimensions[col_letter].width = width
    
    # Đặt chiều cao cho header row
    ws.row_dimensions[1].height = 30
    
    # Tạo response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"Danh_sach_hoc_sinh_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    wb.save(response)
    return response


@admin_required
def edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    parent = student.parent if hasattr(student, 'parent') else None
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        student_id = request.POST.get('student_id')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        student_class = request.POST.get('student_class')
        religion = request.POST.get('religion')
        joining_date = request.POST.get('joining_date')
        mobile_number = request.POST.get('mobile_number')
        admission_number = request.POST.get('admission_number')
        section = request.POST.get('section')
        student_image = request.FILES.get('student_image')  if request.FILES.get('student_image') else student.student_image

        # Retrieve parent data from the form
        parent.father_name = request.POST.get('father_name')
        parent.father_occupation = request.POST.get('father_occupation')
        parent.father_mobile = request.POST.get('father_mobile')
        parent.father_email = request.POST.get('father_email')
        parent.mother_name = request.POST.get('mother_name')
        parent.mother_occupation = request.POST.get('mother_occupation')
        parent.mother_mobile = request.POST.get('mother_mobile')
        parent.mother_email = request.POST.get('mother_email')
        parent.present_address = request.POST.get('present_address')
        parent.permanent_address = request.POST.get('permanent_address')
        parent.save()

#  update student information

        # Get class object if provided
        class_obj = None
        if student_class:
            try:
                class_obj = Class.objects.get(pk=student_class)
            except Class.DoesNotExist:
                pass
        
        student.first_name= first_name
        student.last_name= last_name
        student.student_id= student_id
        student.gender= gender
        student.date_of_birth= date_of_birth
        student.student_class= class_obj
        student.religion= religion
        student.joining_date= joining_date
        student.mobile_number = mobile_number
        student.admission_number = admission_number
        student.section = section
        student.student_image = student_image
        student.save()
        from school.models import Notification
        Notification.objects.create(user=request.user, message=f"Đã cập nhật học sinh: {student.first_name} {student.last_name}")
        messages.success(request, "Đã cập nhật học sinh thành công!")
        return redirect("student_list")
    
    classes = Class.objects.all()
    return render(request, "students/edit-student.html",{'student':student, 'parent':parent, 'classes': classes} )


@login_required
def view_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    # Kiểm tra quyền: Admin xem tất cả, giáo viên xem học sinh trong lớp của mình, học sinh chỉ xem của mình
    if request.user.is_student:
        # Học sinh chỉ xem thông tin của mình (so sánh qua email hoặc username)
        # Tạm thời cho phép học sinh xem tất cả, nhưng có thể cải thiện bằng cách thêm user vào Student model
        pass
    elif request.user.is_teacher:
        # Giáo viên chỉ xem học sinh trong lớp của mình
        if student.student_class and student.student_class.class_teacher != request.user:
            messages.error(request, "Bạn không có quyền xem thông tin học sinh này!")
            return redirect('student_list')
    # Admin có thể xem tất cả
    
    context = {
        'student': student
    }
    return render(request, "students/student-details.html", context)


@admin_required
def delete_student(request, pk):
    if request.method == "POST":
        student = get_object_or_404(Student, pk=pk)
        student_name = f"{student.first_name} {student.last_name}"
        student.delete()
        from school.models import Notification
        Notification.objects.create(user=request.user, message=f"Đã xóa học sinh: {student_name}")
        messages.success(request, "Đã xóa học sinh thành công!")
        return redirect ('student_list')
    return HttpResponseForbidden()

# ========== CLASS MANAGEMENT ==========
@admin_or_teacher_required
def class_list(request):
    # Admin xem tất cả lớp, giáo viên chỉ xem lớp của mình
    if request.user.is_admin:
        classes = Class.objects.annotate(student_count=Count('students')).all().order_by('class_name')
    else:
        classes = Class.objects.filter(class_teacher=request.user).annotate(student_count=Count('students')).order_by('class_name')
    
    context = {
        'classes': classes,
    }
    return render(request, "students/class-list.html", context)

@admin_required
def add_class(request):
    if request.method == "POST":
        class_name = request.POST.get('class_name')
        class_code = request.POST.get('class_code')
        grade_level = request.POST.get('grade_level')
        capacity = request.POST.get('capacity', 30)
        class_teacher_id = request.POST.get('class_teacher')
        
        if Class.objects.filter(class_code=class_code).exists():
            messages.error(request, "Mã lớp đã tồn tại!")
            return render(request, "students/add-class.html")
        
        class_teacher = None
        if class_teacher_id:
            # Lấy user từ Teacher model
            teacher_obj = Teacher.objects.filter(id=class_teacher_id).first()
            if teacher_obj:
                class_teacher = teacher_obj.user
        
        Class.objects.create(
            class_name=class_name,
            class_code=class_code,
            grade_level=grade_level,
            capacity=capacity,
            class_teacher=class_teacher
        )
        from school.models import Notification
        Notification.objects.create(user=request.user, message=f"Đã thêm lớp: {class_name}")
        messages.success(request, "Đã thêm lớp học thành công!")
        return redirect('class_list')
    
    # Chỉ hiển thị giáo viên đã có profile Teacher
    teachers = Teacher.objects.filter(is_active=True).select_related('user')
    context = {'teachers': teachers}
    return render(request, "students/add-class.html", context)

@admin_required
def edit_class(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    if request.method == "POST":
        class_obj.class_name = request.POST.get('class_name')
        class_obj.class_code = request.POST.get('class_code')
        class_obj.grade_level = request.POST.get('grade_level')
        class_obj.capacity = request.POST.get('capacity', 30)
        class_teacher_id = request.POST.get('class_teacher')
        
        if class_teacher_id:
            # Lấy user từ Teacher model
            teacher_obj = Teacher.objects.filter(id=class_teacher_id).first()
            if teacher_obj:
                class_obj.class_teacher = teacher_obj.user
            else:
                class_obj.class_teacher = None
        else:
            class_obj.class_teacher = None
        
        class_obj.save()
        from school.models import Notification
        Notification.objects.create(user=request.user, message=f"Đã cập nhật lớp: {class_obj.class_name}")
        messages.success(request, "Đã cập nhật lớp học thành công!")
        return redirect('class_list')
    
    # Chỉ hiển thị giáo viên đã có profile Teacher
    teachers = Teacher.objects.filter(is_active=True).select_related('user')
    context = {'class_obj': class_obj, 'teachers': teachers}
    return render(request, "students/edit-class.html", context)

@admin_required
def delete_class(request, pk):
    if request.method == "POST":
        class_obj = get_object_or_404(Class, pk=pk)
        class_name = class_obj.class_name
        class_obj.delete()
        from school.models import Notification
        Notification.objects.create(user=request.user, message=f"Đã xóa lớp: {class_name}")
        messages.success(request, "Đã xóa lớp học thành công!")
        return redirect('class_list')
    return HttpResponseForbidden()

# ========== SUBJECT MANAGEMENT ==========
@admin_or_teacher_required
def subject_list(request):
    # Admin xem tất cả môn học, giáo viên chỉ xem môn học của mình
    if request.user.is_admin:
        subjects = Subject.objects.select_related('teacher').all().order_by('subject_name')
    else:
        subjects = Subject.objects.filter(teacher=request.user).select_related('teacher').order_by('subject_name')
    
    context = {'subjects': subjects}
    return render(request, "students/subject-list.html", context)

@admin_required
def add_subject(request):
    if request.method == "POST":
        subject_name = request.POST.get('subject_name')
        subject_code = request.POST.get('subject_code')
        description = request.POST.get('description', '')
        teacher_id = request.POST.get('teacher')
        
        if Subject.objects.filter(subject_code=subject_code).exists():
            messages.error(request, "Mã môn học đã tồn tại!")
            return render(request, "students/add-subject.html")
        
        teacher = None
        if teacher_id:
            from home_auth.models import CustomUser
            # Lấy user từ Teacher model
            teacher_obj = Teacher.objects.filter(id=teacher_id).first()
            if teacher_obj:
                teacher = teacher_obj.user
            else:
                teacher = None
        else:
            teacher = None
        
        Subject.objects.create(
            subject_name=subject_name,
            subject_code=subject_code,
            description=description,
            teacher=teacher
        )
        from school.models import Notification
        Notification.objects.create(user=request.user, message=f"Đã thêm môn học: {subject_name}")
        messages.success(request, "Đã thêm môn học thành công!")
        return redirect('subject_list')
    
    # Chỉ hiển thị giáo viên đã có profile Teacher
    teachers = Teacher.objects.filter(is_active=True).select_related('user')
    context = {'teachers': teachers}
    return render(request, "students/add-subject.html", context)

@admin_required
def edit_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == "POST":
        subject.subject_name = request.POST.get('subject_name')
        subject.subject_code = request.POST.get('subject_code')
        subject.description = request.POST.get('description', '')
        teacher_id = request.POST.get('teacher')
        
        if teacher_id:
            from home_auth.models import CustomUser
            # Lấy user từ Teacher model
            teacher_obj = Teacher.objects.filter(id=teacher_id).first()
            if teacher_obj:
                subject.teacher = teacher_obj.user
            else:
                subject.teacher = None
        else:
            subject.teacher = None
        
        subject.save()
        from school.models import Notification
        Notification.objects.create(user=request.user, message=f"Đã cập nhật môn học: {subject.subject_name}")
        messages.success(request, "Đã cập nhật môn học thành công!")
        return redirect('subject_list')
    
    # Chỉ hiển thị giáo viên đã có profile Teacher
    teachers = Teacher.objects.filter(is_active=True).select_related('user')
    context = {'subject': subject, 'teachers': teachers}
    return render(request, "students/edit-subject.html", context)

@admin_required
def delete_subject(request, pk):
    if request.method == "POST":
        subject = get_object_or_404(Subject, pk=pk)
        subject_name = subject.subject_name
        subject.delete()
        from school.models import Notification
        Notification.objects.create(user=request.user, message=f"Đã xóa môn học: {subject_name}")
        messages.success(request, "Đã xóa môn học thành công!")
        return redirect('subject_list')
    return HttpResponseForbidden()

# ========== GRADE MANAGEMENT ==========
@login_required
def grade_list(request):
    # Admin xem tất cả điểm, giáo viên chỉ xem điểm của lớp mình chủ nhiệm và môn học mình dạy
    # Chỉ hiển thị điểm đã được duyệt (is_approved=True)
    if request.user.is_admin:
        grades = Grade.objects.select_related('student', 'subject').filter(is_approved=True)
        all_classes = Class.objects.all()
        subjects = Subject.objects.all()
    elif request.user.is_teacher:
        # Giáo viên chỉ xem điểm của học sinh trong lớp mình chủ nhiệm VÀ môn học mình dạy
        teacher_classes = Class.objects.filter(class_teacher=request.user)
        teacher_subjects = Subject.objects.filter(teacher=request.user)
        grades = Grade.objects.filter(
            student__student_class__in=teacher_classes,
            subject__in=teacher_subjects,
            is_approved=True
        ).select_related('student', 'subject')
        # Chỉ hiển thị lớp của giáo viên
        all_classes = teacher_classes
        subjects = teacher_subjects
    else:
        # Học sinh chỉ xem điểm của mình (tạm thời cho phép xem tất cả, cần cải thiện)
        grades = Grade.objects.select_related('student', 'subject').filter(is_approved=True)
        all_classes = Class.objects.all()
        subjects = Subject.objects.all()
    
    # Filtering
    class_id = request.GET.get('class')
    subject_id = request.GET.get('subject')
    exam_type = request.GET.get('exam_type')
    
    # Filter theo lớp
    selected_class = None
    if class_id:
        try:
            selected_class = Class.objects.get(id=class_id)
            # Nếu là giáo viên, kiểm tra xem lớp có thuộc giáo viên không
            if request.user.is_teacher and selected_class.class_teacher != request.user:
                messages.error(request, "Bạn không có quyền xem điểm của lớp này!")
                selected_class = None
            else:
                grades = grades.filter(student__student_class=selected_class)
        except Class.DoesNotExist:
            selected_class = None
    
    if subject_id:
        grades = grades.filter(subject_id=subject_id)
    if exam_type:
        grades = grades.filter(exam_type=exam_type)
    
    # Sắp xếp theo alphabet (tên học sinh)
    grades = grades.order_by('student__first_name', 'student__last_name', '-exam_date')
    
    context = {
        'grades': grades,
        'classes': all_classes,
        'subjects': subjects,
        'selected_class': selected_class,
    }
    return render(request, "students/grade-list.html", context)

@teacher_required
def add_grade(request):
    if request.method == "POST":
        from decimal import Decimal, InvalidOperation
        
        student_id = request.POST.get('student')
        subject_id = request.POST.get('subject')
        exam_type = request.POST.get('exam_type')
        score_str = request.POST.get('score')
        max_score_str = request.POST.get('max_score', '100')
        exam_date = request.POST.get('exam_date')
        remarks = request.POST.get('remarks', '')
        
        # Convert score và max_score từ string sang Decimal
        try:
            score = Decimal(str(score_str)) if score_str else Decimal('0')
            max_score = Decimal(str(max_score_str)) if max_score_str else Decimal('100')
        except (ValueError, InvalidOperation) as e:
            messages.error(request, f"Điểm số không hợp lệ: {str(e)}")
            # Lấy lại danh sách lớp, học sinh và môn học theo quyền
            if request.user.is_admin:
                all_classes = Class.objects.all().order_by('class_name')
                students = Student.objects.filter(is_active=True).order_by('first_name', 'last_name')
                subjects = Subject.objects.all().order_by('subject_name')
            else:
                all_classes = Class.objects.filter(class_teacher=request.user).order_by('class_name')
                teacher_classes = Class.objects.filter(class_teacher=request.user)
                students = Student.objects.filter(student_class__in=teacher_classes, is_active=True).order_by('first_name', 'last_name')
                subjects = Subject.objects.filter(teacher=request.user).order_by('subject_name')
            context = {
                'students': students, 
                'subjects': subjects,
                'all_classes': all_classes,
                'selected_class': None
            }
            return render(request, "students/add-grade.html", context)
        
        student = get_object_or_404(Student, id=student_id)
        subject = get_object_or_404(Subject, id=subject_id)
        
        # Kiểm tra quyền: giáo viên chỉ thêm điểm cho học sinh trong lớp mình chủ nhiệm và môn học mình dạy
        if not request.user.is_admin:
            if not student.student_class or student.student_class.class_teacher != request.user:
                messages.error(request, "Bạn không có quyền thêm điểm cho học sinh này! Học sinh không thuộc lớp bạn chủ nhiệm.")
                # Lấy lại danh sách lớp, học sinh và môn học theo quyền
                all_classes = Class.objects.filter(class_teacher=request.user).order_by('class_name')
                teacher_classes = Class.objects.filter(class_teacher=request.user)
                students = Student.objects.filter(student_class__in=teacher_classes, is_active=True).order_by('first_name', 'last_name')
                subjects = Subject.objects.filter(teacher=request.user).order_by('subject_name')
                context = {
                    'students': students, 
                    'subjects': subjects,
                    'all_classes': all_classes,
                    'selected_class': None
                }
                return render(request, "students/add-grade.html", context)
            
            if subject.teacher != request.user:
                messages.error(request, "Bạn không có quyền thêm điểm cho môn học này! Bạn không dạy môn học này.")
                # Lấy lại danh sách lớp, học sinh và môn học theo quyền
                all_classes = Class.objects.filter(class_teacher=request.user).order_by('class_name')
                teacher_classes = Class.objects.filter(class_teacher=request.user)
                students = Student.objects.filter(student_class__in=teacher_classes, is_active=True).order_by('first_name', 'last_name')
                subjects = Subject.objects.filter(teacher=request.user).order_by('subject_name')
                context = {
                    'students': students, 
                    'subjects': subjects,
                    'all_classes': all_classes,
                    'selected_class': None
                }
                return render(request, "students/add-grade.html", context)
        
        # Nếu là admin, điểm được tự động duyệt. Nếu là giáo viên, cần chờ duyệt
        is_approved = request.user.is_admin
        
        grade = Grade.objects.create(
            student=student,
            subject=subject,
            exam_type=exam_type,
            score=score,
            max_score=max_score,
            exam_date=exam_date,
            remarks=remarks,
            is_approved=is_approved,
            approved_by=request.user if is_approved else None,
            approved_at=timezone.now() if is_approved else None
        )
        from school.models import Notification
        if is_approved:
            Notification.objects.create(user=request.user, message=f"Đã thêm điểm cho {student.first_name} - {subject.subject_name}")
            messages.success(request, "Đã thêm điểm thành công!")
        else:
            Notification.objects.create(user=request.user, message=f"Đã gửi yêu cầu thêm điểm cho {student.first_name} - {subject.subject_name}, đang chờ duyệt")
            messages.success(request, "Đã gửi yêu cầu thêm điểm thành công! Điểm sẽ được hiển thị sau khi được admin duyệt.")
        return redirect('grade_list')
    
    # Lấy danh sách lớp theo quyền
    if request.user.is_admin:
        all_classes = Class.objects.all().order_by('class_name')
    else:
        # Giáo viên chỉ thấy lớp mình chủ nhiệm
        all_classes = Class.objects.filter(class_teacher=request.user).order_by('class_name')
    
    # Lọc học sinh theo lớp được chọn
    selected_class = None
    class_id = request.GET.get('class')
    if class_id:
        try:
            selected_class = Class.objects.get(id=class_id)
            # Kiểm tra quyền: giáo viên chỉ chọn được lớp của mình
            if request.user.is_teacher and selected_class.class_teacher != request.user:
                messages.error(request, "Bạn không có quyền chọn lớp này!")
                selected_class = None
        except Class.DoesNotExist:
            selected_class = None
    
    # Lấy danh sách học sinh và môn học theo quyền
    if request.user.is_admin:
        if selected_class:
            students = Student.objects.filter(student_class=selected_class, is_active=True).order_by('first_name', 'last_name')
        else:
            students = Student.objects.filter(is_active=True).order_by('first_name', 'last_name')
        subjects = Subject.objects.all().order_by('subject_name')
    else:
        # Giáo viên chỉ thấy học sinh trong lớp mình chủ nhiệm và môn học mình dạy
        teacher_classes = Class.objects.filter(class_teacher=request.user)
        if selected_class:
            # Nếu chọn lớp, chỉ hiển thị học sinh của lớp đó
            if selected_class in teacher_classes:
                students = Student.objects.filter(student_class=selected_class, is_active=True).order_by('first_name', 'last_name')
            else:
                students = Student.objects.none()
        else:
            students = Student.objects.filter(student_class__in=teacher_classes, is_active=True).order_by('first_name', 'last_name')
        subjects = Subject.objects.filter(teacher=request.user).order_by('subject_name')
    
    context = {
        'students': students, 
        'subjects': subjects,
        'all_classes': all_classes,
        'selected_class': selected_class
    }
    return render(request, "students/add-grade.html", context)

@teacher_required
def edit_grade(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    
    # Kiểm tra quyền: giáo viên chỉ sửa được điểm của học sinh trong lớp mình chủ nhiệm và môn học mình dạy
    if not request.user.is_admin:
        if not grade.student.student_class or grade.student.student_class.class_teacher != request.user:
            messages.error(request, "Bạn không có quyền sửa điểm này! Học sinh không thuộc lớp bạn chủ nhiệm.")
            return redirect('grade_list')
        if grade.subject.teacher != request.user:
            messages.error(request, "Bạn không có quyền sửa điểm này! Bạn không dạy môn học này.")
            return redirect('grade_list')
    
    if request.method == "POST":
        from decimal import Decimal, InvalidOperation
        
        new_student_id = request.POST.get('student')
        new_subject_id = request.POST.get('subject')
        exam_type = request.POST.get('exam_type')
        
        # Kiểm tra quyền với học sinh và môn học mới (nếu có thay đổi)
        if not request.user.is_admin:
            new_student = get_object_or_404(Student, id=new_student_id)
            new_subject = get_object_or_404(Subject, id=new_subject_id)
            
            if not new_student.student_class or new_student.student_class.class_teacher != request.user:
                messages.error(request, "Bạn không có quyền sửa điểm này! Học sinh không thuộc lớp bạn chủ nhiệm.")
                # Lấy lại danh sách học sinh và môn học theo quyền
                teacher_classes = Class.objects.filter(class_teacher=request.user)
                students = Student.objects.filter(student_class__in=teacher_classes, is_active=True)
                subjects = Subject.objects.filter(teacher=request.user)
                context = {'grade': grade, 'students': students, 'subjects': subjects}
                return render(request, "students/edit-grade.html", context)
            
            if new_subject.teacher != request.user:
                messages.error(request, "Bạn không có quyền sửa điểm này! Bạn không dạy môn học này.")
                # Lấy lại danh sách học sinh và môn học theo quyền
                teacher_classes = Class.objects.filter(class_teacher=request.user)
                students = Student.objects.filter(student_class__in=teacher_classes, is_active=True)
                subjects = Subject.objects.filter(teacher=request.user)
                context = {'grade': grade, 'students': students, 'subjects': subjects}
                return render(request, "students/edit-grade.html", context)
        
        grade.student_id = new_student_id
        grade.subject_id = new_subject_id
        grade.exam_type = exam_type
        
        # Convert score và max_score từ string sang Decimal
        try:
            score_str = request.POST.get('score')
            max_score_str = request.POST.get('max_score', '100')
            grade.score = Decimal(str(score_str)) if score_str else Decimal('0')
            grade.max_score = Decimal(str(max_score_str)) if max_score_str else Decimal('100')
        except (ValueError, InvalidOperation) as e:
            messages.error(request, f"Điểm số không hợp lệ: {str(e)}")
            # Lấy lại danh sách học sinh và môn học theo quyền
            if request.user.is_admin:
                students = Student.objects.filter(is_active=True)
                subjects = Subject.objects.all()
            else:
                teacher_classes = Class.objects.filter(class_teacher=request.user)
                students = Student.objects.filter(student_class__in=teacher_classes, is_active=True)
                subjects = Subject.objects.filter(teacher=request.user)
            context = {'grade': grade, 'students': students, 'subjects': subjects}
            return render(request, "students/edit-grade.html", context)
        
        grade.exam_date = request.POST.get('exam_date')
        grade.remarks = request.POST.get('remarks', '')
        
        # Nếu là admin, điểm được tự động duyệt. Nếu là giáo viên, cần chờ duyệt lại
        if request.user.is_admin:
            grade.is_approved = True
            grade.approved_by = request.user
            grade.approved_at = timezone.now()
        else:
            # Giáo viên sửa điểm thì cần duyệt lại
            grade.is_approved = False
            grade.approved_by = None
            grade.approved_at = None
        
        grade.save()
        from school.models import Notification
        if grade.is_approved:
            Notification.objects.create(user=request.user, message=f"Đã cập nhật điểm cho {grade.student.first_name} - {grade.subject.subject_name}")
            messages.success(request, "Đã cập nhật điểm thành công!")
        else:
            Notification.objects.create(user=request.user, message=f"Đã gửi yêu cầu cập nhật điểm cho {grade.student.first_name} - {grade.subject.subject_name}, đang chờ duyệt")
            messages.success(request, "Đã gửi yêu cầu cập nhật điểm thành công! Điểm sẽ được hiển thị sau khi được admin duyệt.")
        return redirect('grade_list')
    
    # Lấy danh sách học sinh và môn học theo quyền
    if request.user.is_admin:
        students = Student.objects.filter(is_active=True)
        subjects = Subject.objects.all()
    else:
        # Giáo viên chỉ thấy học sinh trong lớp mình chủ nhiệm và môn học mình dạy
        teacher_classes = Class.objects.filter(class_teacher=request.user)
        students = Student.objects.filter(student_class__in=teacher_classes, is_active=True)
        subjects = Subject.objects.filter(teacher=request.user)
    
    context = {'grade': grade, 'students': students, 'subjects': subjects}
    return render(request, "students/edit-grade.html", context)

@teacher_required
def delete_grade(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    
    # Kiểm tra quyền: giáo viên chỉ xóa được điểm của học sinh trong lớp mình chủ nhiệm và môn học mình dạy
    if not request.user.is_admin:
        if not grade.student.student_class or grade.student.student_class.class_teacher != request.user:
            messages.error(request, "Bạn không có quyền xóa điểm này! Học sinh không thuộc lớp bạn chủ nhiệm.")
            return redirect('grade_list')
        if grade.subject.teacher != request.user:
            messages.error(request, "Bạn không có quyền xóa điểm này! Bạn không dạy môn học này.")
            return redirect('grade_list')
    
    if request.method == "POST":
        grade.delete()
        messages.success(request, "Đã xóa điểm thành công!")
        return redirect('grade_list')
    return HttpResponseForbidden()

@admin_required
def approve_grades(request):
    """
    Trang admin xem danh sách điểm chờ duyệt
    """
    # Lấy danh sách tất cả lớp và môn học
    all_classes = Class.objects.all().order_by('class_name')
    all_subjects = Subject.objects.all().order_by('subject_name')
    
    # Lấy danh sách các loại kiểm tra thực tế có trong database (từ điểm chờ duyệt)
    exam_types_in_db = Grade.objects.filter(is_approved=False).values_list('exam_type', flat=True).distinct().order_by('exam_type')
    
    # Lấy các filter từ GET parameters
    class_id = request.GET.get('class')
    subject_id = request.GET.get('subject')
    exam_type = request.GET.get('exam_type')
    
    # Khởi tạo queryset điểm chờ duyệt
    pending_grades = Grade.objects.filter(is_approved=False).select_related('student', 'subject', 'student__student_class')
    
    # Lọc theo lớp
    selected_class = None
    if class_id:
        try:
            selected_class = Class.objects.get(id=class_id)
            pending_grades = pending_grades.filter(student__student_class=selected_class)
        except Class.DoesNotExist:
            selected_class = None
    
    # Lọc theo môn học
    selected_subject = None
    if subject_id:
        try:
            selected_subject = Subject.objects.get(id=subject_id)
            pending_grades = pending_grades.filter(subject=selected_subject)
        except Subject.DoesNotExist:
            selected_subject = None
    
    # Lọc theo loại kiểm tra
    selected_exam_type = exam_type if exam_type else None
    if exam_type:
        pending_grades = pending_grades.filter(exam_type=exam_type)
    
    # Sắp xếp theo ngày tạo
    pending_grades = pending_grades.order_by('created_at')
    
    context = {
        'pending_grades': pending_grades,
        'all_classes': all_classes,
        'all_subjects': all_subjects,
        'exam_types_in_db': exam_types_in_db,
        'selected_class': selected_class,
        'selected_subject': selected_subject,
        'selected_exam_type': selected_exam_type,
    }
    return render(request, "students/approve-grades.html", context)

@admin_required
def approve_grade(request, pk):
    """
    Admin duyệt điểm
    """
    grade = get_object_or_404(Grade, pk=pk)
    
    if request.method == "POST":
        grade.is_approved = True
        grade.approved_by = request.user
        grade.approved_at = timezone.now()
        grade.save()
        
        from school.models import Notification
        Notification.objects.create(user=request.user, message=f"Đã duyệt điểm cho {grade.student.first_name} - {grade.subject.subject_name}")
        messages.success(request, f"Đã duyệt điểm cho {grade.student.first_name} - {grade.subject.subject_name} thành công!")
        
        # Giữ lại tất cả filter khi redirect
        params = []
        if request.GET.get('class'):
            params.append(f"class={request.GET.get('class')}")
        if request.GET.get('subject'):
            params.append(f"subject={request.GET.get('subject')}")
        if request.GET.get('exam_type'):
            params.append(f"exam_type={request.GET.get('exam_type')}")
        
        if params:
            return redirect(f"{reverse('approve_grades')}?{'&'.join(params)}")
        return redirect('approve_grades')
    
    return HttpResponseForbidden()

@admin_required
def reject_grade(request, pk):
    """
    Admin từ chối điểm (xóa điểm chờ duyệt)
    """
    grade = get_object_or_404(Grade, pk=pk)
    
    if request.method == "POST":
        student_name = f"{grade.student.first_name} {grade.student.last_name}"
        subject_name = grade.subject.subject_name
        grade.delete()
        
        from school.models import Notification
        Notification.objects.create(user=request.user, message=f"Đã từ chối điểm cho {student_name} - {subject_name}")
        messages.success(request, f"Đã từ chối điểm cho {student_name} - {subject_name}")
        
        # Giữ lại tất cả filter khi redirect
        params = []
        if request.GET.get('class'):
            params.append(f"class={request.GET.get('class')}")
        if request.GET.get('subject'):
            params.append(f"subject={request.GET.get('subject')}")
        if request.GET.get('exam_type'):
            params.append(f"exam_type={request.GET.get('exam_type')}")
        
        if params:
            return redirect(f"{reverse('approve_grades')}?{'&'.join(params)}")
        return redirect('approve_grades')
    
    return HttpResponseForbidden()

@admin_required
def approve_all_grades(request):
    """
    Admin duyệt tất cả điểm chờ duyệt (có thể lọc theo lớp, môn học, loại kiểm tra)
    """
    if request.method == "POST":
        # Lấy các filter từ GET parameters
        class_id = request.GET.get('class')
        subject_id = request.GET.get('subject')
        exam_type = request.GET.get('exam_type')
        
        # Khởi tạo queryset điểm chờ duyệt
        pending_grades = Grade.objects.filter(is_approved=False)
        
        # Lọc theo lớp
        selected_class = None
        if class_id:
            try:
                selected_class = Class.objects.get(id=class_id)
                pending_grades = pending_grades.filter(student__student_class=selected_class)
            except Class.DoesNotExist:
                pass
        
        # Lọc theo môn học
        selected_subject = None
        if subject_id:
            try:
                selected_subject = Subject.objects.get(id=subject_id)
                pending_grades = pending_grades.filter(subject=selected_subject)
            except Subject.DoesNotExist:
                pass
        
        # Lọc theo loại kiểm tra
        if exam_type:
            pending_grades = pending_grades.filter(exam_type=exam_type)
        
        count = pending_grades.count()
        
        if count > 0:
            # Duyệt tất cả điểm
            now = timezone.now()
            pending_grades.update(
                is_approved=True,
                approved_by=request.user,
                approved_at=now
            )
            
            from school.models import Notification
            filter_info = []
            if selected_class:
                filter_info.append(f"lớp {selected_class.class_name}")
            if selected_subject:
                filter_info.append(f"môn {selected_subject.subject_name}")
            if exam_type:
                exam_type_choices = {
                    'Quiz': 'Kiểm tra 15 phút',
                    'Midterm': 'Giữa kỳ',
                    'Final': 'Cuối kỳ',
                    'Assignment': 'Bài tập',
                }
                exam_type_display = exam_type_choices.get(exam_type, exam_type)
                filter_info.append(f"loại {exam_type_display}")
            
            filter_text = f" ({', '.join(filter_info)})" if filter_info else ""
            Notification.objects.create(user=request.user, message=f"Đã duyệt tất cả {count} điểm chờ duyệt{filter_text}")
            messages.success(request, f"Đã duyệt thành công {count} điểm{filter_text}!")
        else:
            messages.info(request, "Không có điểm nào đang chờ duyệt.")
        
        # Giữ lại tất cả filter khi redirect
        params = []
        if class_id:
            params.append(f"class={class_id}")
        if subject_id:
            params.append(f"subject={subject_id}")
        if exam_type:
            params.append(f"exam_type={exam_type}")
        
        if params:
            return redirect(f"{reverse('approve_grades')}?{'&'.join(params)}")
        return redirect('approve_grades')
    
    return HttpResponseForbidden()

@login_required
def student_grades(request, pk):
    student = get_object_or_404(Student, pk=pk)
    # Chỉ hiển thị điểm đã được duyệt
    grades = Grade.objects.filter(student=student, is_approved=True).select_related('subject').order_by('subject__subject_name', '-exam_date')
    
    # Calculate statistics - sắp xếp môn học theo alphabet
    subjects = Subject.objects.all().order_by('subject_name')
    subject_stats = []
    for subject in subjects:
        subject_grades = grades.filter(subject=subject)
        if subject_grades.exists():
            avg_score = subject_grades.aggregate(Avg('score'))['score__avg']
            subject_stats.append({
                'subject': subject,
                'average': round(avg_score, 2),
                'count': subject_grades.count()
            })
    
    context = {
        'student': student,
        'grades': grades,
        'subject_stats': subject_stats,
    }
    return render(request, "students/student-grades.html", context)

# ========== ATTENDANCE MANAGEMENT ==========
@login_required
def attendance_list(request):
    # Admin xem tất cả điểm danh, giáo viên chỉ xem điểm danh của lớp mình, học sinh chỉ xem của mình
    if request.user.is_admin:
        attendances = Attendance.objects.select_related('student').all()
        students = Student.objects.filter(is_active=True)
        all_classes = Class.objects.all()
    elif request.user.is_teacher:
        # Giáo viên chỉ xem điểm danh của học sinh trong lớp của mình
        classes = Class.objects.filter(class_teacher=request.user)
        students = Student.objects.filter(student_class__in=classes, is_active=True)
        attendances = Attendance.objects.filter(student__in=students).select_related('student')
        all_classes = classes
    else:
        # Học sinh chỉ xem điểm danh của mình (tạm thời cho phép xem tất cả)
        attendances = Attendance.objects.select_related('student').all()
        students = Student.objects.filter(is_active=True)
        all_classes = Class.objects.all()
    
    # Filtering
    class_id = request.GET.get('class')
    student_id = request.GET.get('student')
    date = request.GET.get('date')
    status = request.GET.get('status')
    
    # Filter theo lớp
    if class_id:
        try:
            selected_class = Class.objects.get(id=class_id)
            # Nếu là giáo viên, kiểm tra xem lớp có thuộc giáo viên không
            if request.user.is_teacher and selected_class.class_teacher != request.user:
                messages.error(request, "Bạn không có quyền xem điểm danh của lớp này!")
                selected_class = None
            else:
                students = students.filter(student_class=selected_class)
                attendances = attendances.filter(student__student_class=selected_class)
        except Class.DoesNotExist:
            selected_class = None
    else:
        selected_class = None
    
    if student_id:
        attendances = attendances.filter(student_id=student_id)
    if date:
        attendances = attendances.filter(date=date)
    if status:
        attendances = attendances.filter(status=status)
    
    # Sắp xếp theo alphabet (tên học sinh)
    attendances = attendances.order_by('student__first_name', 'student__last_name', '-date')
    
    context = {
        'attendances': attendances,
        'students': students,
        'classes': all_classes,
        'selected_class': selected_class,
    }
    return render(request, "students/attendance-list.html", context)

@teacher_required
def add_attendance(request):
    if request.method == "POST":
        date_str = request.POST.get('date')
        student_ids = request.POST.getlist('students')
        statuses = request.POST.getlist('status')
        remarks_list = request.POST.getlist('remarks')
        
        # Kiểm tra ngày có hợp lệ không
        try:
            from datetime import datetime
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, "Ngày không hợp lệ!")
            return redirect('add_attendance')
        
        # Kiểm tra không cho phép điểm danh vào chủ nhật (isoweekday() == 7)
        if attendance_date.isoweekday() == 7:
            messages.error(request, "Không thể điểm danh vào chủ nhật!")
            return redirect('add_attendance')
        
        for i, student_id in enumerate(student_ids):
            student = get_object_or_404(Student, id=student_id)
            status = statuses[i] if i < len(statuses) else 'Present'
            remarks = remarks_list[i] if i < len(remarks_list) else ''
            
            Attendance.objects.update_or_create(
                student=student,
                date=attendance_date,
                defaults={'status': status, 'remarks': remarks}
            )
        
        from school.models import Notification
        Notification.objects.create(user=request.user, message=f"Đã điểm danh ngày {attendance_date}")
        messages.success(request, "Đã điểm danh thành công!")
        return redirect('attendance_list')
    
    # Get today's date or selected date
    selected_date = request.GET.get('date', timezone.now().date().isoformat())
    class_id = request.GET.get('class')
    
    # Lấy danh sách lớp (giáo viên chỉ thấy lớp của mình)
    if request.user.is_admin:
        classes = Class.objects.all()
    else:
        # Giáo viên chỉ thấy lớp của mình
        classes = Class.objects.filter(class_teacher=request.user)
    
    if class_id:
        try:
            selected_class = Class.objects.get(id=class_id)
            # Kiểm tra quyền: giáo viên chỉ có thể điểm danh lớp của mình
            if not request.user.is_admin and selected_class.class_teacher != request.user:
                messages.error(request, "Bạn không có quyền điểm danh lớp này!")
                selected_class = None
                students = Student.objects.none()
            else:
                students = Student.objects.filter(student_class=selected_class, is_active=True)
        except Class.DoesNotExist:
            selected_class = None
            students = Student.objects.none()
    else:
        selected_class = None
        # Nếu không chọn lớp, giáo viên chỉ thấy học sinh trong lớp của mình
        if request.user.is_admin:
            students = Student.objects.filter(is_active=True)
        else:
            students = Student.objects.filter(student_class__in=classes, is_active=True)
    
    # Get existing attendance for the date
    existing_attendance = {}
    if selected_date:
        for att in Attendance.objects.filter(date=selected_date, student__in=students):
            existing_attendance[att.student.id] = {'status': att.status, 'remarks': att.remarks}
    
    context = {
        'students': students,
        'classes': classes,
        'selected_date': selected_date,
        'selected_class': selected_class,
        'existing_attendance': existing_attendance,
    }
    return render(request, "students/add-attendance.html", context)

@teacher_required
def edit_attendance(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    
    # Giáo viên chỉ sửa được điểm danh của học sinh trong lớp của mình
    if not request.user.is_admin:
        if not attendance.student.student_class or attendance.student.student_class.class_teacher != request.user:
            messages.error(request, "Bạn không có quyền sửa điểm danh này!")
            return redirect('attendance_list')
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == "POST":
        attendance.date = request.POST.get('date')
        attendance.status = request.POST.get('status')
        attendance.remarks = request.POST.get('remarks', '')
        attendance.save()
        messages.success(request, "Đã cập nhật điểm danh thành công!")
        return redirect('attendance_list')
    
    context = {'attendance': attendance}
    return render(request, "students/edit-attendance.html", context)

@teacher_required
def delete_attendance(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    
    # Giáo viên chỉ xóa được điểm danh của học sinh trong lớp của mình
    if not request.user.is_admin:
        if not attendance.student.student_class or attendance.student.student_class.class_teacher != request.user:
            messages.error(request, "Bạn không có quyền xóa điểm danh này!")
            return redirect('attendance_list')
    
    if request.method == "POST":
        attendance.delete()
        messages.success(request, "Đã xóa điểm danh thành công!")
        return redirect('attendance_list')
    return HttpResponseForbidden()

@login_required
def student_attendance(request, pk):
    student = get_object_or_404(Student, pk=pk)
    attendances = Attendance.objects.filter(student=student).order_by('-date')
    
    # Calculate statistics
    total_days = attendances.count()
    present_count = attendances.filter(status='Present').count()
    absent_count = attendances.filter(status='Absent').count()
    late_count = attendances.filter(status='Late').count()
    excused_count = attendances.filter(status='Excused').count()
    
    attendance_rate = (present_count / total_days * 100) if total_days > 0 else 0
    
    context = {
        'student': student,
        'attendances': attendances,
        'total_days': total_days,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'excused_count': excused_count,
        'attendance_rate': round(attendance_rate, 2),
    }
    return render(request, "students/student-attendance.html", context)

# ========== REPORTS & STATISTICS ==========
@admin_or_teacher_required
def reports_dashboard(request):
    # Student statistics
    total_students = Student.objects.filter(is_active=True).count()
    total_classes = Class.objects.count()
    total_subjects = Subject.objects.count()
    
    # Attendance statistics (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_attendance = Attendance.objects.filter(date__gte=thirty_days_ago)
    attendance_rate = 0
    if recent_attendance.exists():
        present_count = recent_attendance.filter(status='Present').count()
        attendance_rate = (present_count / recent_attendance.count()) * 100
    
    # Grade statistics
    recent_grades = Grade.objects.filter(exam_date__gte=thirty_days_ago)
    avg_score = recent_grades.aggregate(Avg('score'))['score__avg'] or 0
    
    # Class statistics
    class_stats = []
    for class_obj in Class.objects.all():
        student_count = class_obj.students.filter(is_active=True).count()
        
        # Tính điểm trung bình của lớp (điểm trung bình của tất cả học sinh trong lớp)
        students_in_class = class_obj.students.filter(is_active=True)
        average_grade = None
        if students_in_class.exists():
            # Lấy tất cả điểm của học sinh trong lớp
            grades_in_class = Grade.objects.filter(student__in=students_in_class)
            if grades_in_class.exists():
                avg_result = grades_in_class.aggregate(Avg('score'))['score__avg']
                if avg_result:
                    average_grade = float(avg_result)
        
        class_stats.append({
            'class': class_obj,
            'student_count': student_count,
            'capacity': class_obj.capacity,
            'fill_rate': (student_count / class_obj.capacity * 100) if class_obj.capacity > 0 else 0,
            'average_grade': average_grade
        })
    
    context = {
        'total_students': total_students,
        'total_classes': total_classes,
        'total_subjects': total_subjects,
        'attendance_rate': round(attendance_rate, 2),
        'avg_score': round(avg_score, 2),
        'class_stats': class_stats,
    }
    return render(request, "students/reports-dashboard.html", context)

# ========== TEACHER MANAGEMENT ==========
@admin_required
def teacher_list(request):
    # Lấy tất cả giáo viên có Teacher profile, sắp xếp theo alphabet
    teachers = Teacher.objects.select_related('user').filter(is_active=True).order_by('user__first_name', 'user__last_name')
    context = {'teachers': teachers}
    return render(request, "students/teacher-list.html", context)

@admin_required
def add_teacher(request):
    from home_auth.models import CustomUser
    
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number', '')
        specialization = request.POST.get('specialization', '')
        
        # Kiểm tra username đã tồn tại chưa
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Tên đăng nhập đã tồn tại!")
            return render(request, "students/add-teacher.html")
        
        # Kiểm tra email đã tồn tại chưa
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email đã tồn tại!")
            return render(request, "students/add-teacher.html")
        
        try:
            # Tạo tài khoản giáo viên
            user_account = CustomUser.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
            )
            user_account.is_teacher = True
            user_account.is_authorized = True  # Tự động authorize cho giáo viên được admin tạo
            user_account.save()
            
            # Tự động tạo teacher_id
            teacher_id = f"GV{user_account.id:04d}"
            counter = 1
            while Teacher.objects.filter(teacher_id=teacher_id).exists():
                teacher_id = f"GV{user_account.id:04d}-{counter}"
                counter += 1
            
            # Tạo profile giáo viên với các giá trị mặc định
            teacher = Teacher.objects.create(
                teacher_id=teacher_id,
                user=user_account,
                phone_number=phone_number,
                address='',
                specialization=specialization,
                qualification='',
                joining_date=user_account.date_joined.date() if user_account.date_joined else None,
                is_active=True
            )
            
            from school.models import Notification
            Notification.objects.create(user=request.user, message=f"Đã thêm giáo viên: {teacher.get_full_name()}")
            messages.success(request, "Đã thêm giáo viên thành công!")
            return redirect('teacher_list')
        except Exception as e:
            messages.error(request, f"Có lỗi xảy ra: {str(e)}")
            return render(request, "students/add-teacher.html")
    
    return render(request, "students/add-teacher.html")

@admin_required
def edit_teacher(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    user = teacher.user
    
    if request.method == "POST":
        new_username = request.POST.get('username')
        new_email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number', '')
        specialization = request.POST.get('specialization', '')
        
        # Kiểm tra username đã tồn tại chưa (trừ chính giáo viên này)
        if user.username != new_username and user.__class__.objects.filter(username=new_username).exclude(pk=user.pk).exists():
            messages.error(request, "Tên đăng nhập đã tồn tại!")
            context = {'teacher': teacher}
            return render(request, "students/edit-teacher.html", context)
        
        # Kiểm tra email đã tồn tại chưa (trừ chính giáo viên này)
        if user.email != new_email and user.__class__.objects.filter(email=new_email).exclude(pk=user.pk).exists():
            messages.error(request, "Email đã tồn tại!")
            context = {'teacher': teacher}
            return render(request, "students/edit-teacher.html", context)
        
        # Cập nhật thông tin tài khoản
        user.username = new_username
        user.email = new_email
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        # Cập nhật thông tin Teacher profile
        teacher.phone_number = phone_number
        teacher.specialization = specialization
        teacher.save()
        
        # Cập nhật mật khẩu nếu có
        new_password = request.POST.get('password')
        if new_password:
            user.set_password(new_password)
        
        user.save()
        
        from school.models import Notification
        Notification.objects.create(user=request.user, message=f"Đã cập nhật thông tin giáo viên: {teacher.get_full_name()}")
        messages.success(request, "Đã cập nhật thông tin giáo viên thành công!")
        return redirect('teacher_list')
    
    context = {'teacher': teacher}
    return render(request, "students/edit-teacher.html", context)

@admin_required
def delete_teacher(request, pk):
    if request.method == "POST":
        teacher = get_object_or_404(Teacher, pk=pk)
        teacher_name = teacher.get_full_name()
        user = teacher.user
        
        # Xóa profile giáo viên (sẽ không xóa tài khoản user)
        teacher.delete()
        
        # Có thể xóa hoặc vô hiệu hóa tài khoản user
        # Nếu muốn xóa tài khoản: user.delete()
        # Nếu chỉ vô hiệu hóa:
        user.is_teacher = False
        user.save()
        
        from school.models import Notification
        Notification.objects.create(user=request.user, message=f"Đã xóa giáo viên: {teacher_name}")
        messages.success(request, "Đã xóa giáo viên thành công!")
        return redirect('teacher_list')
    return HttpResponseForbidden()