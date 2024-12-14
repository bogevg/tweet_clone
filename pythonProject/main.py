from fastapi import FastAPI

from pythonProject.models import User
from routers import api_router
from fastapi.staticfiles import StaticFiles
import uvicorn

from database import Session

app = FastAPI(title="twits")
app.include_router(api_router)

app.mount('/', StaticFiles(directory='static', html=True))

# session = Session()
# #test_user1 = User(api_key="test", name='krytaypshka')
# test_user2 = User(api_key="test2", name='vto      roy')
# #session.add(test_user1)
# session.add(test_user2)
# session.commit()
# session.close()


if __name__ == "__main__":
    uvicorn.run("main:app",  host = "127.0.0.1", port = 8000)