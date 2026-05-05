#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Home.settings')
django.setup()

from student.models import Class, Subject, Teacher
from django.contrib.auth import get_user_model

User = get_user_model()

# ============ TIMETABLE GENERATOR ============

CLASSES_LIST = ['10A1', '10A2', '10A3', '11A1', '11A2', '11A3', '12A1', '12A2', '12A3']
DAYS = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7']
PERIODS = [1, 2, 3, 4, 5]

# Môn học & tiết/tuần (chuẩn hóa tên)
SUBJECTS_HOURS = {
    'Toán': 5,
    'Ngữ văn': 5,
    'Tiếng Anh': 4,
    'Vật lý': 3,
    'Hóa học': 3,
    'Sinh học': 2,
    'Lịch sử': 2,
    'Địa lý': 2,
    'Giáo dục công dân': 1,
    'Tin học': 1,
    'Công nghệ': 1
}

# Mapping từ tên DB sang tên chuẩn
SUBJECT_NAME_MAPPING = {
    'Toán học': 'Toán',
    'Toán': 'Toán',
    'Ngữ văn': 'Ngữ văn',
    'Ngữ Văn': 'Ngữ văn',
    'Tiếng anh': 'Tiếng Anh',
    'Tiếng Anh': 'Tiếng Anh',
    'Vật lý': 'Vật lý',
    'Hóa học': 'Hóa học',
    'Sinh học': 'Sinh học',
    'Lịch sử': 'Lịch sử',
    'Địa lý': 'Địa lý',
    'Giáo dục công dân': 'Giáo dục công dân',
    'Tin học': 'Tin học',
    'Công nghệ': 'Công nghệ',
}

# Bộ môn -> giáo viên (từ database)
SUBJECT_TEACHERS = {}

def load_teachers_from_db():
    """Tải danh sách giáo viên từ DB"""
    global SUBJECT_TEACHERS
    subjects = Subject.objects.filter(teacher__isnull=False)
    for subject in subjects:
        teacher = subject.teacher
        teacher_name = f"{teacher.first_name} {teacher.last_name}"
        # Chuẩn hóa tên môn
        std_name = SUBJECT_NAME_MAPPING.get(subject.subject_name, subject.subject_name)
        SUBJECT_TEACHERS[std_name] = teacher_name
    
    # Sinh học không có giáo viên trong DB, gán mặc định
    if 'Sinh học' not in SUBJECT_TEACHERS:
        # Tìm một giáo viên nào có thể dạy Sinh học
        from student.models import Teacher
        teachers = Teacher.objects.filter(user__is_teacher=True)
        if teachers.exists():
            t = teachers.first()
            SUBJECT_TEACHERS['Sinh học'] = f"{t.user.first_name} {t.user.last_name}"

def generate_timetable():
    """Sinh thời khóa biểu"""
    load_teachers_from_db()
    
    # Cấu trúc: class -> day -> period -> {subject, teacher}
    timetable = {cls: {} for cls in CLASSES_LIST}
    for cls in CLASSES_LIST:
        for day in DAYS:
            timetable[cls][day] = {}
    
    # Thời gian cố định
    for cls in CLASSES_LIST:
        timetable[cls]['Thứ 2'][1] = {'subject': 'Chào cờ', 'teacher': None}
        timetable[cls]['Thứ 7'][5] = {'subject': 'Sinh hoạt', 'teacher': None}
    
    # Xếp môn học cho từng lớp
    subject_class_count = {subject: {cls: 0 for cls in CLASSES_LIST} for subject in SUBJECTS_HOURS}
    
    for cls in CLASSES_LIST:
        for subject, hours in SUBJECTS_HOURS.items():
            subject_class_count[subject][cls] = hours
    
    # Xếp lịch theo lớp
    for cls in CLASSES_LIST:
        slot_counter = 0
        
        # Tạo danh sách slot hợp lệ (bỏ qua tiết cố định)
        valid_slots = []
        for day in DAYS:
            for period in PERIODS:
                if (day == 'Thứ 2' and period == 1) or (day == 'Thứ 7' and period == 5):
                    continue
                valid_slots.append((day, period))
        
        # Xếp môn vào slot
        # Ưu tiên: Toán, Văn, Anh trước (môn chính)
        priority_subjects = ['Toán', 'Ngữ văn', 'Tiếng Anh']
        other_subjects = [s for s in SUBJECTS_HOURS.keys() if s not in priority_subjects]
        
        for subject_list in [priority_subjects, other_subjects]:
            for subject in subject_list:
                remaining = subject_class_count[subject][cls]
                for _ in range(remaining):
                    if slot_counter < len(valid_slots):
                        day, period = valid_slots[slot_counter]
                        teacher = SUBJECT_TEACHERS.get(subject)
                        timetable[cls][day][period] = {
                            'subject': subject,
                            'teacher': teacher
                        }
                        subject_class_count[subject][cls] -= 1
                        slot_counter += 1
    
    return timetable

def format_output():
    """Định dạng output JSON"""
    timetable = generate_timetable()
    
    # 1. Thời khóa biểu theo lớp
    class_schedules = []
    for cls in CLASSES_LIST:
        timetable_list = []
        for day in DAYS:
            for period in PERIODS:
                slot = timetable[cls][day].get(period, {})
                timetable_list.append({
                    'day': day,
                    'period': period,
                    'subject': slot.get('subject', ''),
                    'teacher': slot.get('teacher')
                })
        class_schedules.append({
            'class': cls,
            'timetable': timetable_list
        })
    
    # 2. Thời khóa biểu giáo viên
    teacher_schedules_dict = {}
    for cls in CLASSES_LIST:
        for day in DAYS:
            for period in PERIODS:
                slot = timetable[cls][day].get(period, {})
                teacher = slot.get('teacher')
                subject = slot.get('subject')
                
                if teacher and subject not in ['Chào cờ', 'Sinh hoạt']:
                    if teacher not in teacher_schedules_dict:
                        teacher_schedules_dict[teacher] = []
                    teacher_schedules_dict[teacher].append({
                        'day': day,
                        'period': period,
                        'class': cls,
                        'subject': subject
                    })
    
    teacher_schedules = [
        {'teacher': teacher, 'timetable': sorted(slots, key=lambda x: (DAYS.index(x['day']), x['period']))}
        for teacher, slots in sorted(teacher_schedules_dict.items())
    ]
    
    # 3. Phân công giáo viên
    assignments = []
    for subject in SUBJECTS_HOURS.keys():
        teacher = SUBJECT_TEACHERS.get(subject)
        classes = CLASSES_LIST  # Giáo viên dạy tất cả lớp
        if teacher:
            assignments.append({
                'teacher': teacher,
                'subject': subject,
                'classes': classes
            })
    
    output = {
        'class_schedules': class_schedules,
        'teacher_schedules': teacher_schedules,
        'assignments': assignments
    }
    
    return output

if __name__ == '__main__':
    result = format_output()
    # Loại bỏ print statements, chỉ output JSON
    print(json.dumps(result, indent=2, ensure_ascii=False))
