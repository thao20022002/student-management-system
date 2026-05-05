#!/usr/bin/env python
"""
Script để tạo dữ liệu mẫu cho thời khóa biểu
"""
import os
import django
import sys

# Thêm đường dẫn project vào sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Home.settings')

django.setup()

from student.models import Schedule, Class, Subject, Teacher
from home_auth.models import CustomUser

def create_sample_timetable():
    """Tạo dữ liệu mẫu cho thời khóa biểu"""
    print("Tạo dữ liệu mẫu cho thời khóa biểu...")

    # Lấy các object cần thiết
    try:
        # Lấy lớp 10A1
        class_10a1 = Class.objects.filter(class_name__icontains='10A1').first()
        if not class_10a1:
            print("Không tìm thấy lớp 10A1")
            return

        # Lấy một số môn học
        subjects = Subject.objects.all()[:5]  # Lấy 5 môn đầu
        if not subjects:
            print("Không có môn học nào")
            return

        # Lấy giáo viên
        teachers = Teacher.objects.filter(is_active=True)[:5]
        if not teachers:
            print("Không có giáo viên nào")
            return

        # Tạo thời khóa biểu mẫu
        sample_schedules = [
            # Thứ Hai
            {'day': 'Monday', 'period': '1', 'subject': subjects[0], 'teacher': teachers[0], 'room': '101'},
            {'day': 'Monday', 'period': '2', 'subject': subjects[1], 'teacher': teachers[1], 'room': '102'},
            {'day': 'Monday', 'period': '3', 'subject': subjects[2], 'teacher': teachers[2], 'room': '103'},
            {'day': 'Monday', 'period': '4', 'subject': subjects[3], 'teacher': teachers[3], 'room': '104'},
            {'day': 'Monday', 'period': '5', 'subject': subjects[4], 'teacher': teachers[4], 'room': '105'},

            # Thứ Ba
            {'day': 'Tuesday', 'period': '1', 'subject': subjects[1], 'teacher': teachers[1], 'room': '102'},
            {'day': 'Tuesday', 'period': '2', 'subject': subjects[2], 'teacher': teachers[2], 'room': '103'},
            {'day': 'Tuesday', 'period': '3', 'subject': subjects[3], 'teacher': teachers[3], 'room': '104'},
            {'day': 'Tuesday', 'period': '4', 'subject': subjects[4], 'teacher': teachers[4], 'room': '105'},
            {'day': 'Tuesday', 'period': '5', 'subject': subjects[0], 'teacher': teachers[0], 'room': '101'},

            # Thứ Tư
            {'day': 'Wednesday', 'period': '1', 'subject': subjects[2], 'teacher': teachers[2], 'room': '103'},
            {'day': 'Wednesday', 'period': '2', 'subject': subjects[3], 'teacher': teachers[3], 'room': '104'},
            {'day': 'Wednesday', 'period': '3', 'subject': subjects[4], 'teacher': teachers[4], 'room': '105'},
            {'day': 'Wednesday', 'period': '4', 'subject': subjects[0], 'teacher': teachers[0], 'room': '101'},
            {'day': 'Wednesday', 'period': '5', 'subject': subjects[1], 'teacher': teachers[1], 'room': '102'},
        ]

        # Tạo các bản ghi Schedule
        created_count = 0
        for schedule_data in sample_schedules:
            # Kiểm tra xem đã tồn tại chưa
            existing = Schedule.objects.filter(
                class_obj=class_10a1,
                day_of_week=schedule_data['day'],
                period=schedule_data['period'],
                academic_year='2026-2027',
                semester='1'
            ).first()

            if not existing:
                Schedule.objects.create(
                    class_obj=class_10a1,
                    subject=schedule_data['subject'],
                    teacher=schedule_data['teacher'].user,
                    day_of_week=schedule_data['day'],
                    period=schedule_data['period'],
                    room=schedule_data['room'],
                    academic_year='2026-2027',
                    semester='1',
                    is_active=True
                )
                created_count += 1

        print(f"Đã tạo {created_count} bản ghi thời khóa biểu mẫu cho lớp {class_10a1.class_name}")

    except Exception as e:
        print(f"Lỗi khi tạo dữ liệu mẫu: {e}")

if __name__ == '__main__':
    create_sample_timetable()