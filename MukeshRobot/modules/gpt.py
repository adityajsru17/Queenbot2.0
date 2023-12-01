import requests
from MukeshRobot import telethn as tbot
from MukeshRobot.events import register

GPT_API_URL = "https://chatgpt.apinepdev.workers.dev"


@register(pattern="^/gpt (.*)")
async def chat_gpt(event):
    if event.fwd_from:
        return

    query = event.pattern_match.group(1)

    if query:
        # Make a request to GPT API
        response = requests.get(f"{GPT_API_URL}/?question={query}")

        if response.status_code == 200:
            # Extract the answer from the API response
            result = response.json()

            # Check if "join" key is present and remove it
            if "join" in result:
                del result["join"]

            reply_message = result.get("answer", "No answer received from ChatGPT.")
        else:
            reply_message = "Error communicating with ChatGPT API."
    else:
        reply_message = "Please provide a question after /gpt command."

    await event.reply(reply_message)


__mod_name__ = "ChatGPT"
