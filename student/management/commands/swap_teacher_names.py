from django.core.management.base import BaseCommand
from student.models import Teacher


class Command(BaseCommand):
    help = 'Hoán đổi first_name và last_name cho tất cả giáo viên'

    def handle(self, *args, **options):
        teachers = Teacher.objects.all()
        count = 0
        
        for teacher in teachers:
            user = teacher.user
            user.first_name, user.last_name = user.last_name, user.first_name
            user.save()
            count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Đã hoán đổi tên cho {count} giáo viên thành công!')
        )
