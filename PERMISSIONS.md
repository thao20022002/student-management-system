# Hệ Thống Phân Quyền - Student Management System

## Tổng Quan

Hệ thống có 3 loại người dùng chính với các quyền khác nhau:

1. **Admin (Quản trị viên)**
2. **Teacher (Giáo viên)**
3. **Student (Học sinh)**

---

## 1. ADMIN (Quản trị viên)

### Quyền truy cập:
- ✅ **Toàn quyền** trong hệ thống
- ✅ Xem, thêm, sửa, xóa tất cả dữ liệu

### Chức năng cụ thể:

#### Quản lý Học sinh:
- ✅ Xem danh sách tất cả học sinh
- ✅ Thêm học sinh mới
- ✅ Sửa thông tin học sinh
- ✅ Xóa học sinh

#### Quản lý Lớp học:
- ✅ Xem danh sách tất cả lớp học
- ✅ Thêm lớp học mới
- ✅ Sửa thông tin lớp học
- ✅ Xóa lớp học
- ✅ Gán giáo viên chủ nhiệm cho lớp

#### Quản lý Môn học:
- ✅ Xem danh sách tất cả môn học
- ✅ Thêm môn học mới
- ✅ Sửa thông tin môn học
- ✅ Xóa môn học
- ✅ Gán giáo viên cho môn học

#### Quản lý Giáo viên:
- ✅ Xem danh sách tất cả giáo viên
- ✅ Thêm giáo viên mới
- ✅ Sửa thông tin giáo viên
- ✅ Xóa giáo viên

#### Quản lý Điểm số:
- ✅ Xem tất cả điểm số
- ✅ Thêm điểm (thông qua giáo viên)
- ✅ Sửa điểm
- ✅ Xóa điểm

#### Quản lý Điểm danh:
- ✅ Xem tất cả điểm danh
- ✅ Thêm điểm danh
- ✅ Sửa điểm danh
- ✅ Xóa điểm danh

#### Báo cáo:
- ✅ Xem tất cả báo cáo và thống kê

---

## 2. TEACHER (Giáo viên)

### Quyền truy cập:
- ✅ Xem và quản lý dữ liệu liên quan đến lớp/môn học của mình
- ❌ Không thể quản lý giáo viên
- ❌ Không thể thêm/sửa/xóa lớp học, môn học

### Chức năng cụ thể:

#### Quản lý Học sinh:
- ✅ Xem danh sách học sinh **trong lớp mà mình là giáo viên chủ nhiệm**
- ✅ Xem chi tiết học sinh trong lớp của mình
- ❌ Không thể thêm học sinh
- ❌ Không thể sửa thông tin học sinh
- ❌ Không thể xóa học sinh

#### Quản lý Lớp học:
- ✅ Xem danh sách lớp học **mà mình là giáo viên chủ nhiệm**
- ❌ Không thể thêm lớp học
- ❌ Không thể sửa lớp học
- ❌ Không thể xóa lớp học

#### Quản lý Môn học:
- ✅ Xem danh sách môn học **mà mình dạy**
- ❌ Không thể thêm môn học
- ❌ Không thể sửa môn học
- ❌ Không thể xóa môn học

#### Quản lý Điểm số:
- ✅ Xem điểm của học sinh **trong môn học mình dạy**
- ✅ Thêm điểm cho học sinh
- ✅ Sửa điểm **chỉ của môn học mình dạy**
- ✅ Xóa điểm **chỉ của môn học mình dạy**

#### Quản lý Điểm danh:
- ✅ Xem điểm danh của học sinh **trong lớp mình chủ nhiệm**
- ✅ Thêm điểm danh cho học sinh trong lớp của mình
- ✅ Sửa điểm danh **chỉ của học sinh trong lớp mình**
- ✅ Xóa điểm danh **chỉ của học sinh trong lớp mình**

#### Báo cáo:
- ✅ Xem báo cáo và thống kê **của lớp/môn học mình quản lý**

---

## 3. STUDENT (Học sinh)

### Quyền truy cập:
- ✅ Chỉ xem thông tin của chính mình
- ❌ Không thể thêm, sửa, xóa bất kỳ dữ liệu nào

### Chức năng cụ thể:

#### Thông tin cá nhân:
- ✅ Xem thông tin của mình (khi được liên kết với tài khoản)
- ✅ Xem chi tiết học sinh

