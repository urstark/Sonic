
import os
import random
import asyncio
from datetime import datetime 
from telegraph import upload_file
from PIL import Image , ImageDraw
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatType, ParseMode

#BOT FILE NAME
from Sonic import app as app

def get_button():
    try:
        username = app.username if app.username else "BotUsername"
    except:
        username = "BotUsername"
    return [
        [
            InlineKeyboardButton(
                text="➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ",
                url=f"https://t.me/{username}?startgroup=true",
            ),
        ],
    ]

def dt():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M")
    dt_list = dt_string.split(" ")
    return dt_list

def dt_tom():
    a = (
        str(int(dt()[0].split("/")[0]) + 1)
        + "/"
        + dt()[0].split("/")[1]
        + "/"
        + dt()[0].split("/")[2]
    )
    return a

tomorrow = str(dt_tom())
today = str(dt()[0])

def prepare_pfp(path, size=(480, 480), border_width=0, border_color="white"):
    """Processed PFP with high-quality circular crop and optional border."""
    try:
        # Open and ensure RGBA
        img = Image.open(path).convert("RGBA")
        img = img.resize(size, Image.LANCZOS)
        
        # Create high-res mask for better AA
        mask_size = (size[0] * 4, size[1] * 4)
        mask = Image.new('L', mask_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + mask_size, fill=255)
        mask = mask.resize(size, Image.LANCZOS)
        
        # Apply circular crop
        output = Image.new('RGBA', size, (0, 0, 0, 0))
        output.paste(img, (0, 0), mask)
        
        # Add border if requested
        if border_width > 0:
            border_mask = Image.new('L', mask_size, 0)
            border_draw = ImageDraw.Draw(border_mask)
            # Draw a slightly larger circle for the border
            border_draw.ellipse((0, 0) + mask_size, outline=255, width=border_width * 4)
            border_mask = border_mask.resize(size, Image.LANCZOS)
            
            border_img = Image.new('RGBA', size, border_color)
            output.paste(border_img, (0, 0), border_mask)
            
        return output
    except Exception as e:
        print(f"Error preparing PFP: {e}")
        return None

def generate_couples_image(p1_path, p2_path, output_path):
    # --- CONFIGURATION AREA ---
    PFP_SIZE = (487, 487)      # Increase this to make PFPs bigger
    BORDER_WIDTH = 0           # Set to 0 to remove, or higher for a thicker border
    BORDER_COLOR = "#FFFFFF"   # White border looks best
    
    # Coordinates (using your latest adjustments)
    COORD_P1 = (73, 160)
    COORD_P2 = (734, 160)
    # --------------------------

    try:
        img1 = prepare_pfp(p1_path, size=PFP_SIZE, border_width=BORDER_WIDTH, border_color=BORDER_COLOR)
        img2 = prepare_pfp(p2_path, size=PFP_SIZE, border_width=BORDER_WIDTH, border_color=BORDER_COLOR)
        
        bg_path = "Sonic/assets/couples.jpg"
        if not os.path.exists(bg_path):
             print(f"Error: Background asset not found at {bg_path}")
             return False
             
        background = Image.open(bg_path).convert("RGBA")

        if img1:
            background.paste(img1, COORD_P1, img1)
        if img2:
            background.paste(img2, COORD_P2, img2)

        background.save(output_path)
        return True
    except Exception as e:
        print(f"Error generating couples image: {e}")
        return False

@app.on_message(filters.command(["couples", "couple"]))
async def ctest(_, message):
    cid = message.chat.id
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("This command only works in groups.")
    
    p1 = None
    p2 = None
    output_img = f'test_{cid}_{message.id}.png'
    
    try:
         msg = await message.reply_text("Generating couples image...")
         #GET LIST OF USERS
         list_of_users = []
         async for i in app.get_chat_members(cid, limit=50):
             if not i.user.is_bot:
                list_of_users.append(i.user.id)

         if len(list_of_users) < 2:
            return await msg.edit_text("Not enough users to generate a couple.")

         c1_id = random.choice(list_of_users)
         c2_id = random.choice(list_of_users)
         while c1_id == c2_id:
              c1_id = random.choice(list_of_users)

         u1 = await app.get_users(c1_id)
         u2 = await app.get_users(c2_id)
         
         photo1 = u1.photo
         photo2 = u2.photo
  
         N1 = u1.mention 
         N2 = u2.mention
         
         try:
            if photo1:
                p1 = await app.download_media(photo1.big_file_id, file_name=f"pfp_{c1_id}_{message.id}.png")
            else:
                p1 = "Sonic/assets/upic.png"
         except Exception:
            p1 = "Sonic/assets/upic.png"
            
         try:
            if photo2:
                p2 = await app.download_media(photo2.big_file_id, file_name=f"pfp_{c2_id}_{message.id}.png")
            else:
                p2 = "Sonic/assets/upic.png"
         except Exception:
            p2 = "Sonic/assets/upic.png"
            
         is_generated = await asyncio.to_thread(generate_couples_image, p1, p2, output_img)
         if is_generated:
             TXT = f"""
<b>Today's Couple Of The Day:</b>

{N1} + {N2} = ❤️

<b>Next couples will be selected on {tomorrow} !!</b>
"""
             try:
                 await msg.delete()
             except:
                 pass

             await message.reply_photo(output_img, caption=TXT, reply_markup=InlineKeyboardMarkup(get_button()), parse_mode=ParseMode.HTML)
         else:
             await msg.edit_text("Failed to generate couples image. Please check bot logs.")
    
    except Exception as e:
        print(f"Couples Error: {e}")
    finally:
        try:
            if p1 and p1 != "Sonic/assets/upic.png" and os.path.exists(p1):
                os.remove(p1)
            if p2 and p2 != "Sonic/assets/upic.png" and os.path.exists(p2):
                os.remove(p2)
            if os.path.exists(output_img):
                os.remove(output_img)
        except Exception:
            pass
         

__mod__ = "COUPLES"
__help__ = """
** /couples** - Get Todays Couples Of The Group In Interactive View
"""
