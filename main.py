import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import asyncio
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GIF_URL = "https://cdn.discordapp.com/avatars/1368258704855666788/2eac3d43fa7ce554a9ad69445b93d9b9.webp?size=1024"

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

CONFIG_FILE = 'config.json'
ACTIVE_TICKETS_FILE = 'active_tickets.json'
TICKET_STATS_FILE = 'ticket_stats.json'

def load_json(file_path: str, default_data: dict) -> dict:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return default_data

def save_json(file_path: str, data: dict) -> None:
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_config() -> dict:
    return load_json(CONFIG_FILE, {"guild_settings": {}})

def save_config(config: dict) -> None:
    save_json(CONFIG_FILE, config)

def load_active_tickets() -> dict:
    return load_json(ACTIVE_TICKETS_FILE, {})

def save_active_tickets(tickets: dict) -> None:
    save_json(ACTIVE_TICKETS_FILE, tickets)

def load_ticket_stats() -> dict:
    return load_json(TICKET_STATS_FILE, {
        "total_opened": 0,
        "total_completed": 0,
        "currently_processing": 0
    })

def save_ticket_stats(stats: dict) -> None:
    save_json(TICKET_STATS_FILE, stats)


class TicketTypeSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Hỗ trợ kỹ thuật",
                description="Tạo ticket hỗ trợ kỹ thuật",
                emoji="🔧",
                value="hotrokythuat"
            ),
            discord.SelectOption(
                label="Hỗ trợ nạp thẻ",
                description="Tạo ticket hỗ trợ nạp thẻ",
                emoji="💳",
                value="napthe"
            ),
            discord.SelectOption(
                label="Realm Survival",
                description="Tạo ticket realm survival",
                emoji="🎮",
                value="realmsurvival"
            ),
            discord.SelectOption(
                label="Chủ đề khác",
                description="Tạo ticket chủ đề khác",
                emoji="📝",
                value="chudekhac"
            )
        ]
        super().__init__(
            placeholder="Chọn loại hỗ trợ",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_type_select"
        )

    async def callback(self, interaction: discord.Interaction):
        ticket_type = self.values[0]

        try:
            if ticket_type == "hotrokythuat":
                modal = TechnicalSupportModal()
                await interaction.response.send_modal(modal)
            elif ticket_type == "napthe":
                modal = CardSupportModal()
                await interaction.response.send_modal(modal)
            elif ticket_type == "realmsurvival":
                modal = RealmSurvivalModal()
                await interaction.response.send_modal(modal)
            else:
                await create_ticket(interaction, ticket_type)
        except discord.errors.NotFound:
            pass
        except discord.errors.HTTPException:
            pass


