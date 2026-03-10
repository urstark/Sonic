import random
from typing import Union

from pyrogram import filters, types
from pyrogram.types import InlineKeyboardMarkup, Message

from Sonic import app
from Sonic.utils import help_pannel
from Sonic.utils.database import get_lang
from Sonic.utils.decorators.language import LanguageStart, languageCB
from Sonic.utils.inline.help import help_back_markup, private_help_panel, help_category_markup
from config import BANNED_USERS, STARK_IMG, SUPPORT_GROUP
from strings import get_string, helpers


@app.on_message(filters.command(["help"]) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("settings_back_helper") & ~BANNED_USERS)
async def helper_private(
    client: app, update: Union[types.Message, types.CallbackQuery]
):
    is_callback = isinstance(update, types.CallbackQuery)
    if is_callback:
        try:
            await update.answer()
        except:
            pass
        chat_id = update.message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)
        keyboard = help_pannel(_, True)
        try:
            await update.edit_message_text(
                _["help_1"].format(SUPPORT_GROUP), reply_markup=keyboard
            )
        except:
            pass
    else:
        try:
            await update.delete()
        except:
            pass
        language = await get_lang(update.chat.id)
        _ = get_string(language)
        keyboard = help_pannel(_)
        await update.reply_photo(
            photo=random.choice(STARK_IMG),
            caption=_["help_1"].format(SUPPORT_GROUP),
            reply_markup=keyboard,
        )


@app.on_message(filters.command(["help"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_com_group(client, message: Message, _):
    keyboard = private_help_panel(_)
    await message.reply_text(_["help_2"], reply_markup=InlineKeyboardMarkup(keyboard))


@app.on_callback_query(filters.regex("help_category") & ~BANNED_USERS)
@languageCB
async def helper_category_cb(client, CallbackQuery, _):
    data = CallbackQuery.data.strip().split(None, 2)
    category = data[1]
    page = int(data[2]) if len(data) > 2 else 0
    keyboard = help_category_markup(_, category, page)
    try:
        await CallbackQuery.edit_message_text(
            _["help_1"].format(SUPPORT_GROUP), reply_markup=keyboard
        )
    except:
        pass


@app.on_callback_query(filters.regex("help_callback") & ~BANNED_USERS)
@languageCB
async def helper_cb(client, CallbackQuery, _):
    data = CallbackQuery.data.strip().split(None, 3)
    cb = data[1]
    category = data[2] if len(data) > 2 else "music"
    page = int(data[3]) if len(data) > 3 else 0
    
    keyboard = help_back_markup(_, category, page)
    text = helpers.HELP_16.format(app.name) if cb == "hb16" else getattr(helpers, f"HELP_{cb[2:]}", "")
    try:
        await CallbackQuery.edit_message_text(text, reply_markup=keyboard)
    except:
        pass
