from fastapi import APIRouter, Depends
from app.authentication.oauth2 import get_current_user
from app.database.models import UserModel, BirthdayModel
from app.birthdays.schemas import Birthday
from beanie import WriteRules
from fastapi import status

router = APIRouter(prefix="/api/v1/birthdays", tags=["birthdays"])


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add(birthday: Birthday, user: UserModel = Depends(get_current_user)):
    saved_birthday = await BirthdayModel(**birthday.dict()).create()
    user.birthdays = [saved_birthday]
    await user.save(link_rule=WriteRules.WRITE)

    birthday_db = await BirthdayModel.get(saved_birthday.id)
    return birthday_db