class TechnicalSupportModal(discord.ui.Modal, title="Hỗ Trợ Kỹ Thuật"):
    ingame_name = discord.ui.TextInput(
        label="Tên nhân vật trong game",
        placeholder="Nhập tên ingame của bạn...",
        required=True,
        max_length=50
    )

    issue = discord.ui.TextInput(
        label="Vấn đề gặp phải",
        placeholder="Mô tả chi tiết vấn đề của bạn...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket(interaction, "hotrokythuat", self.ingame_name.value, self.issue.value)


class CardSupportModal(discord.ui.Modal, title="Hỗ Trợ Nạp Thẻ"):
    ingame_name = discord.ui.TextInput(
        label="Tên nhân vật trong game",
        placeholder="Nhập tên ingame của bạn...",
        required=True,
        max_length=50
    )

    issue = discord.ui.TextInput(
        label="Vấn đề gặp phải",
        placeholder="Mô tả chi tiết vấn đề nạp thẻ của bạn...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket(interaction, "napthe", self.ingame_name.value, self.issue.value)


class RealmSurvivalModal(discord.ui.Modal, title="Realm Survival"):
    ingame_name = discord.ui.TextInput(
        label="Tên nhân vật trong game",
        placeholder="Nhập tên ingame của bạn...",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket(interaction, "realmsurvival", self.ingame_name.value)


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketTypeSelect())


class TicketControlView(discord.ui.View):
    def __init__(self, ticket_id: str):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id

    @discord.ui.button(label="Đóng Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket", emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_message("🔒 Ticket sẽ được đóng trong 5 giây...", ephemeral=False)
        except discord.errors.NotFound:
            return
        except discord.errors.HTTPException:
            return
        
        await asyncio.sleep(5)

        active_tickets = load_active_tickets()
        stats = load_ticket_stats()

        channel = interaction.channel
        if channel is None:
            return

        ticket_id = str(channel.id)

        if ticket_id in active_tickets:
            del active_tickets[ticket_id]
            save_active_tickets(active_tickets)
            stats["currently_processing"] = max(0, stats.get("currently_processing", 0) - 1)
            save_ticket_stats(stats)

        try:
            if isinstance(channel, discord.TextChannel):
                await channel.delete()
        except discord.HTTPException:
            pass

    @discord.ui.button(label="Nhận Ticket", style=discord.ButtonStyle.primary, custom_id="claim_ticket", emoji="✋")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=False)
        except discord.errors.NotFound:
            return
        except discord.errors.HTTPException:
            return
            
        config = load_config()
        active_tickets = load_active_tickets()

        if not interaction.guild:
            await interaction.followup.send("❌ Lỗi: Không tìm thấy server!", ephemeral=True)
            return

        channel = interaction.channel
        if channel is None:
            await interaction.followup.send("❌ Lỗi: Không tìm thấy channel!", ephemeral=True)
            return

        guild_id = str(interaction.guild.id)

        if guild_id not in config.get("guild_settings", {}):
            await interaction.followup.send("❌ Chưa thiết lập hệ thống ticket!", ephemeral=True)
            return

        settings = config["guild_settings"][guild_id]
        support_roles = settings.get("support_roles", [])

        member = interaction.user
        if isinstance(member, discord.Member):
            user_role_ids = [str(role.id) for role in member.roles]
            has_permission = any(role_id in user_role_ids for role_id in support_roles)
        else:
            has_permission = False

        if not has_permission:
            await interaction.followup.send("❌ Bạn không có quyền nhận ticket!", ephemeral=True)
            return

        ticket_id = str(channel.id)

        if ticket_id not in active_tickets:
            await interaction.followup.send("❌ Không tìm thấy thông tin ticket!", ephemeral=True)
            return

        if active_tickets[ticket_id].get("claimed_by"):
            claimer_id = active_tickets[ticket_id]["claimed_by"]
            await interaction.followup.send(f"❌ Ticket này đã được nhận bởi <@{claimer_id}>!", ephemeral=True)
            return

        active_tickets[ticket_id]["claimed_by"] = str(interaction.user.id)
        save_active_tickets(active_tickets)

        await interaction.followup.send(f"✅ **Ticket Đã Được Nhận**\nStaff {interaction.user.mention} đã nhận ticket này và sẽ hỗ trợ bạn.")

    @discord.ui.button(label="Hoàn Thành", style=discord.ButtonStyle.success, custom_id="complete_ticket", emoji="✅")
    async def complete_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=False)
        except discord.errors.NotFound:
            return
        except discord.errors.HTTPException:
            return
            
        active_tickets = load_active_tickets()
        stats = load_ticket_stats()

        channel = interaction.channel
        if channel is None:
            await interaction.followup.send("❌ Lỗi: Không tìm thấy channel!", ephemeral=True)
            return

        ticket_id = str(channel.id)

        if ticket_id not in active_tickets:
            await interaction.followup.send("❌ Không tìm thấy thông tin ticket!", ephemeral=True)
            return

        ticket_data = active_tickets[ticket_id]
        claimed_by = ticket_data.get("claimed_by")

        if not claimed_by:
            await interaction.followup.send("❌ Ticket này chưa được nhận!", ephemeral=True)
            return

        if claimed_by != str(interaction.user.id):
            await interaction.followup.send("❌ Chỉ người nhận ticket mới có thể hoàn thành!", ephemeral=True)
            return

        stats["total_completed"] = stats.get("total_completed", 0) + 1
        stats["currently_processing"] = max(0, stats.get("currently_processing", 0) - 1)
        save_ticket_stats(stats)

        del active_tickets[ticket_id]
        save_active_tickets(active_tickets)

        await interaction.followup.send("✅ Ticket đã hoàn thành! Channel sẽ được xóa trong 5 giây...", ephemeral=False)
        await asyncio.sleep(5)

        try:
            if isinstance(channel, discord.TextChannel):
                await channel.delete()
        except discord.HTTPException:
            pass


async def create_ticket(
    interaction: discord.Interaction, 
    ticket_type: str, 
    ingame_name: Optional[str] = None, 
    issue: Optional[str] = None
):
    await interaction.response.defer(ephemeral=True)

    config = load_config()
    active_tickets = load_active_tickets()
    stats = load_ticket_stats()

    if not interaction.guild:
        await interaction.followup.send("❌ Lệnh này chỉ hoạt động trong server!", ephemeral=True)
        return

    guild_id = str(interaction.guild.id)

    if guild_id not in config.get("guild_settings", {}):
        await interaction.followup.send("❌ Chưa thiết lập hệ thống ticket! Vui lòng yêu cầu admin sử dụng /ticket setup", ephemeral=True)
        return

    settings = config["guild_settings"][guild_id]
    category_id = settings.get("category_id")

    if not category_id:
        await interaction.followup.send("❌ Chưa thiết lập category cho ticket!", ephemeral=True)
        return

    category = interaction.guild.get_channel(int(category_id))
    if not category or not isinstance(category, discord.CategoryChannel):
        await interaction.followup.send("❌ Không tìm thấy category ticket!", ephemeral=True)
        return

    username = interaction.user.name.lower().replace(" ", "-")[:20]
    channel_name = f"{ticket_type}-{username}"

    overwrites: dict = {
        interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_channels=True)
    }

    if isinstance(interaction.user, discord.Member):
        overwrites[interaction.user] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

    support_roles = settings.get("support_roles", [])
    for role_id in support_roles:
        role = interaction.guild.get_role(int(role_id))
        if role:
            overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

    ticket_channel = await category.create_text_channel(name=channel_name, overwrites=overwrites)

    ticket_id = str(ticket_channel.id)
    active_tickets[ticket_id] = {
        "user_id": str(interaction.user.id),
        "ticket_type": ticket_type,
        "ingame_name": ingame_name,
        "issue": issue,
        "claimed_by": None
    }
    save_active_tickets(active_tickets)

    stats["total_opened"] = stats.get("total_opened", 0) + 1
    stats["currently_processing"] = stats.get("currently_processing", 0) + 1
    save_ticket_stats(stats)

    type_names = {
        "hotrokythuat": "🔧 Hỗ Trợ Kỹ Thuật",
        "napthe": "💳 Hỗ Trợ Nạp Thẻ",
        "realmsurvival": "🎮 Realm Survival",
        "chudekhac": "📝 Chủ Đề Khác"
    }

    role_mentions = []
    for role_id in support_roles:
        role = interaction.guild.get_role(int(role_id))
        if role:
            role_mentions.append(role.mention)

    ticket_content = f"**{type_names.get(ticket_type, 'Ticket')}**\n\n"
    ticket_content += f"Xin chào {interaction.user.mention}!\n"
    ticket_content += f"Ticket của bạn đã được tạo. Vui lòng chờ staff hỗ trợ.\n\n"

    info_parts = []
    if ingame_name:
        info_parts.append(f"Tên Ingame: {ingame_name}")
    if issue:
        info_parts.append(f"Vấn Đề: {issue}")
    info_parts.append(f"Ticket ID: {ticket_id}")

    ticket_content += "```\nThông tin:\n" + "\n".join(info_parts) + "\n```"

    if role_mentions:
        ticket_content += f"\n{' '.join(role_mentions)}"

    view = TicketControlView(ticket_id)
    await ticket_channel.send(ticket_content, view=view)

    await interaction.followup.send(f"✅ Ticket đã được tạo: {ticket_channel.mention}", ephemeral=True)