#### Điểm số:
- ✅ Xem điểm số của mình
- ❌ Không thể thêm, sửa, xóa điểm

#### Điểm danh:
- ✅ Xem điểm danh của mình
- ❌ Không thể thêm, sửa, xóa điểm danh

#### Báo cáo:
- ❌ Không thể xem báo cáo tổng hợp

---

## Bảng Tóm Tắt Phân Quyền

| Chức năng | Admin | Teacher | Student |
|-----------|-------|---------|---------|
| **Quản lý Học sinh** |
| Xem danh sách | ✅ Tất cả | ✅ Lớp của mình | ❌ |
| Thêm học sinh | ✅ | ❌ | ❌ |
| Sửa học sinh | ✅ | ❌ | ❌ |
| Xóa học sinh | ✅ | ❌ | ❌ |
| **Quản lý Lớp học** |
| Xem danh sách | ✅ Tất cả | ✅ Lớp của mình | ❌ |
| Thêm lớp | ✅ | ❌ | ❌ |
| Sửa lớp | ✅ | ❌ | ❌ |
| Xóa lớp | ✅ | ❌ | ❌ |
| **Quản lý Môn học** |
| Xem danh sách | ✅ Tất cả | ✅ Môn của mình | ❌ |
| Thêm môn | ✅ | ❌ | ❌ |
| Sửa môn | ✅ | ❌ | ❌ |
| Xóa môn | ✅ | ❌ | ❌ |
| **Quản lý Giáo viên** |
| Xem danh sách | ✅ | ❌ | ❌ |
| Thêm giáo viên | ✅ | ❌ | ❌ |
| Sửa giáo viên | ✅ | ❌ | ❌ |
| Xóa giáo viên | ✅ | ❌ | ❌ |
| **Quản lý Điểm số** |
| Xem điểm | ✅ Tất cả | ✅ Môn của mình | ✅ Của mình |
| Thêm điểm | ✅ | ✅ | ❌ |
| Sửa điểm | ✅ | ✅ Môn của mình | ❌ |
| Xóa điểm | ✅ | ✅ Môn của mình | ❌ |
| **Quản lý Điểm danh** |
| Xem điểm danh | ✅ Tất cả | ✅ Lớp của mình | ✅ Của mình |
| Thêm điểm danh | ✅ | ✅ Lớp của mình | ❌ |
| Sửa điểm danh | ✅ | ✅ Lớp của mình | ❌ |
| Xóa điểm danh | ✅ | ✅ Lớp của mình | ❌ |
| **Báo cáo** |
| Xem báo cáo | ✅ Tất cả | ✅ Lớp/Môn của mình | ❌ |

---

## Cơ Chế Bảo Mật

### Decorators được sử dụng:
1. `@admin_required` - Chỉ admin mới truy cập được
2. `@teacher_required` - Giáo viên hoặc admin mới truy cập được
3. `@admin_or_teacher_required` - Admin hoặc giáo viên mới truy cập được
4. `@login_required` - Yêu cầu đăng nhập

### Kiểm tra quyền trong views:
- Mỗi view đều kiểm tra quyền trước khi thực hiện
- Giáo viên chỉ thao tác được với dữ liệu của lớp/môn học mình quản lý
- Học sinh chỉ xem được thông tin của mình

### Menu động:
- Menu sidebar tự động ẩn/hiện theo quyền của người dùng
- Chỉ hiển thị các chức năng mà người dùng có quyền truy cập

---

## Lưu Ý

1. **Học sinh hiện tại**: Do Student model chưa có liên kết trực tiếp với CustomUser, học sinh có thể xem tất cả thông tin. Để cải thiện, cần thêm ForeignKey từ Student đến CustomUser.

2. **Giáo viên chủ nhiệm**: Giáo viên chỉ quản lý được học sinh trong lớp mà họ được gán làm giáo viên chủ nhiệm (thông qua trường `class_teacher` trong model Class).

3. **Giáo viên bộ môn**: Giáo viên chỉ quản lý được điểm số của môn học mà họ được gán (thông qua trường `teacher` trong model Subject).

4. **Bảo mật**: Tất cả các views đều được bảo vệ bằng decorator và kiểm tra quyền bổ sung trong logic.





