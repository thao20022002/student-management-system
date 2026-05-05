from django.core.management.base import BaseCommand
from student.models import Student


class Command(BaseCommand):
    help = 'Hoán đổi first_name và last_name cho tất cả học sinh'

    def handle(self, *args, **options):
        students = Student.objects.all()
        count = 0
        
        for student in students:
            student.first_name, student.last_name = student.last_name, student.first_name
            student.save()
            count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Đã hoán đổi tên cho {count} học sinh thành công!')
        )