@bot.event
async def on_ready():
    print(f'{bot.user} đã đăng nhập!')

    bot.add_view(TicketView())

    active_tickets = load_active_tickets()
    for ticket_id in active_tickets:
        bot.add_view(TicketControlView(ticket_id))

    bot.loop.create_task(update_stats_embeds())
    print('Đã khởi động task cập nhật thống kê.')

    try:
        synced = await bot.tree.sync()
        print(f'Đã đồng bộ {len(synced)} lệnh.')
    except Exception as e:
        print(f'Lỗi khi đồng bộ lệnh: {e}')


ticket_group = app_commands.Group(name="ticket", description="Quản lý hệ thống ticket")

@ticket_group.command(name="setup", description="Thiết lập kênh tạo ticket")
@app_commands.describe(
    category="Category để chứa các ticket",
    support_role="Role có quyền nhận ticket"
)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def ticket_setup(
    interaction: discord.Interaction,
    category: discord.CategoryChannel,
    support_role: discord.Role
):
    if not interaction.guild:
        await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong server!", ephemeral=True)
        return

    channel = interaction.channel
    if channel is None or not isinstance(channel, discord.TextChannel):
        await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong text channel!", ephemeral=True)
        return

    config = load_config()
    guild_id = str(interaction.guild.id)

    if guild_id not in config["guild_settings"]:
        config["guild_settings"][guild_id] = {}

    config["guild_settings"][guild_id]["category_id"] = str(category.id)
    config["guild_settings"][guild_id]["ticket_channel_id"] = str(channel.id)

    if "support_roles" not in config["guild_settings"][guild_id]:
        config["guild_settings"][guild_id]["support_roles"] = []

    if str(support_role.id) not in config["guild_settings"][guild_id]["support_roles"]:
        config["guild_settings"][guild_id]["support_roles"].append(str(support_role.id))

    save_config(config)

    embed = discord.Embed(
        title="🎟️ TẠO PHIẾU HỖ TRỢ",
        description="Khi tạo ticket, hãy đảm bảo thể hiện đầy đủ thông tin bạn cần được hỗ trợ, và chờ admin - staff hỗ trợ bạn.\n\n**Khung giờ hỗ trợ:** 24/7\nVIETREALM TICKET | STAFF VIETREALM",
        color=discord.Color.gold()
    )

    embed.set_image(url=GIF_URL)

    view = TicketView()

    await channel.send(embed=embed, view=view)

    await interaction.response.send_message("✅ Đã thiết lập kênh ticket thành công!", ephemeral=True)


