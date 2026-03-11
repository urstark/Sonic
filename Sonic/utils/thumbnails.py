# ATLEAST GIVE CREDITS IF YOU STEALING :(((((((((((((((((((((((((((((((((((((
# ELSE NO FURTHER PUBLIC THUMBNAIL UPDATES

import os
import random
import aiofiles
import aiohttp
import asyncio
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from py_yt import VideosSearch

from config import YOUTUBE_IMG_URL
from Sonic import LOGGER

async def gen_thumb(videoid: str, thumb_size=(1280, 720)):
    # Local assets paths
    FONT_LIGHT = "Sonic/assets/font2.ttf"
    FONT_BOLD = "Sonic/assets/font3.ttf"
    
    path = f"cache/{videoid}.png"
    if os.path.isfile(path):
        return path
        
    try:
        if not os.path.exists("cache"):
            os.makedirs("cache")
            
        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        res = await results.next()
        
        if not res or not res.get("result"):
            LOGGER.debug(f"Direct URL search failed for {videoid}, trying generic search...")
            results = VideosSearch(videoid, limit=1)
            res = await results.next()
            
        if not res or not res.get("result"):
            raise Exception("No results found on YouTube")
            
        data = res["result"][0]
        
        title = data.get("title", "Unsupported Title")
        duration = data.get("duration") or "00:00"
        channel = data.get("channel", {}).get("name", "Unknown Channel")
        thumb_url = data["thumbnails"][0]["url"].split("?")[0]
        
        async with aiohttp.ClientSession() as session:
            async with session.get(thumb_url) as resp:
                content = await resp.read()

        temp_path = f"cache/thumb_{videoid}.png"
        if not os.path.exists("cache"):
            os.makedirs("cache")
        async with aiofiles.open(temp_path, "wb") as f:
            await f.write(content)

        
        is_generated = await asyncio.to_thread(
            _generate_image_sync, 
            temp_path, path, thumb_size, title, channel, duration
        )
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return path if is_generated else YOUTUBE_IMG_URL

    except Exception as ex:
        LOGGER(__name__).exception(f"Error generating thumbnail for {videoid}: {ex}")
        return YOUTUBE_IMG_URL

