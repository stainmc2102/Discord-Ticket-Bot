# Discord Ticket Bot - VietRealm

## Overview
Bot Discord hệ thống ticket hỗ trợ cho server VietRealm. Bot sử dụng Python với thư viện discord.py, hỗ trợ slash commands và modals.

## Tính năng chính
- **4 loại ticket**: Hỗ trợ kỹ thuật, Hỗ trợ nạp thẻ, Realm Survival, Chủ đề khác
- **Form modal theo loại**:
  - Hỗ trợ kỹ thuật: Tên ingame + Vấn đề gặp phải
  - Hỗ trợ nạp thẻ: Tên ingame + Vấn đề gặp phải
  - Realm Survival: Chỉ tên ingame
  - Chủ đề khác: Không có form (tạo ticket trực tiếp)
- **Quản lý ticket**: Đóng (ai cũng bấm được), Nhận (chỉ role support), Hoàn thành (chỉ người nhận ticket)
- **Thống kê tự động**: Cập nhật tên voice channel hiển thị số liệu ticket
- **Phân quyền**: Chỉ role được set mới có thể nhận ticket
- **Tự động xóa**: Channel ticket xóa sau 5 giây khi đóng/hoàn thành

## Cấu trúc dự án
```
├── main.py              # Code chính của bot
├── config.json          # Lưu settings server (category, roles, channels)
├── active_tickets.json  # Lưu các ticket đang hoạt động
├── ticket_stats.json    # Lưu số liệu thống kê
├── .gitignore           # Git ignore file
└── replit.md            # File hướng dẫn này
```

## Các lệnh slash commands

### Nhóm lệnh /ticket
- `/ticket setup` - Thiết lập kênh ticket (Admin)
  - `category`: Category chứa các ticket
  - `support_role`: Role có quyền nhận ticket
- `/ticket addrole` - Thêm role support (Admin)
- `/ticket removerole` - Xóa role support (Admin)

### Nhóm lệnh /stats
- `/stats set` - Set channel thống kê (Admin)
  - `type`: Chọn loại (total/processing/completed)
  - `channel`: Voice channel hiển thị
- `/stats view` - Xem thống kê ticket
- `/stats remove` - Xóa channel thống kê (Admin)
- `/stats reset` - Reset số liệu về 0 (Admin)

## Hướng dẫn sử dụng
1. Thêm bot vào server Discord với các quyền: Manage Channels, Manage Roles, Send Messages, Embed Links
2. Tạo một Category để chứa ticket
3. (Tùy chọn) Tạo 3 Voice Channel để hiển thị thống kê
4. Sử dụng `/setticketchannel` trong kênh bạn muốn đặt menu tạo ticket
5. Người dùng chọn loại hỗ trợ từ dropdown menu
6. Staff có role được set sẽ thấy và có thể nhận ticket

## Định dạng tên channel ticket
- hotrokythuat-username
- napthe-username
- realmsurvival-username
- chudakhac-username

## Cấu hình
Bot sử dụng Discord Bot Token được lưu trong Replit Secrets với key `DISCORD_BOT_TOKEN`.

**Lưu ý**: Không cần bật Privileged Intents trong Discord Developer Portal.

## Recent Changes
- Dec 2024: Khởi tạo dự án với đầy đủ tính năng ticket system