@ticket_group.command(name="addrole", description="Thêm role có quyền nhận ticket")
@app_commands.describe(role="Role cần thêm")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def ticket_addrole(interaction: discord.Interaction, role: discord.Role):
    if not interaction.guild:
        await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong server!", ephemeral=True)
        return

    config = load_config()
    guild_id = str(interaction.guild.id)

    if guild_id not in config.get("guild_settings", {}):
        await interaction.response.send_message("❌ Chưa thiết lập hệ thống ticket! Dùng `/ticket setup` trước.", ephemeral=True)
        return

    if "support_roles" not in config["guild_settings"][guild_id]:
        config["guild_settings"][guild_id]["support_roles"] = []

    if str(role.id) in config["guild_settings"][guild_id]["support_roles"]:
        await interaction.response.send_message(f"❌ Role {role.mention} đã có trong danh sách!", ephemeral=True)
        return

    config["guild_settings"][guild_id]["support_roles"].append(str(role.id))
    save_config(config)

    await interaction.response.send_message(f"✅ Đã thêm role {role.mention} vào danh sách support!", ephemeral=True)


@ticket_group.command(name="removerole", description="Xóa role khỏi danh sách nhận ticket")
@app_commands.describe(role="Role cần xóa")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def ticket_removerole(interaction: discord.Interaction, role: discord.Role):
    if not interaction.guild:
        await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong server!", ephemeral=True)
        return

    config = load_config()
    guild_id = str(interaction.guild.id)

    if guild_id not in config.get("guild_settings", {}):
        await interaction.response.send_message("❌ Chưa thiết lập hệ thống ticket!", ephemeral=True)
        return

    if str(role.id) not in config["guild_settings"][guild_id].get("support_roles", []):
        await interaction.response.send_message(f"❌ Role {role.mention} không có trong danh sách!", ephemeral=True)
        return

    config["guild_settings"][guild_id]["support_roles"].remove(str(role.id))
    save_config(config)

    await interaction.response.send_message(f"✅ Đã xóa role {role.mention} khỏi danh sách support!", ephemeral=True)

