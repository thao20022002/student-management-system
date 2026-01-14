from django.core.management.base import BaseCommand
from home_auth.models import CustomUser

class Command(BaseCommand):
    help = 'Loại bỏ định dạng @gmail.com khỏi username và thay thế bằng tên đăng nhập bình thường'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Bắt đầu sửa lại username có @gmail.com...'))
        
        # Tìm tất cả username có chứa @gmail.com
        users_with_email = CustomUser.objects.filter(username__contains='@gmail.com')
        
        updated_count = 0
        skipped_count = 0
        
        for user in users_with_email:
            old_username = user.username
            
            # Loại bỏ @gmail.com và các phần sau
            if '@gmail.com' in old_username:
                new_username = old_username.split('@')[0]
            else:
                # Nếu không có @gmail.com, bỏ qua
                self.stdout.write(self.style.NOTICE(f'  - {old_username}: Không có @gmail.com'))
                skipped_count += 1
                continue
            
            # Kiểm tra xem username mới đã tồn tại chưa
            if CustomUser.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                # Nếu đã tồn tại, thêm số vào cuối
                counter = 1
                while CustomUser.objects.filter(username=f"{new_username}{counter}").exclude(pk=user.pk).exists():
                    counter += 1
                new_username = f"{new_username}{counter}"
            
            try:
                user.username = new_username
                user.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Đã sửa: {old_username} -> {new_username}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Lỗi khi sửa {old_username}: {e}'))
                skipped_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Hoàn thành!'))
        self.stdout.write(self.style.SUCCESS(f'  Đã sửa: {updated_count} tài khoản'))
        self.stdout.write(self.style.NOTICE(f'  Bỏ qua: {skipped_count} tài khoản'))



