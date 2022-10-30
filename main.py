from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from fastapi import (
    FastAPI, Query, Path, Body, Cookie, Header, status, Form, File, UploadFile,
    HTTPException, Depends, Request, BackgroundTasks
)
from datetime import datetime, time, timedelta
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None
    tags: set[str] = Field(default=set(), example={"tag1", "tag2"})
    images: list[Image] | None = Field(
        default=None, description="Here you can save your images"
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            }
        }


class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]


class User(BaseModel):
    username: str
    full_name: str | None = None


class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None


class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "items",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]


description = """
ChimichangApp API helps you do awesome stuff. 🚀

## Items

You can **read items**.

## Users

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).
"""


app = FastAPI(
    title="ChimichangApp",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Deadpoolio the Amazing",
        "url": "http://x-force.example.com/contact/",
        "email": "dp@x-force.example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {"message": "Hello World"}


@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
        user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    match model_name:
        case ModelName.alexnet:
            return {"model_name": model_name, "message": "Deep Learning FTW!"}

        case ModelName.lenet:
            return {"model_name": model_name, "message": "Deep Learning FTW!"}

        case ModelName.resnet:
            return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


fake_items_db = [
    {"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}
]


@app.get("/item/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip:skip + limit]


# @app.get("/items/")
# async def read_items(ads_id: str | None = Cookie(default=None)):
#     return {"ads_id": ads_id}


# @app.get("/items/")
# async def read_items(user_agent: str | None = Header(default=None)):
#     return {"User-Agent": user_agent}


@app.get("/items/")
async def read_items(q: str | None = Query(default=None, title="Query String",
                                           description="Query string for the items to search in the database that have a good match",
                                           alias="item-query",
                                           deprecated=True,
                                           min_length=3, max_length=50, regex="fixedquery")):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item


@app.put("/items/{item_id}")
async def update_item(
        *,
        item_id: int = Path(title="The ID of the item to get", ge=0, le=1000),
        q: str | None = None,
        item: Item = Body(
            example={
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            },
            default=None
        ),
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if item:
        results.update({"item": item})
    return results


@app.get("/items/{item_id}")
async def read_items(
        item_id: int = Path(title="The ID of the item to get", ge=1, le=1000),
        q: str | None = Query(default=None, alias="item-query"),
        size: float = Query(gt=0, lt=10.5)
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, user: User, importance: int = Body()):
    results = {"item_id": item_id, "item": item, "user": user}
    return results


@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer


@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):
    return images


@app.put("/items/{item_id}")
async def read_items(
    item_id: UUID,
    start_datetime: datetime | None = Body(default=None),
    end_datetime: datetime | None = Body(default=None),
    repeat_at: time | None = Body(default=None),
    process_after: timedelta | None = Body(default=None),
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "repeat_at": repeat_at,
        "process_after": process_after,
        "start_process": start_process,
        "duration": duration,
    }


@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn):
    return user


@app.post("/login/")
async def login(username: str = Form(), password: str = Form()):
    return {"username": username}


@app.post("/files/")
async def create_file(file: bytes = File()):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}


# items = {
#     "foo": {"name": "Foo", "price": 50.2},
#     "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
#     "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
# }

# @app.patch("/items/{item_id}", response_model=Item)
# async def update_item(item_id: str, item: Item):
#     stored_item_data = items[item_id]
#     stored_item_model = Item(**stored_item_data)
#     update_data = item.dict(exclude_unset=True)
#     updated_item = stored_item_model.copy(update=update_data)
#     items[item_id] = jsonable_encoder(updated_item)
#     return updated_item


async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons


@app.get("/users/")
async def read_users(commons: dict = Depends(common_parameters)):
    return commons


class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


@app.get("/items/")
# async def read_items(commons: CommonQueryParams = Depends()): shortcut
async def read_items(commons: CommonQueryParams = Depends(CommonQueryParams)):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response.update({"items": items})
    return response


async def verify_token(x_token: str = Header()):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: str = Header()):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


@app.get("/items/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items():
    return [{"item": "Foo"}, {"item": "Bar"}]


# global dependencies
# app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


def write_notification(email: str, message=""):
    with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)


@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}