bot.tree.add_command(ticket_group)


STATS_MESSAGES_FILE = 'stats_messages.json'

def load_stats_messages() -> dict:
    return load_json(STATS_MESSAGES_FILE, {})

def save_stats_messages(data: dict) -> None:
    save_json(STATS_MESSAGES_FILE, data)

def create_stats_embed() -> discord.Embed:
    stats = load_ticket_stats()
    from datetime import datetime
    
    embed = discord.Embed(
        title="📊 THỐNG KÊ TICKET",
        description="Thống kê hệ thống ticket VIETREALM",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🎫 Tổng Ticket Đã Mở",
        value=f"```{stats.get('total_opened', 0)}```",
        inline=True
    )
    
    embed.add_field(
        name="⏳ Đang Xử Lý",
        value=f"```{stats.get('currently_processing', 0)}```",
        inline=True
    )
    
    embed.add_field(
        name="✅ Đã Hoàn Thành",
        value=f"```{stats.get('total_completed', 0)}```",
        inline=True
    )
    
    embed.set_footer(text=f"Cập nhật lúc: {datetime.now().strftime('%H:%M:%S %d/%m/%Y')} | Tự động cập nhật mỗi 60s")
    
    return embed

async def update_stats_embeds():
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            stats_messages = load_stats_messages()
            
            for guild_id, data in list(stats_messages.items()):
                try:
                    guild = bot.get_guild(int(guild_id))
                    if not guild:
                        continue
                    
                    channel = guild.get_channel(int(data.get("channel_id", 0)))
                    if not channel or not isinstance(channel, discord.TextChannel):
                        continue
                    
                    try:
                        message = await channel.fetch_message(int(data.get("message_id", 0)))
                        embed = create_stats_embed()
                        await message.edit(embed=embed)
                    except discord.NotFound:
                        del stats_messages[guild_id]
                        save_stats_messages(stats_messages)
                    except discord.HTTPException:
                        pass
                        
                except Exception:
                    pass
                    
        except Exception:
            pass
        
        await asyncio.sleep(60)

