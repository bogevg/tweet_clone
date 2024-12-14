from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select, desc, delete, exists

from database import Session, get_db
from pythonProject.models import User, Twit, Twit_image, follows
from pythonProject.schems import SchemaUser, SchemaTweetCreate

api_router = APIRouter(prefix="/api")


@api_router.get("/users/me")
def get_self_user(api_key: str = Header(None), db: Session = Depends(get_db)):
    if not api_key:
        raise HTTPException(detail="API key is required")

    user = db.query(User).filter(User.api_key == api_key).limit(1).first()
    if user:
        followers = [{'id': str(follower.id), 'name': follower.name} for follower in user.followers]
        following = [{'id': str(following_user.id), 'name': following_user.name} for following_user in user.following]
        return {
                "result": "true",
                "user": {
                        "id": user.id,
                        "name": user.name
                         },
                "followers": followers,
                "following": following
                }
    else:
        return {"result": "false"}




@api_router.post("/tweets")
def save_tweet(input_tweet: SchemaTweetCreate, api_key: str = Header(None), db: Session = Depends(get_db)):
    if not api_key:
        raise HTTPException(detail="API key is required")
    id_user = db.scalar(select(User.id).where(User.api_key == api_key))
    if id_user is None:
        raise HTTPException(detail="User not found")
    try:
        tweet = Twit(text_content=input_tweet.tweet_data, id_user=id_user)
        db.add(tweet)
        db.flush()
        db.refresh(tweet)
        for img_id in input_tweet.tweet_media_ids:
            tweet_img = Twit_image(id_twit=tweet.id, url_media=f"images/{img_id}")
            db.add(tweet_img)
        db.commit()
        print("твит успешно добавлен")
        return {"result": True,
                "tweet_id": tweet.id}
    except Exception as e:
        db.rollback()  # Откат изменений в случае ошибки
        return {"result": False}


@api_router.delete("/tweets/{id}")
def delete_tweet(id: int, api_key: str = Header(None), db: Session = Depends(get_db)):
    try:
        tweet = db.execute(select(Twit).where(Twit.id == id)).scalar_one_or_none()
        if not tweet:
            raise HTTPException(detail="Твит не найден")
        if tweet.user_id != db.scalar(select(User.id).where(User.api_key == api_key)):
            raise HTTPException(detail="Вы не можете удалить не свой твит")
        db.execute(delete(Twit).where(Twit.id == id)) # все норм удалится, потому что добавла каскад                 наверное нормально.....
        db.commit()
        return {"result": True}

    except Exception as e:
        print(f"Ошибка при удалении твита: {e}")
        db.rollback()  # откатываем транзакцию в случае ошибки
        return {"result": False}


@api_router.post("/tweets/{id}/likes")
def like_to_tweet(id: int, api_key: str = Header(None), db: Session = Depends(get_db)):
    try:
        if not api_key:
            raise HTTPException(detail="API key is required")
        user = db.scalar(select(User).where(User.api_key == api_key))
        if user is None:
            raise HTTPException(detail="User not found")
        tweet = db.scalar(select(Twit).where(Twit.id == id))
        if tweet is None:
            raise HTTPException(detail="Tweet not found")#на всякий проверяем, что твит существует
            # может твит уже лайкнут, проверим
        is_liked = db.execute(select(exists().where(Twit.likers.any(id=user.id), Twit.id == id))).scalar()
        if not is_liked: #если лайка еще нет, то надо добавить
            tweet.likers.append(user)
            message = True
        else:
            tweet.likers.remove(user)
            message = False
        db.commit()
        return {"result": message}
    except Exception as e:
        print(f"Ошибка с лайком: {e}")
        db.rollback()
        return {"result": False}






@api_router.post("/users/{id}/follow")
def following(id: int, api_key: str = Header(None), db: Session = Depends(get_db)):
    try:
        user = db.execute(select(User).where(User.api_key == api_key)).scalar_one_or_none()
        if not user:
            raise HTTPException(detail="API key is required")
        following_user = db.execute(select(User).where(User.id == id)).scalar_one_or_none()
        if following_user is None:
            raise HTTPException(detail="Пользователь не найден")
        if id == user.id:
            raise HTTPException(detail="Невозможно подписаться на себя")
        is_already_following = db.execute(select(exists().where(follows.c.follower_id == user.id, follows.c.following_id == following_user.id))).scalar()
        if is_already_following:
            raise HTTPException(detail="Вы уже подписаны на этого пользователя")
        user.following.append(following_user)  # Добавляем подписку через relationship
        db.commit()
        return {"result": True}

    except Exception as e:
        print(f"Ошибка при попытке подписаться: {e}")
        db.rollback()
        return {"result": False}

