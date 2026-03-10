from typing import Union

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Sonic import app

def help_pannel(_, START: Union[bool, int] = None):
    first = [InlineKeyboardButton(text=_("CLOSE_BUTTON", clean=True), callback_data=f"close")]
    second = [
        InlineKeyboardButton(
            text=_("BACK_BUTTON", clean=True),
            callback_data=f"settingsback_helper",
        ),
    ]
    mark = second if START else first
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_("CAT_MUSIC", clean=True),
                    callback_data="help_category music 0",
                ),
                InlineKeyboardButton(
                    text=_("CAT_GROUP", clean=True),
                    callback_data="help_category group 0",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_("CAT_FUN", clean=True),
                    callback_data="help_category fun 0",
                ),
                InlineKeyboardButton(
                    text=_("CAT_SUDO", clean=True),
                    callback_data="help_category sudo 0",
                ),
            ],
            mark,
        ]
    )
    return upl

def help_category_markup(_, category: str, page: int = 0):
    categories = {
        "music": [
            ("H_B_1", "hb1"),
            ("H_B_2", "hb2"),
            ("H_B_6", "hb6"),
            ("H_B_8", "hb8"),
            ("H_B_10", "hb10"),
            ("H_B_11", "hb11"),
            ("H_B_12", "hb12"),
            ("H_B_13", "hb13"),
            ("H_B_14", "hb14"),
            ("H_B_16", "hb16"),
            ("H_B_22", "hb22"),
        ],
        "group": [
            ("H_B_15", "hb15"),
            ("H_B_17", "hb17"),
            ("H_B_19", "hb19"),
            ("H_B_21", "hb21"),
        ],
        "fun": [
            ("H_B_18", "hb18"),
            ("H_B_20", "hb20"),
        ],
        "sudo": [
            ("H_B_3", "hb3"),
            ("H_B_4", "hb4"),
            ("H_B_5", "hb5"),
            ("H_B_7", "hb7"),
            ("H_B_9", "hb9"),
        ]
    }

    items = categories.get(category, [])
    num_per_page = 12
    total_pages = (len(items) + num_per_page - 1) // num_per_page
    start = page * num_per_page
    end = start + num_per_page
    current_items = [items[i] for i in range(start, min(end, len(items)))]

    buttons = []
    # 3 items per row
    row = []
    for text_key, callback_value in current_items:
        row.append(
            InlineKeyboardButton(
                text=_(text_key, clean=True), 
                callback_data=f"help_callback {callback_value} {category} {page}"
            )
        )
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    return_btn = InlineKeyboardButton(
        text=_("BACK_BUTTON", clean=True), 
        callback_data="settings_back_helper"
    )

    if total_pages <= 1:
        buttons.append([return_btn])
    else:
        pagination_row = []
        if page > 0:
            pagination_row.append(
                InlineKeyboardButton(
                    text="«", 
                    callback_data=f"help_category {category} {page - 1}"
                )
            )
        
        pagination_row.append(return_btn)
        
        if page < total_pages - 1:
            pagination_row.append(
                InlineKeyboardButton(
                    text="»", 
                    callback_data=f"help_category {category} {page + 1}"
                )
            )
        buttons.append(pagination_row)

    return InlineKeyboardMarkup(buttons)


def help_back_markup(_, category: str, page: int = 0):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_("BACK_BUTTON", clean=True),
                    callback_data=f"help_category {category} {page}",
                ),
            ]
        ]
    )
    return upl


def private_help_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_("S_B_4", clean=True),
                url=f"https://t.me/{app.username}?start=help",
            ),
        ],
    ]
    return buttons
