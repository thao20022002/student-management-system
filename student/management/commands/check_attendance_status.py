from django.core.management.base import BaseCommand
from student.models import Attendance
from collections import defaultdict
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Kiểm tra và báo cáo trạng thái điểm danh trong database'

    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write('BÁO CÁO TRẠNG THÁI ĐIỂM DANH')
        self.stdout.write('=' * 60)
        
        # Tổng số bản ghi
        all_attendances = Attendance.objects.all()
        total_count = all_attendances.count()
        self.stdout.write(f'\nTổng số bản ghi điểm danh: {total_count}')
        
        if total_count == 0:
            self.stdout.write(self.style.WARNING('Không có dữ liệu điểm danh trong database.'))
            return
        
        # Kiểm tra điểm danh vào chủ nhật
        sunday_attendances = []
        saturday_attendances = []
        weekday_attendances = []
        
        for attendance in all_attendances:
            weekday = attendance.date.isoweekday()
            if weekday == 7:  # Chủ nhật
                sunday_attendances.append(attendance)
            elif weekday == 6:  # Thứ 7
                saturday_attendances.append(attendance)
            else:
                weekday_attendances.append(attendance)
        
        # Báo cáo theo ngày trong tuần
        self.stdout.write('\n' + '-' * 60)
        self.stdout.write('PHÂN TÍCH THEO NGÀY TRONG TUẦN:')
        self.stdout.write('-' * 60)
        self.stdout.write(f'  Thứ 2 - Thứ 6: {len(weekday_attendances)} bản ghi')
        self.stdout.write(f'  Thứ 7:         {len(saturday_attendances)} bản ghi')
        self.stdout.write(f'  Chủ nhật:      {len(sunday_attendances)} bản ghi')
        
        # Kiểm tra chủ nhật
        if len(sunday_attendances) > 0:
            self.stdout.write('\n' + self.style.ERROR('⚠ PHÁT HIỆN ĐIỂM DANH VÀO CHỦ NHẬT!'))
            self.stdout.write(self.style.ERROR(f'  Số lượng: {len(sunday_attendances)} bản ghi'))
            
            # Nhóm theo ngày
            by_date = defaultdict(list)
            for att in sunday_attendances:
                by_date[att.date].append(att)
            
            self.stdout.write('\n  Chi tiết các ngày chủ nhật có điểm danh:')
            for date_obj in sorted(by_date.keys()):
                atts = by_date[date_obj]
                self.stdout.write(f'    - {date_obj.strftime("%Y-%m-%d")} ({date_obj.strftime("%A")}): {len(atts)} bản ghi')
                # Hiển thị một vài ví dụ
                for att in atts[:3]:
                    self.stdout.write(f'        • {att.student.first_name} {att.student.last_name} - {att.status}')
                if len(atts) > 3:
                    self.stdout.write(f'        ... và {len(atts) - 3} bản ghi khác')
        else:
            self.stdout.write('\n' + self.style.SUCCESS('✓ KHÔNG CÓ ĐIỂM DANH VÀO CHỦ NHẬT'))
            self.stdout.write(self.style.SUCCESS('✓ Database đã đúng, không cần sửa.'))
        
        # Thống kê theo tháng
        self.stdout.write('\n' + '-' * 60)
        self.stdout.write('THỐNG KÊ THEO THÁNG (30 ngày gần nhất):')
        self.stdout.write('-' * 60)
        
        today = date.today()
        month_stats = defaultdict(int)
        for attendance in all_attendances:
            month_key = attendance.date.strftime('%Y-%m')
            month_stats[month_key] += 1
        
        for month in sorted(month_stats.keys(), reverse=True)[:6]:
            self.stdout.write(f'  {month}: {month_stats[month]} bản ghi')
        
        self.stdout.write('\n' + '=' * 60)


