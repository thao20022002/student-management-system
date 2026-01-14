from django.core.management.base import BaseCommand
from student.models import Attendance
from django.utils import timezone

class Command(BaseCommand):
    help = 'Xóa tất cả các bản ghi điểm danh vào cuối tuần (thứ 7 và chủ nhật)'

    def handle(self, *args, **options):
        # Lấy tất cả các bản ghi điểm danh
        all_attendances = Attendance.objects.all()
        
        # Đếm số bản ghi vào cuối tuần (thứ 7 = 6, chủ nhật = 7 trong isoweekday)
        weekend_attendances = [a for a in all_attendances if a.date.isoweekday() in [6, 7]]
        count = len(weekend_attendances)
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('Không có bản ghi điểm danh nào vào cuối tuần (thứ 7 và chủ nhật).'))
            return
        
        # Phân loại thứ 7 và chủ nhật
        saturday_count = len([a for a in weekend_attendances if a.date.isoweekday() == 6])
        sunday_count = len([a for a in weekend_attendances if a.date.isoweekday() == 7])
        
        # Hiển thị thông tin trước khi xóa
        self.stdout.write(f'Tìm thấy {count} bản ghi điểm danh vào cuối tuần:')
        self.stdout.write(f'  - Thứ 7: {saturday_count} bản ghi')
        self.stdout.write(f'  - Chủ nhật: {sunday_count} bản ghi')
        self.stdout.write('Ví dụ 5 bản ghi đầu tiên:')
        for a in weekend_attendances[:5]:
            day_name = 'Thứ 7' if a.date.isoweekday() == 6 else 'Chủ nhật'
            self.stdout.write(f'  - {a.date} ({day_name}) - {a.student.first_name} {a.student.last_name} - {a.status}')
        
        # Xóa các bản ghi vào cuối tuần
        deleted_count = 0
        for attendance in weekend_attendances:
            attendance.delete()
            deleted_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Đã xóa thành công {deleted_count} bản ghi điểm danh vào cuối tuần.'))

