from datetime import datetime
from sqlalchemy import ForeignKey, Table, Column, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref
from database import Base, engine

follows = Table( "follows", Base.metadata,
               #сам юзер
        Column("follower_id", Integer, ForeignKey("users.id")),
               #его подписка
              Column("following_id", Integer, ForeignKey("users.id"))
                 )

likes = Table("likes", Base.metadata,
              Column("id_twit", Integer, ForeignKey("twits.id")),
                    Column("id_user", Integer, ForeignKey("users.id"))
              )

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    api_key: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    twits: Mapped[list["Twit"]] = relationship(back_populates="user",cascade="all, delete-orphan", uselist=True)
    #все подписьки))
    following: Mapped[list["User"]] = relationship(
        "User",
        secondary=follows,
        primaryjoin=id == follows.c.follower_id,
        secondaryjoin=id == follows.c.following_id,
        backref=backref("followers", lazy="dynamic") #создаем обратное отношение таблиц
    )#че в итоге то - user.following - подписки юзера, user.follover - подписчики пользователя
    liked_twits: Mapped[list["Twit"]] = relationship(
        "Twit",
        secondary=likes,
        back_populates="likers",
        uselist=True
    )



class Twit(Base):
    __tablename__= 'twits'
    id: Mapped[int] = mapped_column(primary_key= True, autoincrement=True)
    text_content: Mapped[str]
    user: Mapped["User"] = relationship(back_populates="twits", uselist=False)
    id_user: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete='CASCADE'))
    images: Mapped[list["Twit_image"]] = relationship(back_populates='twit',cascade="all, delete-orphan", uselist=True)
    data_pub: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    likers: Mapped[list["User"]] = relationship(
        "User",
        secondary=likes,
        back_populates="liked_twits",
        uselist=True
    )


class Twit_image(Base):
    __tablename__ = 'twit_image'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement= True)
    twit: Mapped["Twit"] = relationship(back_populates="images", uselist=False)
    id_twit: Mapped[int] = mapped_column(ForeignKey("twits.id",ondelete='CASCADE'))
    url_media: Mapped[str]


Base.metadata.create_all(engine)
