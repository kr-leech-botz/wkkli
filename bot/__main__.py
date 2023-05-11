from signal import signal, SIGINT
import pytz
from os import path as ospath, remove as osremove, execl as osexecl
from subprocess import run as srun, check_output
from psutil import (boot_time, cpu_count, cpu_percent, cpu_freq, disk_usage,
                    net_io_counters, swap_memory, virtual_memory)
from time import time
from sys import executable
from telegram.ext import CommandHandler
from telegram import ParseMode


from bot import bot, dispatcher, updater, botStartTime, IGNORE_PENDING_REQUESTS, SET_BOT_COMMANDS, TIMEZONE, IMAGE_URL, LOGGER, Interval, INCOMPLETE_TASK_NOTIFIER, DB_URI, alive, app, main_loop, AUTHORIZED_CHATS, app_session, USER_SESSION_STRING, \
    OWNER_ID, SUDO_USERS, START_BTN1_NAME, START_BTN1_URL, START_BTN2_NAME, START_BTN2_URL
from .helper.ext_utils.fs_utils import start_cleanup, clean_all, exit_clean_up
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.ext_utils.db_handler import DbManger
from .helper.telegram_helper.bot_commands import BotCommands
from .helper.telegram_helper.message_utils import sendMessage, sendMarkup, editMessage, sendLogFile
from .helper.telegram_helper.filters import CustomFilters
from .helper.telegram_helper.button_build import ButtonMaker

from .modules import authorize, list, cancel_mirror, mirror_status, mirror_leech, clone, ytdlp, shell, eval, delete, count, leech_settings, search, rss, bt_select, sleep, addons
from datetime import datetime

IMAGE_X = f"{IMAGE_URL}"
now=datetime.now(pytz.timezone(f'{TIMEZONE}'))

def progress_bar(percentage):
    p_used = '⬢'
    p_total = '⬡'
    if isinstance(percentage, str):
        return 'NaN'
    try:
        percentage=int(percentage)
    except:
        percentage = 0
    return ''.join(
        p_used if i <= percentage // 10 else p_total for i in range(1, 11)
    )

def stats(update, context):
    if ospath.exists('.git'):
        last_commit = check_output(["git log -1 --date=short --pretty=format:'%cr \n<b>Version: </b> %cd'"], shell=True).decode()
    else:
        last_commit = 'No UPSTREAM_REPO'
    sysTime = get_readable_time(time() - boot_time())
    botTime = get_readable_time(time() - botStartTime)
    total, used, free, disk= disk_usage('/')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(net_io_counters().bytes_sent)
    recv = get_readable_file_size(net_io_counters().bytes_recv)
    cpuUsage = cpu_percent(interval=1)
    v_core = cpu_count(logical=True) - cpu_count(logical=False)
    memory = virtual_memory()
    swap = swap_memory()
    mem_p = memory.percent
    stats = f'<b><i><u>Bot Statistics</u></i></b>\n\n'\
            f'<code>CPU  :{progress_bar(cpuUsage)} {cpuUsage}%</code>\n' \
            f'<code>RAM  :{progress_bar(mem_p)} {mem_p}%</code>\n' \
            f'<code>SWAP :{progress_bar(swap.percent)} {swap.percent}%</code>\n' \
            f'<code>DISK :{progress_bar(disk)} {disk}%</code>\n\n' \
            f'<b>Updated:</b> {last_commit}\n' \
            f'<b>SYS Uptime:</b> <code>{sysTime}</code>\n' \
            f'<b>BOT Uptime:</b> <code>{botTime}</code>\n\n' \
            f'<b>CPU Total Core(s):</b> <code>{cpu_count(logical=True)}</code>\n' \
            f'<b>P-Core(s):</b> <code>{cpu_count(logical=False)}</code> | <b>V-Core(s):</b> <code>{v_core}</code>\n' \
            f'<b>Frequency:</b> <code>{cpu_freq(percpu=False).current} Mhz</code>\n\n' \
            f'<b>RAM In Use:</b> <code>{get_readable_file_size(memory.used)}</code> [{mem_p}%]\n' \
            f'<b>Total:</b> <code>{get_readable_file_size(memory.total)}</code> | <b>Free:</b> <code>{get_readable_file_size(memory.available)}</code>\n\n' \
            f'<b>SWAP In Use:</b> <code>{get_readable_file_size(swap.used)}</code> [{swap.percent}%]\n' \
            f'<b>Allocated</b> <code>{get_readable_file_size(swap.total)}</code> | <b>Free:</b> <code>{get_readable_file_size(swap.free)}</code>\n\n' \
            f'<b>Drive In Use:</b> <code>{used}</code> [{disk}%]\n' \
            f'<b>Total:</b> <code>{total}</code> | <b>Free:</b> <code>{free}</code>\n' \
            f'<b>T-UL:</b> <code>{sent}</code> | <b>T-DL:</b> <code>{recv}</code>\n'
    update.effective_message.reply_photo(IMAGE_X, stats, parse_mode=ParseMode.HTML)


