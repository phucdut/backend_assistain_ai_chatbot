from fastapi import APIRouter

router = APIRouter()


@router.get("/model")
def get_models():
    models = ['gpt-3.5-turbo', 'gpt-4o', 'gpt-4-turbo']
    total = len(models)
    model_out = {
        "total": total,
        "models": models
    }
    return model_out