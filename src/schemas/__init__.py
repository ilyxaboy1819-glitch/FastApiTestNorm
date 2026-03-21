from .user import UserRead, UserCreate, UserUpdate
from .profile import ProfileRead, ProfileCreate, ProfileBase
from .role import RoleRead, RoleCreate, RoleUpdate
from .application import ApplicationRead, ApplicationCreate, ApplicationUpdate
from .category import CategoryRead, CategoryUpdate
from .comment import CommentRead, CommentCreate

CategoryRead.model_rebuild()
RoleRead.model_rebuild()
CommentRead.model_rebuild()
ApplicationRead.model_rebuild()
ProfileRead.model_rebuild()
UserRead.model_rebuild()
