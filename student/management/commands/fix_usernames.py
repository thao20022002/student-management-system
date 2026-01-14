from django.core.management.base import BaseCommand
from home_auth.models import CustomUser
import unicodedata

class Command(BaseCommand):
    help = 'Sửa lại tên đăng nhập cho tất cả tài khoản (loại bỏ dấu tiếng Việt)'

    def remove_vietnamese_accents(self, text):
        """Loại bỏ dấu tiếng Việt"""
        # Mapping các ký tự đặc biệt
        vietnamese_map = {
            'à': 'a', 'á': 'a', 'ạ': 'a', 'ả': 'a', 'ã': 'a',
            'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ậ': 'a', 'ẩ': 'a', 'ẫ': 'a',
            'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ặ': 'a', 'ẳ': 'a', 'ẵ': 'a',
            'è': 'e', 'é': 'e', 'ẹ': 'e', 'ẻ': 'e', 'ẽ': 'e',
            'ê': 'e', 'ề': 'e', 'ế': 'e', 'ệ': 'e', 'ể': 'e', 'ễ': 'e',
            'ì': 'i', 'í': 'i', 'ị': 'i', 'ỉ': 'i', 'ĩ': 'i',
            'ò': 'o', 'ó': 'o', 'ọ': 'o', 'ỏ': 'o', 'õ': 'o',
            'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ộ': 'o', 'ổ': 'o', 'ỗ': 'o',
            'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ợ': 'o', 'ở': 'o', 'ỡ': 'o',
            'ù': 'u', 'ú': 'u', 'ụ': 'u', 'ủ': 'u', 'ũ': 'u',
            'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ự': 'u', 'ử': 'u', 'ữ': 'u',
            'ỳ': 'y', 'ý': 'y', 'ỵ': 'y', 'ỷ': 'y', 'ỹ': 'y',
            'đ': 'd',
            'À': 'A', 'Á': 'A', 'Ạ': 'A', 'Ả': 'A', 'Ã': 'A',
            'Â': 'A', 'Ầ': 'A', 'Ấ': 'A', 'Ậ': 'A', 'Ẩ': 'A', 'Ẫ': 'A',
            'Ă': 'A', 'Ằ': 'A', 'Ắ': 'A', 'Ặ': 'A', 'Ẳ': 'A', 'Ẵ': 'A',
            'È': 'E', 'É': 'E', 'Ẹ': 'E', 'Ẻ': 'E', 'Ẽ': 'E',
            'Ê': 'E', 'Ề': 'E', 'Ế': 'E', 'Ệ': 'E', 'Ể': 'E', 'Ễ': 'E',
            'Ì': 'I', 'Í': 'I', 'Ị': 'I', 'Ỉ': 'I', 'Ĩ': 'I',
            'Ò': 'O', 'Ó': 'O', 'Ọ': 'O', 'Ỏ': 'O', 'Õ': 'O',
            'Ô': 'O', 'Ồ': 'O', 'Ố': 'O', 'Ộ': 'O', 'Ổ': 'O', 'Ỗ': 'O',
            'Ơ': 'O', 'Ờ': 'O', 'Ớ': 'O', 'Ợ': 'O', 'Ở': 'O', 'Ỡ': 'O',
            'Ù': 'U', 'Ú': 'U', 'Ụ': 'U', 'Ủ': 'U', 'Ũ': 'U',
            'Ư': 'U', 'Ừ': 'U', 'Ứ': 'U', 'Ự': 'U', 'Ử': 'U', 'Ữ': 'U',
            'Ỳ': 'Y', 'Ý': 'Y', 'Ỵ': 'Y', 'Ỷ': 'Y', 'Ỹ': 'Y',
            'Đ': 'D',
        }
        
        result = ''
        for char in text:
            result += vietnamese_map.get(char, char)
        
        return result

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Bắt đầu sửa lại tên đăng nhập...'))
        
        users = CustomUser.objects.all()
        updated_count = 0
        skipped_count = 0
        
        for user in users:
            old_username = user.username
            new_username = self.remove_vietnamese_accents(old_username).lower()
            
            # Nếu username không thay đổi, bỏ qua
            if old_username == new_username:
                self.stdout.write(self.style.NOTICE(f'  - {old_username}: Không cần thay đổi'))
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

