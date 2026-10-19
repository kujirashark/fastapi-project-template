"""分类路由。"""

from fastapi import APIRouter, Query, status

from app.api.deps import CategoryServiceDep, CurrentUser
from app.domain.schemas.category import CategoryCreate, CategoryOut

router = APIRouter()


@router.get(
    "",
    response_model=list[CategoryOut],
    summary="分类列表",
)
async def list_categories(
    category_service: CategoryServiceDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[CategoryOut]:
    items = await category_service.list(skip=skip, limit=limit)
    return [CategoryOut.model_validate(c) for c in items]


@router.post(
    "",
    response_model=CategoryOut,
    status_code=status.HTTP_201_CREATED,
    summary="创建分类(需要登录)",
)
async def create_category(
    data: CategoryCreate,
    _current_user: CurrentUser,
    category_service: CategoryServiceDep,
) -> CategoryOut:
    category = await category_service.create(data)
    return CategoryOut.model_validate(category)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除分类(需要登录)",
)
async def delete_category(
    category_id: int,
    _current_user: CurrentUser,
    category_service: CategoryServiceDep,
) -> None:
    await category_service.delete(category_id)