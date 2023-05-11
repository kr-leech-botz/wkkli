from pyrogram import enums
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot import LOGGER, DB_URI, OWNER_ID, PRE_DICT, LEECH_DICT, dispatcher, CAP_DICT, REM_DICT, SUF_DICT
from bot.helper.telegram_helper.message_utils import *
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.ext_utils.db_handler import DbManger


def prename_set(update, context):
    user_id_ = update.message.from_user.id 
    u_men = update.message.from_user.first_name
    if (BotCommands.PreNameCommand in update.message.text) and (len(update.message.text.split(' ')) == 1):
        sendMessage(f'<b>Set Prename Like👇 \n/{BotCommands.PreNameCommand} channelName</b>', context.bot, update.message)
    else:
        lm = sendMessage(f"<b>Please Wait....Processing🤖</b>", context.bot, update.message)
        pre_send = update.message.text.split(" ", maxsplit=1)
        reply_to = update.message.reply_to_message
        if len(pre_send) > 1:
            txt = pre_send[1]
        elif reply_to is not None:
            txt = reply_to.text
        else:
            txt = ""
        prefix_ = txt
        PRE_DICT[user_id_] = prefix_    
        if DB_URI:
            DbManger().user_pre(user_id_, prefix_)
            LOGGER.info(f"User : {user_id_} Prename is Saved in DB")
        editMessage(f"<b>{u_men} Prename for the Leech file is Set now🚀</b>\n\n<b>Your Prename Text: </b>{txt}", lm)


##Need to edit after DB Reset
def suffix_set(update, context):
    user_id_ = update.message.from_user.id 
    u_men = update.message.from_user.first_name
    if (BotCommands.SufNameCommand in update.message.text) and (len(update.message.text.split(' ')) == 1):
        sendMessage(f'<b>Set Suffix Like👇 \n/{BotCommands.SufNameCommand} channelName</b>', context.bot, update.message)
    else:
        lm = sendMessage(f"<b>Please Wait....Processing🤖</b>", context.bot, update.message)
        pre_send = update.message.text.split(" ", maxsplit=1)
        reply_to = update.message.reply_to_message
        if len(pre_send) > 1:
            txt = pre_send[1]
        elif reply_to is not None:
            txt = reply_to.text
        else:
            txt = ""
        suffix_ = txt
        SUF_DICT[user_id_] = suffix_
        if DB_URI:
            DbManger().user_suf(user_id_, suffix_)
            LOGGER.info(f"User : {user_id_} Surname is Saved in DB")
        editMessage(f"<b>{u_men} Suffix for the Leech file is Set now🚀</b>\n\n<b>Your Surname Text: </b>{txt}", lm)



def caption_set(update, context):
    user_id_ = update.message.from_user.id 
    u_men = update.message.from_user.first_name
    if (BotCommands.CaptionCommand in update.message.text) and (len(update.message.text.split(' ')) == 1):
        sendMessage(f'<b>Set Caption Like👇 \n/{BotCommands.CaptionCommand} text</b>', context.bot, update.message)
    else:
        lm = sendMessage(f"<b>Please Wait....Processing🤖</b>", context.bot, update.message)
        pre_send = update.message.text.split(" ", maxsplit=1)
        reply_to = update.message.reply_to_message
        if len(pre_send) > 1:
            txt = pre_send[1]
        elif reply_to is not None:
            txt = reply_to.text
        else:
            txt = ""
        caption_ = txt
        CAP_DICT[user_id_] = caption_
        if DB_URI:
            DbManger().user_cap(user_id_, caption_)
            LOGGER.info(f"User : {user_id_} Caption is Saved in DB")
        editMessage(f"<b>{u_men} Caption for the Leech file is Set now🌋</b>\n\n<b>Your Caption Text: </b>{txt}", lm)


