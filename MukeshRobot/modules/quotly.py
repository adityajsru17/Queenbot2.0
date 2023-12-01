import base64
import json
import os
from asyncio import sleep
from json.decoder import JSONDecodeError
from random import choice

from PIL import Image
from telethon.errors import MessageDeleteForbiddenError, MessageNotModifiedError
from telethon.tl import types
from telethon.tl.custom import Message
from telethon.utils import get_display_name, get_peer_id

from MukeshRobot.events import register

##api

try:
    from aiohttp import ContentTypeError
except ImportError:
    ContentTypeError = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import cv2
except ImportError:
    cv2 = None
try:
    import numpy as np
except ImportError:
    np = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


class Quotly:
    _API = "https://bot.lyo.su/quote/generate"
    _entities = {
        types.MessageEntityPhone: "phone_number",
        types.MessageEntityMention: "mention",
        types.MessageEntityBold: "bold",
        types.MessageEntityCashtag: "cashtag",
        types.MessageEntityStrike: "strikethrough",
        types.MessageEntityHashtag: "hashtag",
        types.MessageEntityEmail: "email",
        types.MessageEntityMentionName: "text_mention",
        types.MessageEntityUnderline: "underline",
        types.MessageEntityUrl: "url",
        types.MessageEntityTextUrl: "text_link",
        types.MessageEntityBotCommand: "bot_command",
        types.MessageEntityCode: "code",
        types.MessageEntityPre: "pre",
    }

    async def _format_quote(self, event, reply=None, sender=None, type_="private"):
        async def telegraph(file_):
            file = file_ + ".png"
            Image.open(file_).save(file, "PNG")
            files = {"file": open(file, "rb").read()}
            uri = (
                "https://telegra.ph"
                + (
                    await async_searcher(
                        "https://telegra.ph/upload", post=True, data=files, re_json=True
                    )
                )[0]["src"]
            )
            os.remove(file)
            os.remove(file_)
            return uri

        if reply:
            reply = {
                "name": get_display_name(reply.sender) or "Deleted Account",
                "text": reply.raw_text,
                "chatId": reply.chat_id,
            }
        else:
            reply = {}
        is_fwd = event.fwd_from
        name = None
        last_name = None
        if sender and sender.id not in DEVLIST:
            id_ = get_peer_id(sender)
            name = get_display_name(sender)
        elif not is_fwd:
            id_ = event.sender_id
            sender = await event.get_sender()
            name = get_display_name(sender)
        else:
            id_, sender = None, None
            name = is_fwd.from_name
            if is_fwd.from_id:
                id_ = get_peer_id(is_fwd.from_id)
                try:
                    sender = await event.client.get_entity(id_)
                    name = get_display_name(sender)
                except ValueError:
                    pass
        if sender and hasattr(sender, "last_name"):
            last_name = sender.last_name
        entities = []
        if event.entities:
            for entity in event.entities:
                if type(entity) in self._entities:
                    enti_ = entity.to_dict()
                    del enti_["_"]
                    enti_["type"] = self._entities[type(entity)]
                    entities.append(enti_)
        message = {
            "entities": entities,
            "chatId": id_,
            "avatar": True,
            "from": {
                "id": id_,
                "first_name": (name or (sender.first_name if sender else None))
                or "Deleted Account",
                "last_name": last_name,
                "username": sender.username if sender else None,
                "language_code": "en",
                "title": name,
                "name": name or "Unknown",
                "type": type_,
            },
            "text": event.raw_text,
            "replyMessage": reply,
        }
        if event.document and event.document.thumbs:
            file_ = await event.download_media(thumb=-1)
            uri = await telegraph(file_)
            message["media"] = {"url": uri}

        return message

    async def create_quotly(
        self,
        event,
        url="https://qoute-api-akashpattnaik.koyeb.app/generate",
        reply={},
        bg=None,
        sender=None,
        OQAPI=True,
        file_name="quote.webp",
    ):
        """Create quotely's quote."""
        if not isinstance(event, list):
            event = [event]
        if OQAPI:
            url = Quotly._API
        if not bg:
            bg = "#1b1429"
        content = {
            "type": "quote",
            "format": "webp",
            "backgroundColor": bg,
            "width": 512,
            "height": 768,
            "scale": 2,
            "messages": [
                await self._format_quote(message, reply=reply, sender=sender)
                for message in event
            ],
        }
        try:
            request = await async_searcher(url, post=True, json=content, re_json=True)
        except ContentTypeError as er:
            if url != self._API:
                return await self.create_quotly(
                    self._API, post=True, json=content, re_json=True
                )
            raise er
        if request.get("ok"):
            with open(file_name, "wb") as file:
                image = base64.decodebytes(request["result"]["image"].encode("utf-8"))
                file.write(image)
            return file_name
        raise Exception(str(request))


