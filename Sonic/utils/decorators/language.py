from pyrogram.types import LinkPreviewOptions
from Sonic import app
from Sonic.misc import SUDOERS
from Sonic.utils.database import get_lang, is_maintenance
from config import SUPPORT_GROUP
from strings import get_string


def language(mystic):
    async def wrapper(_, message, **kwargs):
        if await is_maintenance() is False:
            if message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    text=f"{app.mention} is under maintenance, visit <a href={SUPPORT_GROUP}>support chat</a> for knowing the reason.",
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                )
        try:
            await message.delete()
        except:
            pass

        try:
            language = await get_lang(message.chat.id)
            language = get_string(language)
        except:
            language = get_string("en")
        return await mystic(_, message, language)

    return wrapper


def languageCB(mystic):
    async def wrapper(_, CallbackQuery, **kwargs):
        if await is_maintenance() is False:
            if CallbackQuery.from_user.id not in SUDOERS:
                return await CallbackQuery.answer(
                    f"{app.mention} is under maintenance, visit <a href={SUPPORT_GROUP}>support chat</a> for knowing the reason.",
                    show_alert=True,
                )
        try:
            language = await get_lang(CallbackQuery.message.chat.id)
            language = get_string(language)
        except:
            language = get_string("en")
        return await mystic(_, CallbackQuery, language)

    return wrapper


def LanguageStart(mystic):
    async def wrapper(_, message, **kwargs):
        try:
            language = await get_lang(message.chat.id)
            language = get_string(language)
        except:
            language = get_string("en")
        return await mystic(_, message, language)

    return wrapper
