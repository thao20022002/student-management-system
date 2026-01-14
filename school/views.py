from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notification
import json
from decimal import Decimal
from datetime import date, datetime

# Custom JSON encoder để xử lý Decimal và các kiểu không thể serialize
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super(DecimalEncoder, self).default(obj)

# Create your views here.

def index(request):
    return render(request, "authentication/login.html")

@login_required
def dashboard(request):
    unread_notification = Notification.objects.filter(user=request.user, is_read=False)
    unread_notification_count = unread_notification.count()
    
    # Thêm thống kê theo role
    context = {
        'unread_notification': unread_notification,
        'unread_notification_count': unread_notification_count
    }
    
    # Thêm thống kê cho admin và giáo viên
    if request.user.is_admin or request.user.is_teacher:
        from student.models import Student, Class, Subject, Grade, Attendance, Teacher
        from home_auth.models import CustomUser
        from django.db.models import Count, Avg, Q
        from django.utils import timezone
        from datetime import timedelta
        
        # Lấy danh sách lớp học
        all_classes = Class.objects.all().order_by('grade_level', 'class_name')
        context['all_classes'] = all_classes
        
        # Lấy lớp được chọn từ request (nếu có)
        selected_class_id = request.GET.get('class_id')
        selected_class = None
        if selected_class_id:
            try:
                selected_class = Class.objects.get(id=selected_class_id)
                context['selected_class'] = selected_class
            except Class.DoesNotExist:
                pass
        
        # Nếu là giáo viên, chỉ hiển thị lớp của họ
        if request.user.is_teacher:
            teacher_classes = Class.objects.filter(class_teacher=request.user)
            context['all_classes'] = teacher_classes
            # Nếu giáo viên chọn lớp khác lớp của mình, bỏ qua
            if selected_class and selected_class not in teacher_classes:
                selected_class = None
                context['selected_class'] = None
        
        # Thống kê cơ bản (theo lớp nếu có chọn)
        if selected_class:
            students_query = Student.objects.filter(is_active=True, student_class=selected_class)
            context['total_students'] = students_query.count()
            context['total_classes'] = 1
            context['selected_class_name'] = selected_class.class_name
        else:
            students_query = Student.objects.filter(is_active=True)
            context['total_students'] = students_query.count()
            context['total_classes'] = Class.objects.count()
            context['selected_class_name'] = 'Tất cả các lớp'
        
        context['total_subjects'] = Subject.objects.count()
        context['total_teachers'] = Teacher.objects.filter(is_active=True).count()
        
        # Thống kê điểm danh 30 ngày gần nhất (theo lớp nếu có chọn)
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        if selected_class:
            recent_attendance = Attendance.objects.filter(
                date__gte=thirty_days_ago,
                student__student_class=selected_class
            )
        else:
            recent_attendance = Attendance.objects.filter(date__gte=thirty_days_ago)
        
        if recent_attendance.exists():
            present_count = recent_attendance.filter(status='Present').count()
            context['attendance_rate'] = round((present_count / recent_attendance.count()) * 100, 2)
            context['total_attendance'] = recent_attendance.count()
            context['present_count'] = present_count
        else:
            context['attendance_rate'] = 0
            context['total_attendance'] = 0
            context['present_count'] = 0
        
        # Thống kê điểm số (theo lớp nếu có chọn)
        if selected_class:
            recent_grades = Grade.objects.filter(
                exam_date__gte=thirty_days_ago,
                student__student_class=selected_class
            )
        else:
            recent_grades = Grade.objects.filter(exam_date__gte=thirty_days_ago)
        
        if recent_grades.exists():
            context['avg_score'] = round(recent_grades.aggregate(Avg('score'))['score__avg'] or 0, 2)
            context['total_grades'] = recent_grades.count()
        else:
            context['avg_score'] = 0
            context['total_grades'] = 0
        
        # Top học sinh theo điểm trung bình (theo lớp nếu có chọn)
        if selected_class:
            top_students = Student.objects.filter(
                student_class=selected_class,
                grades__exam_date__gte=thirty_days_ago
            ).annotate(
                avg_grade=Avg('grades__score')
            ).filter(
                avg_grade__isnull=False
            ).order_by('-avg_grade')[:5]
        else:
            top_students = Student.objects.filter(
                grades__exam_date__gte=thirty_days_ago
            ).annotate(
                avg_grade=Avg('grades__score')
            ).filter(
                avg_grade__isnull=False
            ).order_by('-avg_grade')[:5]
        context['top_students'] = top_students
        
        # Thống kê theo lớp (nếu chọn lớp thì chỉ hiển thị lớp đó)
        class_stats = []
        if selected_class:
            student_count = selected_class.students.filter(is_active=True).count()
            class_stats.append({
                'class': selected_class,
                'student_count': student_count,
                'capacity': selected_class.capacity,
                'fill_rate': round((student_count / selected_class.capacity * 100) if selected_class.capacity > 0 else 0, 2)
            })
        else:
            for class_obj in Class.objects.all():
                student_count = class_obj.students.filter(is_active=True).count()
                class_stats.append({
                    'class': class_obj,
                    'student_count': student_count,
                    'capacity': class_obj.capacity,
                    'fill_rate': round((student_count / class_obj.capacity * 100) if class_obj.capacity > 0 else 0, 2)
                })
        context['class_stats'] = class_stats
        
        # 1. Biểu đồ phân bố học sinh theo lớp (Pie Chart)
        # Nếu chọn lớp, chỉ hiển thị lớp đó
        if selected_class:
            class_distribution = [{
                'name': selected_class.class_name,
                'value': selected_class.students.filter(is_active=True).count()
            }]
        else:
            class_distribution = []
            for class_obj in Class.objects.all():
                student_count = class_obj.students.filter(is_active=True).count()
                if student_count > 0:
                    class_distribution.append({
                        'name': class_obj.class_name,
                        'value': student_count
                    })
        context['class_distribution'] = json.dumps(class_distribution, cls=DecimalEncoder)
        
        # 2. Biểu đồ điểm trung bình theo môn học (Bar Chart) - theo lớp nếu có chọn
        subject_avg_grades = []
        for subject in Subject.objects.all():
            if selected_class:
                grades_query = Grade.objects.filter(subject=subject, student__student_class=selected_class)
            else:
                grades_query = Grade.objects.filter(subject=subject)
            avg_grade = grades_query.aggregate(Avg('score'))['score__avg']
            if avg_grade is not None:
                subject_avg_grades.append({
                    'name': subject.subject_name,
                    'avg': round(float(avg_grade), 2)
                })
        context['subject_avg_grades'] = json.dumps(subject_avg_grades, cls=DecimalEncoder)
        
        # 3. Biểu đồ phân bố điểm số (Grade Distribution - Pie Chart) - theo lớp nếu có chọn
        grade_distribution = {
            'A+': 0, 'A': 0, 'B+': 0, 'B': 0,
            'C+': 0, 'C': 0, 'D': 0, 'F': 0
        }
        if selected_class:
            all_grades = Grade.objects.filter(student__student_class=selected_class)
        else:
            all_grades = Grade.objects.all()
        for grade in all_grades:
            grade_letter = grade.grade_letter
            if grade_letter in grade_distribution:
                grade_distribution[grade_letter] += 1
        context['grade_distribution'] = json.dumps([
            {'name': k, 'value': v} for k, v in grade_distribution.items() if v > 0
        ], cls=DecimalEncoder)
        
        # 4. Biểu đồ tỷ lệ điểm danh theo thời gian (7 ngày gần nhất - Line Chart) - theo lớp nếu có chọn
        attendance_chart_data = []
        attendance_chart_labels = []
        for i in range(6, -1, -1):  # 7 ngày gần nhất
            date_obj = timezone.now().date() - timedelta(days=i)
            if selected_class:
                day_attendance = Attendance.objects.filter(date=date_obj, student__student_class=selected_class)
            else:
                day_attendance = Attendance.objects.filter(date=date_obj)
            if day_attendance.exists():
                present = day_attendance.filter(status='Present').count()
                total = day_attendance.count()
                rate = round((present / total * 100) if total > 0 else 0, 2)
            else:
                rate = 0
            attendance_chart_data.append(float(rate))
            day_names = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']
            day_name = day_names[date_obj.weekday()]
            attendance_chart_labels.append(f"{day_name}\n{date_obj.strftime('%d/%m')}")
        context['attendance_chart_data'] = json.dumps(attendance_chart_data, cls=DecimalEncoder)
        context['attendance_chart_labels'] = json.dumps(attendance_chart_labels, cls=DecimalEncoder)
        
        # 5. Biểu đồ phân bố học sinh theo giới tính (Pie Chart) - theo lớp nếu có chọn
        gender_distribution = []
        if selected_class:
            male_count = Student.objects.filter(is_active=True, gender='Male', student_class=selected_class).count()
            female_count = Student.objects.filter(is_active=True, gender='Female', student_class=selected_class).count()
            other_count = Student.objects.filter(is_active=True, gender='Others', student_class=selected_class).count()
        else:
            male_count = Student.objects.filter(is_active=True, gender='Male').count()
            female_count = Student.objects.filter(is_active=True, gender='Female').count()
            other_count = Student.objects.filter(is_active=True, gender='Others').count()
        if male_count > 0:
            gender_distribution.append({'name': 'Nam', 'value': male_count})
        if female_count > 0:
            gender_distribution.append({'name': 'Nữ', 'value': female_count})
        if other_count > 0:
            gender_distribution.append({'name': 'Khác', 'value': other_count})
        context['gender_distribution'] = json.dumps(gender_distribution, cls=DecimalEncoder)
        
        # 6. Biểu đồ số lượng học sinh theo lớp (Bar Chart) - nếu chọn lớp thì chỉ hiển thị lớp đó
        if selected_class:
            class_student_count = [{
                'name': selected_class.class_name,
                'count': selected_class.students.filter(is_active=True).count()
            }]
        else:
            class_student_count = []
            for class_obj in Class.objects.all():
                student_count = class_obj.students.filter(is_active=True).count()
                class_student_count.append({
                    'name': class_obj.class_name,
                    'count': student_count
                })
        context['class_student_count'] = json.dumps(class_student_count, cls=DecimalEncoder)
        
        # Logic cho giáo viên đã được xử lý ở trên (filter all_classes và selected_class)
        # Không cần xử lý lại ở đây
    
    return render(request, "Home/index.html", context)



def mark_notification_as_read(request):
    if request.method == 'POST':
        notification = Notification.objects.filter(user=request.user, is_read=False)
        notification.update(is_read=True)
        return JsonResponse({'status': 'success'})
    return HttpResponseForbidden()

def clear_all_notification(request):
    if request.method == "POST":
        notification = Notification.objects.filter(user=request.user)
        notification.delete()
        return JsonResponse({'status': 'success'})
    return HttpResponseForbidden
