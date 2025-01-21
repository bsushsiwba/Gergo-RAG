from fastapi import APIRouter


router = APIRouter()


@router.get(
    "/",
    summary="Default Endpoint to check if site is running corectly",
    description=(
        "This is the default endpoint to check if the site is running correctly. "
    ),
    responses={
        200: {
            "description": "Site is running correctly",
            "content": {
                "application/json": {
                    "example": "The site is running correctly, use chat endpoint."
                }
            },
        },
        500: {
            "description": "Internal Server Error",
            "content": {"application/json": {"example": "Internal Server Error"}},
        },
    },
)
def welcome():
    return "The site is running correctly, use chat endpoint."
