from django.core.management.base import BaseCommand
from home_auth.models import CustomUser

class Command(BaseCommand):
    help = 'Đặt lại mật khẩu mặc định cho tất cả tài khoản'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Bắt đầu đặt lại mật khẩu...'))
        
        default_password = 'Thao2002.'
        users = CustomUser.objects.all()
        updated_count = 0
        
        for user in users:
            user.set_password(default_password)
            user.save()
            updated_count += 1
            self.stdout.write(self.style.SUCCESS(f'  ✓ Đã đặt lại mật khẩu cho: {user.username}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Hoàn thành! Đã đặt lại mật khẩu cho {updated_count} tài khoản'))
        self.stdout.write(self.style.WARNING(f'⚠ Mật khẩu mặc định: {default_password}'))



