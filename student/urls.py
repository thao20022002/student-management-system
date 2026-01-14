from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    # Student management
    path("", views.student_list, name='student_list'),
    path("add/", views.add_student, name="add_student"),
    path('view/<int:pk>/', views.view_student, name='view_student'),
    path('edit/<int:pk>/', views.edit_student, name='edit_student'),
    path('delete/<int:pk>/', views.delete_student, name='delete_student'),
    path('export-excel/', views.export_students_excel, name='export_students_excel'),
    
    # Class management
    path('classes/', views.class_list, name='class_list'),
    path('classes/add/', views.add_class, name='add_class'),
    path('classes/edit/<int:pk>/', views.edit_class, name='edit_class'),
    path('classes/delete/<int:pk>/', views.delete_class, name='delete_class'),
    
    # Subject management
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/add/', views.add_subject, name='add_subject'),
    path('subjects/edit/<int:pk>/', views.edit_subject, name='edit_subject'),
    path('subjects/delete/<int:pk>/', views.delete_subject, name='delete_subject'),
    
    # Grade management
    path('grades/', views.grade_list, name='grade_list'),
    path('grades/add/', views.add_grade, name='add_grade'),
    path('grades/edit/<int:pk>/', views.edit_grade, name='edit_grade'),
    path('grades/delete/<int:pk>/', views.delete_grade, name='delete_grade'),
    path('grades/approve/', views.approve_grades, name='approve_grades'),
    path('grades/approve/<int:pk>/', views.approve_grade, name='approve_grade'),
    path('grades/approve-all/', views.approve_all_grades, name='approve_all_grades'),
    path('grades/reject/<int:pk>/', views.reject_grade, name='reject_grade'),
    path('students/<int:pk>/grades/', views.student_grades, name='student_grades'),
    
    # Attendance management
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/add/', views.add_attendance, name='add_attendance'),
    path('attendance/edit/<int:pk>/', views.edit_attendance, name='edit_attendance'),
    path('attendance/delete/<int:pk>/', views.delete_attendance, name='delete_attendance'),
    path('students/<int:pk>/attendance/', views.student_attendance, name='student_attendance'),
    
    # Reports
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    
    # Teacher management
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/add/', views.add_teacher, name='add_teacher'),
    path('teachers/edit/<int:pk>/', views.edit_teacher, name='edit_teacher'),
    path('teachers/delete/<int:pk>/', views.delete_teacher, name='delete_teacher'),
]
