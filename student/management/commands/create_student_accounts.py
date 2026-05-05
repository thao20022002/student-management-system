from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from student.models import Student
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Tạo tài khoản đăng nhập cho học sinh (username = student_id, password = student_id)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Tạo tài khoản cho tất cả học sinh chưa có tài khoản',
        )
        parser.add_argument(
            '--student-id',
            type=str,
            help='Tạo tài khoản cho học sinh cụ thể theo student_id',
        )
        parser.add_argument(
            '--class-name',
            type=str,
            help='Tạo tài khoản cho tất cả học sinh trong lớp (vd: 10A1)',
        )

    def handle(self, *args, **options):
        if options['student_id']:
            # Tạo tài khoản cho học sinh cụ thể
            try:
                student = Student.objects.get(student_id=options['student_id'])
                self.create_student_account(student)
            except Student.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Không tìm thấy học sinh với ID: {options["student_id"]}')
                )
        elif options['class_name']:
            # Tạo tài khoản cho tất cả học sinh trong lớp
            students = Student.objects.filter(
                student_class__class_name=options['class_name'],
                is_active=True
            ).exclude(user__isnull=False)

            if not students:
                self.stdout.write(
                    self.style.WARNING(f'Không có học sinh nào trong lớp {options["class_name"]} cần tạo tài khoản')
                )
                return

            self.stdout.write(f'Tìm thấy {students.count()} học sinh trong lớp {options["class_name"]}')

            for student in students:
                self.create_student_account(student)

        elif options['all']:
            # Tạo tài khoản cho tất cả học sinh chưa có tài khoản
            students = Student.objects.filter(
                is_active=True,
                user__isnull=True
            )

            if not students:
                self.stdout.write(
                    self.style.WARNING('Không có học sinh nào cần tạo tài khoản')
                )
                return

            self.stdout.write(f'Tìm thấy {students.count()} học sinh cần tạo tài khoản')

            for student in students:
                self.create_student_account(student)
        else:
            self.stdout.write(
                self.style.ERROR('Vui lòng chỉ định --all, --student-id, hoặc --class-name')
            )

    def create_student_account(self, student):
        """Tạo tài khoản cho một học sinh"""
        login_code = (student.student_id or "").strip()
        if not login_code:
            self.stdout.write(
                self.style.WARNING(f'Học sinh {student} chưa có student_id, bỏ qua')
            )
            return

        if student.user:
            self.stdout.write(
                self.style.WARNING(f'Học sinh {student} đã có tài khoản, bỏ qua')
            )
            return

        try:
            with transaction.atomic():
                email = self._build_unique_email(login_code)
                # Tạo user account
                # Lưu ý: Student.first_name là "Tên", Student.last_name là "Họ"
                # Nhưng User.first_name cần là tên riêng, User.last_name là họ
                # Nên swap lại: User.first_name = Student.last_name, User.last_name = Student.first_name
                user = User.objects.create_user(
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

                # Liên kết với student
                student.user = user
                student.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Đã tạo tài khoản cho {student.get_full_name()}: username={login_code}, password={login_code}'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Lỗi khi tạo tài khoản cho {student}: {e}')
            )

    def _build_unique_email(self, login_code):
        base_email = f"{login_code}@student.edu.vn"
        if not User.objects.filter(email=base_email).exists():
            return base_email

        counter = 1
        while True:
            candidate = f"{login_code}.{counter}@student.edu.vn"
            if not User.objects.filter(email=candidate).exists():
                return candidate
            counter += 1