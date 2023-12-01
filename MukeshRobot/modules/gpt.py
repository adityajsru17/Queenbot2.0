import requests
from MukeshRobot import telethn as tbot
from MukeshRobot.events import register

GPT_API_URL = "https://chatgpt.apinepdev.workers.dev"


@register(pattern="^/gpt (.*)")
async def chat_gpt(event):
    if event.fwd_from:
        return

    query = event.pattern_match.group(1)

    params = {"message": query}
    response = requests.post(GPT_API_URL, data=params)

    if response.status_code == 200:
        result = response.json()

        # Check if "join" key is present and remove it
        if "join" in result:
            del result["join"]

        reply_message = result.get("message", "No response from ChatGPT")
    else:
        reply_message = "Error communicating with ChatGPT API"

    await event.reply(reply_message)


__mod_name__ = "ChatGPT"
