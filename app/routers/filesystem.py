from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from app.dependencies import CurrentUser
from app.schemas.filesystem import FsWriteRequest, FsMkdirRequest, FsRenameRequest
from app.services import fs_service

router = APIRouter(prefix="/api/fs")


def _guard(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except (FileNotFoundError, IsADirectoryError, NotADirectoryError, OSError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/list")
async def fs_list(user: CurrentUser, path: str = Query(default="")):
    return _guard(fs_service.list_dir, user["id"], path)


@router.get("/read")
async def fs_read(user: CurrentUser, path: str = Query(...)):
    return _guard(fs_service.read_file, user["id"], path)


@router.get("/download")
async def fs_download(user: CurrentUser, path: str = Query(...)):
    try:
        resolved = fs_service.resolve_path(user["id"], path)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not resolved.is_file():
        raise HTTPException(status_code=400, detail="Path is not a file")
    return FileResponse(str(resolved), filename=resolved.name)


@router.post("/write")
async def fs_write(body: FsWriteRequest, user: CurrentUser):
    return _guard(fs_service.write_file, user["id"], body.path, body.content, body.encoding, body.create_dirs)


@router.post("/mkdir")
async def fs_mkdir(body: FsMkdirRequest, user: CurrentUser):
    return _guard(fs_service.make_dir, user["id"], body.path)


@router.post("/rename")
async def fs_rename(body: FsRenameRequest, user: CurrentUser):
    return _guard(fs_service.rename_entry, user["id"], body.path, body.next_path)


@router.delete("/delete")
async def fs_delete(user: CurrentUser, path: str = Query(...)):
    return _guard(fs_service.delete_entry, user["id"], path)
