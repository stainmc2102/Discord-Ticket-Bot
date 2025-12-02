# DISCORD Ticket Bot

Bot Discord hỗ trợ quản lý hệ thống ticket cho server . Bot sử dụng Slash Commands và có giao diện trực quan với các nút bấm, dropdown menu.

## Tính Năng

### Hệ Thống Ticket
- **4 loại ticket hỗ trợ:**
  - Hỗ trợ kỹ thuật - Các vấn đề kỹ thuật, lỗi game
  - Hỗ trợ nạp thẻ - Vấn đề về nạp thẻ, thanh toán
  - Realm Survival - Hỗ trợ liên quan Realm Survival
  - Chủ đề khác - Các vấn đề khác

- **Form thông tin:** Mỗi loại ticket có form riêng để thu thập thông tin (tên ingame, mô tả vấn đề)
- **Tự động tạo channel:** Mỗi ticket được tạo trong channel riêng biệt
- **Phân quyền tự động:** Chỉ người tạo ticket và staff mới thấy được channel
- **Ping staff:** Tự động tag role support khi có ticket mới

### Quản Lý Ticket (Dành cho Staff)
- **Nhận Ticket:** Staff có thể nhận ticket để xử lý
- **Hoàn Thành:** Đánh dấu ticket đã xử lý xong và tự động xóa channel
- **Đóng Ticket:** Đóng ticket mà không cần hoàn thành

### Thống Kê
- **Embed thống kê (auto-update):** Bot có thể tạo một embed hiển thị các chỉ số chính và tự động cập nhật nội dung của message đó mỗi 60 giây. Embed được lưu (message_id + channel_id) trong `stats_messages.json` để bot có thể chỉnh sửa lại message khi thay đổi số liệu.
- **Tên Voice Channel hiển thị:** Ngoài embed, bot có thể cập nhật tên của các voice channel để hiển thị các chỉ số trực tiếp (ví dụ: `🎫 Tổng Ticket: 12`). Hệ thống hỗ trợ 3 loại kênh:
   - `total_opened` (Tổng ticket đã mở)
   - `currently_processing` (Đang xử lý)
   - `total_completed` (Đã hoàn thành)
- **Tự động cập nhật:** Cả embed và tên voice channel được cập nhật tự động mỗi 60 giây bởi một task nền.
- **Dữ liệu thống kê:** Các số liệu được lưu trong `ticket_stats.json` với các khóa `total_opened`, `currently_processing`, `total_completed`.

### Quản Lý Role Support
- Thêm/xóa nhiều role có quyền nhận ticket
- Linh hoạt trong việc phân quyền

## Yêu Cầu

- Python 3.11+
- discord.py 2.0+
- python-dotenv

## Cài Đặt

### Bước 1: Clone Repository

```bash
git clone https://github.com/stainmc2102/Discord-Ticket-Bot
cd vietrealm-ticket-bot
```

### Bước 2: Cài Đặt Dependencies

```bash
pip install discord.py python-dotenv
```

### Bước 3: Tạo Bot Discord

