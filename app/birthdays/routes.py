from fastapi import APIRouter, Depends, HTTPException, Query
from app.authentication.oauth2 import get_current_user
from app.database.models import UserModel, BirthdayModel
from app.birthdays.schemas import Birthday
from beanie import WriteRules
from fastapi import status
from beanie import PydanticObjectId

router = APIRouter(prefix="/api/v1/birthdays", tags=["birthdays"])


@router.post(
    "/add",
    status_code=status.HTTP_201_CREATED,
    response_model=BirthdayModel
)
async def add_birthday(
    birthday: Birthday,
    user: UserModel = Depends(get_current_user),
):
    saved_birthday = await BirthdayModel(**birthday.dict()).create()
    user.birthdays = [saved_birthday]
    await user.save(link_rule=WriteRules.WRITE)

    birthday_db = await BirthdayModel.get(saved_birthday.id)
    return birthday_db


@router.get("/{birthday_id}", response_model=BirthdayModel)
async def get_birthday(birthday_id: PydanticObjectId):
    birthday = await BirthdayModel.get(birthday_id)

    if not birthday:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Such birthday does not exist'
        )

    return birthday
