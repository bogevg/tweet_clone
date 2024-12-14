from pydantic import BaseModel

class SchemaUser(BaseModel):
    id: int
    api_key: int
    name: str
    follower_ids: list[int] #айдишники подписчиков
    following_ids: list[int] # те, на кого пользователь подписан
    twit_ids: list[int]


class SchemaTweetCreate(BaseModel):
    tweet_data: str
    tweet_media_ids: list[int]