@api_router.delete("/users/{id}/follow")
def unfollowing(id: int, api_key: str = Header(None), db: Session = Depends(get_db)):
    try:
        user = db.execute(select(User).where(User.api_key == api_key)).scalar_one_or_none()
        if not user:
            raise HTTPException(detail="API key is required")
        following_user = db.execute(select(User).where(User.id == id)).scalar_one_or_none()
        if following_user is None:
            raise HTTPException(detail="Пользователь не найден")
        if id == user.id:
            raise HTTPException(detail="Невозможно подписаться на себя")
        is_already_following = db.execute(select(exists().where(follows.c.follower_id == user.id, follows.c.following_id == following_user.id))).scalar()
        if not is_already_following:
            raise HTTPException(detail="Вы не подписаны на этого пользователя")
        user.following.remove(following_user)
        db.commit()
        return {"result": True}

    except Exception as e:
        print(f"Ошибка при попытке отписаться: {e}")
        db.rollback()








# @api_router.delete("/tweets/{id}/like") бля я хз почему не рбоатет так
# def unlike_to_tweet(id: int, api_key: str = Header(None), db: Session = Depends(get_db)):
#     try:
#         if api_key is None:
#             raise HTTPException(detail="API key is required")
#         user = db.scalar(select(User).where(User.api_key == api_key))
#         if user is None:
#             raise HTTPException(detail="User not found")
#         tweet = db.scalar(select(Twit).where(Twit.id == id))
#         if tweet is None:
#             raise HTTPException(detail="Tweet not found")#на всякий проверяем, что твит существует
#             # может твит не лайкнут, проверим
#         is_liked = db.execute(select(exists().where(Twit.likers.any(id=user.id), Twit.id == id))).scalar()
#         if not is_liked:
#             return {"result": False}
#
#         tweet.likers.remove(user)
#         db.commit()
#         return {"result": True}
#         print("ура дулили лайк")
#
#     except Exception as e:
#         print(f"Ошибка при удалении лайка: {e}")
#         db.rollback()
#         raise HTTPException(detail=f"Ошибка при удалении лайка: {e}")


@api_router.get("/users/{id}")
def get_inf_user(id: int, db: Session = Depends(get_db)):
    try:
        user = db.execute(select(User).where(User.id == id)).scalar_one_or_none()
        if not user:
            raise HTTPException(detail="User не существует")

        return {
            "result":True,
            "user":{
                "id": user.id,
                "name": user.name,
                "followers": user.twits
            }
        }

    except HTTPException as e:
        print(f"Ошибка : {e}")
        return {"result": False}










@api_router.get("/tweets")
def get_tweets(api_key: str = Header(None), db: Session = Depends(get_db)):
    # #мне необходимо получить список твитов. он состоит из твитов изеров, на которых подписан пользователь. твиты должны быть отсортирован по популярности
    # if api_key is None:
    #     raise HTTPException(detail="API key is required")
    # user = db.scalar(select(User).where(User.api_key == api_key))
    # if not user:
    #     raise HTTPException(detail="User not found")
    # twits = select(Twit).join(follows, follows.c.following_id == Twit.id_user).were()
    try: #пока тут все твиты, а не только подписок пользователей
        tweets = db.execute(select(Twit).order_by(desc(Twit.data_pub))).scalars().all()

        if not tweets:
            return {"result": False, "message": "Нет твитов"}
        tweets_list = []
        for tweet in tweets:
            tweet_data = {
                "id": tweet.id,
                "content": tweet.text_content,
                "attachments": [a.url_media for a in tweet.images],  # Получаем ссылки на медиа
                "author": {"id": tweet.user.id, "name": tweet.user.name},
                "likes": [{"tweet_id": tweet.id, "user_id": liker.id} for liker in tweet.likers]
            }
            tweets_list.append(tweet_data)
        return {"result": True, "tweets": tweets_list}
    except HTTPException as e:
        return {
            "result": False,
            "error_type": e,
            "error_message": e
        }
@api_router.delete("/tweets/{id}/likes")
def like_delete():
    pass