def start(update, context):
    buttons = ButtonMaker()
    buttons.buildbutton("Kristy X Leech", "https://t.me/KristyXLeech")
    reply_markup = buttons.build_menu(1)
    currentTime = get_readable_time(time() - botStartTime)
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        start_string = f'''
<b>XV BoT is Working.\n\nStill {currentTime}\n\n#BaashaXclouD</b>
'''
        sendMarkup(start_string, context.bot, update.message, reply_markup)
    else:
        msg1 = f"<b>Bot Started In PM\nNow I send Your Future Updates To My Leech Dump & Here Too\n\nPowerded By <a href='https://telegram.dog/Abt_Kristy'>╰ Kʀɪꜱᴛʏ கிறிஸ்டி ╮</a> | <a href='https://telegram.dog/TeamLCU'>TeamLCU</a></b>"
        update.effective_message.reply_photo(IMAGE_X, msg1, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

def restart(update, context):
    restart_message = sendMessage("Restarting...", context.bot, update.message)
    if Interval:
        Interval[0].cancel()
        Interval.clear()
    alive.kill()
    clean_all()
    srun(["pkill", "-9", "-f", "gunicorn|chrome|firefox|megasdkrest"])
    srun(["python3", "update.py"])
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    osexecl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update.message)
    end_time = int(round(time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.bot, update.message)


help_string_telegraph = f'''
NOTE: Try each command without any perfix to see more detalis.<br><br>
<b>Mirror Related Commands:</b><br>
<b>/{BotCommands.MirrorCommand}</b> : Start mirroring to Google Drive.<br><br>
<b>/{BotCommands.ZipMirrorCommand}</b>: Start mirroring and upload the file/folder compressed with zip extension.<br><br>
<b>/{BotCommands.UnzipMirrorCommand}</b>: Start mirroring and upload the file/folder extracted from any archive extension.<br><br>
<b>/{BotCommands.QbMirrorCommand}</b>: Start Mirroring to Google Drive using qBittorrent.<br><br>
<b>/{BotCommands.QbZipMirrorCommand}</b> : Start mirroring using qBittorrent and upload the file/folder compressed with zip extension.<br><br>
<b>/{BotCommands.QbUnzipMirrorCommand}</b>: Start mirroring using qBittorrent and upload the file/folder extracted from any archive extension.<br><br>
<b>/{BotCommands.YtdlCommand}</b>: Mirror yt-dlp supported link.<br><br>
<b>/{BotCommands.YtdlZipCommand}</b>: Mirror yt-dlp supported link as zip.<br><br>
<b>Leech Related Commands:</b><br>
<b>/{BotCommands.LeechCommand}</b>: Start leeching to Telegram.<br><br>
<b>/{BotCommands.ZipLeechCommand}</b>: Start leeching and upload the file/folder compressed with zip extension.<br><br>
<b>/{BotCommands.UnzipLeechCommand}</b>: Start leeching and upload the file/folder extracted from any archive extension.<br><br>
<b>/{BotCommands.QbLeechCommand}</b>: Start leeching using qBittorrent.<br><br>
<b>/{BotCommands.QbZipLeechCommand}</b>: Start leeching using qBittorrent and upload the file/folder compressed with zip extension.<br><br>
<b>/{BotCommands.QbUnzipLeechCommand}</b>: Start leeching using qBittorrent and upload the file/folder extracted from any archive extension<br><br>
<b>/{BotCommands.YtdlLeechCommand}</b>: Leech yt-dlp supported link.<br><br>
<b>/{BotCommands.YtdlZipLeechCommand}</b>: Leech yt-dlp supported link as zip.<br><br>
<b>Other Commands:</b><br>
<b>/{BotCommands.CloneCommand}</b> [drive_url]: Copy file/folder to Google Drive.<br><br>
<b>/{BotCommands.CountCommand}</b> [drive_url]: Count file/folder of Google Drive.<br><br>
<b>/{BotCommands.LeechSetCommand}</b> [query]: Leech settings.<br><br>
<b>/{BotCommands.SetThumbCommand}</b>: Reply photo to set it as Thumbnail.<br><br>
<b>/{BotCommands.BtSelectCommand}</b>: Select files from torrents by gid or reply.<br><br>
<b>/{BotCommands.CancelMirror}</b>: Cancel task by gid or reply.<br><br>
<b>/{BotCommands.ListCommand}</b> [query]: Search in Google Drive(s).<br><br>
<b>/{BotCommands.SearchCommand}</b> [query]: Search for torrents with API.<br><br>
<b>/{BotCommands.StatusCommand}</b>: Shows a status of all the downloads.<br><br>
<b>/{BotCommands.StatsCommand}</b>: Show stats of the machine where the bot is hosted in.<br><br>
<b>/{BotCommands.PingCommand}</b>: Check how long it takes to Ping the Bot (Only Owner & Sudo).<br><br>
<b>Sudo/Owner Only Commands:</b> <br>
<b>/{BotCommands.SleepCommand}:/</b> idle the bot (Only Owner & Sudo).<br><br>
<b>/{BotCommands.DeleteCommand}</b> [drive_url]: Delete file/folder from Google Drive (Only Owner & Sudo).<br><br>
<b>/{BotCommands.CancelAllCommand}</b> [query]: Cancel all [status] tasks.<br><br>
<b>/{BotCommands.AuthorizeCommand}</b>: Authorize a chat or a user to use the bot (Only Owner & Sudo).<br><br>
<b>/{BotCommands.UnAuthorizeCommand}</b>: Unauthorize a chat or a user to use the bot (Only Owner & Sudo).<br><br>
<b>/{BotCommands.AuthorizedUsersCommand}</b>: Show authorized users (Only Owner & Sudo).<br><br>
<b>/{BotCommands.AddleechlogCommand}</b>: Add Leech Log. (Only Owner & Sudo).<br><br>
<b>/{BotCommands.RmleechlogCommand}</b>: Remove Leech Log. (Only Owner & Sudo).<br><br>
<b>/{BotCommands.AddSudoCommand}</b>: Add sudo user (Only Owner).<br><br>
<b>/{BotCommands.RmSudoCommand}</b>: Remove sudo users (Only Owner).<br><br>
<b>/{BotCommands.RestartCommand}</b>: Restart and update the bot (Only Owner & Sudo).<br><br>
<b>/{BotCommands.LogCommand}</b>: Get a log file of the bot. Handy for getting crash reports (Only Owner & Sudo).<br><br>
<b>/{BotCommands.ShellCommand}</b>: Run shell commands (Only Owner).<br><br>
<b>/{BotCommands.EvalCommand}</b>: Run Python Code Line | Lines (Only Owner).<br><br>
<b>/{BotCommands.ExecCommand}</b>: Run Commands In Exec (Only Owner).<br><br>
<b>/{BotCommands.ClearLocalsCommand}</b>: Clear <b>{BotCommands.EvalCommand}</b> or <b>{BotCommands.ExecCommand}</b> locals (Only Owner).<br><br>
<b>RSS Related Commands:</b><br>
<b>/{BotCommands.RssListCommand}</b>: List all subscribed rss feed info (Only Owner & Sudo).<br><br>
<b>/{BotCommands.RssGetCommand}</b>: Force fetch last N links (Only Owner & Sudo).<br><br>
<b>/{BotCommands.RssSubCommand}</b>: Subscribe new rss feed (Only Owner & Sudo).<br><br>
<b>/{BotCommands.RssUnSubCommand}</b>: Unubscribe rss feed by title (Only Owner & Sudo).<br><br>
<b>/{BotCommands.RssSettingsCommand}</b>[query]: Rss Settings (Only Owner & Sudo).<br><br>
'''
help_string = f'''
Hei, Need Help!!
'''
try:
    help = telegraph.create_page(
        title='Helios-Mirror Help',
        content=help_string_telegraph,
    )["path"]
except Exception as err:
    LOGGER.warning(f"{err}")
    pass
def bot_help(update, context):
    button = ButtonMaker()
    button.buildbutton("Click Here", f"https://graph.org/{help}")
    reply_markup = button.build_menu(1)
    sendMarkup(help_string, context.bot, update.message, reply_markup)
    
if SET_BOT_COMMANDS:
    botcmds = [
        (f'{BotCommands.MirrorCommand}', 'Mirror'),
        (f'{BotCommands.ZipMirrorCommand}','Mirror and upload as zip'),
        (f'{BotCommands.UnzipMirrorCommand}','Mirror and extract files'),
        (f'{BotCommands.QbMirrorCommand}','Mirror torrent using qBittorrent'),
        (f'{BotCommands.QbZipMirrorCommand}','Mirror torrent and upload as zip using qb'),
        (f'{BotCommands.QbUnzipMirrorCommand}','Mirror torrent and extract files using qb'),
        (f'{BotCommands.CloneCommand}','Copy file/folder to Drive'),
        (f'{BotCommands.LeechCommand}','Leech'),
        (f'{BotCommands.ZipLeechCommand}','Leech and upload as zip'),
        (f'{BotCommands.UnzipLeechCommand}','Leech and extract files'),
        (f'{BotCommands.QbLeechCommand}','Leech torrent using qBittorrent'),
        (f'{BotCommands.QbZipLeechCommand}','Leech torrent and upload as zip using qb'),
        (f'{BotCommands.QbUnzipLeechCommand}','Leech torrent and extract using qb'),
        (f'{BotCommands.PreNameCommand}','Set Prename for Leech Files'),
        (f'{BotCommands.SufNameCommand}','Set Suffix for Leech Files'),
        (f'{BotCommands.CaptionCommand}','Set Caption for Leech Files'),
        (f'{BotCommands.RemnameCommand}','Remove Specific words from filename'),
        (f'{BotCommands.UserLogCommand}','Set Dump Channel for Leech Files'),
        (f'{BotCommands.CancelMirror}','Cancel a task'),
        (f'{BotCommands.ListCommand}','Search in Drive'),
        (f'{BotCommands.LeechSetCommand}','Leech settings'),
        (f'{BotCommands.SetThumbCommand}','Set thumbnail'),
        (f'{BotCommands.StatusCommand}','Get mirror status message'),
        (f'{BotCommands.RestartCommand}','Restart the bot'),
        (f'{BotCommands.LogCommand}','Get the bot Log'),
        (f'{BotCommands.HelpCommand}','Get detailed help')
    ]

def main():
    if SET_BOT_COMMANDS:
        bot.set_my_commands(botcmds)
    start_cleanup()
    date = now.strftime('%d/%m/%y')
    time = now.strftime('%I:%M:%S %p')
    notifier_dict = False
    if INCOMPLETE_TASK_NOTIFIER and DB_URI is not None:
        if notifier_dict := DbManger().get_incomplete_tasks():
            for cid, data in notifier_dict.items():
                if ospath.isfile(".restartmsg"):
                    with open(".restartmsg") as f:
                        chat_id, msg_id = map(int, f)
                    msg = f"<b>Every New End is a New Begining.\n\nXV BOT RESTARTED ⚡️\n\n📅DATE: {date}\n⌚TIME: {time}\n🗺️ TimeZone: {TIMEZONE}\n\nPlease Re-Add the Torrent's</b>"
                else:
                    msg = f"<b>Every New End is a New Begining.\n\nXV BOT RESTARTED ⚡️\n\n📅DATE: {date}\n⌚TIME: {time}\n🗺️ TimeZone: {TIMEZONE}\n\nPlease Re-Add the Torrent's</b>"

                for tag, links in data.items():
                     msg += f"\n{tag}: "
                     for index, link in enumerate(links, start=1):
                         msg += f" <a href='{link}'>{index}</a> |"
                         if len(msg.encode()) > 4000:
                             if '😎Restarted successfully❗' in msg and cid == chat_id:
                                 bot.editMessageText(msg, chat_id, msg_id, parse_mode='HTML', disable_web_page_preview=True)
                                 osremove(".restartmsg")
                             else:
                                 try:
                                     bot.sendMessage(cid, msg, 'HTML', disable_web_page_preview=True)
                                 except Exception as e:
                                     LOGGER.error(e)
                             msg = ''
                if '😎Restarted successfully❗' in msg and cid == chat_id:
                     bot.editMessageText(msg, chat_id, msg_id, parse_mode='HTML', disable_web_page_preview=True)
                     osremove(".restartmsg")
                else:
                    try:
                        bot.sendMessage(cid, msg, 'HTML', disable_web_page_preview=True)
                    except Exception as e:
                        LOGGER.error(e)

    if ospath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        msg = f"Restarted successfully❗\n\n📅DATE: {date}\n⌚TIME: {time}\n🌐TIMEZONE: {TIMEZONE}\n"
        bot.edit_message_text(msg, chat_id, msg_id)
        osremove(".restartmsg")
    elif not notifier_dict and AUTHORIZED_CHATS:
        text = f"Bot Restarted\n\n📅DATE: {date} \n⌚TIME: {time} \n🌐TIMEZONE: {TIMEZONE}"
        for id_ in AUTHORIZED_CHATS:
            try:
                bot.sendMessage(chat_id=id_, text=text, parse_mode=ParseMode.HTML)
            except Exception as e:
                LOGGER.error(e)

    start_handler = CommandHandler(BotCommands.StartCommand, start, run_async=True)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("Bot Started!")
    signal(SIGINT, exit_clean_up)

app.start()
main()
if USER_SESSION_STRING:
    app_session.run()
else:
    pass
main_loop.run_forever()
