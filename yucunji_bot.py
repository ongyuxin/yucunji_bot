from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import logging

# 初始化日志
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 记录用户余额的字典
balance = {}

# 管理员列表 (这里可以通过 chat 管理员列表动态获取)
admins = []

# 异步启动函数
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('欢迎使用,我是预存机\n使用前请将我设置群的管理员！\n通过指令让我读取群管理后才能完整使用\n\n以下为预存机指令格式\n读取管理员“/refresh_admins”\n查预存“/my_balance”\n用预存“/deduct_balance 金额”\n加预存“/add_balance @用户 金额”\n仅管理员拥有加预存权限')

# 初始化余额
def init_balance(username):
    if username not in balance:
        balance[username] = 0

# 检查是否管理员
def is_admin(user_id):
    return user_id in admins

# 加余额
async def add_balance(update: Update, context: CallbackContext):
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("只有管理员可以加款")
        return
    
    if len(context.args) != 2 or not context.args[1].replace('.', '', 1).isdigit():
        await update.message.reply_text("请使用正确的格式：/add_balance @用户名 金额")
        return

    username = context.args[0][1:]  # 去掉@符号
    amount = float(context.args[1].replace('#', ''))

    init_balance(username)
    balance[username] += amount

    await update.message.reply_text(f"已为 @{username} 加款\n加款金额：{amount:.2f}r\n加款后余额：{balance[username]:.2f}r")

# 扣余额
async def deduct_balance(update: Update, context: CallbackContext):
    username = update.message.from_user.username

    if len(context.args) != 1 or not context.args[0].replace('.', '', 1).isdigit():
        await update.message.reply_text("请使用正确的格式：/deduct_balance 金额")
        return

    amount = float(context.args[0].replace('#', ''))

    init_balance(username)
    
    if amount <= balance[username]:
        balance[username] -= amount
        await update.message.reply_text(f"@{username}\n您的原余额：{balance[username] + amount:.2f}r\n即将减少：{amount:.2f}r\n您的余额剩余：{balance[username]:.2f}r")
    else:
        await update.message.reply_text(f"@{username}\n您的余额：{balance[username]:.2f}r\n不足以支持减少本次金额")

# 查询余额
async def my_balance(update: Update, context: CallbackContext):
    username = update.message.from_user.username
    init_balance(username)
    await update.message.reply_text(f"@{username}\n您的余额：{balance[username]:.2f}r")

# 管理员权限检测
async def refresh_admins(update: Update, context: CallbackContext):
    global admins
    chat_id = update.message.chat_id
    admins = [admin.user.id for admin in await context.bot.get_chat_administrators(chat_id)]
    await update.message.reply_text(f"管理员已刷新：{', '.join([str(admin) for admin in admins])}")

# 错误处理器
async def error_handler(update: Update, context: CallbackContext) -> None:
    logging.error(msg="Exception while handling an update:", exc_info=context.error)
    if update:
        await update.message.reply_text('抱歉，发生了一个错误！')

def main() -> None:
    # 使用你自己的Token
    application = Application.builder().token("7285164524:AAHEXp8ZQxw-WW7DtNk6TMy_I8P86n8f5u4").build()

    # 处理命令
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_balance", add_balance))
    application.add_handler(CommandHandler("deduct_balance", deduct_balance))
    application.add_handler(CommandHandler("my_balance", my_balance))

    # 刷新管理员
    application.add_handler(CommandHandler("refresh_admins", refresh_admins))

    # 添加错误处理器
    application.add_error_handler(error_handler)

    # 启动 bot
    application.run_polling()

if __name__ == '__main__':
    main()