1. Truy cập [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** và đặt tên cho bot
3. Vào tab **"Bot"** và click **"Add Bot"**
4. Bật các **Privileged Gateway Intents:**
   - SERVER MEMBERS INTENT
   - MESSAGE CONTENT INTENT (tùy chọn)
5. Copy **Token** của bot

### Bước 4: Cấu Hình Token

Tạo file `.env` trong thư mục gốc:

```env
DISCORD_BOT_TOKEN=your_bot_token_here
```

### Bước 5: Mời Bot Vào Server

1. Vào tab **"OAuth2"** > **"URL Generator"**
2. Chọn scopes: `bot`, `applications.commands`
3. Chọn permissions:
   - Manage Channels
   - Send Messages
   - Embed Links
   - Read Message History
   - Use Slash Commands
   - Manage Messages
4. Copy URL và mở trong trình duyệt để mời bot

### Bước 6: Chạy Bot

```bash
python main.py
```

## Hướng Dẫn Sử Dụng

### Thiết Lập Ban Đầu (Admin)

1. **Tạo Category:** Tạo một category để chứa các ticket channel
2. **Tạo Text Channel:** Tạo channel để đặt bảng tạo ticket
3. **Tạo Role Support:** Tạo role cho staff hỗ trợ
4. **Chạy lệnh setup:** Trong channel vừa tạo, chạy:
   ```
   /ticket setup [category] [support_role]
   ```

### Các Lệnh Slash Commands

#### Lệnh Ticket (Chỉ Admin)

| Lệnh | Mô tả |
|------|-------|
| `/ticket setup [category] [role]` | Thiết lập hệ thống ticket |
| `/ticket addrole [role]` | Thêm role có quyền nhận ticket |
| `/ticket removerole [role]` | Xóa role khỏi danh sách support |


#### Lệnh Thống Kê (Chỉ Admin)

| Lệnh | Mô tả |
|------|-------|
| `/stats embed` | Tạo một embed thống kê trong channel hiện tại. Bot sẽ lưu message và tự động cập nhật nội dung embed mỗi 60s. |
| `/stats set [type] [voice_channel]` | Thiết lập voice channel để bot cập nhật tên hiển thị cho loại thống kê tương ứng. `type` = `total` / `processing` / `completed`. |
| `/stats remove [type]` | Xóa thiết lập voice channel cho loại thống kê đã chọn. |
| `/stats view` | Hiển thị số liệu thống kê hiện tại (ephemeral). |

#### Lệnh Khác

| Lệnh | Mô tả |
|------|-------|
| `/help` | Xem hướng dẫn sử dụng bot |

### Cách Sử Dụng (Người Dùng)

1. Vào channel ticket đã được thiết lập
2. Chọn loại hỗ trợ từ dropdown menu
3. Điền form thông tin (tên ingame, mô tả vấn đề)
4. Chờ staff hỗ trợ trong channel ticket được tạo

### Cách Sử Dụng (Staff)

1. Khi có ticket mới, staff sẽ được ping
2. Vào channel ticket và bấm **"Nhận Ticket"** để claim
3. Hỗ trợ người dùng trong channel
4. Khi xong, bấm **"Hoàn Thành"** để đóng ticket
5. Hoặc bấm **"Đóng Ticket"** nếu cần đóng ngay

## Cấu Trúc File

```
discord-ticket-bot/
├── main.py                 # File chính của bot
├── .env                    # Chứa token bot (không commit)
├── config.json             # Cấu hình server (tự động tạo)
├── active_tickets.json     # Danh sách ticket đang mở (tự động tạo)
├── ticket_stats.json       # Thống kê ticket (tự động tạo)
├── stats_messages.json     # Lưu message thống kê (tự động tạo)
└── README.md               # File này
```

## Phân Quyền

| Role | Quyền hạn |
|------|-----------|
| **Admin** | Toàn quyền quản lý bot, thiết lập hệ thống |
| **Staff (Support Role)** | Nhận và xử lý ticket |
| **Member** | Tạo ticket hỗ trợ |

## Xử Lý Sự Cố

### Bot không phản hồi lệnh slash
- Đảm bảo bot có quyền `Use Slash Commands`
- Đợi vài phút để Discord đồng bộ lệnh
- Thử kick và mời lại bot

### Không thấy dropdown menu
- Đảm bảo đã chạy `/ticket setup` trước
- Kiểm tra bot có quyền gửi tin nhắn trong channel

### Ticket channel không được tạo
- Kiểm tra bot có quyền `Manage Channels`
- Đảm bảo category vẫn tồn tại
- Kiểm tra giới hạn channel của server

### Thống kê không cập nhật
- Đảm bảo bot đang chạy
- Kiểm tra message thống kê chưa bị xóa
- Chạy lại `/stats` để tạo message mới

## Đóng Góp

Mọi đóng góp đều được chào đón! Vui lòng tạo issue hoặc pull request.

## License

MIT License

## Liên Hệ

- Discord: @stainmc2102
- Developer: Stain
