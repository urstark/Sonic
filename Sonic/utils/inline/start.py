from pyrogram.types import InlineKeyboardButton

import config
from Sonic import app


def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_("S_B_1", clean=True), url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(text=_("S_B_2", clean=True), url=config.SUPPORT_GROUP),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_("S_B_3", clean=True),
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [InlineKeyboardButton(text=_("S_B_4", clean=True), callback_data="settings_back_helper")],
        [
            InlineKeyboardButton(text=_("S_B_2", clean=True), url=config.SUPPORT_GROUP),
            InlineKeyboardButton(text=_("S_B_6", clean=True), url=config.SUPPORT_CHANNEL),
        ],
        [
            InlineKeyboardButton(text=_("S_B_5", clean=True), user_id=config.OWNER_ID),
        ],
    ]
    return buttons
