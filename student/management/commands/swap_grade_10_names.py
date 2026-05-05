from django.core.management.base import BaseCommand
from student.models import Student


class Command(BaseCommand):
    help = 'Hoán đổi first_name và last_name cho học sinh khối 10'

    def handle(self, *args, **options):
        students = Student.objects.filter(student_class__grade_level='10')
        count = 0
        
        for student in students:
            student.first_name, student.last_name = student.last_name, student.first_name
            student.save()
            count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Đã hoán đổi tên cho {count} học sinh khối 10 thành công!')
        )