def _generate_image_sync(temp_path, path, thumb_size, title, channel, duration):
    try:
        FONT_LIGHT = "Sonic/assets/font2.ttf"
        FONT_BOLD = "Sonic/assets/font3.ttf"
        
        # 1. Background (Optimized Blur: resize small -> blur -> scale up)
        background_raw = Image.open(temp_path).convert("RGBA")
        target_w, target_h = thumb_size
        
        # Resize to 1/8 for ultra-fast blur
        background = background_raw.resize((target_w // 8, target_h // 8), Image.NEAREST)
        background = background.filter(ImageFilter.GaussianBlur(radius=5)) # Radius 5 on small image = ~40 on large
        background = background.resize((target_w, target_h), Image.BICUBIC)
        background = ImageEnhance.Brightness(background).enhance(0.45)
        
        img = background
        draw = ImageDraw.Draw(img)
        
        # 2. Main Album Art (Left Side) - Aggressive Zoom & Crop to hide empty spaces
        art_w, art_h = 500, 460
        art_x, art_y = 120, 132
        album_art = Image.open(temp_path).convert("RGBA")
        
        # Aggressive zoom: crop 4% from all edges to hide baked-in borders/empty spaces
        width, height = album_art.size
        zoom_margin_w = int(width * 0.04)
        zoom_margin_h = int(height * 0.04)
        album_art = album_art.crop((zoom_margin_w, zoom_margin_h, width - zoom_margin_w, height - zoom_margin_h))
        
        # Calculate aspect ratios of the zoomed image
        width, height = album_art.size
        aspect = width / height
        target_aspect = art_w / art_h
        
        if aspect > target_aspect:
            # Image is wider than target
            new_width = int(height * target_aspect)
            offset = (width - new_width) // 2
            album_art = album_art.crop((offset, 0, offset + new_width, height))
        else:
            # Image is taller than target
            new_height = int(width / target_aspect)
            offset = (height - new_height) // 2
            album_art = album_art.crop((0, offset, width, offset + new_height))
            
        album_art = album_art.resize((art_w, art_h), Image.LANCZOS)
        
        # Rounded mask
        mask = Image.new("L", (art_w, art_h), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([(0, 0), (art_w, art_h)], radius=50, fill=255)
        img.paste(album_art, (art_x, art_y), mask)
        
        # 3. Right Pane Setup
        pane_x = 720
        pane_w = 460
        target_center_x = pane_x + (pane_w // 2)
        
        font_title = ImageFont.truetype(FONT_BOLD, 45)
        font_artist = ImageFont.truetype(FONT_LIGHT, 30)
        font_time = ImageFont.truetype(FONT_BOLD, 18)
        
        title_disp = title[:18] + "..." if len(title) > 23 else title
        artist_disp = channel[:10] + "..." if len(channel) > 33 else channel
        
        # 4. Text (White dots/buttons removed as requested)
        draw.text((pane_x, 150), title_disp, font=font_title, fill="white")
        draw.text((pane_x, 205), artist_disp, font=font_artist, fill=(180, 180, 180, 255))
        
        # 5. Progress Bar
        bar_y = 295
        bar_h = 16
        progress = random.uniform(0.15, 0.45)
        passed_w = int(pane_w * progress)
        
        # Track line (Standardized Grayish semi-opaque background)
        draw.rounded_rectangle([(pane_x, bar_y), (pane_x + pane_w, bar_y + bar_h)], radius=8, fill=(120, 120, 120, 80))
        # Passed line (Rounded left, Flat right)
        if passed_w > 8:
            # Rounded start
            draw.pieslice([(pane_x, bar_y), (pane_x + 16, bar_y + bar_h)], 90, 270, fill="white")
            # Flat middle/end
            draw.rectangle([(pane_x + 8, bar_y), (pane_x + passed_w, bar_y + bar_h)], fill="white")
        else:
            draw.rounded_rectangle([(pane_x, bar_y), (pane_x + passed_w + 2, bar_y + bar_h)], radius=4, fill="white")
        
        # Time Labels
        try:
            parts = duration.split(":")
            total_sec = int(parts[0])*60 + int(parts[1]) if len(parts)==2 else (int(parts[0])*3600 + int(parts[1])*60 + int(parts[2]) if len(parts)==3 else 0)
        except: total_sec = 0
        curr_m, curr_s = divmod(int(total_sec * progress), 60)
        rem_m, rem_s = divmod(total_sec - int(total_sec * progress), 60)
        draw.text((pane_x, bar_y + 25), f"{curr_m}:{curr_s:02d}", font=font_time, fill=(180, 180, 180, 160))
        draw.text((pane_x + pane_w - 60, bar_y + 25), f"-{rem_m}:{rem_s:02d}", font=font_time, fill=(180, 180, 180, 160))
        
        # 6. Playback Controls
        ctrl_y = 425
        def load_icon(name, size):
            try:
                ipath = f"Sonic/assets/{name}.png"
                icon = Image.open(ipath).convert("RGBA")
                return icon.resize((size, size), Image.LANCZOS)
            except Exception as e:
                LOGGER.debug(f"Failed to load icon {name}: {e}")
                return None
        
        icon_prev = load_icon("prev", 53)
        icon_pause = load_icon("pause", 73)
        icon_next = load_icon("next", 53)
        
        if icon_prev:
            img.paste(icon_prev, (target_center_x - 145, ctrl_y - 30), icon_prev)
        if icon_pause:
            img.paste(icon_pause, (target_center_x - 40, ctrl_y - 40), icon_pause)
        if icon_next:
            img.paste(icon_next, (target_center_x + 85, ctrl_y - 30), icon_next)
        
        # 7. Volume Bar
        vol_y = 535
        vol_h = 12
        vol_progress = 0.9
        
        icon_low = load_icon("low-volume", 32)
        icon_high = load_icon("high-volume", 32)
        
        # Volume group total width = 460 (same as pane_w)
        # Track width = 370, Icons = 32x2, Padding approx 13x2
        vol_track_w = 370
        vol_passed_w = int(vol_track_w * vol_progress)
        vol_track_x = pane_x + 45
        
        if icon_low:
            img.paste(icon_low, (pane_x, vol_y - 10), icon_low)
        
        # Track (Standardized Grayish semi-opaque background)
        draw.rounded_rectangle([(vol_track_x, vol_y - 2), (vol_track_x + vol_track_w, vol_y + 10)], radius=6, fill=(120, 120, 120, 80))
        
        # Level (Rounded left, Flat right)
        if vol_passed_w > 6:
            draw.pieslice([(vol_track_x, vol_y - 2), (vol_track_x + 12, vol_y + 10)], 90, 270, fill="white")
            draw.rectangle([(vol_track_x + 6, vol_y - 2), (vol_track_x + vol_passed_w, vol_y + 10)], fill="white")
        else:
            draw.rounded_rectangle([(vol_track_x, vol_y - 2), (vol_track_x + vol_passed_w + 2, vol_y + 10)], radius=3, fill="white")
        
        if icon_high:
            img.paste(icon_high, (vol_track_x + vol_track_w + 13, vol_y - 10), icon_high)
        
        # 8. Bottom Icons
        bot_y = 635
        heart_x, heart_y = pane_x + 90, bot_y - 25
        heart_size = 35 # Reduced size
        
        icon_heart = load_icon("heart_filled", heart_size)
        if icon_heart:
            img.paste(icon_heart, (heart_x, heart_y + 14), icon_heart)
        
        icon_playlist = load_icon("playlist", 55) # Reduced size
        
        if icon_playlist:
            img.paste(icon_playlist, (pane_x + pane_w - 140, heart_y + 1), icon_playlist)
        
        img.save(path)
        return True
    except Exception as e:
        print(f"DEBUG: Sync PIL processing failed - {e}")
        return False