import asyncio
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from pyrogram.enums import ParseMode
from py_yt import VideosSearch

from Sonic import app
from Sonic.mongo.playlists_db import (
    create_playlist, get_playlist, get_all_playlists, get_public_playlists, delete_playlist, rename_playlist, set_playlist_visibility, add_track, remove_track
)
from Sonic.utils.stream.stream import stream
from config import BANNED_USERS

# Helper to truncate long names
def truncate(text: str, length: int = 30) -> str:
    return text[:length] + "..." if len(text) > length else text

@app.on_message(filters.command(["playlist", "playlists"]) & ~BANNED_USERS)
async def playlist_menu_cmd(client, message: Message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Create Playlist", callback_data="pl_create")],
        [InlineKeyboardButton("My Playlists", callback_data="pl_my"), InlineKeyboardButton("Public Playlists", callback_data="pl_public")]
    ])
    await message.reply_text("<b>Ultimate Playlist Manager</b>\nManage your personal and public playlists.", reply_markup=keyboard, parse_mode=ParseMode.HTML)

@app.on_callback_query(filters.regex(r"^pl_") & ~BANNED_USERS)
async def playlist_callback(client, callback_query: CallbackQuery):
    data = callback_query.data.split("|")
    cmd = data[0]
    user_id = callback_query.from_user.id
    
    if cmd == "pl_menu":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Create Playlist", callback_data="pl_create")],
            [InlineKeyboardButton("My Playlists", callback_data="pl_my"), InlineKeyboardButton("Public Playlists", callback_data="pl_public")]
        ])
        try:
            await callback_query.edit_message_text("<b>Ultimate Playlist Manager</b>\nManage your personal and public playlists.", reply_markup=keyboard, parse_mode=ParseMode.HTML)
        except:
            pass
        
    elif cmd == "pl_create":
        try:
            await callback_query.edit_message_text(
                "Use the command `/createplaylist [name]` to create a new playlist.\nExample: `/createplaylist My Favorites`",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="pl_menu")]])
            )
        except:
            pass

    elif cmd == "pl_my":
        playlists = await get_all_playlists(user_id)
        if not playlists:
            try:
                return await callback_query.edit_message_text("You don't have any playlists yet.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="pl_menu")]]))
            except:
                return
        
        buttons = []
        for pl in playlists:
            buttons.append([InlineKeyboardButton(f"{truncate(pl['name'])}", callback_data=f"pl_view|{user_id}|{pl['name']}")])
        buttons.append([InlineKeyboardButton("Back", callback_data="pl_menu")])
        try:
            await callback_query.edit_message_text("<b>Your Playlists:</b>", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
        except:
            pass

    elif cmd == "pl_public":
        try:
            await callback_query.edit_message_text("Try searching inline! Type `@BotUsername public` in your chat box to explore public playlists.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="pl_menu")]]))
        except:
            pass

    elif cmd == "pl_view":
        pl_user_id = int(data[1])
        pl_name = data[2]
        playlist = await get_playlist(pl_user_id, pl_name)
        
        if not playlist:
            return await callback_query.answer("Playlist not found.", show_alert=True)
            
        tracks = playlist.get("tracks", [])
        
        total_seconds = 0
        for t in tracks:
            duration_min = t.get("duration_min", "0:00")
            parts = str(duration_min).split(":")
            if len(parts) == 2:
                total_seconds += int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:
                total_seconds += int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                
        hrs = total_seconds // 3600
        mins = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        dur_str = f"{hrs}h " if hrs > 0 else ""
        dur_str += f"{mins}m {secs}s"
        
        text = f"<b>Playlist:</b> {playlist['name']}\n"
        text += f"<b>Owner:</b> <code>{pl_user_id}</code>\n"
        text += f"<b>{'Public' if playlist.get('is_public') else 'Private'}</b> | <b>Tracks:</b> {len(tracks)} | <b>Total Time:</b> {dur_str}\n\n"
        
        if not tracks:
            text += " <i>This playlist is completely empty!</i>\n"
        else:
            for idx, t in enumerate(tracks[:15]):
                dur = t.get("duration_min", "0:00")
                title = truncate(t.get('title', 'Unknown Track'), 45)
                text += f"<b>{idx+1}.</b> {title} <code>[{dur}]</code>\n"
            if len(tracks) > 15:
                text += f"\n<i>... and {len(tracks) - 15} more hidden tracks.</i>"
            
        keyboard = []
        if len(tracks) > 0:
            keyboard.append([InlineKeyboardButton("Play Playlist", callback_data=f"pl_play|{pl_user_id}|{pl_name}")])
            
        if pl_user_id == user_id:
            vis_btn = "Make Public" if not playlist.get("is_public") else "Make Private"
            keyboard.append([
                InlineKeyboardButton(vis_btn, callback_data=f"pl_vis|{pl_name}"),
                InlineKeyboardButton("Delete", callback_data=f"pl_del|{pl_name}")
            ])
            if tracks:
                keyboard.append([
                    InlineKeyboardButton("Add Song", callback_data=f"pl_add_guide|{pl_name}"),
                    InlineKeyboardButton("Remove Song", callback_data=f"pl_rm_menu|{pl_name}")
                ])
            else:
                keyboard.append([InlineKeyboardButton("Add Song", callback_data=f"pl_add_guide|{pl_name}")])
            keyboard.append([InlineKeyboardButton("Back", callback_data="pl_my")])
        else:
            keyboard.append([InlineKeyboardButton("Save to My Playlists", callback_data=f"pl_save|{pl_user_id}|{pl_name}")])
            
        try:
            await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
        except:
            pass

    elif cmd == "pl_add_guide":
        pl_name = data[1]
        try:
            await callback_query.edit_message_text(
                f"<b>How to add a song to {pl_name}:</b>\n\n"
                f"Use the command: <code>/addsong {pl_name} | song name</code>\n\n"
                f"<b>Tip:</b> If you only have one playlist, you can just use <code>/addsong song name</code>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data=f"pl_view|{user_id}|{pl_name}")]])
            )
        except:
            pass

    elif cmd == "pl_play":
        pl_user_id = int(data[1])
        pl_name = data[2]
        playlist = await get_playlist(pl_user_id, pl_name)
        if not playlist or not playlist.get("tracks"):
            return await callback_query.answer("Empty or invalid playlist.", show_alert=True)
            
        tracks = playlist["tracks"]
        chat_id = callback_query.message.chat.id
        from Sonic.utils.decorators.language import get_lang
        from strings import get_string
        try:
            language = await get_lang(chat_id)
            _ = get_string(language)
        except:
            _ = get_string("en")
        
        await callback_query.answer("Loading playlist into queue...", show_alert=False)
        mystic = await callback_query.message.reply_text(
            "Loading playlist into queue..."
        )
        
        try:
            await stream(
                _,
                mystic,
                user_id,
                tracks,
                chat_id,
                callback_query.from_user.first_name,
                chat_id,
                video=False,
                streamtype="db_playlist",
                spotify=False,
                forceplay=False,
            )
        except Exception as e:
            await mystic.edit_text(f"Error playing playlist: {e}")

    elif cmd == "pl_search":
        public_playlists = await get_public_playlists(limit=20)
        if not public_playlists:
            return await callback_query.answer("No public playlists found.", show_alert=True)
            
        text = "<b>Search Public Playlists</b>\n\nSelect a playlist to view details:"
        buttons = []
        for pl in public_playlists:
            buttons.append([InlineKeyboardButton(f"{pl['name']} (by {pl['user_id']})", callback_data=f"pl_view|{pl['user_id']}|{pl['name']}")])
        buttons.append([InlineKeyboardButton("Back", callback_data="pl_menu")])
        try:
            await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
        except:
            pass

    elif cmd == "pl_save":
        pl_user_id = int(data[1])
        pl_name = data[2]
        success = await clone_playlist(pl_user_id, pl_name, user_id)
        if success:
            await callback_query.answer("Playlist saved to your account!", show_alert=True)
        else:
            await callback_query.answer("Failed to save. You might already have a playlist with this name.", show_alert=True)
        pl_name = data[2]
        playlist = await get_playlist(pl_user_id, pl_name)
        if not playlist:
            return await callback_query.answer("Playlist not found.", show_alert=True)
            
        new_name = playlist['name'] + " (Saved)"
        existing = await get_playlist(user_id, new_name)
        if existing:
            return await callback_query.answer("You already saved this playlist.", show_alert=True)
            
        await create_playlist(user_id, new_name, is_public=False)
        for t in playlist.get("tracks", []):
            await add_track(user_id, new_name, t)
        await callback_query.answer("Playlist saved to your collection!", show_alert=True)

    elif cmd == "pl_vis":
        pl_name = data[1]
        playlist = await get_playlist(user_id, pl_name)
        if not playlist: return await callback_query.answer("Error", show_alert=True)
        await set_playlist_visibility(user_id, pl_name, not playlist.get("is_public", False))
        
        # update inline keyboard directly without recursion
        playlist = await get_playlist(user_id, pl_name)
        tracks = playlist.get("tracks", [])
        
        total_seconds = 0
        for t in tracks:
            duration_min = t.get("duration_min", "0:00")
            parts = str(duration_min).split(":")
            if len(parts) == 2:
                total_seconds += int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:
                total_seconds += int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                
        hrs = total_seconds // 3600
        mins = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        dur_str = f"{hrs}h " if hrs > 0 else ""
        dur_str += f"{mins}m {secs}s"
        
        text = f"<b>Playlist:</b> {playlist['name']}\n"
        text += f"<b>Owner:</b> <code>{user_id}</code>\n"
        text += f"<b>{'Public' if playlist.get('is_public') else 'Private'}</b> | <b>Tracks:</b> {len(tracks)} | <b>Total Time:</b> {dur_str}\n\n"
        
        if not tracks:
            text += " <i>This playlist is completely empty!</i>\n"
        else:
            for idx, t in enumerate(tracks[:15]):
                dur = t.get("duration_min", "0:00")
                title = truncate(t.get('title', 'Unknown Track'), 45)
                text += f"<b>{idx+1}.</b> {title} <code>[{dur}]</code>\n"
            if len(tracks) > 15:
                text += f"\n<i>... and {len(tracks) - 15} more hidden tracks.</i>"
            
        keyboard = []
        if len(tracks) > 0:
            keyboard.append([InlineKeyboardButton("Play Playlist", callback_data=f"pl_play|{user_id}|{pl_name}")])
            
        if user_id != callback_query.from_user.id:
            keyboard.append([InlineKeyboardButton("Save to My Playlists", callback_data=f"pl_save|{user_id}|{pl_name}")])
        else:
            vis_btn = "Make Public" if not playlist.get("is_public") else "Make Private"
            keyboard.append([
                InlineKeyboardButton(vis_btn, callback_data=f"pl_vis|{pl_name}"),
                InlineKeyboardButton("Delete", callback_data=f"pl_del|{pl_name}")
            ])
            if tracks:
                keyboard.append([
                    InlineKeyboardButton("Add Song", callback_data=f"pl_add_guide|{pl_name}"),
                    InlineKeyboardButton("Remove Song", callback_data=f"pl_rm_menu|{pl_name}")
                ])
            else:
                keyboard.append([InlineKeyboardButton("Add Song", callback_data=f"pl_add_guide|{pl_name}")])
            
        keyboard.append([InlineKeyboardButton("Back", callback_data="pl_menu")])
            
        try:
            await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
        except:
            pass
        await callback_query.answer("Visibility updated.", show_alert=False)

    elif cmd == "pl_del":
        pl_name = data[1]
        await delete_playlist(user_id, pl_name)
        await callback_query.answer("Playlist deleted.", show_alert=True)
        try:
            await callback_query.edit_message_text("Playlist deleted.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="pl_menu")]]))
        except:
            pass

    elif cmd == "pl_rm_menu":
        pl_name = data[1]
        playlist = await get_playlist(user_id, pl_name)
        tracks = playlist.get("tracks", [])
        buttons = []
        for t in tracks:
            buttons.append([InlineKeyboardButton(f"{truncate(t['title'], 30)}", callback_data=f"pl_rm_exec|{pl_name}|{t['vidid']}")])
        buttons.append([InlineKeyboardButton("Back", callback_data=f"pl_view|{user_id}|{pl_name}")])
        try:
            await callback_query.edit_message_text("Select a song to remove:", reply_markup=InlineKeyboardMarkup(buttons))
        except:
            pass

    elif cmd == "pl_rm_exec":
        pl_name = data[1]
        vidid = data[2]
        await remove_track(user_id, pl_name, vidid)
        
        # update menu directly instead of recursion
        playlist = await get_playlist(user_id, pl_name)
        tracks = playlist.get("tracks", [])
        buttons = []
        for t in tracks:
            buttons.append([InlineKeyboardButton(f"{truncate(t['title'], 30)}", callback_data=f"pl_rm_exec|{pl_name}|{t['vidid']}")])
        buttons.append([InlineKeyboardButton("Back", callback_data=f"pl_view|{user_id}|{pl_name}")])
        
        try:
            await callback_query.edit_message_text("Select a song to remove:", reply_markup=InlineKeyboardMarkup(buttons))
        except:
            pass
        await callback_query.answer("Song removed.", show_alert=False)


@app.on_message(filters.command("createplaylist") & ~BANNED_USERS)
async def create_playlist_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/createplaylist [Playlist Name]`")
    name = message.text.split(None, 1)[1].strip()
    
    if await get_playlist(message.from_user.id, name):
        return await message.reply_text("A playlist with this name already exists.")
        
    await create_playlist(message.from_user.id, name, is_public=False)
    await message.reply_text(f"Playlist <b>{name}</b> created successfully! Use `/playlist` to manage it.")


@app.on_message(filters.command("addsong") & ~BANNED_USERS)
async def add_song_cmd(client, message: Message):
    user_id = message.from_user.id
    playlists = await get_all_playlists(user_id)
    
    if not playlists:
        return await message.reply_text("You don't have any playlists. Create one first using `/createplaylist`.")
    
    pl_name = None
    query = None
    
    if "|" in message.text:
        try:
            args = message.text.split(None, 1)[1].split("|")
            pl_name = args[0].strip()
            query = args[1].strip()
        except:
             return await message.reply_text("Usage: `/addsong [Playlist Name] | [Song Name or Link]`")
    else:
        if len(playlists) == 1:
            pl_name = playlists[0]['name']
            query = message.text.split(None, 1)[1].strip() if len(message.command) > 1 else None
        else:
            return await message.reply_text("You have multiple playlists. Please use: `/addsong [Playlist Name] | [Song Name]`")

    if not query:
        return await message.reply_text(f"Usage: `/addsong {pl_name or '[Playlist Name]'} | [Song Name or Link]`")

    playlist = await get_playlist(user_id, pl_name)
    if not playlist:
        return await message.reply_text(f"Playlist <b>{pl_name}</b> not found.")
        
    mystic = await message.reply_text("Searching for the song...")
    try:
        from Sonic import YouTube
        details, track_id = await YouTube.track(query)
        if not details:
            return await mystic.edit_text("Couldn't find the song.")
            
        track_doc = {
            "title": details["title"],
            "duration_min": details["duration_min"],
            "vidid": track_id,
            "filepath": "", 
            "streamtype": "youtube"
        }
        await add_track(user_id, pl_name, track_doc)
        await mystic.edit_text(f"Added <b>{details['title']}</b> to <b>{pl_name}</b>.")
    except Exception as e:
        await mystic.edit_text("Error adding song.")