@bot.tree.command(name="stats", description="Hiển thị thống kê ticket (tự động cập nhật mỗi 60s)")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def stats_command(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong server!", ephemeral=True)
        return
    
    channel = interaction.channel
    if not isinstance(channel, discord.TextChannel):
        await interaction.response.send_message("❌ Lệnh này chỉ hoạt động trong text channel!", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    stats_messages = load_stats_messages()
    guild_id = str(interaction.guild.id)
    
    if guild_id in stats_messages:
        try:
            old_channel = interaction.guild.get_channel(int(stats_messages[guild_id].get("channel_id", 0)))
            if old_channel and isinstance(old_channel, discord.TextChannel):
                try:
                    old_message = await old_channel.fetch_message(int(stats_messages[guild_id].get("message_id", 0)))
                    await old_message.delete()
                except (discord.NotFound, discord.HTTPException):
                    pass
        except Exception:
            pass
    
    embed = create_stats_embed()
    message = await channel.send(embed=embed)
    
    stats_messages[guild_id] = {
        "channel_id": str(channel.id),
        "message_id": str(message.id)
    }
    save_stats_messages(stats_messages)
    
    await interaction.followup.send("✅ Đã tạo bảng thống kê! Embed sẽ tự động cập nhật mỗi 60 giây.", ephemeral=True)


@bot.tree.command(name="help", description="Hướng dẫn sử dụng bot ticket")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📚 HƯỚNG DẪN SỬ DỤNG VIETREALM TICKET BOT",
        description="Bot hỗ trợ quản lý ticket cho server VIETREALM",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="🚀 THIẾT LẬP BAN ĐẦU",
        value=(
            "```\n"
            "1. Tạo một category để chứa các ticket\n"
            "2. Tạo một text channel để đặt bảng tạo ticket\n"
            "3. Tạo role cho staff hỗ trợ\n"
            "4. Chạy lệnh /ticket setup trong channel đó\n"
            "```"
        ),
        inline=False
    )

    embed.add_field(
        name="🎟️ LỆNH TICKET",
        value=(
            "```\n"
            "/ticket setup [category] [role]\n"
            "  → Thiết lập hệ thống ticket\n"
            "  → category: Category chứa ticket\n"
            "  → role: Role staff hỗ trợ\n\n"
            "/ticket addrole [role]\n"
            "  → Thêm role có quyền nhận ticket\n\n"
            "/ticket removerole [role]\n"
            "  → Xóa role khỏi danh sách hỗ trợ\n\n"
            "/ticket listroles\n"
            "  → Xem danh sách role hỗ trợ\n"
            "```"
        ),
        inline=False
    )

    embed.add_field(
        name="📊 LỆNH THỐNG KÊ",
        value=(
            "```\n"
            "/stats\n"
            "  → Hiển thị bảng thống kê ticket\n"
            "  → Tự động cập nhật mỗi 60 giây\n"
            "```"
        ),
        inline=False
    )

    embed.add_field(
        name="🔧 LOẠI TICKET",
        value=(
            "```\n"
            "🔧 Hỗ Trợ Kỹ Thuật\n"
            "   → Các vấn đề kỹ thuật, lỗi game\n\n"
            "💳 Hỗ Trợ Nạp Thẻ\n"
            "   → Vấn đề về nạp thẻ, thanh toán\n\n"
            "🎮 Realm Survival\n"
            "   → Hỗ trợ liên quan Realm Survival\n\n"
            "📝 Chủ Đề Khác\n"
            "   → Các vấn đề khác\n"
            "```"
        ),
        inline=False
    )

    embed.add_field(
        name="👥 QUYỀN HẠN",
        value=(
            "```\n"
            "• Admin: Toàn quyền quản lý bot\n"
            "• Staff (Support Role): Nhận và xử lý ticket\n"
            "• Member: Tạo ticket hỗ trợ\n"
            "```"
        ),
        inline=False
    )

    embed.add_field(
        name="📝 CÁCH SỬ DỤNG TICKET",
        value=(
            "```\n"
            "Người dùng:\n"
            "1. Bấm nút loại ticket phù hợp\n"
            "2. Điền tên ingame và mô tả vấn đề\n"
            "3. Chờ staff hỗ trợ\n\n"
            "Staff:\n"
            "1. Bấm 'Nhận Ticket' để claim\n"
            "2. Hỗ trợ người dùng trong channel\n"
            "3. Bấm 'Hoàn Thành' khi xong\n"
            "4. Xác nhận đóng ticket\n"
            "```"
        ),
        inline=False
    )

    embed.set_footer(text="VIETREALM Ticket Bot | Liên hệ Admin nếu cần hỗ trợ thêm")

    await interaction.response.send_message(embed=embed, ephemeral=True)


if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Lỗi: Không tìm thấy DISCORD_BOT_TOKEN!")
