from fastapi_laser import fastapi_ext


router = fastapi_ext.get_router()


@router.get("/ping")
async def ping():
    return {"message": "Pong"}
