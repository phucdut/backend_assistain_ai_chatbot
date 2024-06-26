import datetime
import json
import os
import traceback
import uuid
from typing import List, Optional

import PyPDF2
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.common import utils
from fastapi.responses import JSONResponse
from app.common.logger import setup_logger
from app.crud.crud_knowledgeBase import crud_knowledgebase
from app.schemas.knowledge_base import (
    KnowledgeBaseAdd,
    KnowledgeBaseInDB,
    KnowledgeBaseOut,
    KnowledgeBaseRemove,
)
from app.services.abc.knowledgebase_service import KnowledgeBaseService
from app.schemas.user_subscription_plan import UserSubscriptionPlan


logger = setup_logger()


class KnowledgeBaseServiceImpl(KnowledgeBaseService):

    def __init__(self):
        self.__crud_knowledgeBase = crud_knowledgebase

    def create(
        self, db: Session, chatbot_id: str, file_path: str, file_name: str
    ) -> KnowledgeBaseOut:
        try:
            # # Kiểm tra xem tiêu đề kiến thức đã tồn tại trong cơ sở dữ liệu chưa
            # existing_knowledge_base = (
            #     self.__crud_knowledgeBase.get_by_name_knowledge_base(
            #         db=db, name=file_name, chatbot_id=chatbot_id
            #     )
            # )
            # if existing_knowledge_base:
            #     logger.exception(
            #         f"Exception in {__name__}.{self.__class__.__name__}.create: Tiêu đề kiến thức đã tồn tại"
            #     )
            #     raise HTTPException(
            #         detail="Thêm kiến thức thất bại: Tiêu đề kiến thức đã tồn tại",
            #         status_code=400,
            #     )

            # Đọc nội dung từ tệp tin
            if not os.path.exists(file_path):
                raise HTTPException(
                    detail=f"File path {file_path} does not exist.",
                    status_code=400,
                )

            content_data = None
            if file_name.endswith(".pdf"):
                content_data = utils.read_pdf(file_path)
            elif file_name.endswith(".csv"):
                content_data = utils.read_csv(file_path)
            elif file_name.endswith(".docx"):
                content_data = utils.read_docx(file_path)
            else:
                raise HTTPException(
                    detail="Unsupported file type",
                    status_code=400,
                )

            # Xây dựng dữ liệu cho mục kiến thức
            knowledge_base_data = {
                "title": file_name,  # Thêm tiêu đề phù hợp
                "content_type": file_name.split(".")[
                    -1
                ].lower(),  # Định dạng loại nội dung dựa trên tên tệp
                "file_path": file_path,
                "character_count": len(content_data),
                "file_size": os.path.getsize(file_path),
                "chatbot_id": chatbot_id,
            }

            # Tạo mục kiến thức mới trong cơ sở dữ liệu
            KN_created = self.__crud_knowledgeBase.create(
                db=db, obj_in=knowledge_base_data
            )

            if KN_created:
                result: KnowledgeBaseOut = KnowledgeBaseOut(
                    **KN_created.__dict__
                )
                return result

        except HTTPException:
            raise  # Ném lại HTTPException để truyền lên
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(
                detail="Adding knowledge about failures", status_code=400
            )

    def get_knowledgeBase_by_chatbot_id(self, db: Session, chatbot_id: str):
        try:
            chatbot_id = uuid.UUID(chatbot_id)
            knowledgeBases = (
                self.__crud_knowledgeBase.get_knowledgeBase_by_chatbot_id(
                    db, chatbot_id
                )
            )
            knowledgeBases_dict = [
                dict(**knowledgeBase.__dict__)
                for knowledgeBase in knowledgeBases
            ]
            return knowledgeBases_dict
        except:
            traceback.print_exc()
            pass

    def get_all(
        self,
        db: Session,
        chatbot_id: str,
        current_user_role_permission: str,  # Thêm đối số này
    ) -> List[KnowledgeBaseInDB]:
        if "read_knowledge_base" not in current_user_role_permission:
            raise HTTPException(
                status_code=400,
                detail="User does not have permission to read knowledge base",
            )

        try:
            chatbot_found = self.__crud_chatbot.get_one_by(
                db=db, filter={"id": chatbot_id}
            )
            if chatbot_found is None:
                raise HTTPException(status_code=404, detail="Chatbot not found")

            knowledge_bases: List[KnowledgeBaseInDB] = (
                self.__crud_knowledge_base.get_multi(
                    db=db,
                    filter_param={
                        "filter": json.dumps(
                            {"chatbot_id": str(chatbot_found.id)}
                        )
                    },
                )
            )
            return knowledge_bases
        except Exception as e:
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.get_all"
            )
            raise HTTPException(
                status_code=400, detail="Get all knowledge base failed"
            )

    def delete(
        self,
        db: Session,
        chatbot_id: str,
        knowledge_base_id: str,
        # current_user_membership: UserSubscriptionPlan,
    ):
        try:
            knowledge_base_found = self.__crud_knowledgeBase.get_one_by(
                db=db,
                filter={"id": knowledge_base_id, "chatbot_id": chatbot_id},
            )

            if knowledge_base_found is None:
                return JSONResponse(
                    status_code=404,
                    content={
                        "status": 404,
                        "message": "Knowledge base not found",
                    },
                )

            knowledge_base_deleted = self.__crud_knowledgeBase.remove(
                db=db, id=knowledge_base_found.id
            )
        except:
            logger.exception(
                f"Exception in {__name__}.{self.__class__.__name__}.remove_knowledge_base"
            )
            return JSONResponse(
                status_code=400,
                content={
                    "status": 400,
                    "message": "Remove knowledge base failed",
                },
            )
        return {
            "chatbot_id": chatbot_id,
            "knowledge_base": {
                "id": knowledge_base_deleted.id,
                "knowledge_base_name": knowledge_base_deleted.title,
                "deleted_at": knowledge_base_deleted.deleted_at,
            },
        }
