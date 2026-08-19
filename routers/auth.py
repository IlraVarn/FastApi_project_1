from fastapi import APIRouter, Depends

from auth.dependencies import AuthContext, get_authenticated_user


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.get("/me")
def get_me(
    current_user: AuthContext = Depends(get_authenticated_user),
):
    return {
        "user_id": current_user.user_id,
    }