def userlog_set(update, context):
    user_id_ = update.message.from_user.id 
    u_men = update.message.from_user.first_name

    if (BotCommands.UserLogCommand in update.message.text) and (len(update.message.text.split(' ')) == 1):
        help_msg = "<b>Send channel id after command:</b>"
        help_msg += f"\n<code>/{BotCommands.UserLogCommand}" + " -100xxxxxxx" + "</code>\n"
        help_msg += "\n<b>By Replying to Message (Including Channel ID):</b>"
        help_msg += f"\n<code>/{BotCommands.UserLogCommand}" + " {message}" + "</code>"
        sendMessage(help_msg, context.bot, update.message)
        return
    lm = sendMessage("Checking your Channel ID... 🛃", context.bot, update.message)          
    pre_send = update.message.text.split(" ", maxsplit=1)
    reply_to = update.message.reply_to_message
    if len(pre_send) > 1:
        dumpid_ = pre_send[1]
    elif reply_to is not None:
        dumpid_ = reply_to.text
    else:
        dumpid_ = ""
    if not dumpid_.startswith('-100'):
        editMessage("<i><b>Your Channel ID Should Start with</b> -100xxxxxxxx, <u>Retry Again</u> !!</i>", lm)
        return
    dumpid_ = int(dumpid_.strip())
    try:
        editMessage("<i>Checking Your Channel Interaction ...</i> ♻️", lm)
        bot.sendMessage(chat_id=dumpid_, text=f'''╭─《 WZML DUMP CHANNEL 》
│
├🆔 <b>Dump ID :</b> <code>{dumpid_}</code>
│
╰📂 <i>From Now On, The Bot will Send you Files in this Channel !!</i>''',  parse_mode='HTML')
    except Exception as err:
        editMessage(f"<i>Make Sure You have Added the Bot as Admin with Post Permission, Retry Again.</i>\n\nError : {err}", lm)
        return
    LEECH_DICT[user_id_] = str(dumpid_)
    if DB_URI:
        DbManger().user_dump(user_id_, str(dumpid_))
        LOGGER.info(f"User : {user_id_} LeechLog ID Saved in DB")
    editMessage(f"<b><a href='tg://user?id={user_id_}'>{u_men}</a>'s Dump Channel ID Saved Successfully...🛸</b>", lm)



def remname_set(update, context):
    user_id_ = update.message.from_user.id 
    u_men = update.message.from_user.first_name
    if (BotCommands.RemnameCommand in update.message.text) and (len(update.message.text.split(' ')) == 1):
        hlp_me = "<b>Send text with format along with command line:</b>\n"
        hlp_me += "<code>/cmd</code> previousname:newname:times|previousname:newname:times\n\n"
        hlp_me += f"<b>Example:</b> /{BotCommands.RemnameCommand} " + "Baasha:X|Normal:Paid:1|BX\n\n"
        hlp_me += "Output : Star Now : Click Here.txt\n\n"
        hlp_me += "<b>Explanation :</b> Here, Baasha changed to X, Normal changed to Paid, only 1 time and BX is removed.\n\n"
        hlp_me += '''<b>Filter Notes:</b>
1. All Spaces are sensitive, if you give space unnecessarily, it will not work.

2. Use | for different changes, you can use as many times you need. If you keep single word or letter, it will be Removed and you can Change Specific Work or letter by : separator respectively. (optional)

3. For Changing, A work or Letter in a Limited no. of Times, use again : separator to specify no. of times to remove. (optional)

4. Filename is Changed according to your Remname, so No need to change in Caption, again for filename.''' 
        sendMessage(hlp_me, context.bot, update.message)
    else:
        lm = sendMessage(f"<b>Please Wait....Processing🤖</b>", context.bot, update.message)
        pre_send = update.message.text.split(" ", maxsplit=1)
        reply_to = update.message.reply_to_message
        if len(pre_send) > 1:
            txt = pre_send[1]
        elif reply_to is not None:
            txt = reply_to.text
        else:
            txt = ""
        remname_ = txt
        REM_DICT[user_id_] = remname_
        if DB_URI:
            DbManger().user_rem(user_id_, remname_)
            LOGGER.info(f"User : {user_id_} Remname is Saved in DB")
        editMessage(f"<b><a href='tg://user?id={user_id_}'>{u_men}</a>'s Remname is Set Successfully :</b>\n\n<b>• Remname Text: </b>{txt}", lm)

            
prename_set_handler = CommandHandler(BotCommands.PreNameCommand, prename_set,
                                       filters=(CustomFilters.authorized_chat | CustomFilters.authorized_user), run_async=True)
suffix_set_handler = CommandHandler(BotCommands.SufNameCommand, suffix_set,
                                       filters=(CustomFilters.authorized_chat | CustomFilters.authorized_user), run_async=True)
caption_set_handler = CommandHandler(BotCommands.CaptionCommand, caption_set,
                                       filters=(CustomFilters.authorized_chat | CustomFilters.authorized_user), run_async=True)
userlog_set_handler = CommandHandler(BotCommands.UserLogCommand, userlog_set,
                                       filters=(CustomFilters.authorized_chat | CustomFilters.authorized_user), run_async=True)
remname_set_handler = CommandHandler(BotCommands.RemnameCommand, remname_set,
                                       filters=(CustomFilters.authorized_chat | CustomFilters.authorized_user), run_async=True) 

dispatcher.add_handler(prename_set_handler)
dispatcher.add_handler(suffix_set_handler)
dispatcher.add_handler(caption_set_handler)
dispatcher.add_handler(userlog_set_handler)
dispatcher.add_handler(remname_set_handler)
