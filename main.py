import strawberry
import uvicorn
from fastapi import Depends, FastAPI
from fastapi_pagination import add_pagination
from strawberry.fastapi import GraphQLRouter

from db.session import create_db_and_tables
from graphql_schemas.context import Context
from graphql_schemas.mutation import Mutation
from graphql_schemas.query import Query
from models.user import User
from schemas.users_schemas import UserCreate, UserRead, UserUpdate
from auth.auth import auth_backend, current_active_user, fastapi_users, get_user_manager
from chat.chat import router as chat_router

app = FastAPI(title="WORKERS API")
add_pagination(app)


async def get_context(user_manager=Depends(get_user_manager)) -> Context:
    return Context(user_manager)


schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
app.include_router(chat_router)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


# @app.on_event("startup")
# async def on_startup():
#     # Not needed if you setup a migration system like Alembic
#     await create_db_and_tables()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", log_level="info", reload=True)
