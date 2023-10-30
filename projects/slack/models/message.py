
from typing import List, Optional
from slack_sdk.models.blocks import Block
from slack_sdk.models.attachments import Attachment
from slack_sdk.models.files import File
from slack_sdk.models.reaction import Reaction
from slack_sdk.models.user import User

class Message:
    def __init__(
            self,
            text: str,
            blocks: Optional[List[Block]] = None,
            attachments: Optional[List[Attachment]] = None,
            files: Optional[List[File]] = None,
            reactions: Optional[List[Reaction]] = None,
            user: Optional[User] = None,
            ts: Optional[str] = None,
            thread_ts: Optional[str] = None,
            reply_count: Optional[int] = None,
            replies: Optional[List[Message]] = None,
    ):
        self.text = text
        self.blocks = blocks
        self.attachments = attachments
        self.files = files
        self.reactions = reactions
        self.user = user
        self.ts = ts
        self.thread_ts = thread_ts
        self.reply_count = reply_count
        self.replies = replies

    @classmethod
    def from_dict(cls, data: dict):
        text = data.get("text")
        blocks = data.get("blocks")
        attachments = data.get("attachments")
        files = data.get("files")
        reactions = data.get("reactions")
        user = User.from_dict(data.get("user"))
        ts = data.get("ts")
        thread_ts = data.get("thread_ts")
        reply_count = data.get("reply_count")
        replies = [cls.from_dict(reply) for reply in data.get("replies", [])]
        return cls(
            text=text,
            blocks=blocks,
            attachments=attachments,
            files=files,
            reactions=reactions,
            user=user,
            ts=ts,
            thread_ts=thread_ts,
            reply_count=reply_count,
            replies=replies,
        )