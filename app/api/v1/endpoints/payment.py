from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api import deps
from app.common.logger import setup_logger
from app.services.abc.payment_vnpay_service import PaymentVnPayService
from app.services.impl.payment_vnpay_service_impl import PaymentVnPayServiceImpl

logger = setup_logger()

payment_vnpay_service: PaymentVnPayService = PaymentVnPayServiceImpl()

router = APIRouter()


@router.get("/payment", status_code=status.HTTP_200_OK)
def read_root(
    vnp_Amount: str = Query(..., description="Amount to be paid"),
    vnp_TxnRef: str = Query(..., description="Transaction reference"),
    vnp_OrderInfo: str = Query(..., description="Order information"),
) -> RedirectResponse:
    """
    Ngân hàng: NCB
    Số thẻ: 9704198526191432198
    Tên chủ thẻ: NGUYEN VAN A
    Ngày phát hành: 07/15
    Mật khẩu OTP: 123456
    """
    return payment_vnpay_service.read_root(
        vnp_Amount, vnp_TxnRef, vnp_OrderInfo
    )


@router.get("/payment-return", status_code=status.HTTP_200_OK)
def read_item(
    request: Request,
    db: Session = Depends(deps.get_db),
) -> RedirectResponse:
    return payment_vnpay_service.read_item(request=request, db=db)
