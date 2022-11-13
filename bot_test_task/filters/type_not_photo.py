from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class FileTypeFilter(BoundFilter):
    """
    Check message content type
    """

    key = 'not_content_types'
    required = True
    default = types.ContentTypes.TEXT

    def __init__(self, not_content_types):
        if isinstance(not_content_types, str):
            not_content_types = (not_content_types,)
        self.not_content_types = not_content_types

    async def check(self, message):
        return types.ContentType.ANY not in self.content_types or \
               message.content_type not in self.content_types
