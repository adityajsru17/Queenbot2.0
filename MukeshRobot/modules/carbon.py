import requests
from pyrogram import filters
from MukeshRobot import pbot
from MukeshRobot.utils.errors import capture_err

CARBON_API_URL = "https://carbonara.solopov.dev/api/cook"

@pbot.on_message(filters.command("carbon"))
@capture_err
async def carbon_func(_, message):
    if message.reply_to_message:
        if message.reply_to_message.text:
            txt = message.reply_to_message.text
        else:
            return await message.reply_text("Reply to a message or provide some text.")
    else:
        try:
            txt = message.text.split(None, 1)[1]
        except IndexError:
            return await message.reply_text("Reply to a message or provide some text.")

    m = await message.reply_text("Generating carbon...")
    
    # Make a request to the external API to generate the carbon image
    response = requests.post(CARBON_API_URL, json={"code": txt})
    
    if response.status_code == 200:
        # Successfully received the carbon image
        carbon_image_url = response.json().get("url")
        await m.edit_text("Uploading generated carbon...")
        await pbot.send_photo(
            message.chat.id,
            photo=carbon_image_url,
            caption=f"Requested by: {message.from_user.mention}",
        )
    else:
        # Handle API error
        await m.edit_text(f"Failed to generate carbon image. API Error: {response.text}")

    await m.delete()

__mod_name__ = "Carbon"

__help__ = """
Generates a carbon image of the given text and sends it to you.

❍ /carbon *:* Generates carbon if replied to a text
"""
