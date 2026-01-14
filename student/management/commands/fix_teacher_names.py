from django.core.management.base import BaseCommand
from student.models import Teacher
from home_auth.models import CustomUser

class Command(BaseCommand):
    help = 'Sửa lại tên giáo viên trong database theo đúng logic tên Việt Nam (Họ trước, Tên sau)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Bắt đầu sửa lại tên giáo viên...'))
        
        teachers = Teacher.objects.all()
        updated_count = 0
        
        for teacher in teachers:
            user = teacher.user
            old_first_name = user.first_name
            old_last_name = user.last_name
            old_full_name = teacher.get_full_name()
            
            # Kiểm tra xem tên có cần sửa không
            # Nếu last_name chứa họ (như "Nguyễn", "Trần", "Lê", "Phạm", etc.) và first_name chứa tên
            # thì cần đảo ngược
            
            # Danh sách các họ phổ biến ở Việt Nam
            common_last_names = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 
                               'Đặng', 'Bùi', 'Đỗ', 'Hồ', 'Ngô', 'Dương', 'Lý', 'Đinh', 'Đào', 'Tạ', 'Tôn',
                               'Lương', 'Trương', 'Vương', 'Đoàn', 'Bạch', 'Cao', 'Chu', 'Đồng', 'Hà', 'Lưu']
            
            # Kiểm tra nếu last_name bắt đầu bằng một trong các họ phổ biến
            # và first_name không bắt đầu bằng họ => cần đảo ngược
            needs_swap = False
            
            if old_last_name and old_first_name:
                # Kiểm tra nếu last_name bắt đầu bằng họ
                last_name_starts_with_ho = any(old_last_name.startswith(ho) for ho in common_last_names)
                first_name_starts_with_ho = any(old_first_name.startswith(ho) for ho in common_last_names)
                
                # Nếu last_name bắt đầu bằng họ và first_name không => cần đảo
                if last_name_starts_with_ho and not first_name_starts_with_ho:
                    needs_swap = True
                # Nếu cả hai đều không bắt đầu bằng họ, nhưng last_name ngắn hơn (có thể là tên)
                # và first_name dài hơn (có thể là họ tên đầy đủ) => cần đảo
                elif not last_name_starts_with_ho and not first_name_starts_with_ho:
                    # Nếu first_name có nhiều từ và last_name có ít từ hơn => có thể cần đảo
                    if len(old_first_name.split()) > len(old_last_name.split()):
                        needs_swap = True
            
            if needs_swap:
                # Đảo ngược first_name và last_name
                new_first_name = old_last_name
                new_last_name = old_first_name
                
                user.first_name = new_first_name
                user.last_name = new_last_name
                user.save()
                
                new_full_name = teacher.get_full_name()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Đã sửa: {old_full_name} -> {new_full_name}'))
            else:
                # Kiểm tra xem format đã đúng chưa
                # Nếu first_name bắt đầu bằng họ => đã đúng
                if old_first_name and any(old_first_name.startswith(ho) for ho in common_last_names):
                    self.stdout.write(self.style.NOTICE(f'  - {old_full_name}: Đã đúng format'))
                else:
                    self.stdout.write(self.style.WARNING(f'  - {old_full_name}: Không xác định được format, bỏ qua'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Hoàn thành! Đã sửa {updated_count} giáo viên'))



