from django.core.management.base import BaseCommand
from student.models import Class

class Command(BaseCommand):
    help = 'Sửa các mã lớp viết thường thành viết hoa'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Bắt đầu sửa mã lớp...'))
        
        classes = Class.objects.all()
        updated_count = 0
        
        for class_obj in classes:
            old_code = class_obj.class_code
            new_code = old_code.upper()
            
            if old_code != new_code:
                # Kiểm tra xem mã mới đã tồn tại chưa
                if Class.objects.filter(class_code=new_code).exclude(id=class_obj.id).exists():
                    self.stdout.write(self.style.WARNING(f'  - Lớp {class_obj.class_name}: Mã {new_code} đã tồn tại, bỏ qua'))
                    continue
                
                class_obj.class_code = new_code
                class_obj.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Đã sửa lớp {class_obj.class_name}: {old_code} -> {new_code}'))
            else:
                self.stdout.write(self.style.NOTICE(f'  - Lớp {class_obj.class_name}: Mã {old_code} đã đúng'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Hoàn thành! Đã sửa {updated_count} mã lớp'))



