from django.core.management.base import BaseCommand
from student.models import Attendance
from django.utils import timezone
from datetime import date

class Command(BaseCommand):
    help = 'Xóa tất cả các bản ghi điểm danh vào chủ nhật và đảm bảo database sạch'

    def handle(self, *args, **options):
        self.stdout.write('Đang kiểm tra database điểm danh...')
        
        # Lấy tất cả các bản ghi điểm danh
        all_attendances = Attendance.objects.all()
        total_count = all_attendances.count()
        
        self.stdout.write(f'Tổng số bản ghi điểm danh: {total_count}')
        
        # Tìm các bản ghi vào chủ nhật (isoweekday() == 7)
        sunday_attendances = []
        for attendance in all_attendances:
            if attendance.date.isoweekday() == 7:  # 7 = Chủ nhật
                sunday_attendances.append(attendance)
        
        sunday_count = len(sunday_attendances)
        
        if sunday_count == 0:
            self.stdout.write(self.style.SUCCESS('✓ Không có bản ghi điểm danh nào vào chủ nhật.'))
            self.stdout.write(self.style.SUCCESS('✓ Database đã sạch, không cần cập nhật.'))
            return
        
        # Hiển thị thông tin chi tiết
        self.stdout.write(self.style.WARNING(f'\nTìm thấy {sunday_count} bản ghi điểm danh vào chủ nhật:'))
        self.stdout.write('Danh sách các bản ghi sẽ bị xóa:')
        
        # Nhóm theo ngày để dễ xem
        by_date = {}
        for att in sunday_attendances:
            date_str = att.date.strftime('%Y-%m-%d')
            if date_str not in by_date:
                by_date[date_str] = []
            by_date[date_str].append(att)
        
        # Hiển thị theo từng ngày
        for date_str in sorted(by_date.keys()):
            atts = by_date[date_str]
            self.stdout.write(f'\n  Ngày {date_str} (Chủ nhật): {len(atts)} bản ghi')
            for att in atts[:5]:  # Hiển thị tối đa 5 bản ghi đầu tiên
                self.stdout.write(f'    - {att.student.first_name} {att.student.last_name} ({att.student.student_id}) - {att.status}')
            if len(atts) > 5:
                self.stdout.write(f'    ... và {len(atts) - 5} bản ghi khác')
        
        # Xác nhận và xóa
        self.stdout.write(self.style.WARNING(f'\nBắt đầu xóa {sunday_count} bản ghi điểm danh vào chủ nhật...'))
        
        deleted_count = 0
        for attendance in sunday_attendances:
            try:
                attendance.delete()
                deleted_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Lỗi khi xóa bản ghi {attendance.id}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Đã xóa thành công {deleted_count}/{sunday_count} bản ghi điểm danh vào chủ nhật.'))
        
        # Kiểm tra lại
        remaining = Attendance.objects.filter(date__isoweekday=7).count()
        if remaining == 0:
            self.stdout.write(self.style.SUCCESS('✓ Xác nhận: Không còn bản ghi điểm danh nào vào chủ nhật trong database.'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Cảnh báo: Vẫn còn {remaining} bản ghi vào chủ nhật.'))


