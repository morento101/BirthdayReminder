from beanie import PydanticObjectId, WriteRules
from fastapi import APIRouter, Depends, status, Response

from app.authentication.oauth2 import get_current_user
from app.birthdays.schemas import Birthday, UpdateBirthday
from app.core.utils import get_or_404
from app.database.models import BirthdayModel, UserModel

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
async def get_birthday(
    birthday_id: PydanticObjectId,
    user: UserModel = Depends(get_current_user),
):
    return await get_or_404(BirthdayModel, birthday_id)


@router.patch("/{birthday_id}", response_model=BirthdayModel)
async def edit_birthday(
    birthday_id: PydanticObjectId,
    birthday_data: UpdateBirthday,
    user: UserModel = Depends(get_current_user),
):
    birthday = await get_or_404(BirthdayModel, birthday_id)

    update_query = {"$set": {
        field: value
        for field, value
        in birthday_data.dict(exclude_none=True).items()
    }}

    await birthday.update(update_query)
    return birthday


@router.delete("/{birthday_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_birthday(
    birthday_id: PydanticObjectId,
    user: UserModel = Depends(get_current_user)
):
    birthday = await get_or_404(BirthdayModel, birthday_id)
    await birthday.delete()
