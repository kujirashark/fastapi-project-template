"""标签路由。"""

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, TagServiceDep
from app.domain.schemas.tag import TagCreate, TagOut

router = APIRouter()


@router.get(
    "",
    response_model=list[TagOut],
    summary="标签列表",
)
async def list_tags(
    tag_service: TagServiceDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[TagOut]:
    items = await tag_service.list(skip=skip, limit=limit)
    return [TagOut.model_validate(t) for t in items]


@router.post(
    "",
    response_model=TagOut,
    status_code=status.HTTP_201_CREATED,
    summary="创建标签(需要登录)",
)
async def create_tag(
    data: TagCreate,
    _current_user: CurrentUser,
    tag_service: TagServiceDep,
) -> TagOut:
    tag = await tag_service.create(data)
    return TagOut.model_validate(tag)


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除标签(需要登录)",
)
async def delete_tag(
    tag_id: int,
    _current_user: CurrentUser,
    tag_service: TagServiceDep,
) -> None:
    await tag_service.delete(tag_id)