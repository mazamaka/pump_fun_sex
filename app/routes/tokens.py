from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from ..models import TokenEventRead
from ..repository import TokenEventRepository

router = APIRouter(prefix="/tokens", tags=["tokens"])


@router.get("/", response_model=List[TokenEventRead])
def list_tokens(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    repo: TokenEventRepository = Depends(TokenEventRepository),
):
    return repo.list(limit=limit, offset=offset)


@router.get("/{signature}", response_model=TokenEventRead)
def get_token(signature: str, repo: TokenEventRepository = Depends(TokenEventRepository)):
    obj = repo.get_by_signature(signature)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj
