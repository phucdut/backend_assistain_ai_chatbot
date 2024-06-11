from fastapi import APIRouter

from app.api.v1.endpoints import auth, chatbot, conversation, user, payment, dashboard, public, subscription_plan

api_router = APIRouter()
api_router.include_router(public.router, prefix="/public",
                          tags=["public"])
api_router.include_router(auth.router, prefix="/auth",
                          tags=["authentications"])
api_router.include_router(chatbot.router, prefix="/chatbot",
                          tags=["chatbots"])
api_router.include_router(conversation.router, prefix="/conversation",
                          tags=["conversations"])
api_router.include_router(subscription_plan.router, prefix="/subscription_plan",
                          tags=["subscription_plans"])
api_router.include_router(user.router, prefix="/user", tags=["users"])
api_router.include_router(payment.router, prefix="/payment", tags=["payments"])
api_router.include_router(
    dashboard.router, prefix="/dashboard", tags=["dashboard"]
)