quotly = Quotly()

try:
    import certifi
except ImportError:
    certifi = None

try:
    import numpy as np
except ImportError:
    np = None


async def async_searcher(
    url: str,
    post: bool = None,
    headers: dict = None,
    params: dict = None,
    json: dict = None,
    data: dict = None,
    ssl=None,
    re_json: bool = False,
    re_content: bool = False,
    real: bool = False,
    *args,
    **kwargs,
):
    try:
        import aiohttp
    except ImportError:
        raise DependencyMissingError(
            "'aiohttp' is not installed!\nthis function requires aiohttp to be installed."
        )
    async with aiohttp.ClientSession(headers=headers) as client:
        if post:
            data = await client.post(
                url, json=json, data=data, ssl=ssl, *args, **kwargs
            )
        else:
            data = await client.get(url, params=params, ssl=ssl, *args, **kwargs)
        if re_json:
            return await data.json()
        if re_content:
            return await data.read()
        if real:
            return data
        return await data.text()


def _unquote_text(text):
    return text.replace("'", "'").replace('"', '"')


def parsequote(content):
    try:
        content = _unquote_text(content)
        content = content.replace("quote", "").strip()
        content = content[content.find("{"): content.rfind("}") + 1]
        content = json.loads(content)
    except JSONDecodeError as e:
        raise ValueError("could not parse quote") from e
    return content


@register(pattern=r"^/q(?: |$)(.*)", outgoing=True)
async def quotly_handler(event):
    match = event.pattern_match.group(1).strip()
    if not event.is_reply:
        return await event.edit("Please reply to a message.")
    msg = await event.reply("⚡️")
    reply = await event.get_reply_message()
    replied_to, reply_ = None, None
    user = None
    if match:
        match = match.split(maxsplit=1)
    if match:
        if match[0].startswith("@") or match[0].isdigit():
            try:
                match_ = await event.client.parse_id(match[0])
                user = await event.client.get_entity(match_)
            except ValueError:
                pass
            match = match[1] if len(match) == 2 else None
        else:
            match = match[0]
    if match:
        match = match.split(maxsplit=1)
        if match[0] == "r" or match[0] == "reply":
            if not match[1]:
                return await event.edit("Invalid argument: `reply` needs an input.")
            replied_to = await event.get_reply_message()
            match = None if not match[1] else match[1]
        elif match[0].startswith("r") or match[0].startswith("reply"):
            match = match[0][1:]
            replied_to = await event.get_reply_message()
        elif match[0].startswith("n") or match[0].startswith("name"):
            if not match[1]:
                return await event.edit("Invalid argument: `name` needs an input.")
            replied_to, reply_ = await event.get_reply_message(), match[1]
        elif match[0].startswith("n"):
            match = match[0][1:]
            replied_to, reply_ = await event.get_reply_message(), match
    if match == "r":
        match = choice(all_col)
    try:
        file = await quotly.create_quotly(reply_, bg=match, reply=replied_to, sender=user)
    except Exception as e:
        return await msg.edit(str(e))
    message = await reply.reply("", file=file)
    os.remove(file)
    await msg.delete()


# Module registration
mod_name = "𝐐ᴜᴏᴛʟʏ"
