from pydantic import BaseModel


class FsWriteRequest(BaseModel):
    path: str
    content: str = ""
    encoding: str = "utf-8"
    create_dirs: bool = True


class FsMkdirRequest(BaseModel):
    path: str


class FsRenameRequest(BaseModel):
    path: str
    next_path: str


class FsEntry(BaseModel):
    name: str
    path: str
    type: str
    size: int
    updated_at: str
