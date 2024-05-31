import re
from datetime import datetime
from typing import List, Optional
from fastapi import Depends, HTTPException

from fastapi import Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.common.logger import setup_logger
from app.core.config import settings
from app.core.vnpay import Vnpay
from app.services.abc.payment_vnpay_service import PaymentVnPayService

from app.crud.crud_user import crud_user
from app.crud.crud_subscription_plan import crud_subscription_plan
from app.crud.crud_user_subscription import crud_user_subscription
from app.schemas.user_subscription_plan import UserSubscriptionPlan

from app.schemas.user_subscription import (
    UserSubscriptionUpdate,
    UserSubscriptionOut,
)

logger = setup_logger()


class PaymentVnPayServiceImpl(PaymentVnPayService):
    def __init__(self):
        self.__vnpay = Vnpay(
            tmn_code=f"{settings.VNPAY_TMN_CODE}",
            secret_key=f"{settings.VNPAY_HASH_SECRET_KEY}",
            return_url=f"{settings.VNPAY_RETURN_URL}",
            vnpay_payment_url=f"{settings.VNPAY_PAYMENT_URL}",
            api_url=f"{settings.VNPAY_API_URL}",
        )
        self.__crud_user = crud_user
        self.__crud_subscription_plan = crud_subscription_plan
        self.__crud_user_subscription = crud_user_subscription

    def read_root(
        self, vnp_Amount: str, vnp_TxnRef: str, vnp_OrderInfo: str
    ) -> RedirectResponse:
        req = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": f"{settings.VNPAY_TMN_CODE}",
            "vnp_Amount": vnp_Amount,
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": vnp_TxnRef,
            "vnp_OrderInfo": vnp_OrderInfo,
            "vnp_OrderType": "ao_tunaasd",
            "vnp_Locale": "vn",
            "vnp_BankCode": "NCB",
            "vnp_CreateDate": datetime.now().strftime("%Y%m%d%H%M%S"),
            "vnp_IpAddr": "192.168.1.11",
            "vnp_ReturnUrl": f"{settings.VNPAY_RETURN_URL}",
        }
        return RedirectResponse(self.__vnpay.get_payment_url(req))

    # def read_item(self, request: Request, db: Session) -> str:
    #     data = request.query_params.items()

    #     response = {}
    #     for i in data:
    #         response[i[0]] = i[1]
    #     if self.__vnpay.validate_response(response):
    #         return "Thành công"
    #     else:
    #         return "Thất bại"

    def read_item(self, request: Request, db: Session) -> RedirectResponse:
        response = dict(request.query_params)
        res_vnp_Amount = str(int(response.get("vnp_Amount")) / 100)

        if not self.__vnpay.validate_response(response):
            logger.error("Payment validation failed")
            return RedirectResponse(
                f"{settings.REDIRECT_FRONTEND_URL}/user/payment-failure?vnp_Amount={res_vnp_Amount}&vnp_TxnRef={response['vnp_TxnRef']}"
            )

        try:
            url = response["vnp_OrderInfo"]
            # logger.info("Payment validation succeeded", url)
            match = re.search(
                r"user_id=(\S+)\s+subscription_plan_id=(\S+)", url
            )
            if match:
                user_id = match.group(1)
                subscription_plan_id = match.group(2)
            else:
                print(
                    "Không tìm thấy user_id và subscription_plan_id trong vnp_OrderInfo"
                )

            logger.info("Payment validation succeeded", user_id, subscription_plan_id)
            # user = self.__crud_user.get(db=db, id=user_id)
            # if not user or user.status in [
            #     "ORDER-CANCELLED",
            #     "ORDER-DELIVERED",
            # ]:
            #     logger.error("Invalid order status or order not found")
            #     return RedirectResponse(
            #         f"{settings.REDIRECT_FRONTEND_URL}/user/payment-failure?vnp_Amount={res_vnp_Amount}&vnp_TxnRef={response['vnp_TxnRef']}"
            #     )
            user_subscription = self.get_edit_one_with_filter_or_none(
                db=db, filter={"user_id": user_id}
            )
            if user_subscription is None:
                logger.exception(
                    f"Exception in {__name__}.{self.__class__.__name__}.update_one_with_filter: user not found"
                )
                raise HTTPException(
                    detail="Update user subscription plan failed: User not found",
                    status_code=404,
                )

            upgrade_membership = self.__crud_user_subscription.update_one_by(
                db=db,
                filter={"user_id": user_id},
                obj_in=UserSubscriptionUpdate(
                    plan_id=subscription_plan_id, updated_at=datetime.now()
                ),
            )
            if not upgrade_membership:
                logger.error("Upgrade membership update failed")
                return RedirectResponse(
                    f"{settings.REDIRECT_FRONTEND_URL}/success/?payment-failure?vnp_Amount={res_vnp_Amount}&vnp_TxnRef={response['vnp_TxnRef']}"
                )
        except Exception as e:
            logger.error(f"Error: {e}")
            return RedirectResponse(
                f"{settings.REDIRECT_FRONTEND_URL}/success/?payment-failure?vnp_Amount={res_vnp_Amount}&vnp_TxnRef={response['vnp_TxnRef']}"
            )

        logger.info("Payment validation succeeded")
        return RedirectResponse(
            f"{settings.REDIRECT_FRONTEND_URL}/success/?payment-success?vnp_Amount={res_vnp_Amount}&vnp_TxnRef={response['vnp_TxnRef']}&vnp_TransactionNo={response['vnp_TransactionNo']}"
        )

    def get_edit_one_with_filter_or_none(
        self, db: Session, filter: dict
    ) -> Optional[UserSubscriptionOut]:
        try:
            return self.__crud_user_subscription.get_one_by(db=db, filter=filter)
        except:
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.get_edit_one_with_filter_or_none"
            )
            return None


    def get_all_or_none(
        self, db: Session, current_user_membership: UserSubscriptionPlan
    ) -> Optional[List[UserSubscriptionOut]]:
        try:
            results = self.__crud_user_subscription.get_multi(
                db=db, filter_param={"user_id": current_user_membership.u_id}
            )
            return results
        except:
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.get_all_or_none"
            )
            return None